import './App.css'
import Orb from './components/Orb'
import MicButton from './components/MicButton'
import UploadButton from './components/UploadButton'
import Subtitle from './components/Subtitle'
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
    <div className="min-h-dvh w-full flex flex-col items-center justify-between px-6 py-8">
      {/* Top safe area */}
      <div />

      {/* Center orb */}
      <div className="flex flex-col items-center">
        <Orb state={orbState} loudness={0} />
        <Subtitle text={subtitle} isThinking={busy && !isListening} />
        {error && (
          <p className="mt-4 text-xs text-rose-300/80">{error}</p>
        )}
      </div>

      {/* Bottom controls: Upload and Mic */}
      <div className="pb-4 flex items-center gap-4">
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
