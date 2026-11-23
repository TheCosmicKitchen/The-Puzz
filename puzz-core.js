// The Puzz core: the helpers every game shares, written once.
// Load it before a game's own script:  <script src="puzz-core.js?v=2"></script>
// WHEN YOU CHANGE THIS FILE, bump ?v= in every page that loads it. Pages cache it for 10 minutes, and a new page with an old core breaks.
// It defines plain globals (same names the games already use), so a game moves onto it by deleting its own copies.
// The pure parts (seeded random numbers, dates) also work in Node: require('./puzz-core.js'), for sims and tests.
// Careful: shuffle is NOT here yet. Games disagree on its argument order, and a swap would change dailies.

// ---- seeded random numbers: the same seed gives the same puzzle for everyone
function hseed(str){let h=1779033703^str.length;for(let i=0;i<str.length;i++){h=Math.imul(h^str.charCodeAt(i),3432918353);h=h<<13|h>>>19}h=Math.imul(h^h>>>16,2246822507);h=Math.imul(h^h>>>13,3266489909);return (h^h>>>16)>>>0}
function mulberry(a){return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}

// ---- days: puzzle #1 was 25 Oct 2026, local midnight
const PUZZ_START=[2026,9,25];
function puzzDay(on){const d=on?new Date(on+'T12:00'):new Date(),t=new Date(d.getFullYear(),d.getMonth(),d.getDate()),s=new Date(...PUZZ_START);
  const iso=`${t.getFullYear()}-${String(t.getMonth()+1).padStart(2,'0')}-${String(t.getDate()).padStart(2,'0')}`,wk=t.getDay();
  return{num:Math.round((t-s)/864e5)+1,iso,wk,weekend:wk===0||wk===6,label:t.toLocaleDateString(undefined,{weekday:'short',month:'short',day:'numeric'})}}

// games that need extra day fields (puzzle size, theme) define their own dayInfo built on puzzDay
function dayInfo(on){return puzzDay(on)}

// ---- small text helpers
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt=s=>`${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`;
const newCode=()=>Math.random().toString(36).slice(2,7);

if(typeof module!=='undefined'&&module.exports){module.exports={hseed,mulberry,puzzDay,dayInfo,esc,fmt,newCode}}
else{
  // ---- browser only
  var $=id=>document.getElementById(id);
  // saves: never throw (private windows, full storage), never crash a game
  var store={get(k){try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
  // a timer bound to a state object with .elapsed (seconds)
  var Timer={h:null,start(st,el){this.stop();const t0=Date.now()-(st.elapsed||0)*1000;this.h=setInterval(()=>{st.elapsed=Math.floor((Date.now()-t0)/1000);if(el)el.textContent=fmt(st.elapsed)},500)},stop(){clearInterval(this.h);this.h=null}};
  // a copy button that falls back to selecting the text when the clipboard says no
  var wireCopy=function(btn,getText,preId){btn.onclick=()=>{const ok=()=>{btn.textContent='Copied';setTimeout(()=>btn.textContent='Copy result',1500)},fb=()=>{const r=document.createRange();r.selectNodeContents($(preId));const s=getSelection();s.removeAllRanges();s.addRange(r);btn.textContent='Selected · copy it'};
    try{navigator.clipboard.writeText(getText()).then(ok,fb)}catch(e){fb()}}};
  // Daily / Endless style tab buttons
  var setTabs=function(mode){document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.mode===mode))};
}
