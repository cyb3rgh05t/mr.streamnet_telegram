/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      // Using CSS variables defined in index.css
      // To change theme colors, edit :root in index.css
      colors: {
        telegram: {
          blue: "#0088cc",
          light: "#64b5ef",
          dark: "#006699",
        },
        discord: {
          blurple: "var(--discord-blurple)",
          green: "var(--discord-green)",
          yellow: "var(--discord-yellow)",
          fuchsia: "var(--discord-fuchsia)",
          red: "var(--discord-red)",
        },
        dark: {
          sidebar: "var(--sidebar-bg)",
          navbar: "var(--navbar-bg)",
          card: "var(--card-bg)",
          input: "var(--input-bg)",
          border: "var(--border-color)",
        },
        status: {
          online: "var(--status-online)",
          offline: "var(--status-offline)",
          success: "var(--success-color)",
          warning: "var(--warning-color)",
          danger: "var(--danger-color)",
          info: "var(--info-color)",
        },
        text: {
          DEFAULT: "var(--text)",
          hover: "var(--text-hover)",
          muted: "var(--text-muted)",
        },
        accent: {
          DEFAULT: "var(--accent-color)",
          hover: "var(--accent-color-hover)",
        },
        stat: {
          channels: "var(--stat-channels)",
          roles: "var(--stat-roles)",
          commands: "var(--stat-commands)",
          services: "var(--stat-services)",
        },
      },
      spacing: {
        navbar: "var(--navbar-height)",
        sidebar: "var(--sidebar-width)",
      },
    },
  },
  plugins: [],
  darkMode: "class",
};
