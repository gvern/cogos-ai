'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ConstellationScene from '@/components/constellation/ConstellationScene';
import { Button } from '@/components/ui/button';
import { RefreshCw, ArrowLeft } from 'lucide-react';

const ConstellationPage = () => {
    const router = useRouter();
    const [constellationData, setConstellationData] = useState<{ nodes: any[], links: any[] }>({ nodes: [], links: [] });
    const [selectedNode, setSelectedNode] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [retryCount, setRetryCount] = useState(0);

    // Sample data for testing
    const getSampleData = () => ({
        nodes: [
            {
                id: 'ai-1',
                title: 'Machine Learning Fundamentals',
                content: 'Core concepts of machine learning including supervised, unsupervised, and reinforcement learning',
                type: 'concept',
                domain: 'AI',
                importance: 0.9,
                position: { x: 0, y: 0, z: 0 }
            },
            {
                id: 'ai-2',
                title: 'Neural Networks',
                content: 'Deep learning architectures and neural network designs',
                type: 'technical',
                domain: 'AI',
                importance: 0.8,
                position: { x: 5, y: 2, z: 1 }
            },
            {
                id: 'dev-1',
                title: 'React Development',
                content: 'Frontend development with React and modern JavaScript',
                type: 'skill',
                domain: 'Development',
                importance: 0.7,
                position: { x: -3, y: 1, z: -2 }
            },
            {
                id: 'proj-1',
                title: 'CogOS Project',
                content: 'Personal cognitive operating system with AI capabilities',
                type: 'project',
                domain: 'Projects',
                importance: 0.95,
                position: { x: 2, y: -1, z: 3 }
            },
            {
                id: 'data-1',
                title: 'Vector Databases',
                content: 'Understanding embeddings and vector similarity search',
                type: 'technical',
                domain: 'Data',
                importance: 0.6,
                position: { x: -1, y: 3, z: -1 }
            }
        ],
        links: [
            { source: 'ai-1', target: 'ai-2', strength: 0.9 },
            { source: 'ai-2', target: 'proj-1', strength: 0.7 },
            { source: 'dev-1', target: 'proj-1', strength: 0.8 },
            { source: 'data-1', target: 'ai-1', strength: 0.6 },
            { source: 'data-1', target: 'proj-1', strength: 0.5 }
        ]
    });

    // Load constellation data from API or use sample data
    const loadConstellation = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch('http://localhost:8001/api/knowledge-graph', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            setConstellationData(data);
            setLoading(false);
        } catch (err) {
            console.warn('API not available, using sample data:', err);
            // Use sample data when API is not available
            setConstellationData(getSampleData());
            setLoading(false);
        }
    };

    // Load data on component mount
    useEffect(() => {
        loadConstellation();
    }, []);

    // Handle node selection
    const handleNodeSelect = (node) => {
        setSelectedNode(node);
    };

    // Handle retry
    const handleRetry = () => {
        setRetryCount(prev => prev + 1);
        loadConstellation();
    };

    // Navigate back to dashboard
    const handleBackToDashboard = () => {
        router.push('/dashboard');
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 text-white relative overflow-hidden">
            {/* Header */}
            <div className="absolute top-0 left-0 right-0 z-10 p-4 border-b border-white/10 bg-black/30 backdrop-blur-md">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-400 via-blue-500 to-orange-500">
                            🌌 CogOS Knowledge Constellation
                        </h1>
                        <p className="text-sm text-gray-400 mt-1">
                            Interactive 3D visualization of your knowledge graph
                        </p>
                    </div>

                    <div className="flex gap-2">
                        <Button
                            onClick={handleRetry}
                            variant="outline"
                            className="bg-green-500/20 border-green-500 text-white hover:bg-green-500/30"
                        >
                            <RefreshCw className="mr-2 h-4 w-4" />
                            Refresh
                        </Button>
                        <Button
                            onClick={handleBackToDashboard}
                            variant="outline"
                            className="bg-blue-500/20 border-blue-500 text-white hover:bg-blue-500/30"
                        >
                            <ArrowLeft className="mr-2 h-4 w-4" />
                            Dashboard
                        </Button>
                    </div>
                </div>
            </div>

            {/* Status Panel */}
            {(loading || error) && (
                <div className="absolute inset-0 flex items-center justify-center z-20 pointer-events-none">
                    <div className="bg-white/10 p-8 rounded-xl backdrop-blur-md border border-white/20 text-center pointer-events-auto max-w-md">
                        {loading && (
                            <div>
                                <div className="w-12 h-12 border-4 border-white/30 border-t-green-500 rounded-full animate-spin mx-auto mb-4" />
                                <div className="text-xl font-bold mb-2">
                                    🔄 Loading your knowledge constellation...
                                </div>
                                <div className="text-gray-400">
                                    Fetching nodes and connections from the knowledge graph
                                </div>
                            </div>
                        )}

                        {error && (
                            <div>
                                <div className="text-red-400 text-xl font-bold mb-4">
                                    ❌ Connection Error
                                </div>
                                <div className="mb-4">
                                    Cannot connect to CogOS backend
                                </div>
                                <div className="bg-black/30 p-4 rounded-lg font-mono text-sm mb-4 text-left overflow-auto max-h-32">
                                    Error: {error}
                                </div>
                                <div className="bg-white/5 p-4 rounded-lg text-sm mb-4">
                                    Make sure the backend is running:<br />
                                    <code className="text-green-400">cd app/api && python run.py</code>
                                </div>
                                <Button
                                    onClick={handleRetry}
                                    className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white rounded-full px-8"
                                >
                                    <RefreshCw className="mr-2 h-4 w-4" />
                                    Retry Connection
                                </Button>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* 3D Constellation */}
            {!loading && !error && (
                <div className="w-full h-screen">
                    <ConstellationScene
                        nodes={constellationData.nodes}
                        links={constellationData.links}
                        onNodeSelect={handleNodeSelect}
                        selectedNodeId={selectedNode?.id}
                    />
                </div>
            )}

            {/* Selected Node Details */}
            {selectedNode && (
                <div className="fixed bottom-5 left-5 right-5 md:left-auto md:right-5 md:w-96 bg-black/90 backdrop-blur-md p-6 rounded-xl border-2 border-green-500 z-30 shadow-2xl">
                    <div className="flex justify-between items-start mb-4">
                        <h3 className="text-xl font-bold text-green-500">
                            🌟 {selectedNode.label || selectedNode.id}
                        </h3>
                        <button
                            onClick={() => setSelectedNode(null)}
                            className="text-white/70 hover:text-white"
                        >
                            ✕
                        </button>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                        <div>
                            <strong className="text-gray-400">Type:</strong>
                            <div className="capitalize">{selectedNode.type}</div>
                        </div>
                        <div>
                            <strong className="text-gray-400">Domain:</strong>
                            <div>{selectedNode.domain || 'General'}</div>
                        </div>
                        <div>
                            <strong className="text-gray-400">Importance:</strong>
                            <div>{Math.round((selectedNode.importance || 0) * 100)}%</div>
                        </div>
                    </div>

                    {selectedNode.metadata?.full_content && (
                        <div>
                            <strong className="text-gray-400 text-sm">Content:</strong>
                            <div className="mt-2 p-3 bg-white/5 rounded-lg text-sm leading-relaxed max-h-40 overflow-y-auto">
                                {selectedNode.metadata.full_content}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default ConstellationPage;
