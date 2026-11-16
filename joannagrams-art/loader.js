// Turns a hand-drawn PNG into a Joannagrams weekly picture, and draws pictures as SVG.
// Shared by joannagrams.html and joannagrams-art/preview.html, so the preview shows exactly what players see.
//
// Two shapes of picture:
//  - one picture (any size up to 64 × 64): uncovered in seven bands, top to bottom in the reveal order
//  - a strip of seven squares, seven times as wide as it is tall: one square per finished day
// Transparent pixels become the background colour (cream unless the art list names another).
// A PNG exported scaled up (every pixel drawn as a 10 × 10 block, say) is shrunk back to its real pixels.
const JGArt = (() => {
  const CREAM = '#F6EEDC', MAX = 64;
  const hex = (r, g, b) => '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('').toUpperCase();

  // The Monday of the week a 'yyyy-mm-dd' date falls in, as 'yyyy-mm-dd'.
  function monday(iso) {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || ''); if (!m) return null;
    const d = new Date(+m[1], +m[2] - 1, +m[3]); d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  }

  // The size of one drawn pixel: the biggest block size where every block is a single colour, as long as
  // what's left is still a usable picture (seven rows or more, or a seven-square strip).
  function blockSize(px, W, H) {
    const same = (a, b) => px[a] === px[b] && px[a + 1] === px[b + 1] && px[a + 2] === px[b + 2] && px[a + 3] === px[b + 3];
    for (let k = Math.min(W, H); k > 1; k--) {
      if (W % k || H % k || W / k > MAX * 7 || H / k > MAX) continue;
      if (H / k < 7 && W / k !== 7 * H / k) continue;
      let ok = true;
      for (let y = 0; y < H && ok; y++) for (let x = 0; x < W && ok; x++) {
        const bx = x - x % k, by = y - y % k;
        if (!same((y * W + x) * 4, (by * W + bx) * 4)) ok = false;
      }
      if (ok) return k;
    }
    return 1;
  }

  // Read a loaded <img> into a picture. Throws with a plain message if the image won't work.
  function read(img, { bg = CREAM } = {}) {
    const W0 = img.naturalWidth, H0 = img.naturalHeight;
    if (!W0 || !H0) throw new Error('The image is empty.');
    if (W0 * H0 > 2048 * 2048) throw new Error(`The image is ${W0} × ${H0}, far too big. Export it at its real pixel size.`);
    const c = document.createElement('canvas'); c.width = W0; c.height = H0;
    const g = c.getContext('2d', { willReadFrequently: true }); g.drawImage(img, 0, 0);
    const px = g.getImageData(0, 0, W0, H0).data, k = blockSize(px, W0, H0), W = W0 / k, H = H0 / k;
    const grid = [...Array(H)].map((_, y) => [...Array(W)].map((_, x) => {
      const i = (y * k * W0 + x * k) * 4;
      return px[i + 3] < 128 ? bg : hex(px[i], px[i + 1], px[i + 2]);
    }));
    const colours = new Set(grid.flat()).size;
    if (W === 7 * H) {
      if (H > MAX) throw new Error(`Each square is ${H} × ${H} pixels. Keep squares to ${MAX} or smaller.`);
      const tiles = [...Array(7)].map((_, t) => grid.map(row => row.slice(t * H, t * H + H)));
      return { kind: 'tiles', tiles, width: W, height: H, scale: k, colours };
    }
    if (W > MAX || H > MAX) throw new Error(`The picture is ${W} × ${H} pixels. Keep it to ${MAX} × ${MAX} or smaller.`);
    if (H < 7) throw new Error(`The picture is only ${H} pixel${H === 1 ? '' : 's'} tall. It needs at least 7 rows, one band per day.`);
    return { kind: 'picture', pic: grid, width: W, height: H, scale: k, colours };
  }

  // Load an image file by URL (or a File from a drop) and read it.
  function load(src, opts) {
    return new Promise((resolve, reject) => {
      const im = new Image();
      im.onload = () => { try { resolve(read(im, opts)); } catch (e) { reject(e); } finally { if (src instanceof Blob) URL.revokeObjectURL(im.src); } };
      im.onerror = () => reject(new Error('That file could not be opened as an image. Use a PNG.'));
      im.src = src instanceof Blob ? URL.createObjectURL(src) : src;
    });
  }

  // Which rows belong to band k (0-6): the picture split into seven nearly equal bands, top to bottom.
  const band = (H, k) => [Math.floor(k * H / 7), Math.floor((k + 1) * H / 7)];

  // One rect per run of same-coloured pixels in a row.
  function runs(grid, y0, y1) {
    let s = '';
    for (let y = y0; y < y1; y++) {
      const row = grid[y]; let x = 0;
      while (x < row.length) { const c = row[x]; let e = x + 1; while (e < row.length && row[e] === c) e++; s += `<rect x="${x}" y="${y}" width="${e - x}" height="1" fill="${c}"/>`; x = e; }
    }
    return s;
  }

  // A whole picture with the bands in `shown` uncovered; `fresh` is the band that just appeared.
  // Covered bands are drawn as felt with a dashed stitch line, the way the game shows them.
  function pictureSVG(pic, shown, fresh) {
    const H = pic.length, W = pic[0].length; let s = '', knit = '';
    for (let k = 0; k < 7; k++) {
      const [y0, y1] = band(H, k), h = y1 - y0;
      if (shown.has(k)) {
        s += runs(pic, y0, y1);
        knit += `<rect x="0" y="${y0}" width="${W}" height="${h}" fill="url(#jgKnit)"/>`;
        if (k === fresh) knit += `<rect class="fresh" x="0" y="${y0}" width="${W}" height="${h}" fill="#fff"/>`;
      } else {
        const m = Math.min(.2, h * .1);
        s += `<rect x="${m}" y="${y0 + m}" width="${W - 2 * m}" height="${h - 2 * m}" rx="${Math.min(.45, h * .22)}" fill="var(--felt)"/>` +
          `<line x1="${Math.min(.9, W * .06)}" y1="${y0 + h / 2}" x2="${W - Math.min(.9, W * .06)}" y2="${y0 + h / 2}" stroke="var(--line)" stroke-width="${Math.max(.16, h * .08)}" stroke-dasharray=".5 .35"/>`;
      }
    }
    return `<svg viewBox="0 0 ${W} ${H}" aria-hidden="true"><defs><pattern id="jgKnit" width="1" height="1" patternUnits="userSpaceOnUse"><path d="M.18,.22 L.5,.82 L.82,.22" fill="none" stroke="rgba(0,0,0,.13)" stroke-width=".09"/></pattern></defs><g shape-rendering="crispEdges">${s}</g>${knit}</svg>`;
  }

  // One square of a seven-square strip.
  function squareSVG(grid) {
    const N = grid.length;
    return `<svg viewBox="0 0 ${grid[0].length} ${N}" shape-rendering="crispEdges" aria-hidden="true">${runs(grid, 0, N)}</svg>`;
  }

  // The art list (joannagrams-art/art.js), cleaned up: one entry per week, keyed by that week's Monday.
  function list() {
    const out = {};
    (window.JG_ART || []).forEach(a => {
      const wk = a && monday(a.week);
      if (wk && a.file) out[wk] = { ...a, week: wk, name: a.name || 'This week\'s picture' };
    });
    return out;
  }

  // A loaded picture in the shape joannagrams.html uses for its built-in scenes.
  function scene(entry, art) {
    const piece = i => (entry.pieces && entry.pieces[i]) || (art.kind === 'tiles' ? 'a new square' : 'more of the picture');
    return art.kind === 'tiles'
      ? { name: entry.name, squares: art.tiles, tiles: art.tiles.map((_, i) => ({ name: piece(i) })) }
      : { name: entry.name, pic: art.pic, tiles: [...Array(7)].map((_, i) => ({ name: piece(i) })) };
  }

  return { read, load, list, scene, monday, band, pictureSVG, squareSVG, CREAM, MAX };
})();
