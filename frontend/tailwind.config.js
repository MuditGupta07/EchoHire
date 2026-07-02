/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#08090D',
        surface: '#10131A',
        elevated: '#151922',
        border: '#2B3445',
        primary: '#16F2B3',
        ice: '#3DD9FF',
        gold: '#D9B45A',
        text: {
          primary: '#F8FAFC',
          secondary: '#9AA5B5',
          muted: '#6B7482',
        }
      },
      boxShadow: {
        glow: '0 0 30px rgba(22, 242, 179, 0.25)',
        grounded: '0 15px 40px rgba(0, 0, 0, 0.25)',
      }
    },
  },
  plugins: [],
}
