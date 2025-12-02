import React, { useState } from 'react'

const ConstellationControls = ({ 
  nodes = [], 
  onNodeSelect = () => {}, 
  selectedNodeId = null 
}) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [filterType, setFilterType] = useState('all')
  const [sortBy, setSortBy] = useState('importance')

  const nodeTypes = ['all', 'memory', 'context', 'skill', 'concept']
  
  // Filter and sort nodes
  const filteredNodes = nodes
    .filter(node => filterType === 'all' || node.type === filterType)
    .sort((a, b) => {
      switch (sortBy) {
        case 'importance':
          return (b.importance || 0) - (a.importance || 0)
        case 'label':
          return (a.label || a.id).localeCompare(b.label || b.id)
        case 'type':
          return a.type.localeCompare(b.type)
        default:
          return 0
      }
    })

  const getTypeColor = (type) => {
    const colors = {
      memory: '#4CAF50',
      context: '#2196F3',
      skill: '#FF9800',
      concept: '#9C27B0'
    }
    return colors[type] || '#ffffff'
  }

  const getTypeEmoji = (type) => {
    const emojis = {
      memory: '💭',
      context: '🌐',
      skill: '⚡',
      concept: '💡'
    }
    return emojis[type] || '🔵'
  }

  return (
    <div style={{
      position: 'absolute',
      top: '10px',
      right: '10px',
      width: isExpanded ? '350px' : '60px',
      maxHeight: '80vh',
      background: 'rgba(0, 0, 0, 0.8)',
      backdropFilter: 'blur(10px)',
      borderRadius: '12px',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      transition: 'all 0.3s ease',
      zIndex: 1000,
      overflow: 'hidden'
    }}>
      {/* Toggle Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          width: '100%',
          height: '50px',
          background: 'transparent',
          border: 'none',
          color: 'white',
          fontSize: '24px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: isExpanded ? '1px solid rgba(255, 255, 255, 0.2)' : 'none'
        }}
      >
        {isExpanded ? '✕' : '⚙️'}
      </button>

      {isExpanded && (
        <div style={{ padding: '20px' }}>
          {/* Filters */}
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ 
              color: 'white', 
              margin: '0 0 10px 0', 
              fontSize: '16px' 
            }}>
              Filter by Type
            </h3>
            <div style={{ 
              display: 'flex', 
              flexWrap: 'wrap', 
              gap: '8px' 
            }}>
              {nodeTypes.map(type => (
                <button
                  key={type}
                  onClick={() => setFilterType(type)}
                  style={{
                    padding: '6px 12px',
                    background: filterType === type 
                      ? getTypeColor(type)
                      : 'rgba(255, 255, 255, 0.1)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '16px',
                    fontSize: '12px',
                    cursor: 'pointer',
                    textTransform: 'capitalize',
                    transition: 'all 0.2s ease'
                  }}
                >
                  {type === 'all' ? '🌟' : getTypeEmoji(type)} {type}
                </button>
              ))}
            </div>
          </div>

          {/* Sort Options */}
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ 
              color: 'white', 
              margin: '0 0 10px 0', 
              fontSize: '16px' 
            }}>
              Sort by
            </h3>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              style={{
                width: '100%',
                padding: '8px',
                background: 'rgba(255, 255, 255, 0.1)',
                color: 'white',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                fontSize: '14px'
              }}
            >
              <option value="importance">Importance</option>
              <option value="label">Name</option>
              <option value="type">Type</option>
            </select>
          </div>

          {/* Node List */}
          <div style={{ marginBottom: '10px' }}>
            <h3 style={{ 
              color: 'white', 
              margin: '0 0 10px 0', 
              fontSize: '16px' 
            }}>
              Nodes ({filteredNodes.length})
            </h3>
          </div>

          <div style={{
            maxHeight: '300px',
            overflowY: 'auto',
            paddingRight: '10px'
          }}>
            {filteredNodes.map(node => (
              <div
                key={node.id}
                onClick={() => onNodeSelect(node)}
                style={{
                  padding: '12px',
                  marginBottom: '8px',
                  background: selectedNodeId === node.id 
                    ? 'rgba(255, 255, 255, 0.2)' 
                    : 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '8px',
                  border: `2px solid ${selectedNodeId === node.id ? getTypeColor(node.type) : 'transparent'}`,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.15)'
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = selectedNodeId === node.id 
                    ? 'rgba(255, 255, 255, 0.2)' 
                    : 'rgba(255, 255, 255, 0.05)'
                }}
              >
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  marginBottom: '4px'
                }}>
                  <span style={{ 
                    color: 'white', 
                    fontWeight: 'bold',
                    fontSize: '14px'
                  }}>
                    {getTypeEmoji(node.type)} {node.label || node.id}
                  </span>
                  <span style={{
                    background: getTypeColor(node.type),
                    color: 'white',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    fontSize: '10px',
                    textTransform: 'uppercase'
                  }}>
                    {node.type}
                  </span>
                </div>
                
                <div style={{ 
                  fontSize: '12px', 
                  color: 'rgba(255, 255, 255, 0.7)' 
                }}>
                  Importance: {Math.round((node.importance || 0) * 100)}%
                </div>
                
                {node.domain && (
                  <div style={{ 
                    fontSize: '12px', 
                    color: 'rgba(255, 255, 255, 0.7)' 
                  }}>
                    Domain: {node.domain}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Stats */}
          <div style={{
            marginTop: '20px',
            padding: '12px',
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '8px',
            fontSize: '12px',
            color: 'rgba(255, 255, 255, 0.8)'
          }}>
            <div>Total Nodes: {nodes.length}</div>
            <div>Filtered: {filteredNodes.length}</div>
            <div>
              Types: {nodeTypes.slice(1).map(type => 
                `${getTypeEmoji(type)}${nodes.filter(n => n.type === type).length}`
              ).join(' ')}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ConstellationControls
