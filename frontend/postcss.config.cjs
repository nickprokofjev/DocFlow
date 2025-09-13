module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

module.exports = {
  extends: ["stylelint-config-standard"],
  rules: {},
  ignoreAtRules: ["tailwind", "apply", "variants", "responsive", "screen"],
};