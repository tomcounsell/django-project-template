/**
 * Minimalist Tailwind config for Django Project Template
 */
const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: [
    /**
     * HTML. Paths to Django template files that will contain Tailwind CSS classes.
     */
    '../templates/**/*.html',
    '../../apps/**/*.html',
    '../../templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        accent: '#ffd404', // Brand yellow for accents
        navy: {
          900: '#0a192f', // Deep navy for footer and primary buttons
          800: '#112240',
          700: '#1d3557',
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
      },
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans],
      },
      backgroundColor: theme => ({
        'footer': theme('colors.navy.900'),
      }),
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}