export default function MicButton({ active = false, thinking = false, onPress }) {
  const getButtonStyle = () => {
    if (thinking) {
      return {
        bg: 'bg-gradient-to-br from-blue-500/30 via-sky-600/20 to-cyan-500/25 hover:from-blue-500/40 hover:via-sky-600/30 hover:to-cyan-500/35',
        border: 'border-blue-400/60 shadow-lg shadow-blue-500/20',
        ring: 'ring-2 ring-blue-400/50 ring-offset-2 ring-offset-blue-900/20'
      }
    }
    if (active) {
      return {
        bg: 'bg-gradient-to-br from-red-500/30 via-red-600/20 to-pink-500/25 hover:from-red-500/40 hover:via-red-600/30 hover:to-pink-500/35',
        border: 'border-red-400/60 shadow-lg shadow-red-500/25',
        ring: 'ring-2 ring-red-400/50 ring-offset-2 ring-offset-red-900/20'
      }
    }
    return {
      bg: 'bg-gradient-to-br from-sky-500/25 via-blue-600/15 to-cyan-500/20 hover:from-sky-500/35 hover:via-blue-600/25 hover:to-cyan-500/30',
      border: 'border-sky-400/50 shadow-md shadow-sky-500/15',
      ring: 'hover:ring-1 hover:ring-sky-400/30'
    }
  }

  const getMicColor = () => {
    if (thinking) return 'fill-blue-300 drop-shadow-sm'
    if (active) return 'fill-red-300 drop-shadow-sm'
    return 'fill-sky-300 group-hover:fill-sky-200 drop-shadow-sm'
  }

  const getMicSecondaryColor = () => {
    if (thinking) return 'fill-blue-200/90'
    if (active) return 'fill-red-200/90'
    return 'fill-sky-200/80 group-hover:fill-sky-100/90'
  }

  const style = getButtonStyle()

  return (
    <button
      onClick={onPress}
      disabled={thinking}
      aria-label={
        thinking ? 'Processing...' : 
        active ? 'Stop listening' : 'Start listening'
      }
      className={[
        'group relative size-10 md:size-20 rounded-full',
        style.bg,
        style.border,
        'transition-all duration-500 ease-out outline-none focus-visible:ring-2 focus-visible:ring-sky-400/40 transform-gpu',
        style.ring,
        thinking ? 'cursor-not-allowed scale-105' : 'cursor-pointer hover:scale-105 active:scale-95'
      ].join(' ')}
    >
      {/* Background glow effect */}
      <div className={`absolute inset-0 rounded-full blur-xl opacity-30 transition-all duration-500 ${
        thinking ? 'bg-blue-400' : 
        active ? 'bg-red-400' : 
        'bg-sky-400'
      }`} />
      
      {/* mic glyph */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        className={`relative z-10 size-7 md:size-9 mx-auto my-auto transition-all duration-500 ${
          thinking ? 'animate-pulse' : ''
        } ${active ? 'scale-110' : ''}`}
      >
        <path
          d="M12 15a3 3 0 0 0 3-3V7a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Z"
          className={getMicColor()}
        />
        <path
          d="M5 11a1 1 0 1 1 2 0 5 5 0 1 0 10 0 1 1 0 1 1 2 0 7 7 0 0 1-6 6.93V21h3a1 1 0 1 1 0 2H10a1 1 0 1 1 0-2h3v-3.07A7 7 0 0 1 5 11Z"
          className={getMicSecondaryColor()}
        />
      </svg>

      {/* Enhanced animated effects */}
      {active && !thinking && (
        <>
          <span className="pointer-events-none absolute inset-0 rounded-full animate-ping bg-gradient-to-r from-red-400/30 to-pink-400/30" />
          <span className="pointer-events-none absolute inset-1 rounded-full animate-pulse bg-gradient-to-br from-red-400/20 to-pink-400/20" />
          <span className="pointer-events-none absolute inset-3 rounded-full animate-bounce bg-red-400/10" style={{ animationDuration: '2s' }} />
        </>
      )}
      
      {thinking && (
        <>
          <span className="pointer-events-none absolute inset-0 rounded-full animate-spin bg-gradient-to-r from-blue-400/30 via-sky-400/20 to-blue-400/30" style={{ animationDuration: '3s' }} />
          <span className="pointer-events-none absolute inset-1 rounded-full animate-pulse bg-gradient-to-br from-blue-400/25 to-sky-400/25" />
          <span className="pointer-events-none absolute inset-2 rounded-full animate-ping bg-blue-400/15" style={{ animationDuration: '2s' }} />
        </>
      )}
      
      {/* Idle state subtle effect */}
      {!active && !thinking && (
        <span className="pointer-events-none absolute inset-0 rounded-full bg-gradient-to-br from-sky-400/5 to-cyan-400/5 group-hover:from-sky-400/15 group-hover:to-cyan-400/15 transition-all duration-300" />
      )}
    </button>
  )
}
