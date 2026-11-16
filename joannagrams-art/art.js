// Hand-drawn weekly pictures for Joannagrams.
//
// To add one: put the PNG in this folder, then add a line to the list below.
//   week    any date in the week it's for ('2026-11-23'); the picture runs Monday to Sunday
//   file    the PNG's file name in this folder
//   name    what it's called; shown when the week's picture is finished ("Snow globe: finished!")
//   pieces  optional: seven names for what each day uncovers, top band (or first square) first.
//           Without them the message says "more of the picture" (or "a new square").
//   bg      optional: the colour transparent pixels become (default cream, '#F6EEDC')
//
// A listed picture takes over its week from the built-in one. To try a PNG before listing it,
// open joannagrams-art/preview.html and drop the file on it. See README.md for sizes.
window.JG_ART = [
  // { week: '2026-11-23', file: 'snow-globe.png', name: 'Snow globe' },
  // { week: '2026-11-30', file: 'tea-party.png', name: 'Tea party', pieces: ['the teapot', 'a cup', 'cake', 'a spoon', 'sugar', 'a doily', 'the table'] },
];
