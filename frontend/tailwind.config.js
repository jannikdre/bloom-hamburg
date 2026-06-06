/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bloom: {
          green: "#3f7d3f",
          light: "#f7f6f1",
        },
      },
    },
  },
  plugins: [],
};
