/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    fontSize: {
      'xs': '0.75rem',    // 12px
      'sm': '0.825rem',   // 13.2px (reduced from 14px)
      'base': '0.875rem', // 14px (reduced from 16px)
      'lg': '1rem',       // 16px (reduced from 18px)
      'xl': '1.125rem',   // 18px (reduced from 20px)
      '2xl': '1.375rem',  // 22px (reduced from 24px)
      '3xl': '1.75rem',   // 28px (reduced from 30px)
      '4xl': '2rem',      // 32px (reduced from 36px)
      '5xl': '2.5rem',    // 40px (reduced from 48px)
      '6xl': '3rem',      // 48px (reduced from 60px)
    },
    extend: {
      fontFamily: {
        'sans': ['Ubuntu', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Oxygen', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', 'sans-serif'],
      },
    },
  },
  plugins: [],
}