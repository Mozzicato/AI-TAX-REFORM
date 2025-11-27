/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2D5016",    // Green (tax-related)
        secondary: "#4A7C2C",  // Light green
        accent: "#1E40AF",     // Blue
        dark: "#1F2937",
        light: "#F9FAFB",
      },
    },
  },
  plugins: [],
};
