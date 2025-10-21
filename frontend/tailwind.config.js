/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        dark: '#0b0f17',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 30px rgba(56,189,248,0.25), 0 0 60px rgba(56,189,248,0.15)' },
          '50%': { boxShadow: '0 0 50px rgba(56,189,248,0.45), 0 0 90px rgba(56,189,248,0.25)' },
        },
        listenWave: {
          '0%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.06)' },
          '100%': { transform: 'scale(1)' },
        },
        speakPulse: {
          '0%': { transform: 'scale(1)', filter: 'brightness(1)' },
          '50%': { transform: 'scale(1.08)', filter: 'brightness(1.2)' },
          '100%': { transform: 'scale(1)', filter: 'brightness(1)' },
        },
        ripple: {
          '0%': { transform: 'scale(1)', opacity: '0.7' },
          '70%': { transform: 'scale(1.35)', opacity: '0.1' },
          '100%': { transform: 'scale(1.6)', opacity: '0' },
        },
        fadeOutUp: {
          '0%': { opacity: '1', transform: 'translateY(0)' },
          '100%': { opacity: '0', transform: 'translateY(-8px)' },
        }
      },
      animation: {
        pulseGlow: 'pulseGlow 2.8s ease-in-out infinite',
        listenWave: 'listenWave 1.2s ease-in-out infinite',
        speakPulse: 'speakPulse 0.9s ease-in-out infinite',
        ripple: 'ripple 1.8s ease-out infinite',
        fadeOutUp: 'fadeOutUp 1.6s ease-out forwards',
      },
    },
  },
  plugins: [],
}
