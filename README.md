# The Puzz

Live at https://thecosmickitchen.github.io/The-Puzz/

Free daily puzzles, served as plain static pages on GitHub Pages. No build step and no server.

- `index.html`: today's set
- `hexstitch.html`: Calico-style hex tiling with pattern hexes and stitched pairs
- `shadowbox.html`: colour-and-shape pieces. Every colour patch is shown off the board as a loose shape to fit in your head; fences, tallies and links settle the shapes.
- `joannagrams.html`: crochet anagrams. The goal is the day's hidden word: chain letters into words, unpick the marked stitches, and rearrange them to join the blanket (a Jumble-style meta). Finishing the granny square is an optional extra. Made for Joanna.
- `whistlestop.html`: train-themed route puzzle in the spirit of The Witness. A 40-stop journey teaches one sign per chapter by experimentation and fills in a sign book; finishing it unlocks endless lines. There is also a daily line.
- `hanko.html` (prototype): daily kanji. Build today's kanji from its parts, find the hub kanji that makes four real words, then a spaced-repetition recall round from your stamp book. Grades 1–2 (240 kanji). Data: KANJIDIC2 / JMdict (EDRDG, CC BY-SA 4.0), KanjiVG (CC BY-SA 3.0).

Every puzzle is generated in the browser from a seed. The daily seed is the date, so everyone gets the same puzzle. Endless mode uses a random seed, which appears in the URL hash so a puzzle can be shared. A built-in solver checks that each puzzle has exactly one solution before showing it.

## Prototypes
- `crosslight.html`: six five-letter words in a waffle grid, shared pool of 15 guesses; green / yellow / blue (letter is in a crossing word).
- `strike.html`: Sumplete-style number grid; strike numbers so every row and column hits its target. Unique solutions.
- `sampler.html`: nonogram stitched as cross-stitch; every pattern is solvable by line logic alone.
- `tally.html`: six numbers, + − × ÷, exact target guaranteed, par = fewest steps.
- `ladder.html`: four-letter word ladders with par and hints.
