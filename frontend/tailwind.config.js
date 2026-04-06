/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#14213d',
        mist: '#f6f7fb',
        accent: '#fca311',
        danger: '#d62828',
        success: '#2a9d8f'
      },
      fontFamily: {
        display: ['Poppins', 'sans-serif'],
        body: ['Manrope', 'sans-serif']
      },
      boxShadow: {
        glow: '0 12px 30px rgba(20, 33, 61, 0.12)'
      },
      keyframes: {
        rise: {
          '0%': { opacity: 0, transform: 'translateY(12px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' }
        }
      },
      animation: {
        rise: 'rise 550ms ease-out forwards'
      }
    }
  },
  plugins: []
};
