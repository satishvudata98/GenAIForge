import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forge: {
          bg: "#f4f1e8",
          surface: "rgba(255,255,255,0.78)",
          border: "rgba(31,27,22,0.10)",
          accent: "#d78e3f",
          text: "#1f1b16",
          muted: "#8a7d6e",
        },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', '"Segoe UI"', "sans-serif"],
        mono: ['"IBM Plex Mono"', "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
