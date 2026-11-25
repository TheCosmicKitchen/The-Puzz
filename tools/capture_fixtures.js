// Captures tools/sim_fixtures.json from scrawl.html. Open scrawl.html (any mode) and run this in the browser console
// (or paste it into a devtools snippet); it returns the JSON. `py tools/scrawl_sim.py selftest` replays the same
// script in Python. The script: each turn, strike the first 3-letter word a triple loop finds in the hand (at slot
// `at`), then end the turn. Nothing is saved: the run is played with mode set to 'capture'.
(function captureFixtures(){
  const keepMode=mode,keepS=S,keepHP=FOE_HP_SCALE,keepATK=FOE_ATK_SCALE;mode='capture';
  const fx=t=>t.fx||null;
  // one turn of the script; at(turn) = the slot the word starts in
  function step(at){S.draft=null;const h=S.hand.filter(t=>!t.crossed);let hit='-';
    outer:for(let x=0;x<h.length;x++)for(let y=0;y<h.length;y++)for(let z=0;z<h.length;z++){
      if(x===y||y===z||x===z)continue;const w=h[x].ch+h[y].ch+h[z].ch;
      if(WORDS.has(w)){S.spell=[];[h[x],h[y],h[z]].forEach((t,i)=>putInBlade(t.id,at+i));strike();hit=w;break outer}}
    return hit}
  function play(seed,runes,turns,at,rec){S=newRun(seed,false,seed.startsWith('endless-')&&turns>6);if(runes)S.runes={...runes};startFight();
    const trail=[];for(let i=0;i<turns;i++){if(S.over)break;const hit=step(at(i));if(S.over)break;S.draft=null;endTurn();trail.push(rec(hit))}
    return trail}
  const out={note:'Captured from scrawl.html in the browser with tools/capture_fixtures.js. trail = a fixed script (strike the first 3-letter word found by a triple loop over the hand, then end the turn), recorded as [word, foe index, your hp, foe hps] after each turn. `py tools/scrawl_sim.py selftest` replays it in Python and must match exactly.',
    captured:new Date().toISOString().slice(0,10),cases:[],deep:[],sword:[]};
  try{
    for(const seed of ['scrawl-2026-10-25','scrawl-2026-11-20','scrawl-2026-11-21','scrawl-2026-11-22','scrawl-2026-11-23','scrawl-2026-11-26','scrawl-2026-11-27','scrawl-2026-12-25','scrawl-2027-03-01','endless-sim1','endless-zzzzz','endless-abcde','endless-q9x2k']){
      S=newRun(seed,false,false);startFight();
      const c={seed,foes:S.foes.map(f=>[f.k,f.hp,f.mi]),edge:S.edge,letter:S.dayLetter,offers0:offers(0),rune0:runeOffer(0),hand0:S.hand.map(t=>[t.ch,fx(t)])};
      c.trail=play(seed,null,6,()=>0,hit=>[hit,S.fi,S.hp,S.foes.map(f=>f.hp)]);out.cases.push(c)}
    // the sword: preset runes, and the word placed at slot (turn mod 4), so the hilt, crossguard, tip and runes all play
    for(const [seed,runes] of [['endless-sim1',{pommel:2,whet:1,leech:1}],['endless-abcde',{fuller:3,flurry:2,parry:1}],['scrawl-2026-12-25',{bastion:3,reach:2,pommel:1}]]){
      const trail=play(seed,runes,8,i=>i%4,hit=>[hit,S.fi,S.hp,S.block,S.foes.map(f=>f.hp),S.hand.filter(t=>t.bag).map(t=>t.ch)]);
      out.sword.push({seed,runes,trail})}
    // the endless descent, scripted deep with foe attacks off and foe HP x0.5 so it goes deep
    const seed='endless-zzzzz';S=newRun(seed,false,true);const deep_foes=[3,4,5,6,9].map(i=>{const f=deepFoe(i);return[f.k,f.hp,f.mi,f.ax]});
    FOE_HP_SCALE=0.5;FOE_ATK_SCALE=0;
    const trail=play(seed,null,45,()=>0,hit=>[hit,S.fi,S.foes[S.fi].hp]);
    out.deep.push({seed,hp_scale:0.5,atk_scale:0,turns:45,deep_foes,trail,depth:S.fi+1});
    // each new foe in turn, 999 HP and attacks off: strike the longest word a permutation search finds (up to three times, from
    // the first slot), Quill the first consonant, end the turn; record what the foe's trick did to the next hand
    FOE_HP_SCALE=keepHP;FOE_ATK_SCALE=0;
    const perms=function*(n,L,pre=[]){if(pre.length===L){yield pre;return}for(let i=0;i<n;i++)if(!pre.includes(i))yield*perms(n,L,[...pre,i])};
    const longest=()=>{const h=S.hand.filter(t=>!t.crossed);
      for(let L=Math.min(maxWord(),h.length);L>=3;L--)for(const p of perms(h.length,L)){const w=p.map(i=>h[i].ch).join('');
        if(WORDS.has(w)){S.spell=p.map(i=>h[i].id);strike();return w}}
      return null};
    out.foes=[];
    for(const k of Object.keys(FOES).slice(6)){const seed='endless-'+k.slice(0,5);S=newRun(seed,false,false);startFight();
      S.foes[0]={k,hp:999,max:999,block:0,mi:0};const trail=[];
      for(let i=0;i<9;i++){if(S.over||S.fi)break;S.draft=null;const words=[];
        for(let j=0;j<3;j++){const w=longest();if(!w)break;words.push(w)}
        const q=S.hand.find(t=>!t.crossed&&TOOLS.quill.ok(t)===true);if(q&&usesLeft('quill')){sel=q.id;useOn('quill')}
        const blk=S.foes[0].block;S.draft=null;endTurn();
        trail.push([words,S.hp,S.foes[0].hp,blk,Object.entries(S.hex).sort(),S.hand.map(t=>t.ch+(t.crossed?'*':'')+(t.fx?t.fx[0]:'')).join(' '),S.bonus.map(b=>b||'-').join('')])}
      out.foes.push({seed,foe:k,trail})}
    out.foes_note='Each new foe with 999 HP and attacks off; the script strikes the longest word it finds (up to three times), Quills the first consonant and ends the turn. trail = [words, your hp, foe hp, foe block before its turn, the trick in force on the next turn, the next hand (* crossed, first letter of an enchantment), the next blade squares joined].';
    // word scoring under each foe trick: fixed words on plain and folded / bonus blades, as a first word and as a later one
    out.hits=[];S=newRun('endless-hits',false,false);startFight();S.edge='haiku';S.muffle=false;S.runes={};
    for(const H of [{},{caps:1},{ellipsis:1},{pedant:1},{hang:'t'},{abridge:1},{rex:1},{reflect:1},{stammer:4}])
      for(const w of ['cat','bell','sweet','queens','abbess','jazz'])
        for(const b of [[null,null,null,null,null,null],['x','dl',null,'tl',null,'dw']])
          for(const [nt,lt] of [[0,0],[1,4]]){S.hex=H;S.bonus=b;S.wordsTurn=nt;S.lenTurn=lt;S.strikes=0;
            S.hand=[...w].map((ch,i)=>({id:'h'+i,ch,fx:i===1?'fire':undefined}));S.spell=S.hand.map(t=>t.id);
            const h=wordHit(w);out.hits.push([H,w,b.map(x=>x||'-'),nt,lt,h.dmg,h.gain,h.back])}
    out.hits_note='wordHit on fixed words from the first slot (2nd tile on fire, edge Haiku, no runes) under each foe trick: [trick, word, blade squares, words already struck this turn, last length, damage, block it gains, damage bounced back].';
    // every trick (scrawl/trick-families): the lab kit, used once each, for two turns; the hand after each use, compact
    FOE_HP_SCALE=keepHP;FOE_ATK_SCALE=keepATK;
    const FXM = { fire: '^', steel: '#', gold: '$', leaf: '+' }, compact = () => S.hand.map(t => t.ch + (FXM[t.fx] || '') + (t.crossed ? '*' : '')).join('');
    const tricks = [], TRICK_SEEDS = ['endless-trk01', 'endless-trk02', 'endless-trk03'];
    // every trick: the lab kit, each used once in kit order on the first tile (or pair, or 3-letter word) that takes it
    for (const seed of TRICK_SEEDS) {
      S = newRun(seed, true, false); startFight(); const log = [];
      for (let turn = 0; turn < 2 && !S.over; turn++) {
        for (const k of S.kit) {
          const T = TOOLS[k]; if (k === 'quill' || !usesLeft(k) || S.over) continue;
          const free = S.hand.filter(t => !t.crossed && !busyIds().has(t.id)), okT = free.filter(t => T.ok(t) === true);
          if (T.notile) { fireTrick(k); if (S.affixing) chooseAffix(S.affixing.opts[0]) }
          else if (T.kind === 'socket') {
            let w = null;
            for (const a of okT) for (const b of okT) for (const c of okT) if (!w && a !== b && b !== c && a !== c && WORDS.has(a.ch + b.ch + c.ch)) w = [a, b, c];
            if (!w) continue; for (const t of w) { sel = t.id; useOn(k) } setSocket(k) }
          else if (T.kind === 'pair') {
            const a = okT[0], b = a && okT.find(t => t !== a && T.pair(a, t)); if (!b) continue;
            sel = a.id; useOn(k); sel = b.id; useOn(k) }
          else { const t = okT[0]; if (!t) continue; sel = t.id; useOn(k);
            if (T.kind === 'choose') chooseLetter(T.options(t).find(c => c !== t.ch)) }
          log.push([k, compact(), foe().hp, S.block, S.hp]) }
        if (!S.over) endTurn() }
      tricks.push({ seed, log }) }
    out.tricks=tricks;
    out.tricks_note='Every trick in the lab kit used once in kit order on the first tile (pair, or 3-letter word) that takes it, for two turns: [trick, hand (^ fire, # steel, $ gold, + leaf, * crossed), foe hp, block, hp].';
  }finally{FOE_HP_SCALE=keepHP;FOE_ATK_SCALE=keepATK;S=keepS;mode=keepMode;render()}
  return JSON.stringify(out)})()
