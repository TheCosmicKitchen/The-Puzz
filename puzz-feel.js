// The Puzz feel layer: shared by every page.  <script src="puzz-feel.js"></script> (in <head>, not deferred, so it can catch the first page reveal)
// Pages load it with ?v=<hash of this file>, set by tools/stamp_assets.py, so changes are never served stale.
(function(){
  if (window.__puzzFeel) return; window.__puzzFeel = true;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Near-instant navigation: fetch a page as soon as you aim at its link. Chrome and Edge use speculation rules;
  // every other browser gets a plain prefetch on hover or touch. Prefetch only (never prerender), so no game's
  // timer starts before you arrive.
  const sameSite = a => a && a.origin === location.origin && !a.hash && a.pathname !== location.pathname && !a.hasAttribute('download');
  if (HTMLScriptElement.supports && HTMLScriptElement.supports('speculationrules')) {
    const s = document.createElement('script'); s.type = 'speculationrules';
    s.textContent = JSON.stringify({prefetch: [{source: 'document', where: {and: [{href_matches: '/The-Puzz/*'}, {not: {selector_matches: '[download]'}}]}, eagerness: 'moderate'}]});
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

  // ---- Motion helpers (from the site-wide polish; only the ones games use so far). Web Animations on scale and
  // filter, which compose with a game's own transform. Each is a no-op with reduced motion and never holds the final
  // state: the element is already in its end state, the animation only plays the way there.
  const buzz = () => !reduced && navigator.vibrate && (!navigator.userActivation || navigator.userActivation.hasBeenActive);
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
  const done = a => a ? a.finished.catch(() => {}) : Promise.resolve();

  window.Puzz = Object.assign(window.Puzz || {}, {
    // Haptics: tick for small confirmations (a piece placed), thud for big moments (a solve).
    // Chrome refuses (and logs an error) before the first tap, so wait for one.
    tick(){ if (buzz()) try { navigator.vibrate(8) } catch (e) {} },
    thud(){ if (buzz()) try { navigator.vibrate([14, 40, 22]) } catch (e) {} },
    // Something was met (a clue, a number changed): pop it. With a value, sets the text first and only pops on a change.
    pop(el, value){
      if (!el) return null;
      if (value !== undefined) { const t = String(value); if (el.textContent === t) return null; el.textContent = t }
      return anim(el, [{scale: 1}, {scale: 1.22, offset: .35}, {scale: 1}], {duration: 240, easing: SPRING});
    },
    // A conflict flashes red once. Colour is paint-only; the shape never moves.
    flash(el, color = '#D2453A'){
      if (!el) return null;
      return anim(el, isSvg(el) ? [{fill: color, stroke: color}, {}] : [{boxShadow: `inset 0 0 0 999px ${color}`, color: '#fff'}, {}],
        {duration: 360, easing: 'ease-out'});
    },
    // A solved board: a highlight sweeps across in reading order.
    sweep(els, {stagger = 30} = {}){
      return Promise.all(list(els).map((el, i) => done(anim(el, [{scale: 1, filter: 'brightness(1)'}, {scale: 1.1, filter: 'brightness(1.3)', offset: .4}, {scale: 1, filter: 'brightness(1)'}],
        {duration: 300, delay: i * stagger}))));
    },
  });
})();
