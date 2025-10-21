# Voice-First AI Assistant UI (React + Tailwind + Framer Motion)

A modern, minimal, futuristic voice-only interface:
- Central glowing orb (AI Ball) that animates for idle/listening/speaking states
- Web Speech API for STT (SpeechRecognition) and TTS (speechSynthesis)
- Subtle, fading subtitles under the orb (for brief context)
- Clean dark gradient background, circular mic button at the bottom
- Fully responsive for mobile and desktop

## Quick start

1. Install dependencies

```sh
npm install
```

2. Start the dev server

```sh
npm run dev
```

3. Open the local URL and click the mic button to grant microphone permission. Speak and wait; when recognition stops, the assistant will reply using TTS.

4. Build for production (optional)

```sh
npm run build
npm run preview
```

## Folder structure (frontend)

- `src/components/Orb.jsx` — Animated orb with idle/listening/speaking visuals
- `src/components/MicButton.jsx` — Minimal circular microphone button
- `src/components/Subtitle.jsx` — Fading subtitles under the orb
- `src/hooks/useVoiceAssistant.js` — Web Speech integration (STT + TTS) and loudness simulation
- `src/utils/respond.js` — Tiny response generator for demo replies
- `tailwind.config.js`, `postcss.config.js` — Tailwind setup and custom animations

## Browser support
- TTS (speechSynthesis): widely supported in modern browsers
- STT (SpeechRecognition): best supported in Chromium-based browsers (Chrome/Edge). Safari/Firefox may not support STT.

If STT is unavailable, a subtle error message appears under the orb. You can still click the mic and the assistant will speak demo replies when `speak()` is called.

## Notes
- The orb’s "speaking" animation is synced to a simulated loudness because the Web Speech TTS API does not expose audio frames.
- Tailwind directives in `src/index.css` are processed by PostCSS during dev/build; your editor’s CSS linter may show warnings — they are safe to ignore.
