/* eslint-disable no-unused-vars */
import { motion, useSpring, useTransform } from 'framer-motion'
import { useEffect } from 'react'
import GalaxyDots from './GalaxyDots'

export default function Orb({ state = 'idle', loudness = 0 }) {
  // state: 'idle' | 'listening' | 'speaking'
  const loudSpring = useSpring(0, { stiffness: 120, damping: 20, mass: 0.4 })
  useEffect(() => {
    loudSpring.set(loudness)
  }, [loudness, loudSpring])

  const scale = useTransform(loudSpring, [0, 1], [1, 1.16])

  const baseClasses =
    'relative size-52 sm:size-60 md:size-64 rounded-full bg-gradient-to-br from-sky-500/50 via-blue-500/60 to-cyan-500/50 border border-white/10'

  const idleRing = (
    <div className="absolute inset-0 rounded-full animate-pulseGlow" aria-hidden />
  )
  const listeningRing = (
    <div className="absolute inset-0 rounded-full animate-listenWave" aria-hidden />
  )
  const speakingRing = (
    <div className="absolute inset-0 rounded-full animate-speakPulse" aria-hidden />
  )

  return (
    <motion.div
      className={baseClasses}
      style={{
        boxShadow: '0 0 120px rgba(14,165,233,0.35)',
      }}
      animate={{
        background: [
          'radial-gradient(circle at 50% 50%, rgba(14,165,233,0.25), rgba(56,189,248,0.15) 60%, rgba(6,182,212,0.05) 100%)',
          'radial-gradient(circle at 50% 50%, rgba(56,189,248,0.25), rgba(14,165,233,0.15) 60%, rgba(6,182,212,0.05) 100%)',
        ],
        filter: state === 'speaking' ? 'brightness(1.25)' : 'brightness(1)',
        scale: state === 'speaking' ? [1, 1.05, 1] : 1,
      }}
      transition={{ 
        duration: state === 'speaking' ? 1.5 : 3, 
        repeat: Infinity, 
        ease: 'easeInOut' 
      }}
    >
      {state === 'idle' && idleRing}
      {state === 'listening' && listeningRing}
      {state === 'speaking' && speakingRing}

      {/* Volume-reactive inner core */}
      <motion.div
        className="absolute inset-5 sm:inset-6 md:inset-7 rounded-full"
        style={{ 
          scale,
          background: 'radial-gradient(circle, rgba(56,189,248,0.3) 0%, rgba(14,165,233,0.2) 50%, transparent 100%)'
        }}
        animate={{
          opacity: state === 'speaking' ? [0.6, 1, 0.6] : 1,
        }}
        transition={{ 
          duration: state === 'speaking' ? 1 : 2, 
          repeat: Infinity, 
          ease: 'easeInOut' 
        }}
      />

      {/* Galaxy dots when active */}
      <GalaxyDots active={state !== 'idle'} intensity={loudness} />

      {/* Ripples for subtle motion */}
      <div className="absolute inset-0" aria-hidden>
        <div className="absolute inset-[-8%] rounded-full border border-sky-300/10 animate-ripple" />
        <div className="absolute inset-[-16%] rounded-full border border-cyan-300/10 animate-ripple [animation-delay:.6s]" />
      </div>
    </motion.div>
  )
}
