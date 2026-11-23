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

  // Games can call Puzz.tick() / Puzz.thud() for their own moments (a word lands, a puzzle is solved).
  window.Puzz = Object.assign(window.Puzz || {}, {
    tick(){ if (!reduced && navigator.vibrate) try { navigator.vibrate(8) } catch (e) {} },
    thud(){ if (!reduced && navigator.vibrate) try { navigator.vibrate([14, 40, 22]) } catch (e) {} },
  });
})();
