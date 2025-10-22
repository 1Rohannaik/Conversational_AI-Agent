export default function Subtitle({ text, isThinking = false }) {
  if (!text && !isThinking) return null
  
  const isThinkingText = text === 'Thinking...' || text === 'Processing...' || text === 'Processing audio...' || text === 'Generating speech...' || isThinking
  
  return (
    <div className="mt-6 text-center">
      <div className={[
        'mx-auto max-w-md text-sm sm:text-base backdrop-blur-sm px-4 py-2 rounded-xl border',
        'transition-all duration-300',
        isThinkingText 
          ? 'text-purple-200 bg-blue-500/15 border-blue-400/30 shadow-md' 
          : 'text-white/80 bg-white/10 border-white/20 animate-fadeOutUp shadow-sm'
      ].join(' ')}>
        {isThinkingText ? (
          <div className="flex items-center justify-center gap-2">
            {/* Simple thinking dots */}
            <div className="flex gap-1">
              <div className="w-1.5 h-1.5 bg-blue-600 rounded-full thinking-dot"></div>
              <div className="w-1.5 h-1.5 bg-blue-600 rounded-full thinking-dot"></div>
              <div className="w-1.5 h-1.5 bg-blue-600 rounded-full thinking-dot"></div>
            </div>
            <span className="ml-1">
              {text || 'Thinking...'}
            </span>
          </div>
        ) : (
          <p>{text}</p>
        )}
      </div>
    </div>
  )
}
