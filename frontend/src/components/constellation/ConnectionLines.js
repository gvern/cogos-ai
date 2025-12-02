import React, { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

const ConnectionLines = ({ links = [], nodes = [] }) => {
  const linesRef = useRef()
  
  // Create line geometries and materials
  const connectionData = useMemo(() => {
    if (!links.length || !nodes.length) return []
    
    return links.map(link => {
      const sourceNode = typeof link.source === 'object' ? link.source : nodes.find(n => n.id === link.source)
      const targetNode = typeof link.target === 'object' ? link.target : nodes.find(n => n.id === link.target)
      
      if (!sourceNode || !targetNode) return null
      
      const points = [
        new THREE.Vector3(sourceNode.x || 0, sourceNode.y || 0, sourceNode.z || 0),
        new THREE.Vector3(targetNode.x || 0, targetNode.y || 0, targetNode.z || 0)
      ]
      
      const geometry = new THREE.BufferGeometry().setFromPoints(points)
      
      // Color based on connection strength
      const strength = link.strength || 0.5
      const color = new THREE.Color().setHSL(0.6, 1, 0.3 + strength * 0.4)
      
      return {
        geometry,
        color,
        strength,
        id: `${sourceNode.id}-${targetNode.id}`,
        sourceNode,
        targetNode
      }
    }).filter(Boolean)
  }, [links, nodes])
  
  // Animate connection lines
  useFrame((state) => {
    if (linesRef.current) {
      linesRef.current.children.forEach((line, index) => {
        const data = connectionData[index]
        if (data && line.material) {
          // Pulse effect based on strength
          const pulse = Math.sin(state.clock.elapsedTime * 2 + index) * 0.3 + 0.7
          line.material.opacity = (data.strength * 0.8 + 0.2) * pulse
          
          // Update line positions if nodes moved
          const sourcePos = new THREE.Vector3(
            data.sourceNode.x || 0, 
            data.sourceNode.y || 0, 
            data.sourceNode.z || 0
          )
          const targetPos = new THREE.Vector3(
            data.targetNode.x || 0, 
            data.targetNode.y || 0, 
            data.targetNode.z || 0
          )
          
          const points = [sourcePos, targetPos]
          line.geometry.setFromPoints(points)
        }
      })
    }
  })

  return (
    <group ref={linesRef}>
      {connectionData.map((data, index) => (
        <line key={data.id || index}>
          <bufferGeometry attach="geometry" {...data.geometry} />
          <lineBasicMaterial
            attach="material"
            color={data.color}
            transparent
            opacity={data.strength * 0.8 + 0.2}
            linewidth={Math.max(1, data.strength * 3)}
          />
        </line>
      ))}
      
      {/* Curved connections for high-strength links */}
      {connectionData
        .filter(data => data.strength > 0.7)
        .map((data, index) => {
          const midPoint = new THREE.Vector3()
            .addVectors(
              new THREE.Vector3(data.sourceNode.x, data.sourceNode.y, data.sourceNode.z),
              new THREE.Vector3(data.targetNode.x, data.targetNode.y, data.targetNode.z)
            )
            .multiplyScalar(0.5)
            .add(new THREE.Vector3(0, 2, 0)) // Arc height
          
          const curve = new THREE.QuadraticBezierCurve3(
            new THREE.Vector3(data.sourceNode.x, data.sourceNode.y, data.sourceNode.z),
            midPoint,
            new THREE.Vector3(data.targetNode.x, data.targetNode.y, data.targetNode.z)
          )
          
          const points = curve.getPoints(50)
          const curveGeometry = new THREE.BufferGeometry().setFromPoints(points)
          
          return (
            <line key={`curve-${data.id || index}`}>
              <bufferGeometry attach="geometry" {...curveGeometry} />
              <lineBasicMaterial
                attach="material"
                color={data.color}
                transparent
                opacity={0.6}
                linewidth={2}
              />
            </line>
          )
        })
      }
      
      {/* Connection strength indicators */}
      {connectionData
        .filter(data => data.strength > 0.8)
        .map((data, index) => {
          const midPoint = new THREE.Vector3()
            .addVectors(
              new THREE.Vector3(data.sourceNode.x, data.sourceNode.y, data.sourceNode.z),
              new THREE.Vector3(data.targetNode.x, data.targetNode.y, data.targetNode.z)
            )
            .multiplyScalar(0.5)
          
          return (
            <mesh key={`indicator-${data.id || index}`} position={midPoint}>
              <sphereGeometry args={[0.2, 8, 8]} />
              <meshBasicMaterial
                color={data.color}
                transparent
                opacity={0.8}
              />
            </mesh>
          )
        })
      }
    </group>
  )
}

export default ConnectionLines
