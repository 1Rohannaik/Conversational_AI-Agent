import './App.css'
import Orb from './components/Orb'
import MicButton from './components/MicButton'
import UploadButton from './components/UploadButton'
import Subtitle from './components/Subtitle'
import GalaxyDots from './components/GalaxyDots'
import { useEffect, useMemo } from 'react'
import useVoiceAssistant from './hooks/useVoiceAssistant'

function App() {
  const { 
    isListening, 
    subtitle, 
    error, 
    busy, 
    startListening, 
    stopListening, 
    setFileId
  } = useVoiceAssistant()

  // Determine orb visual state
  const orbState = useMemo(() => {
    if (busy) return 'speaking'
    if (isListening) return 'listening'
    return 'idle'
  }, [isListening, busy])

  // Simulate loudness for animation
  const orbLoudness = useMemo(() => {
    if (busy) return 0.7 // High intensity for speaking
    if (isListening) return 0.3 // Medium intensity for listening
    return 0 // No intensity for idle
  }, [isListening, busy])

  useEffect(() => {
    // Ready gate for mobile autoplay can be added here if needed.
  }, [])

  const onMicPress = () => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }

  return (
    <div className="relative min-h-dvh w-full flex flex-col items-center justify-between px-6 py-8">
      {/* Space background with stars */}
      <div className="space-background" />
      
      {/* Galaxy dots overlay */}
      <GalaxyDots active={isListening || busy} intensity={busy ? 0.8 : isListening ? 0.5 : 0.2} />
      
      {/* Top safe area */}
      <div />

      {/* Center orb */}
      <div className="relative z-10 flex flex-col items-center">
        <Orb state={orbState} loudness={orbLoudness} />
        <Subtitle text={subtitle} isThinking={busy && !isListening} />
        {error && (
          <p className="mt-4 text-xs text-rose-300/80">{error}</p>
        )}
      </div>

      {/* Bottom controls: Upload (left) and Mic (right) */}
      <div className="relative z-10 w-full pb-4 flex items-center justify-between">
        <UploadButton
          onUploaded={(res) => {
            setFileId(res.id)
          }}
          onError={(e) => console.error('Upload failed:', e?.message)}
        />
        <MicButton 
          active={isListening} 
          thinking={busy && !isListening}
          onPress={onMicPress} 
        />
      </div>
    </div>
  )
}

export default App
