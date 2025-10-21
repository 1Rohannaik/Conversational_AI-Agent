// Lightweight API client for the backend

const BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

async function handleResponse(res) {
  const contentType = res.headers.get('content-type') || ''
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`
    if (contentType.includes('application/json')) {
      try {
        const data = await res.json()
        detail = (data && (data.detail || data.message)) || JSON.stringify(data)
      } catch {
        // ignore parse error; keep default detail
      }
    } else {
      try {
        detail = await res.text()
      } catch {
        // ignore read error
      }
    }
    throw new Error(detail)
  }

  if (contentType.includes('application/json')) return res.json()
  if (contentType.startsWith('audio/')) return res.blob()
  return res.text()
}

export function getBaseUrl() {
  return BASE_URL.replace(/\/$/, '')
}

// Uploads
export async function uploadPdf(file) {
  const fd = new FormData()
  fd.append('file', file)
  
  const url = `${getBaseUrl()}/upload/upload_pdf/`
  console.log('Uploading to:', url)
  console.log('Base URL:', getBaseUrl())
  
  // Create AbortController for timeout
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 30000) // 30 second timeout
  
  try {
    console.log('Making fetch request...')
    const res = await fetch(url, {
      method: 'POST',
      body: fd,
      signal: controller.signal,
    })
    console.log('Response received:', res.status)
    clearTimeout(timeoutId)
    return handleResponse(res)
  } catch (error) {
    console.error('Upload error:', error)
    clearTimeout(timeoutId)
    if (error.name === 'AbortError') {
      throw new Error('Upload timed out. Please try again.')
    }
    throw error
  }
}

// Flow (intent: rag/quiz/summary)
export async function flowAsk(fileId, question, conversationSessionId = null) {
  const body = { file_id: Number(fileId), question }
  if (conversationSessionId) {
    body.conversation_session_id = conversationSessionId
  }
  
  const res = await fetch(`${getBaseUrl()}/flow/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return handleResponse(res)
}



// STT (Groq Whisper)
export async function sttTranscribe(file) {
  const fd = new FormData()
  fd.append('file', file)
  const res = await fetch(`${getBaseUrl()}/api/v1/stt`, { method: 'POST', body: fd })
  return handleResponse(res) // { transcript }
}

// TTS (gTTS): returns a Blob (audio/mpeg)
export async function ttsSynthesize({ text, speed = 1.0 }) {
  const res = await fetch(`${getBaseUrl()}/api/v1/tts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, speed }),
  })
  const blob = await handleResponse(res) // Blob
  return blob
}

export function playAudioBlob(blob) {
  const url = URL.createObjectURL(blob)
  const audio = new Audio(url)
  audio.addEventListener('ended', () => URL.revokeObjectURL(url))
  audio.play()
  return audio
}

export default {
  getBaseUrl,
  uploadPdf,
  flowAsk,
  sttTranscribe,
  ttsSynthesize,
  playAudioBlob,
}
