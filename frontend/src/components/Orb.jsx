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
    'relative size-52 sm:size-60 md:size-64 rounded-full bg-gradient-to-br from-sky-400/60 via-indigo-400/60 to-fuchsia-400/50 backdrop-blur-[2px] border border-white/10'

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
        boxShadow:
          'inset 0 0 60px rgba(255,255,255,0.06), 0 0 120px rgba(99,102,241,0.25)',
      }}
      animate={{
        background: [
          'radial-gradient(60% 60% at 50% 40%, rgba(56,189,248,0.25), rgba(99,102,241,0.15) 70%, rgba(217,70,239,0.07))',
          'radial-gradient(60% 60% at 50% 60%, rgba(99,102,241,0.25), rgba(56,189,248,0.15) 70%, rgba(217,70,239,0.09))',
        ],
        filter: state === 'speaking' ? 'brightness(1.12)' : 'brightness(1)',
      }}
      transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
    >
      {state === 'idle' && idleRing}
      {state === 'listening' && listeningRing}
      {state === 'speaking' && speakingRing}

      {/* Volume-reactive inner core */}
      <motion.div
        className="absolute inset-5 sm:inset-6 md:inset-7 rounded-full bg-gradient-to-br from-white/30 via-white/15 to-transparent"
        style={{ scale }}
      />

      {/* Galaxy dots when active */}
      <GalaxyDots active={state !== 'idle'} intensity={loudness} />

      {/* Ripples for subtle motion */}
      <div className="absolute inset-0" aria-hidden>
        <div className="absolute inset-[-8%] rounded-full border border-sky-300/10 animate-ripple" />
        <div className="absolute inset-[-16%] rounded-full border border-indigo-300/10 animate-ripple [animation-delay:.6s]" />
      </div>
    </motion.div>
  )
}
