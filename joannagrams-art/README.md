# Joannagrams weekly pictures

Each week of Joannagrams has a pixel picture. Every day you finish the whole granny square uncovers a seventh of it, in a surprise order, so the full picture appears once all seven squares are done.

This folder lets hand-drawn pictures take over from the built-in ones. A picture is a PNG plus one line in `art.js`.

## Drawing one

Draw in any pixel-art app (Aseprite, Piskel, Pixilart, Procreate with a pixel grid…) and export a PNG. Two shapes work:

**One picture.** It's uncovered in seven bands, top to bottom in the week's own order.
- Any size up to 64 × 64. The built-in ones are 14 × 14.
- A height of 14, 21, 28… splits evenly into seven bands. Other heights work, but some bands get an extra row.
- Shown about 230 px wide, so 14 × 14 to 28 × 28 reads best on a phone.

**A strip of seven squares.** Each finished day uncovers one square. The image must be exactly seven times as wide as it is tall: 112 × 16 makes seven 16 × 16 squares. Each square can be its own little scene, the way the first weeks' Village Green, Seaside and Starry Night are.

Either way:
- **Transparent pixels** become the cream background (`#F6EEDC`). Or set `bg` in `art.js` to another colour.
- **Export at its real size or scaled up.** Exports at 1×, 4×, 10× and so on are all fine; the game shrinks a scaled-up export back to its real pixels. Don't let the app smooth or blur the edges.
- Keep to a palette. Under about 20 colours looks most like yarn.

`example-maple-leaf.png` is the current Maple Leaf picture as a 14 × 14 PNG, if you want a template to open.

## Trying one out

Open [`preview.html`](preview.html) (in this folder, on the live site or locally) and drop the PNG on it. It shows the picture exactly as players will see it, with a slider for how many days are finished, and says plainly if something's wrong (too big, an uneven height and so on). The preview doesn't change the game.

The preview also lists the next twelve weeks and what each one shows, so you can see which built-in picture you're replacing.

## Putting it in the game

1. Copy the PNG into this folder. Plain names work best, like `snow-globe.png`.
2. Add a line to the list in `art.js`:

   ```js
   { week: '2026-11-23', file: 'snow-globe.png', name: 'Snow globe' },
   ```

   - `week` is any date in that week; the picture runs Monday to Sunday.
   - `name` shows when the picture is finished ("Snow globe: finished!").
   - Optionally add `pieces` (seven names, top band or first square first) so the message after each square says what it uncovered. For example: `pieces: ['the snow', 'a little house', …]`.
3. Commit and push. The site updates in about a minute.

Add a picture before its Monday if you can. Swapping it in mid-week works, but anyone who already uncovered part of the old picture will see the new one from then on. The words in the puzzles never change: only the picture does.

If a PNG is missing or can't be read, that week quietly keeps its built-in picture, and the browser console says why.
