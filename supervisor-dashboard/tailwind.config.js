/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        blue: {
          500: '#6366f1',
          600: '#4f46e5',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        },
        green: {
          500: '#10b981',
          600: '#059669',
        },
        orange: {
          500: '#f59e0b',
          600: '#d97706',
        },
        red: {
          500: '#ef4444',
          600: '#dc2626',
        }
      }
    },
  },
  plugins: [],
} 