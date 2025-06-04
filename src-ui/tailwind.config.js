/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Catppuccin Mocha Theme Colors
      colors: {
        // Base colors with ctp prefix
        'ctp-base': "#1e1e2e",
        'ctp-mantle': "#181825", 
        'ctp-crust': "#11111b",
        
        // Surface colors
        'ctp-surface0': "#313244",
        'ctp-surface1': "#45475a",
        'ctp-surface2': "#585b70",
        
        // Overlay colors  
        'ctp-overlay0': "#6c7086",
        'ctp-overlay1': "#7f849c",
        'ctp-overlay2': "#9399b2",
        
        // Text colors
        'ctp-subtext0': "#a6adc8",
        'ctp-subtext1': "#bac2de",
        'ctp-text': "#cdd6f4",
        
        // Accent colors
        'ctp-lavender': "#b4befe",
        'ctp-blue': "#89b4fa",
        'ctp-sapphire': "#74c7ec",
        'ctp-sky': "#89dceb",
        'ctp-teal': "#94e2d5",
        'ctp-green': "#a6e3a1",
        'ctp-yellow': "#f9e2af",
        'ctp-peach': "#fab387",
        'ctp-maroon': "#eba0ac",
        'ctp-red': "#f38ba8",
        'ctp-mauve': "#cba6f7",
        'ctp-pink': "#f5c2e7",
        'ctp-flamingo': "#f2cdcd",
        'ctp-rosewater': "#f5e0dc",
        
        // Legacy colors without prefix for compatibility
        base: "#1e1e2e",
        mantle: "#181825", 
        crust: "#11111b",
        surface0: "#313244",
        surface1: "#45475a",
        surface2: "#585b70",
        overlay0: "#6c7086",
        overlay1: "#7f849c",
        overlay2: "#9399b2",
        subtext0: "#a6adc8",
        subtext1: "#bac2de",
        text: "#cdd6f4",
        lavender: "#b4befe",
        blue: "#89b4fa",
        sapphire: "#74c7ec",
        sky: "#89dceb",
        teal: "#94e2d5",
        green: "#a6e3a1",
        yellow: "#f9e2af",
        peach: "#fab387",
        maroon: "#eba0ac",
        red: "#f38ba8",
        mauve: "#cba6f7",
        pink: "#f5c2e7",
        flamingo: "#f2cdcd",
        rosewater: "#f5e0dc",
      },
      
      // Custom animations
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
      },
      
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
      },
    },
  },
  plugins: [],
}