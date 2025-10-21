import { useRef, useState } from 'react'
import { uploadPdf } from '../utils/api'

export default function UploadButton({ onUploaded, onError, className = '' }) {
  const fileRef = useRef(null)
  const [loading, setLoading] = useState(false)

  const pickFile = () => {
    if (loading) return
    fileRef.current?.click()
  }

  const onChange = async (e) => {
    const file = e.target.files?.[0]
    // reset the input so selecting the same file again fires change
    e.target.value = ''
    if (!file) return
    if (file.type !== 'application/pdf') {
      onError?.(new Error('Please select a PDF file.'))
      return
    }
    setLoading(true)
    try {
      const res = await uploadPdf(file)
      onUploaded?.(res)
    } catch (err) {
      onError?.(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <input
        ref={fileRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={onChange}
      />
            <button
        type="button"
        onClick={pickFile}
        aria-label="Upload PDF"
        title="Upload PDF"
        className={[
          'group relative size-14 md:size-20 rounded-full',
          'bg-gradient-to-br from-green-500/25 via-emerald-500/20 to-teal-500/25 hover:from-green-500/35 hover:via-emerald-500/30 hover:to-teal-500/35',
          'border border-green-400/60 shadow-lg shadow-green-500/20',
          'transition-all duration-500 ease-out outline-none focus-visible:ring-2 focus-visible:ring-green-400/40 transform-gpu',
          'hover:scale-105 active:scale-95',
          loading ? 'opacity-70 cursor-not-allowed animate-pulse scale-105' : 'cursor-pointer',
          className,
        ].join(' ')}
        disabled={loading}
      >
        {/* Background glow effect */}
        <div className={`absolute inset-0 rounded-full blur-xl opacity-25 transition-all duration-500 ${
          loading ? 'bg-emerald-400' : 'bg-green-400'
        }`} />
        
        {/* plus icon */}
        {!loading ? (
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" className="relative z-10 size-8 md:size-10 mx-auto my-auto transition-all duration-500 drop-shadow-sm" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M12 5v14M5 12h14" className="stroke-green-300 group-hover:stroke-green-200" />
          </svg>
        ) : (
          // Enhanced upload spinner with gradient
          <div className="relative z-10 size-8 md:size-10 mx-auto my-auto">
            <svg className="absolute inset-0 animate-spin text-emerald-300" viewBox="0 0 24 24" style={{ animationDuration: '1s' }}>
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
            </svg>
            <div className="absolute inset-2 rounded-full bg-gradient-to-br from-emerald-400/30 to-green-400/30 animate-pulse" />
          </div>
        )}
        
        {/* Idle state subtle effect */}
        {!loading && (
          <span className="pointer-events-none absolute inset-0 rounded-full bg-gradient-to-br from-green-400/5 to-emerald-400/5 group-hover:from-green-400/15 group-hover:to-emerald-400/15 transition-all duration-300" />
        )}
        
        {/* Loading effects */}
        {loading && (
          <>
            <span className="pointer-events-none absolute inset-0 rounded-full animate-ping bg-gradient-to-r from-emerald-400/30 to-green-400/30" style={{ animationDuration: '2s' }} />
            <span className="pointer-events-none absolute inset-1 rounded-full animate-pulse bg-gradient-to-br from-emerald-400/20 to-green-400/20" />
          </>
        )}
      </button>
    </>
  )
}
