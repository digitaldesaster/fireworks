/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
    "./node_modules/flyonui/dist/js/*.js", // Added FlyonUI JS components path
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require("flyonui"),
    require("flyonui/plugin"), // For FlyonUI JS components
    require('tailwindcss-motion'), // Added motion plugin
  ],
  flyonui: {
    themes: ["light", "dark", "gourmet"],
  },
};
