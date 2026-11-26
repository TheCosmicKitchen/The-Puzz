// Anonymous daily stats, shared through Supabase (schema: supabase/migrations/*_puzz_stats.sql).
// Each daily sends a 'play' when it opens and a 'solve' when it's finished, once per device per day.
// Nothing identifies the player: no account, no device id, just the game, the day, the time taken,
// the player's Puzz streak and a little per-game `meta` ({ steps: 4 }, { peeks: 1 }...).
// The database only accepts new rows; pages read totals back through the puzz_stats() function.
// Everything here is best-effort: offline or blocked, the games carry on exactly as before.
(function () {
  const URL = 'https://gbryzpjwsuluwfggdldb.supabase.co/rest/v1/', KEY = 'sb_publishable_q-S2wKZXRdAv0zqKEjs9pQ_4hrO59xE';
  const HEAD = { apikey: KEY, 'Content-Type': 'application/json' };
  const d = new Date(), DAY = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const SENT = 'puzz-stats-sent';

  // Once per game, kind and day on this device, so reloading a finished puzzle doesn't count it twice.
  function once(game, kind) {
    try {
      const s = JSON.parse(localStorage.getItem(SENT)) || {};
      const k = `${game}:${kind}`;
      if (s.day !== DAY) { s.day = DAY; s.k = []; }
      if (s.k.includes(k)) return false;
      s.k.push(k); localStorage.setItem(SENT, JSON.stringify(s)); return true;
    } catch (e) { return false; }
  }
  function send(row) {
    return fetch(URL + 'puzz_events', { method: 'POST', headers: { ...HEAD, Prefer: 'return=minimal' }, body: JSON.stringify(row), keepalive: true })
      .catch(() => {});
  }

  let stats = null;
  function load(fresh) {
    if (!stats || fresh) stats = fetch(URL + 'rpc/puzz_stats', { method: 'POST', headers: HEAD, body: JSON.stringify({ p_day: DAY }) })
      .then(r => r.ok ? r.json() : null).catch(() => null);
    return stats;
  }

  const mmss = s => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  const plural = (n, w) => `${n.toLocaleString()} ${w}${n === 1 ? '' : 's'}`;
  // One line for a finish screen, e.g. "Today: 41 solves from 58 plays · median 3:12 · longest streak 9 days".
  function line(g) {
    if (!g || !g.solved) return '';
    const bits = [`Today: ${plural(g.solved, 'solve')}${g.plays ? ` from ${plural(g.plays, 'play')}` : ''}`];
    if (g.median_seconds != null) bits.push(`median ${mmss(g.median_seconds)}`);
    if (g.longest_streak > 1) bits.push(`longest streak ${g.longest_streak} days`);
    return bits.join(' · ');
  }

  // Today's daily opened.
  function play(game) { if (once(game, 'play')) send({ game, day: DAY, kind: 'play' }); }

  // Today's daily finished. `el` is the finish panel: a line of everyone's totals is added to it.
  async function solve(game, { seconds, meta } = {}, el) {
    if (once(game, 'solve')) {
      const streak = window.Kitchen ? Kitchen.streak('puzz').current : null;
      await send({ game, day: DAY, kind: 'solve', seconds: Number.isFinite(seconds) ? Math.round(seconds) : null, streak, meta: meta || {} });
      load(true);
    }
    if (!el) return;
    const s = await load(), text = s && line(s.games[game]);
    if (!text || !el.isConnected) return;
    let p = el.querySelector('.puzz-stats');
    if (!p) { p = document.createElement('p'); p.className = 'puzz-stats sub'; el.append(p); }
    p.textContent = text + '. Counted anonymously.';
  }

  window.PuzzStats = { play, solve, load, line, DAY };
})();
