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
  }finally{FOE_HP_SCALE=keepHP;FOE_ATK_SCALE=keepATK;S=keepS;mode=keepMode;render()}
  return JSON.stringify(out)})()
