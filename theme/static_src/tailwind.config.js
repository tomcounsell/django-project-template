/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */
const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: [
    /**
     * HTML. Paths to Django template files that will contain Tailwind CSS classes.
     */

    /*  Templates within theme app (<tailwind_app_name>/templates), e.g. design_system.html. */
    '../templates/**/*.html',

    /*  Templates within other apps, e.g., public app templates. */
    '../../apps/**/*.html',

    /*  Main templates directory of the project (BASE_DIR/templates). */
    '../../templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          300: '#F3E5C7',
          500: '#D4AF37',
          600: '#A67C00',
        },
        success: {500: '#4FAE4E'},
        warning: {500: '#F4C23E'},
        error: {500: '#C83A3B'},
        info: {500: '#4EA9B9'},
        'hover-light': '#F6E8BF',
        'active-gold': '#B1862F',
      },
      textColor: {
        DEFAULT: '#A67C00', // gold-600 as default text color for headers
      },
      fontFamily: {
        sans: ['Avenir', ...defaultTheme.fontFamily.sans],
        body: ['Proxima Nova', ...defaultTheme.fontFamily.sans],
      },
    },
  },
  plugins: [
    /**
     * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
     * for forms. If you don't like it or have own styling for forms,
     * comment the line below to disable '@tailwindcss/forms'.
     */
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
