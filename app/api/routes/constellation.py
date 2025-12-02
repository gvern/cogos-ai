from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime, timedelta
import numpy as np
from pydantic import BaseModel

# Import existing memory and context modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from ...core.memory import query_memory, add_memory_entry, get_recent_entries
from ...core.context_loader import get_raw_context, update_context

router = APIRouter(prefix="/api", tags=["constellation"])

# Pydantic models for API responses
class KnowledgeNode(BaseModel):
    id: str
    label: str
    type: str  # 'concept', 'memory', 'skill', 'goal', 'context'
    domain: str
    importance: float
    connections: List[str]
    position: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None

class KnowledgeLink(BaseModel):
    source: str
    target: str
    strength: float
    type: str  # 'association', 'dependency', 'similarity', 'temporal'

class KnowledgeGraph(BaseModel):
    nodes: List[KnowledgeNode]
    links: List[KnowledgeLink]

class SearchRequest(BaseModel):
    query: str
    limit: int = 50
    filters: Optional[Dict[str, Any]] = None

class ConstellationAPI:
    def __init__(self):
        # Use the imported functions directly instead of class instances
        self._domain_keywords = {
            'technology': ['code', 'programming', 'software', 'tech', 'development', 'ai', 'machine learning', 'computer'],
            'personal': ['goal', 'reflection', 'personal', 'life', 'growth', 'habit', 'diary', 'journal'],
            'work': ['project', 'task', 'meeting', 'work', 'professional', 'career', 'business'],
            'learning': ['study', 'learn', 'education', 'knowledge', 'skill', 'training', 'course'],
            'creative': ['art', 'design', 'creative', 'writing', 'music', 'visual', 'artistic'],
            'health': ['health', 'fitness', 'wellness', 'exercise', 'medical', 'physical'],
            'social': ['social', 'relationship', 'community', 'network', 'people', 'friend']
        }

    def _infer_domain(self, content: str, tags: List[str] = None) -> str:
        """Infer domain based on content and tags"""
        content_lower = content.lower()
        tags_lower = [tag.lower() for tag in (tags or [])]
        
        domain_scores = {}
        
        for domain, keywords in self._domain_keywords.items():
            score = 0
            for keyword in keywords:
                # Check in content
                if keyword in content_lower:
                    score += content_lower.count(keyword)
                
                # Check in tags (higher weight)
                for tag in tags_lower:
                    if keyword in tag:
                        score += 2
            
            domain_scores[domain] = score
        
        # Return domain with highest score, or 'general' if no matches
        if not domain_scores or max(domain_scores.values()) == 0:
            return 'general'
        
        return max(domain_scores, key=domain_scores.get)

    def _calculate_importance(self, content: str, timestamp: str = None, tags: List[str] = None) -> float:
        """Calculate importance score for a piece of content"""
        importance = 0.3  # Base importance
        
        # Factor in content length (longer might be more important)
        content_length = len(content)
        importance += min(content_length / 5000, 0.3)
        
        # Factor in recency if timestamp available
        if timestamp:
            try:
                created_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                days_old = (datetime.now() - created_date.replace(tzinfo=None)).days
                recency_score = max(0, (30 - days_old) / 30 * 0.3)
                importance += recency_score
            except:
                pass
        
        # Factor in tags (more tags might indicate importance)
        if tags:
            importance += min(len(tags) * 0.05, 0.2)
        
        # Factor in specific keywords that indicate importance
        important_keywords = ['important', 'critical', 'urgent', 'key', 'major', 'significant']
        for keyword in important_keywords:
            if keyword in content.lower():
                importance += 0.1
                break
        
        return min(importance, 1.0)

    def _extract_title(self, content: str, max_length: int = 60) -> str:
        """Extract a meaningful title from content"""
        lines = content.strip().split('\n')
        first_line = lines[0].strip()
        
        # If first line looks like a title (short and doesn't end with punctuation)
        if len(first_line) <= max_length and not first_line.endswith(('.', '!', '?')):
            return first_line
        
        # Otherwise, use first sentence or truncated content
        sentences = content.split('.')
        first_sentence = sentences[0].strip()
        
        if len(first_sentence) <= max_length:
            return first_sentence
        
        return content[:max_length-3].strip() + '...'

    async def get_memories(self) -> List[Dict[str, Any]]:
        """Get all memory entries"""
        try:
            memories = []
            
            # Load from memory.jsonl if it exists
            memory_file = "ingested/memory.jsonl"
            if os.path.exists(memory_file):
                with open(memory_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                entry = json.loads(line)
                                memories.append({
                                    'id': entry.get('id', str(hash(entry.get('text', '')))),
                                    'content': entry.get('text', entry.get('content', '')),
                                    'timestamp': entry.get('metadata', {}).get('created_at', datetime.now().isoformat()),
                                    'tags': entry.get('metadata', {}).get('tags', []),
                                    'importance': entry.get('importance', 0.5),
                                    'context': f"Source: {entry.get('metadata', {}).get('source', 'unknown')}",
                                    'embedding': entry.get('embedding')
                                })
                            except json.JSONDecodeError as e:
                                continue
            
            # Also check for data/journal files
            journal_dir = "data/journal"
            if os.path.exists(journal_dir):
                for filename in os.listdir(journal_dir):
                    if filename.endswith('.txt') or filename.endswith('.md'):
                        filepath = os.path.join(journal_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if content.strip():
                                    # Extract date from filename if possible
                                    file_date = filename.replace('.txt', '').replace('.md', '')
                                    memories.append({
                                        'id': f"journal_{filename}",
                                        'content': content,
                                        'timestamp': file_date if file_date.replace('-', '').isdigit() else datetime.now().isoformat(),
                                        'tags': ['journal'],
                                        'importance': 0.6,
                                        'context': f'Journal entry from {filename}'
                                    })
                        except:
                            continue
            
            return memories
        except Exception as e:
            print(f"Error loading memories: {e}")
            return []

    async def get_contexts(self) -> List[Dict[str, Any]]:
        """Get all context entries"""
        try:
            contexts = []
            
            # Load context from memory_mcp.json if it exists
            context_file = "memory/context_mcp.json"
            if os.path.exists(context_file):
                with open(context_file, 'r', encoding='utf-8') as f:
                    try:
                        context_data = json.load(f)
                        for section, content in context_data.items():
                            if isinstance(content, str) and content.strip():
                                contexts.append({
                                    'id': f"context_{section}",
                                    'type': 'context',
                                    'title': section.replace('_', ' ').title(),
                                    'content': content,
                                    'domain': self._infer_domain(content),
                                    'relationships': [],
                                    'lastModified': datetime.now().isoformat()
                                })
                    except json.JSONDecodeError:
                        pass
            
            # Load notes
            notes_dir = "data/notes"
            if os.path.exists(notes_dir):
                for filename in os.listdir(notes_dir):
                    if filename.endswith('.txt') or filename.endswith('.md'):
                        filepath = os.path.join(notes_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if content.strip():
                                    contexts.append({
                                        'id': f"note_{filename}",
                                        'type': 'note',
                                        'title': filename.replace('.txt', '').replace('.md', ''),
                                        'content': content,
                                        'domain': self._infer_domain(content),
                                        'relationships': [],
                                        'lastModified': datetime.fromtimestamp(
                                            os.path.getmtime(filepath)
                                        ).isoformat()
                                    })
                        except:
                            continue
            
            return contexts
        except Exception as e:
            print(f"Error loading contexts: {e}")
            return []

    async def get_agent_actions(self) -> List[Dict[str, Any]]:
        """Get agent action history"""
        try:
            actions = []
            
            # Load from agent_actions.json if it exists
            actions_file = "data/agent_actions.json"
            if os.path.exists(actions_file):
                with open(actions_file, 'r', encoding='utf-8') as f:
                    try:
                        actions_data = json.load(f)
                        if isinstance(actions_data, list):
                            actions = actions_data
                        elif isinstance(actions_data, dict) and 'actions' in actions_data:
                            actions = actions_data['actions']
                    except json.JSONDecodeError:
                        pass
            
            # Ensure each action has required fields
            processed_actions = []
            for action in actions:
                if isinstance(action, dict):
                    processed_actions.append({
                        'id': action.get('id', str(hash(str(action)))),
                        'action': action.get('action', 'Unknown action'),
                        'timestamp': action.get('timestamp', datetime.now().isoformat()),
                        'context': action.get('context', ''),
                        'outcome': action.get('outcome', ''),
                        'skills_used': action.get('skills_used', action.get('skills', ['general']))
                    })
            
            return processed_actions
        except Exception as e:
            print(f"Error loading agent actions: {e}")
            return []

    def transform_to_knowledge_graph(self, memories: List[Dict], contexts: List[Dict], actions: List[Dict]) -> KnowledgeGraph:
        """Transform raw data into knowledge graph format"""
        nodes = []
        links = []
        
        # Transform memories to nodes
        for memory in memories:
            nodes.append(KnowledgeNode(
                id=f"memory_{memory['id']}",
                label=self._extract_title(memory['content']),
                type='memory',
                domain=self._infer_domain(memory['content'], memory.get('tags', [])),
                importance=memory.get('importance', self._calculate_importance(
                    memory['content'], 
                    memory.get('timestamp'),
                    memory.get('tags')
                )),
                connections=[],
                metadata={
                    'timestamp': memory.get('timestamp'),
                    'tags': memory.get('tags', []),
                    'full_content': memory['content'][:500] + '...' if len(memory['content']) > 500 else memory['content'],
                    'embedding': memory.get('embedding')
                }
            ))
        
        # Transform contexts to nodes
        for context in contexts:
            nodes.append(KnowledgeNode(
                id=f"context_{context['id']}",
                label=context['title'],
                type='concept' if context['type'] == 'note' else 'context',
                domain=context['domain'],
                importance=self._calculate_importance(
                    context['content'],
                    context.get('lastModified')
                ),
                connections=context.get('relationships', []),
                metadata={
                    'last_modified': context.get('lastModified'),
                    'original_type': context['type'],
                    'full_content': context['content'][:500] + '...' if len(context['content']) > 500 else context['content']
                }
            ))
        
        # Transform actions to skill nodes
        skill_map = {}
        for action in actions:
            for skill in action.get('skills_used', []):
                if skill not in skill_map:
                    skill_map[skill] = []
                skill_map[skill].append(action)
        
        for skill, related_actions in skill_map.items():
            nodes.append(KnowledgeNode(
                id=f"skill_{skill.replace(' ', '_').lower()}",
                label=skill,
                type='skill',
                domain=self._infer_skill_domain(skill, related_actions),
                importance=min(len(related_actions) / 10, 1.0),
                connections=[],
                metadata={
                    'usage_count': len(related_actions),
                    'last_used': max(action.get('timestamp', '') for action in related_actions),
                    'related_actions': [action['id'] for action in related_actions[:5]]  # Limit to 5
                }
            ))
        
        # Generate links based on various relationships
        links = self._generate_links(nodes)
        
        return KnowledgeGraph(nodes=nodes, links=links)

    def _infer_skill_domain(self, skill: str, actions: List[Dict]) -> str:
        """Infer domain for a skill based on its usage"""
        skill_lower = skill.lower()
        
        domain_mapping = {
            'technology': ['code', 'program', 'develop', 'software', 'tech', 'computer', 'web', 'api'],
            'creative': ['write', 'design', 'create', 'art', 'music', 'visual', 'content'],
            'learning': ['analyze', 'research', 'study', 'learn', 'understand', 'knowledge'],
            'work': ['plan', 'organize', 'manage', 'schedule', 'coordinate', 'business'],
            'personal': ['reflect', 'journal', 'goal', 'habit', 'personal', 'growth']
        }
        
        for domain, keywords in domain_mapping.items():
            if any(keyword in skill_lower for keyword in keywords):
                return domain
        
        return 'general'

    def _generate_links(self, nodes: List[KnowledgeNode]) -> List[KnowledgeLink]:
        """Generate links between nodes based on various relationships"""
        links = []
        
        # 1. Tag-based links for memory nodes
        memory_nodes = [n for n in nodes if n.type == 'memory']
        for i, node1 in enumerate(memory_nodes):
            for node2 in memory_nodes[i+1:]:
                tags1 = set(node1.metadata.get('tags', []))
                tags2 = set(node2.metadata.get('tags', []))
                common_tags = tags1.intersection(tags2)
                
                if common_tags:
                    strength = len(common_tags) / max(len(tags1), len(tags2), 1)
                    links.append(KnowledgeLink(
                        source=node1.id,
                        target=node2.id,
                        strength=min(strength, 0.8),
                        type='association'
                    ))
        
        # 2. Domain-based links (weaker connections)
        domain_groups = {}
        for node in nodes:
            if node.domain not in domain_groups:
                domain_groups[node.domain] = []
            domain_groups[node.domain].append(node)
        
        for domain_nodes in domain_groups.values():
            if len(domain_nodes) > 1:
                # Create sparse connections within domain
                for i, node in enumerate(domain_nodes):
                    # Connect to a few other nodes in the same domain
                    connections = min(3, len(domain_nodes) - 1)
                    for j in range(1, connections + 1):
                        target_idx = (i + j) % len(domain_nodes)
                        if target_idx != i:
                            links.append(KnowledgeLink(
                                source=node.id,
                                target=domain_nodes[target_idx].id,
                                strength=0.2,
                                type='association'
                            ))
        
        # 3. Temporal links for recent items
        recent_nodes = [n for n in nodes if n.metadata and n.metadata.get('timestamp')]
        recent_nodes.sort(key=lambda n: n.metadata.get('timestamp', ''), reverse=True)
        
        # Link recent items together
        for i in range(min(10, len(recent_nodes))):
            for j in range(i+1, min(i+4, len(recent_nodes))):
                links.append(KnowledgeLink(
                    source=recent_nodes[i].id,
                    target=recent_nodes[j].id,
                    strength=0.3,
                    type='temporal'
                ))
        
        # 4. Importance-based links (connect high-importance nodes)
        important_nodes = [n for n in nodes if n.importance > 0.7]
        for i, node1 in enumerate(important_nodes):
            for node2 in important_nodes[i+1:i+3]:  # Limit connections
                if node1.domain == node2.domain:  # Same domain
                    links.append(KnowledgeLink(
                        source=node1.id,
                        target=node2.id,
                        strength=0.4,
                        type='association'
                    ))
        
        return links

# Initialize API instance
constellation_api = ConstellationAPI()

@router.get("/memories", response_model=List[Dict[str, Any]])
async def get_memories():
    """Get all memory entries"""
    return await constellation_api.get_memories()

@router.get("/contexts", response_model=List[Dict[str, Any]])
async def get_contexts():
    """Get all context entries"""
    return await constellation_api.get_contexts()

@router.get("/agent/actions", response_model=List[Dict[str, Any]])
async def get_agent_actions():
    """Get agent action history"""
    return await constellation_api.get_agent_actions()

@router.get("/knowledge-graph", response_model=KnowledgeGraph)
async def get_knowledge_graph():
    """Get complete knowledge graph"""
    try:
        memories = await constellation_api.get_memories()
        contexts = await constellation_api.get_contexts()
        actions = await constellation_api.get_agent_actions()
        
        return constellation_api.transform_to_knowledge_graph(memories, contexts, actions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate knowledge graph: {str(e)}")

@router.post("/search", response_model=KnowledgeGraph)
async def search_knowledge(request: SearchRequest):
    """Search knowledge graph"""
    try:
        # Get all data first
        memories = await constellation_api.get_memories()
        contexts = await constellation_api.get_contexts()
        actions = await constellation_api.get_agent_actions()
        
        # Filter based on search query
        query_lower = request.query.lower()
        
        filtered_memories = [
            m for m in memories 
            if query_lower in m.get('content', '').lower() or 
               any(query_lower in tag.lower() for tag in m.get('tags', []))
        ]
        
        filtered_contexts = [
            c for c in contexts
            if query_lower in c.get('title', '').lower() or 
               query_lower in c.get('content', '').lower()
        ]
        
        filtered_actions = [
            a for a in actions
            if query_lower in a.get('action', '').lower() or
               any(query_lower in skill.lower() for skill in a.get('skills_used', []))
        ]
        
        # Transform to knowledge graph
        graph = constellation_api.transform_to_knowledge_graph(
            filtered_memories[:request.limit//3], 
            filtered_contexts[:request.limit//3], 
            filtered_actions[:request.limit//3]
        )
        
        return graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/stats")
async def get_knowledge_stats():
    """Get knowledge graph statistics"""
    try:
        memories = await constellation_api.get_memories()
        contexts = await constellation_api.get_contexts()
        actions = await constellation_api.get_agent_actions()
        
        # Calculate domain distribution
        all_content = memories + contexts
        domain_counts = {}
        for item in all_content:
            domain = constellation_api._infer_domain(
                item.get('content', item.get('title', '')),
                item.get('tags', [])
            )
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Calculate skill usage
        skill_counts = {}
        for action in actions:
            for skill in action.get('skills_used', []):
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        return {
            'total_memories': len(memories),
            'total_contexts': len(contexts),
            'total_actions': len(actions),
            'domain_distribution': domain_counts,
            'top_skills': dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'last_updated': datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
