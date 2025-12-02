import React, { useRef, useMemo, useState, useEffect } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { 
  OrbitControls, 
  Stars, 
  Text, 
  Html, 
  Environment,
  PerspectiveCamera
} from '@react-three/drei'
import * as THREE from 'three'
import { forceSimulation, forceLink, forceManyBody, forceCenter } from 'd3-force'
import KnowledgeNode from './KnowledgeNode'
import ConnectionLines from './ConnectionLines'
import ConstellationControls from './ConstellationControls'

const ConstellationScene = ({ 
  nodes = [], 
  links = [], 
  onNodeSelect = () => {},
  selectedNodeId = null,
  cameraTarget = null 
}) => {
  const [simulation, setSimulation] = useState(null)
  const [simulatedNodes, setSimulatedNodes] = useState([])
  const [simulatedLinks, setSimulatedLinks] = useState([])
  const [isSimulating, setIsSimulating] = useState(false)

  // Initialize force simulation
  useEffect(() => {
    if (!nodes.length) return

    const nodesCopy = nodes.map(node => ({
      ...node,
      x: (Math.random() - 0.5) * 20,
      y: (Math.random() - 0.5) * 20,
      z: (Math.random() - 0.5) * 20,
      vx: 0,
      vy: 0,
      vz: 0
    }))

    const linksCopy = links.map(link => ({
      ...link,
      source: nodesCopy.find(n => n.id === link.source),
      target: nodesCopy.find(n => n.id === link.target)
    })).filter(link => link.source && link.target)

    const sim = forceSimulation(nodesCopy)
      .force('link', forceLink(linksCopy).id(d => d.id).distance(5).strength(0.1))
      .force('charge', forceManyBody().strength(-100))
      .force('center', forceCenter(0, 0, 0))
      .force('collision', forceManyBody().strength(0.1).distanceMax(3))

    let iterationCount = 0
    const maxIterations = 300

    setIsSimulating(true)

    sim.on('tick', () => {
      iterationCount++
      
      // Add some 3D positioning
      nodesCopy.forEach(node => {
        if (!node.z) node.z = (Math.random() - 0.5) * 10
        if (!node.vz) node.vz = 0
        
        // Apply some z-axis forces based on node type
        const typeForces = {
          'memory': 5,
          'context': 0,
          'skill': -3,
          'concept': -5
        }
        
        const zForce = typeForces[node.type] || 0
        node.vz += (zForce - node.z) * 0.01
        node.z += node.vz * 0.1
        node.vz *= 0.9 // damping
      })

      if (iterationCount % 10 === 0) {
        setSimulatedNodes([...nodesCopy])
        setSimulatedLinks([...linksCopy])
      }

      if (iterationCount >= maxIterations) {
        sim.stop()
        setIsSimulating(false)
      }
    })

    setSimulation(sim)

    return () => {
      sim.stop()
    }
  }, [nodes, links])

  const nodeTypeColors = {
    memory: '#4CAF50',
    context: '#2196F3', 
    skill: '#FF9800',
    concept: '#9C27B0'
  }

  const CameraController = () => {
    const { camera } = useThree()
    
    useEffect(() => {
      if (cameraTarget && camera) {
        const targetNode = simulatedNodes.find(n => n.id === cameraTarget)
        if (targetNode) {
          camera.position.set(
            targetNode.x + 10,
            targetNode.y + 10, 
            targetNode.z + 10
          )
          camera.lookAt(targetNode.x, targetNode.y, targetNode.z)
        }
      }
    }, [cameraTarget, camera, simulatedNodes])

    return null
  }

  return (
    <div style={{ width: '100%', height: '600px', position: 'relative' }}>
      <Canvas
        camera={{ position: [15, 15, 15], fov: 60 }}
        style={{ background: 'linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)' }}
      >
        <CameraController />
        
        {/* Lighting */}
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#4CAF50" />
        
        {/* Environment */}
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        <Environment preset="night" />
        
        {/* Render nodes */}
        {simulatedNodes.map(node => (
          <KnowledgeNode
            key={node.id}
            node={node}
            color={nodeTypeColors[node.type] || '#ffffff'}
            selected={selectedNodeId === node.id}
            onClick={() => onNodeSelect(node)}
          />
        ))}
        
        {/* Render connections */}
        <ConnectionLines 
          links={simulatedLinks}
          nodes={simulatedNodes}
        />
        
        {/* Controls */}
        <OrbitControls 
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={5}
          maxDistance={50}
        />
      </Canvas>
      
      {/* UI Overlay */}
      <div style={{
        position: 'absolute',
        top: '10px',
        left: '10px',
        zIndex: 1000,
        background: 'rgba(0,0,0,0.7)',
        padding: '10px',
        borderRadius: '8px',
        color: 'white',
        fontSize: '14px'
      }}>
        <div>Nodes: {simulatedNodes.length}</div>
        <div>Links: {simulatedLinks.length}</div>
        {isSimulating && <div>⚡ Simulating...</div>}
      </div>
      
      <ConstellationControls
        nodes={simulatedNodes}
        onNodeSelect={onNodeSelect}
        selectedNodeId={selectedNodeId}
      />
    </div>
  )
}

export default ConstellationScene
