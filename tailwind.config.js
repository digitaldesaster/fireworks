/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
    "./node_modules/flyonui/dist/js/*.js", // Added FlyonUI JS components path
    "./node_modules/flatpickr/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require("flyonui"),
    require("flyonui/plugin"), // For FlyonUI JS components
    require("tailwindcss-motion"), // Added motion plugin
  ],
  flyonui: {
    themes: ["light", "dark", "gourmet"],
    vendors: true, // Enable vendor-specific CSS generation
  },
  safelist: [
    'list-inside',
    'list-disc',
    'list-decimal',
    'marker:text-purple-500',
    'mb-2',
    {
      pattern: /^list-/,
      variants: ['hover', 'focus'],
    },
    {
      pattern: /^marker:/,
      variants: ['hover', 'focus'],
    }
  ]
};
