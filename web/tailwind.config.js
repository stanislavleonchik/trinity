module.exports = {
  content: [
    './app/views/**/*.html.erb',
    './app/helpers/**/*.rb',
    './app/assets/stylesheets/**/*.css',
    './app/javascript/**/*.js'
  ],
  theme: {
    fontFamily: {
      'sans': ['ui-sans-serif', 'system-ui'],
      'serif': ['ui-serif', 'Georgia'],
      'mono': ['ui-monospace', 'SFMono-Regular'],
      'lack': ['Lack-Line-Regular'],
      'lucky': [ 'Lack-Italic'],
      'luc': ['Lack-Line-Italic'],
      'lac': ['Lack-Regular', ]
    },
    extend: {
      colors: {
        'soft-blue': '#C6D9F0',
        'bright-deep-blue': '#0527A1',
        'text-gray': '#000000',
        'forms-gray': '#D9D9D9'
      },
    }
  }
}
