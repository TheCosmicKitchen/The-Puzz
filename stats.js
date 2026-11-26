// Your own puzzle history, kept on this device in IndexedDB (database 'puzz', store 'solves').
// Each finished daily adds one row: the game, the day, seconds taken, your Puzz streak at the time and a
// little per-game `meta` ({ steps: 4 }, { peeks: 1 }...). Nothing leaves the device and there are no
// accounts. Finish screens and the home page read it back as your totals. Best-effort: if IndexedDB
// isn't available (some private windows), the games carry on exactly as before.
(function () {
  const d = new Date(), DAY = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  let db;
  const open = () => db || (db = new Promise((res, rej) => {
    const r = indexedDB.open('puzz', 1);
    r.onupgradeneeded = () => r.result.createObjectStore('solves', { keyPath: 'key' });
    r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error);
  }));
  const run = async (mode, fn) => {
    const x = await open();
    return new Promise((res, rej) => {
      const t = x.transaction('solves', mode), req = fn(t.objectStore('solves'));
      t.oncomplete = () => res(req.result); t.onerror = () => rej(t.error);
    });
  };
  // Every solve on this device, oldest first.
  const all = () => run('readonly', s => s.getAll()).catch(() => []);

  const mmss = s => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  // { solved, best, median } for one game's rows; best and median only when the game is timed.
  function summary(rows) {
    const t = rows.map(r => r.seconds).filter(Number.isFinite).sort((a, b) => a - b);
    return { solved: rows.length, best: t.length ? t[0] : null, median: t.length ? t[(t.length - 1) >> 1] : null };
  }
  // e.g. "12 solved · best 0:58 · median 1:40"
  function line(s) {
    if (!s || !s.solved) return '';
    const bits = [`${s.solved.toLocaleString()} solved`];
    if (s.best != null) bits.push(`best ${mmss(s.best)}`);
    if (s.median != null && s.solved > 2) bits.push(`median ${mmss(s.median)}`);
    return bits.join(' · ');
  }

  // Today's daily finished. `el` is the finish panel: a line of your totals for this game is added to it.
  async function solve(game, { seconds, meta } = {}, el) {
    const key = `${DAY}:${game}`;
    try {
      const had = await run('readonly', s => s.get(key));
      if (!had) await run('readwrite', s => s.put({ key, day: DAY, game, at: Date.now(),
        seconds: Number.isFinite(seconds) ? Math.round(seconds) : null,
        streak: window.Kitchen ? Kitchen.streak('puzz').current : null, meta: meta || {} }));
    } catch (e) { return; }
    if (!el) return;
    const text = line(summary((await all()).filter(r => r.game === game)));
    if (!text || !el.isConnected) return;
    let p = el.querySelector('.puzz-stats');
    if (!p) { p = document.createElement('p'); p.className = 'puzz-stats sub'; el.append(p); }
    p.textContent = `Your record on this device: ${text}.`;
  }

  window.PuzzStats = { solve, all, summary, line, DAY };
})();
