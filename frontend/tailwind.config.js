/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paleta Radio Covid - Colores Neón Exactos
        'neon-red':    '#FF1744',
        'neon-orange': '#FF6D00',
        'neon-yellow': '#FFD600',
        'neon-purple': '#AA00FF',
        'dark-purple': '#1A0033',
        'base-black':  '#0A000F',
        'soft-white':  '#F5F0FF',
        // Additional atmospheric color
        'mid-purple':  '#2D0060',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'pulse-live': 'pulse-live 1.5s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #FF1744, 0 0 10px #FF1744' },
          '100%': { boxShadow: '0 0 20px #FF1744, 0 0 30px #FF1744' },
        },
        'pulse-live': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        },
      },
    },
  },
  plugins: [],
}
