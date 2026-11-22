/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        imperial: {
          50: '#fbf8f2',
          100: '#f5eee1',
          200: '#e9dac1',
          300: '#dac09a',
          400: '#caa373',
          500: '#be8a54',
          600: '#b07546',
          700: '#925c3a',
          800: '#774b33',
          900: '#613e2d',
        },
      },
    },
  },
  plugins: [],
};
