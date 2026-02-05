import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#C5B0CD',
          DEFAULT: '#9B5DE0',
          dark: '#450693',
        },
        accent: {
          pink: '#FF2DD1',
          light: '#F7A8C4',
        },
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(to bottom, #C5B0CD, #9B5DE0)',
        'gradient-accent': 'linear-gradient(to bottom, #FF2DD1, #F7A8C4)',
      },
    },
  },
  plugins: [],
};

export default config;
