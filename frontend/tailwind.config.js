/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: 'var(--ink)',
          muted: 'var(--ink-muted)',
        },
        accent: {
          DEFAULT: 'var(--accent)',
          soft: 'var(--accent-soft)',
        },
        primary: {
          DEFAULT: 'var(--primary)',
          hover: 'var(--primary-hover)',
          soft: 'var(--primary-soft)',
          contrast: 'var(--primary-contrast)',
        },
        surface: {
          DEFAULT: 'var(--bg)',
          secondary: 'var(--bg-secondary)',
          elevated: 'var(--bg-elevated)',
          hover: 'var(--surface-hover)',
        },
        content: {
          DEFAULT: 'var(--text)',
          secondary: 'var(--text-secondary)',
        },
        line: 'var(--border)',
        'ai-accent': {
          DEFAULT: 'var(--ai-accent)',
          soft: 'var(--ai-accent-soft)',
        },
        status: {
          high: 'var(--status-high)',
          medium: 'var(--status-medium)',
          'medium-soft': 'var(--status-medium-soft)',
          low: 'var(--status-low)',
        },
      },
      borderColor: {
        DEFAULT: 'var(--border)',
      },
      borderRadius: {
        gsm: 'var(--radius-sm)',
        gmd: 'var(--radius-md)',
        glg: 'var(--radius-lg)',
        pill: 'var(--radius-pill)',
        card: 'var(--radius-card)',
        control: 'var(--radius-control)',
      },
      boxShadow: {
        gsm: 'var(--shadow-sm)',
        gmd: 'var(--shadow-md)',
        glg: 'var(--shadow-lg)',
        'card-default': 'var(--shadow-default)',
        'card-hover': 'var(--shadow-hover)',
        'card-active': 'var(--shadow-active)',
      },
      backgroundImage: {
        'brand-accent': 'var(--primary)',
      },
    },
  },
  plugins: [],
}
