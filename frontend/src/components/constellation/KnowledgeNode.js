import React, { useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { Text, Html, Sphere } from '@react-three/drei'
import * as THREE from 'three'

const KnowledgeNode = ({ 
  node, 
  color = '#ffffff', 
  selected = false, 
  onClick = () => {} 
}) => {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)
  
  // Animation and effects
  useFrame((state) => {
    if (meshRef.current) {
      // Gentle floating animation
      meshRef.current.position.y = node.y + Math.sin(state.clock.elapsedTime + node.x) * 0.1
      
      // Glow effect when selected or hovered
      if (selected || hovered) {
        meshRef.current.scale.setScalar(1.2 + Math.sin(state.clock.elapsedTime * 3) * 0.1)
      } else {
        meshRef.current.scale.setScalar(1)
      }
      
      // Rotation based on importance
      meshRef.current.rotation.y += node.importance * 0.01
    }
  })

  // Calculate node size based on importance
  const nodeSize = 0.5 + (node.importance || 0.5) * 1.5

  // Get node type emoji
  const getNodeEmoji = (type) => {
    switch (type) {
      case 'memory': return '💭'
      case 'context': return '🌐'
      case 'skill': return '⚡'
      case 'concept': return '💡'
      default: return '🔵'
    }
  }

  return (
    <group 
      position={[node.x || 0, node.y || 0, node.z || 0]}
      onClick={(e) => {
        e.stopPropagation()
        onClick(node)
      }}
      onPointerOver={(e) => {
        e.stopPropagation()
        setHovered(true)
        document.body.style.cursor = 'pointer'
      }}
      onPointerOut={(e) => {
        e.stopPropagation()
        setHovered(false)
        document.body.style.cursor = 'auto'
      }}
    >
      {/* Main sphere */}
      <mesh ref={meshRef}>
        <sphereGeometry args={[nodeSize, 32, 32]} />
        <meshPhongMaterial 
          color={color}
          transparent
          opacity={selected ? 0.9 : 0.7}
          emissive={selected || hovered ? color : '#000000'}
          emissiveIntensity={selected || hovered ? 0.3 : 0}
        />
      </mesh>
      
      {/* Outer glow ring */}
      {(selected || hovered) && (
        <mesh>
          <ringGeometry args={[nodeSize * 1.5, nodeSize * 2, 32]} />
          <meshBasicMaterial 
            color={color}
            transparent
            opacity={0.3}
            side={THREE.DoubleSide}
          />
        </mesh>
      )}
      
      {/* Node label */}
      <Text
        position={[0, nodeSize + 1, 0]}
        fontSize={0.8}
        color="white"
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.1}
        outlineColor="black"
      >
        {getNodeEmoji(node.type)} {node.label || node.id}
      </Text>
      
      {/* Detailed info on hover */}
      {hovered && (
        <Html
          position={[nodeSize + 2, 0, 0]}
          style={{
            background: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            padding: '10px',
            borderRadius: '8px',
            fontSize: '12px',
            minWidth: '200px',
            maxWidth: '300px',
            border: `2px solid ${color}`,
            pointerEvents: 'none'
          }}
        >
          <div>
            <strong>{node.label || node.id}</strong>
            <div style={{ marginTop: '5px', opacity: 0.8 }}>
              Type: {node.type}
            </div>
            <div style={{ opacity: 0.8 }}>
              Domain: {node.domain || 'General'}
            </div>
            <div style={{ opacity: 0.8 }}>
              Importance: {Math.round((node.importance || 0) * 100)}%
            </div>
            {node.metadata?.full_content && (
              <div style={{ 
                marginTop: '8px', 
                fontSize: '11px', 
                opacity: 0.9,
                maxHeight: '100px',
                overflow: 'hidden'
              }}>
                {node.metadata.full_content.length > 150 
                  ? node.metadata.full_content.substring(0, 150) + '...'
                  : node.metadata.full_content
                }
              </div>
            )}
          </div>
        </Html>
      )}
      
      {/* Particle effects for high importance nodes */}
      {node.importance > 0.8 && (
        <group>
          {Array.from({ length: 8 }).map((_, i) => (
            <mesh
              key={i}
              position={[
                Math.cos(i * Math.PI / 4) * (nodeSize * 2),
                Math.sin(i * Math.PI / 4) * (nodeSize * 2),
                0
              ]}
            >
              <sphereGeometry args={[0.1, 8, 8]} />
              <meshBasicMaterial 
                color={color}
                transparent
                opacity={0.6}
              />
            </mesh>
          ))}
        </group>
      )}
    </group>
  )
}

export default KnowledgeNode
