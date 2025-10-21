import { useCallback, useEffect, useRef, useState } from 'react'
import { sttTranscribe, flowAsk, ttsSynthesize, playAudioBlob } from '../utils/api'

// Backend-only voice assistant: MediaRecorder -> backend STT -> flow -> backend TTS
export default function useVoiceAssistant() {
  const [isListening, setIsListening] = useState(false)
  const [subtitle, setSubtitle] = useState('')
  const [error, setError] = useState(null)
  const [finalText, setFinalText] = useState('')
  const [fileId, setFileId] = useState(null)
  const [busy, setBusy] = useState(false)
  
  // Conversation state
  const [conversationSessionId, setConversationSessionId] = useState(null)
  const [conversationState, setConversationState] = useState(null)
  const [isInConversation, setIsInConversation] = useState(false)

  const mediaStreamRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const recordedChunksRef = useRef([])
  const subtitleTimerRef = useRef(null)

  const showSubtitle = useCallback((text, lifespan = 2200) => {
    if (subtitleTimerRef.current) clearTimeout(subtitleTimerRef.current)
    setSubtitle(text)
    subtitleTimerRef.current = setTimeout(() => setSubtitle(''), lifespan)
  }, [])

  const handleTranscript = useCallback(async (text) => {
    if (!text) return
    if (!fileId) {
      showSubtitle('📄 Please upload a PDF to start the conversation', 3000)
      return
    }
    setBusy(true)
    try {
      showSubtitle('Thinking...', 10000) // Longer duration for thinking state
      
      // Use conversation session ID if we're in a conversation
      const res = await flowAsk(fileId, text, conversationSessionId)
      const answer = res?.answer || ''
      
      // Update conversation state
      if (res?.conversation_session_id) {
        setConversationSessionId(res.conversation_session_id)
        setConversationState(res.conversation_state)
        setIsInConversation(res.requires_response === true)
      } else if (res?.intent === 'interview_start' && res?.requires_response) {
        // Starting a new interview conversation
        setIsInConversation(true)
      } else if (res?.conversation_state === 'completed' || res?.requires_response === false) {
        // Conversation ended
        setConversationSessionId(null)
        setConversationState(null)
        setIsInConversation(false)
      }
      
      try {
        showSubtitle('Generating speech...', 3000)
        const blob = await ttsSynthesize({ text: answer, speed: 1.0 })
        setSubtitle('') // Clear subtitle when audio starts
        playAudioBlob(blob)
      } catch {
        showSubtitle(answer, Math.min(2800, Math.max(1600, answer.length * 35)))
      }
    } catch (err) {
      setError(err?.message || 'Failed to run flow')
    } finally {
      setBusy(false)
    }
  }, [fileId, conversationSessionId, showSubtitle])

  const startListening = useCallback(() => {
    if (isListening || busy) return
    
    // Check if PDF is uploaded before starting to listen
    if (!fileId) {
      showSubtitle('📄 Please upload a PDF to start the conversation', 3000)
      return
    }
    
    navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
      mediaStreamRef.current = stream
      const rec = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      recordedChunksRef.current = []
      mediaRecorderRef.current = rec
      rec.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) recordedChunksRef.current.push(e.data)
      }
      rec.onstop = async () => {
        setIsListening(false)
        setBusy(true)
        try {
          showSubtitle('Processing audio...', 5000)
          const blob = new Blob(recordedChunksRef.current, { type: 'audio/webm' })
          const file = new File([blob], 'recording.webm', { type: 'audio/webm' })
          const { transcript } = await sttTranscribe(file)
          setFinalText(transcript || '')
          showSubtitle(transcript || '', 2000)
          if (transcript) {
            await handleTranscript(transcript)
          }
        } catch (err) {
          setError(err?.message || 'STT failed')
        } finally {
          stream.getTracks().forEach((t) => t.stop())
          mediaStreamRef.current = null
          setBusy(false)
        }
      }
      rec.start()
      setIsListening(true)
    }).catch((err) => {
      setError(err?.message || 'Microphone access denied')
    })
  }, [isListening, busy, fileId, showSubtitle, handleTranscript])

  const stopListening = useCallback(() => {
    const mr = mediaRecorderRef.current
    if (mr && mr.state !== 'inactive') {
      try { mr.stop() } catch { /* no-op */ }
    }
    const ms = mediaStreamRef.current
    if (ms) {
      ms.getTracks().forEach((t) => t.stop())
      mediaStreamRef.current = null
    }
    setIsListening(false)
  }, [])

  // Function to end conversation manually
  const endConversation = useCallback(() => {
    setConversationSessionId(null)
    setConversationState(null)
    setIsInConversation(false)
  }, [])

  useEffect(() => () => {
    stopListening()
    if (subtitleTimerRef.current) clearTimeout(subtitleTimerRef.current)
  }, [stopListening])

  return {
    isListening,
    subtitle,
    error,
    finalText,
    fileId,
    busy,
    startListening,
    stopListening,
    setFileId,
    // Conversation state
    isInConversation,
    conversationState,
    endConversation,
  }
}
