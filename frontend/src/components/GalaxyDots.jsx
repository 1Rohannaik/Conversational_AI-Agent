import { useEffect, useRef } from 'react'

// Canvas-based 3D sphere of dots, projected into 2D, with slow rotation and
// subtle shimmer. Reacts to `intensity` to boost size/brightness.
// Props: { active: boolean, intensity: number [0..1], color?: string }
export default function GalaxyDots({ active, intensity = 0 }) {
  const canvasRef = useRef(null)
  const rafRef = useRef(0)
  const pointsRef = useRef([])
  const tRef = useRef(0)
  const intensityRef = useRef(intensity)
  const sizeRef = useRef({ w: 0, h: 0, r: 0 })

  useEffect(() => { intensityRef.current = intensity }, [intensity])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d', { alpha: true })
    let mounted = true

    const DPR = Math.min(window.devicePixelRatio || 1, 2)

    const resize = () => {
      const { width, height } = canvas.getBoundingClientRect()
      canvas.width = Math.max(1, Math.floor(width * DPR))
      canvas.height = Math.max(1, Math.floor(height * DPR))
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0)
      sizeRef.current = { w: width, h: height, r: Math.min(width, height) * 0.46 }
    }

    const makePoints = (count) => {
      const pts = []
      for (let i = 0; i < count; i++) {
        // Fibonacci sphere for uniform distribution
        const phi = Math.acos(1 - 2 * (i + 0.5) / count)
        const theta = Math.PI * (1 + Math.sqrt(5)) * (i + 0.5)
        const x = Math.sin(phi) * Math.cos(theta)
        const y = Math.sin(phi) * Math.sin(theta)
        const z = Math.cos(phi)
        pts.push({ x, y, z, jitter: Math.random() * 6.283 })
      }
      pointsRef.current = pts
    }

    const pickCount = () => {
      const { w } = sizeRef.current
      if (w >= 480) return 380
      if (w >= 360) return 300
      return 220
    }

    resize()
    makePoints(pickCount())

    const onResize = () => { resize(); makePoints(pickCount()) }
    window.addEventListener('resize', onResize)

    const baseDot = 1.2
    const maxBoost = 1.6

  const render = () => {
      if (!mounted) return
      tRef.current += 0.016
      const t = tRef.current
      const { w, h, r } = sizeRef.current
      const cx = w / 2
      const cy = h / 2

      // clear
      ctx.clearRect(0, 0, w, h)
      if (!active) {
        // draw faint static cloud
        ctx.globalAlpha = 0.06
      } else {
        ctx.globalAlpha = 1
      }

      const intensityNow = intensityRef.current
      const rotY = t * 0.35
      const rotX = Math.sin(t * 0.25) * 0.3

      // Precompute sin/cos
      const cosY = Math.cos(rotY), sinY = Math.sin(rotY)
      const cosX = Math.cos(rotX), sinX = Math.sin(rotX)

      for (let i = 0; i < pointsRef.current.length; i++) {
        const p = pointsRef.current[i]
        // rotate around Y then X
        let x = p.x * cosY + p.z * sinY
        let z = -p.x * sinY + p.z * cosY
        let y = p.y * cosX - z * sinX
        z = p.y * sinX + z * cosX

        // breathing jitter tied to intensity
        const j = 1 + 0.03 * Math.sin(t * 2 + p.jitter) + 0.08 * intensityNow
        const px = cx + x * r * j
        const py = cy + y * r * j

        // depth [0..1]
        const depth = (z + 1) * 0.5
        const size = baseDot + depth * (active ? 2.2 : 1.6) + intensityNow * maxBoost
        const alpha = 0.25 + depth * 0.55 + intensityNow * 0.2

        // professional blue cosmic glow
        ctx.beginPath()
        const blueColor = depth > 0.6 ? `rgba(14, 165, 233, ${Math.min(0.95, alpha)})` : `rgba(56, 189, 248, ${Math.min(0.8, alpha)})`
        ctx.fillStyle = blueColor
        ctx.arc(px, py, size, 0, Math.PI * 2)
        ctx.fill()
        
        // Add a subtle outer glow for larger dots
        if (size > 2) {
          ctx.beginPath()
          ctx.fillStyle = `rgba(186, 230, 253, ${Math.min(0.3, alpha * 0.5)})`
          ctx.arc(px, py, size * 1.5, 0, Math.PI * 2)
          ctx.fill()
        }
      }

      rafRef.current = requestAnimationFrame(render)
    }

    rafRef.current = requestAnimationFrame(render)

    return () => {
      mounted = false
      window.removeEventListener('resize', onResize)
      cancelAnimationFrame(rafRef.current)
    }
  }, [active])

  return (
    <div className="pointer-events-none absolute inset-0">
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />
    </div>
  )
}
