import type { Config } from 'tailwindcss';

export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#F0FDFA',
          100: '#CCFBF1',
          200: '#99F6E4',
          300: '#5EEAD4',
          400: '#2DD4BF',
          500: '#14B8A6',
          600: '#0D9488',
          700: '#0F766E', // Primary brand per Sec. 17.1
          800: '#115E59',
          900: '#134E4A',
          DEFAULT: '#0F766E',
        },
        surface: {
          page: '#F5F7F8', // Soft gray page background per Sec. 17.1
          card: '#FFFFFF',
          muted: '#F8FAFC',
          border: '#E2E8F0',
        },
        risk: {
          low: {
            DEFAULT: '#16A34A',
            bg: '#F0FDF4',
            border: '#BBF7D0',
            text: '#15803D',
          },
          medium: {
            DEFAULT: '#D97706',
            bg: '#FFFBEB',
            border: '#FDE68A',
            text: '#B45309',
          },
          high: {
            DEFAULT: '#DC2626',
            bg: '#FEF2F2',
            border: '#FECACA',
            text: '#B91C1C',
          },
        },
        stock: {
          in: '#16A34A',
          low: '#D97706',
          out: '#DC2626',
          excess: '#2563EB',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '8px',
        card: '8px',
      },
      maxWidth: {
        layout: '1440px',
      },
      boxShadow: {
        subtle: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        card: '0 1px 3px 0 rgba(0, 0, 0, 0.07), 0 1px 2px -1px rgba(0, 0, 0, 0.04)',
      },
    },
  },
  plugins: [],
} satisfies Config;
