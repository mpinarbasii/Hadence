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
        // Calm, evidence-oriented palette — see docs/architecture.md §"UX / Design direction"
        ink: "#111318",
        paper: "#FAFAF8",
        muted: "#6B7280",
        accent: "#2563EB",
        evidence: {
          strong: "#15803D",
          partial: "#B45309",
          weak: "#B91C1C",
          none: "#6B7280",
        },
      },
    },
  },
  plugins: [],
};

export default config;
