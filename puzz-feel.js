// The Puzz feel layer: shared by every page.  <script src="puzz-feel.js"></script> (in <head>, not deferred, so it can catch the first page reveal)
// Pages load it with ?v=<hash of this file>, set by tools/stamp_assets.py, so changes are never served stale.
(function(){
  if (window.__puzzFeel) return; window.__puzzFeel = true;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Near-instant navigation: fetch a page as soon as you aim at its link. Chrome and Edge use speculation rules;
  // every other browser gets a plain prefetch on hover or touch. Prefetch only (never prerender), so no game's
  // timer starts before you arrive. The pattern is the folder this script is served from (/The-Puzz/ on the live
  // site, / on a local server), so it matches wherever the site runs.
  const me = document.currentScript && document.currentScript.src;
  const root = (me ? new URL('./', me) : new URL('./', location.href)).pathname;
  const sameSite = a => a && a.origin === location.origin && !a.hash && a.pathname !== location.pathname && !a.hasAttribute('download');
  if (HTMLScriptElement.supports && HTMLScriptElement.supports('speculationrules')) {
    const s = document.createElement('script'); s.type = 'speculationrules';
    s.textContent = JSON.stringify({prefetch: [{source: 'document', where: {and: [{href_matches: root + '*'}, {not: {selector_matches: '[download]'}}]}, eagerness: 'moderate'}]});
    document.head.append(s);
  } else {
    const done = new Set();
    const warm = e => { const a = e.target.closest && e.target.closest('a[href]'); if (!sameSite(a) || done.has(a.href)) return;
      done.add(a.href); const l = document.createElement('link'); l.rel = 'prefetch'; l.href = a.href; document.head.append(l) };
    addEventListener('pointerover', warm, {passive: true}); addEventListener('touchstart', warm, {passive: true});
  }

  // A page transition the browser has to skip (a fast double navigation, a resize mid-load) rejects its promises;
  // that's harmless, so don't let it surface as an uncaught error.
  const quiet = e => { const vt = e.viewTransition; if (vt) { vt.ready.catch(() => {}); vt.finished.catch(() => {}); vt.updateCallbackDone && vt.updateCallbackDone.catch(() => {}) } };
  addEventListener('pagereveal', quiet); addEventListener('pageswap', quiet);

  // A tiny haptic tick on presses, on phones that support it (Android). Off with reduced motion.
  if (!reduced && navigator.vibrate && matchMedia('(pointer: coarse)').matches) {
    addEventListener('pointerdown', e => { const b = e.target.closest && e.target.closest('button:not(:disabled), [role="button"], a.card');
      if (b) try { navigator.vibrate(6) } catch (err) {} }, {passive: true});
  }

  // ---- Motion helpers. All use the Web Animations API on transform-style properties (scale, translate, rotate,
  // which compose with a game's own transform) and opacity. Each is a no-op with reduced motion and never holds
  // the final state: the element is already in its end state, the animation only plays the way there.
  const EASE = 'cubic-bezier(.2,.8,.2,1)', SPRING = 'cubic-bezier(.3,1.5,.6,1)';
  const isSvg = el => el instanceof SVGElement && !(el instanceof SVGSVGElement);
  const prep = el => {
    if (isSvg(el)) { el.style.transformBox = 'fill-box'; el.style.transformOrigin = 'center' }
    else if (getComputedStyle(el).display === 'inline') el.style.display = 'inline-block';  // transforms skip inline boxes
  };
  const anim = (el, kf, o) => {
    if (reduced || !el || !el.animate) return null;
    try { prep(el); return el.animate(kf, Object.assign({duration: 200, easing: EASE}, o)) } catch (e) { return null }
  };
  const list = els => !els ? [] : (els.length !== undefined && !(els instanceof Element)) ? Array.from(els) : [els];
  const wait = (ms) => new Promise(r => setTimeout(r, ms));
  const done = a => a ? a.finished.catch(() => {}) : Promise.resolve();

  window.Puzz = Object.assign(window.Puzz || {}, {
    reduced, EASE, SPRING, anim,
    // Haptics: tick for small confirmations (a letter placed), thud for big moments (a word strikes, a solve).
    tick(){ if (!reduced && navigator.vibrate) try { navigator.vibrate(8) } catch (e) {} },
    thud(){ if (!reduced && navigator.vibrate) try { navigator.vibrate([14, 40, 22]) } catch (e) {} },

    // A number changed: pop it. With a value, sets the text first and only pops when it actually changed.
    pop(el, value){
      if (!el) return null;
      if (value !== undefined) { const s = String(value); if (el.textContent === s) return null; el.textContent = s }
      return anim(el, [{scale: 1}, {scale: 1.22, offset: .35}, {scale: 1}], {duration: 240, easing: SPRING});
    },
    // Count a number up (or down) to `to`; the text is always `to` at the end, and at once with reduced motion.
    count(el, to, {from, duration = 320, format = String} = {}){
      if (!el) return;
      if (el.__puzzCount) cancelAnimationFrame(el.__puzzCount);
      const a = from !== undefined ? from : (parseFloat(el.textContent) || 0);
      if (reduced || a === to) { el.textContent = format(to); return }
      const t0 = performance.now();
      const step = t => { const k = Math.min(1, (t - t0) / duration), e = 1 - Math.pow(1 - k, 3);
        el.textContent = format(k < 1 ? Math.round(a + (to - a) * e) : to);
        el.__puzzCount = k < 1 ? requestAnimationFrame(step) : 0 };
      el.__puzzCount = requestAnimationFrame(step);
    },
    // A wrong answer: a 6 px shake, three cycles.
    shake(el){
      return anim(el, [0, -6, 6, -6, 6, -6, 6, 0].map(x => ({translate: `${x}px 0`})), {duration: 320, easing: 'linear'});
    },
    // A typed letter drops into its cell.
    drop(el){
      return anim(el, [{translate: '0 -10px', opacity: .2}, {translate: '0 0', opacity: 1}], {duration: 120, easing: SPRING});
    },
    // A placed piece settles with a tiny bounce.
    settle(el){
      return anim(el, [{scale: 1.12}, {scale: .97, offset: .55}, {scale: 1}], {duration: 200, easing: EASE});
    },
    // A conflict flashes red once. Colour is paint-only; the shape never moves.
    flash(el, color = '#D2453A'){
      if (!el) return null;
      const svg = isSvg(el);
      return anim(el, svg ? [{fill: color, stroke: color}, {}] : [{boxShadow: `inset 0 0 0 999px ${color}`, color: '#fff'}, {}],
        {duration: 360, easing: 'ease-out'});
    },
    // Cells flip in sequence (a right word). `mid(el, i)` runs as each cell turns edge-on, to swap its look.
    flip(els, {stagger = 80, duration = 260, mid} = {}){
      const xs = list(els);
      if (reduced) { if (mid) xs.forEach(mid); return Promise.resolve() }
      return Promise.all(xs.map((el, i) => {
        if (mid) setTimeout(() => mid(el, i), i * stagger + duration / 2);
        return done(anim(el, [{rotate: 'x 0deg'}, {rotate: 'x 90deg', offset: .5}, {rotate: 'x 0deg'}], {duration, delay: i * stagger, easing: 'ease-in-out'}));
      }));
    },
    // A solved board: a highlight sweeps across in reading order.
    sweep(els, {stagger = 30} = {}){
      const xs = list(els);
      return Promise.all(xs.map((el, i) => done(anim(el, [{scale: 1, filter: 'brightness(1)'}, {scale: 1.1, filter: 'brightness(1.3)', offset: .4}, {scale: 1, filter: 'brightness(1)'}],
        {duration: 300, delay: i * stagger}))));
    },
    // Anything into view one after another (cards, offers). Hidden only while waiting, via fill: backwards.
    stagger(els, {stagger = 20, duration = 180, from = {translate: '0 10px', opacity: 0}} = {}){
      if (document.hidden) return Promise.resolve();  // hidden tabs pause animations; never leave things invisible
      return Promise.all(list(els).map((el, i) => done(anim(el, [from, {}],
        {duration, delay: i * stagger, fill: 'backwards'}))));
    },
    // Fly a copy of `el` from where it is to `target` (an element or a DOMRect), then remove the copy.
    // The real element is left alone, so the game's state never depends on the flight.
    fly(el, target, {duration = 240, delay = 0, scale, easing = EASE, arc = 0, keep = false} = {}){
      if (reduced || !el || !target || !document.body.animate) return Promise.resolve();
      const a = el.getBoundingClientRect(), b = target.getBoundingClientRect ? target.getBoundingClientRect() : target;
      if (!a.width || !b.width) return Promise.resolve();
      const g = el.cloneNode(true); g.removeAttribute('id'); g.setAttribute('aria-hidden', 'true');
      Object.assign(g.style, {position: 'fixed', left: a.left + 'px', top: a.top + 'px', width: a.width + 'px', height: a.height + 'px',
        margin: 0, pointerEvents: 'none', zIndex: 60, boxSizing: 'border-box'});
      document.body.append(g);
      const dx = b.left + b.width / 2 - (a.left + a.width / 2), dy = b.top + b.height / 2 - (a.top + a.height / 2);
      const s = scale !== undefined ? scale : Math.min(b.width / a.width, b.height / a.height);
      const kf = arc ? [{translate: '0 0', scale: 1}, {translate: `${dx / 2}px ${dy / 2 - arc}px`, scale: (1 + s) / 2, offset: .5}, {translate: `${dx}px ${dy}px`, scale: s}]
                     : [{translate: '0 0', scale: 1}, {translate: `${dx}px ${dy}px`, scale: s}];
      const an = g.animate(kf, {duration, delay, easing, fill: 'both'});
      return done(an).then(() => { if (!keep) g.remove(); return g });
    },
    wait,
  });

  // Lifted pieces (a selected number, a held tile): add class puzz-lift. See puzz-feel.css.
})();
