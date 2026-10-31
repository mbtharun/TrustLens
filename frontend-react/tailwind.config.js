/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: '#f6f4ef',
        ink: '#1a1918',
        muted: '#6b6860',
        borderline: '#d8d4cc',
        steel: '#4a6d8c',
        'steel-light': '#dce6ef',
        amber: '#c8901a',
        'amber-bg': '#fdf3dc',
      },
      fontFamily: {
        serif: ['Georgia', 'Times New Roman', 'serif'],
        sans: ['system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
      },
      maxWidth: { content: '1120px' },
    },
  },
  plugins: [],
}