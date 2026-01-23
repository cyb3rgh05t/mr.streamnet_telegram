/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        telegram: {
          blue: "#0088cc",
          light: "#64b5ef",
          dark: "#006699",
        },
        dark: {
          bg: "#1a1a2e",
          card: "#16213e",
          accent: "#0f3460",
        },
      },
    },
  },
  plugins: [],
};
