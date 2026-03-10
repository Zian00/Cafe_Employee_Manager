/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  corePlugins: {
    // Disable Tailwind's base reset to prevent conflicts with Ant Design global styles
    preflight: false,
  },
  theme: {
    extend: {},
  },
  plugins: [],
}
