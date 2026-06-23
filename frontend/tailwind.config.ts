import type { Config } from "tailwindcss"

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#00B37E",
          dark: "#009168",
          muted: "#D1FAF0",
        },
        surface: {
          DEFAULT: "#FFFFFF",
          alt: "#F4F4F5",
        },
        utext: {
          DEFAULT: "#18181B",
          muted: "#71717A",
          inverse: "#FAFAF9",
        },
        uborder: {
          DEFAULT: "#E4E4E7",
          focus: "#00B37E",
        },
        citation: {
          bg: "#F0FDF9",
          border: "#6EE7CA",
        },
      },
      fontFamily: {
        heading: ["var(--font-space-grotesk)", "sans-serif"],
        body: ["var(--font-inter)", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "monospace"],
      },
    },
  },
  plugins: [],
}

export default config
