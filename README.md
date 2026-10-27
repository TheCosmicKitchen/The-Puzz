# The Puzz

Live at https://thecosmickitchen.github.io/The-Puzz/

Free daily puzzles, served as plain static pages on GitHub Pages. No build step and no server.

- `index.html`: today's set
- `hexstitch.html`: Calico-style hex tiling with pattern hexes and stitched pairs
- `shadowbox.html`: colour-and-shape pieces. Every colour patch is shown off the board as a loose shape to fit in your head; fences, tallies and links settle the shapes.
- `joannagrams.html`: crochet anagrams. Chain letters into words to build a granny square, then unpick the marked stitches to join the blanket (a Jumble-style meta). Made for Joanna.
- `whistlestop.html`: train-themed route puzzle in the spirit of The Witness. A 40-stop journey teaches one sign per chapter by experimentation and fills in a sign book; finishing it unlocks endless lines. There is also a daily line.

Every puzzle is generated in the browser from a seed. The daily seed is the date, so everyone gets the same puzzle. Endless mode uses a random seed, which appears in the URL hash so a puzzle can be shared. A built-in solver checks that each puzzle has exactly one solution before showing it.
