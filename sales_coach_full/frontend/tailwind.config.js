/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#111827",
          fg: "#F9FAFB",
          muted: "#6B7280",
        },
        accent: "#6366F1",
      },
      boxShadow: {
        card: "0 10px 25px -15px rgba(0,0,0,0.25)",
      },
    },
  },
  plugins: [],
};
