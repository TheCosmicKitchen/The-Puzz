// Weekly pictures for Joannagrams: 30 pixel pictures on a 14×14 grid, uncovered in seven strips of two rows.
// Listed in calendar order from Monday 16 Nov 2026 (after the three tile scenes in joannagrams.html), so the
// present lands in Christmas week and the heart in Valentine's week. '.' is the picture's background yarn (cream unless `bg` names another colour).
const BLANKET_YARN={'.':'#F6EEDC',r:'#C04A62',R:'#A8323E',o:'#E2934A',y:'#F2C14E',g:'#6FA35B',G:'#3F6E45',c:'#7FC4C4',b:'#4F7CC4',B:'#2D3E6E',v:'#8B6BBF',p:'#F0A6B8',n:'#8A5A3C',t:'#D9B38C',k:'#3A2E2A',w:'#FFFDF7',s:'#A9B0B8'};
const BLANKETS=[
 {name:'Maple leaf',art:['......o.......','.....ooo......','..o..ooo..o...','..ooooroooo...','...ooorooo....','.ooooorooooo..','..ooooroooo...','...ooorooo....','....ooroo.....','......n.......','......n.......','.....n........']},
 {name:'Acorn',art:['......kk......','......k.......','...nnnnnnnn...','..nnknnnnknn..','..nnnnnknnnn..','..nknnnnnnkn..','...oooooooo...','...oyooooooo..','...oooooooo...','....oooooo....','.....oooo.....','......oo......']},
 {name:'Owl',art:['..n........n..','..nn......nn..','..nnnnnnnnnn..','..nwwwnnwwwn..','..nwkwnnwkwn..','..nwwwoowwwn..','..nnnnoonnnn..','..nttttttttn..','..ntnttntntn..','..nttttttttn..','...nttttttn...','....oo..oo....','.kkkkkkkkkkkk.']},
 {name:'Mitten',art:['....rrrrr.....','...rrrrrrr....','...rrwrrwr....','...rrrrrrr.rr.','...rrrwrrrrrr.','...rrrrrrrrr..','...rrwrrwrr...','...rrrrrrrr...','...rrrrrrrr...','...wwwwwwww...','...wswswsws...','...wwwwwwww...']},
 {name:'Holly',art:['..gg......gg..','.gGgg....ggGg.','.ggGgg..ggGgg.','..ggGgRRggGg..','...gggRRRggg..','....gRRRRg....','.....RRRR.....','......RR......']},
 {name:'Present',art:['...r....r...','....r..r....','.....rr.....','vvvvvrrvvvvv','vvvvvrrvvvvv','.vvvvrrvvvv.','.vvvvrrvvvv.','.rrrrrrrrrr.','.vvvvrrvvvv.','.vvvvrrvvvv.','.vvvvrrvvvv.']},
 {name:'Star',bg:'B',art:['......y......','......y......','.....yyy.....','.....yyy.....','yyyyyyyyyyyyy','.yyyyyyyyyyy.','..yyyyyyyyy..','...yyyyyyy...','...yyyyyyy...','..yyyy.yyyy..','..yyy...yyy..','.yy.......yy.']},
 {name:'Snowflake',bg:'B',art:['......w......','...w..w..w...','....w.w.w....','.w...www...w.','..w...w...w..','...w..w..w...','wwwwwwcwwwwww','...w..w..w...','..w...w...w..','.w...www...w.','....w.w.w....','...w..w..w...','......w......']},
 {name:'Robin',art:['......nnnn....','.....nnnnkn...','.....nnnnnnyy.','..nnnrrrrnn...','.nnnrrrrrrn...','nnnnrrrrrrn...','n..nnrrrrrt...','....nttttt....','.....k..k.....','..kkkkkkkkkk..']},
 {name:'Snowman',bg:'b',art:['....kkkk....','....kkkk....','...kkkkkk...','....wwww....','...wkwwkww..','...wwwwoo...','....wwww....','..rrrrrrrr..','...wwrwww...','..wwwwkwww..','.wwwwwwwwww.','.wwwwwkwwww.','..wwwwwwww..','...wwwwww...']},
 {name:'Bobble hat',art:['.....pp.....','....pppp....','.....pp.....','...rrrrrr...','..rrwrrwrr..','.rrrrrrrrrr.','.rwrrwrrwrr.','.rrrrrrrrrr.','wwwwwwwwwwww','wswswswswsws','wwwwwwwwwwww']},
 {name:'Penguin',bg:'c',art:['....kkkk....','...kkkkkk...','..kkwkkwkk..','..kkkyykkk..','..kwwwwwwk..','.kkwwwwwwkk.','.kkwwwwwwkk.','kkkwwwwwwkkk','.kkwwwwwwkk.','..kwwwwwwk..','...kwwwwk...','...yy..yy...']},
 {name:'Heart',art:['..rr...rr..','.rrrr.rrrr.','rrwrrrrrrrr','rwrrrrrrrrr','rrrrrrrrrrr','.rrrrrrrrr.','..rrrrrrr..','...rrrrr...','....rrr....','.....r.....']},
 {name:'Moon',bg:'B',art:['..........y...','...yyyy.......','..yyy.........','.yyy......y...','.yyy..........','yyy.....y.....','yyy...........','yyy...........','.yyy.......y..','.yyyy.........','..yyyyy.......','...yyyyyyy....','.....yyy......']},
 {name:'Cat',art:['.k.....k....','.kk...kk....','.kkkkkkk....','.kykkkyk....','.kkkpkkk....','..kkkkk.....','.kkkkkkk....','kkkkkkkkk...','kkkkkkkkk..k','kkkkkkkkk..k','kkkkkkkkkkk.','.kkkkkkkkk..']},
 {name:'Teapot',art:['.......y......','.....vvvv.....','....vvvvvv....','.vvvvvvvvvv..v','v.vvwvvvvvvvvv','v.vwvvvvvvvvv.','.vvvvvvvvvvv..','..vvvvvvvvv...','...vvvvvvv....','..kkkkkkkkk...']},
 {name:'Daffodil',art:['.....yyy.....','...yyyyyyy...','..yyyoooyyy..','..yyoooooyy..','..yyyoooyyy..','...yyyyyyy...','.....yyy.....','......g......','..gg..g......','...gg.g..gg..','....ggg.gg...','......gg.....','......g......']},
 {name:'Umbrella',art:['.b..........b.','......kk......','...rryyrryy...','.rryyrryyrryy.','rryyrryyrryyrr','r..r..kk..r..r','......kk......','.b....kk....b.','......kk......','...k..kk......','...kkkk.......']},
 {name:'Lamb',bg:'g',art:['...wwwwww.....','..wwwwwwwwkk..','.wwwwwwwwkkkk.','.wwwwwwwwkwkk.','.wwwwwwwwwkk..','..wwwwwwww....','...k.k..k.k...']},
 {name:'Chick',bg:'c',art:['....yyyy....','...yyyyyy...','...ykyyky...','...yyooyy...','w.w.yyyy.w.w','wwwwwwwwwwww','.wwwwwwwwww.','.wwwwwwwwww.','..wwwwwwww..','...wwwwww...']},
 {name:'Tulip',art:['...r..r..r...','...rr.r.rr...','...rrrrrrr...','...rrrrrrr...','....rrrrr....','.....rrr.....','......g......','..gg..g..gg..','...ggggggg...','....ggggg....','......g......','......g......']},
 {name:'Bee',bg:'c',art:['....ww...ww...','.....ww.ww....','...yykyykyy...','..yyykyykyyy..','.kkyykyykyyyk.','..kyykyykyyy..','...yykyykyy...']},
 {name:'Rainbow',bg:'c',art:['....rrrrrr....','..rroooooorr..','.rooyyyyyyoor.','.royyggggyyor.','roygggbbgggyor','roygbbvvbbgyor','roygbv..vbgyor','roygbv..vbgyor','wwwww....wwwww','.www......www.']},
 {name:'Fish',art:['.....bbbb.....','...bbbbbbbb..b','..bbkbbcbbbbbb','.bbbbbbbcbbbb.','..bbbbbbbbbbbb','...bbbbbbbb..b','.....bbbb.....']},
 {name:'Strawberry',art:['.....g.g.....','...ggggggg...','..rrgggggrr..','.rrrrrgrrrrr.','.ryrrrrrryrr.','.rrrryrrrrrr.','.rrrrrrryrrr.','..ryrrrrrrr..','..rrrryrrrr..','...rrrrrrr...','....ryrrr....','.....rrr.....']},
 {name:'Cottage',art:['......r.......','.....rrr......','....rrrrr.kk..','...rrrrrrrkk..','..rrrrrrrrrr..','.rrrrrrrrrrrr.','..tttttttttt..','..tyyttttyyt..','..tyytnntyyt..','..ttttnntttt..','..ttttnntttt..']},
 {name:'Sun',bg:'c',art:['......y......','.y....y....y.','..y.......y..','....yyyyy....','...yyyyyyy...','yy.yyyyyyy.yy','...yyyyyyy...','....yyyyy....','..y.......y..','.y....y....y.','......y......']},
 {name:'Yarn ball',art:['.....pppp.....','...pprrpppp...','..pppprrpppp..','..prrpppprrp..','.ppppprrppppp.','.pprrppppprrp.','.pppprrpppppp.','.prrppppprrpp.','..pppprrpppp..','..pprrpppprp..','...pppprrpp...','.....pppp..r..','..........rr..']},
 {name:'Toadstool',art:['....rrrrrr....','..rrwrrrrwrr..','.rrrrrrwrrrrr.','.rwrrrrrrrrwr.','.rrrrrwrrrrrr.','..rrrrrrrrrr..','.....tttt.....','.....tttt.....','.....tttt.....','.....tttt.....','....tttttt....','..gggggggggg..']},
 {name:'Hedgehog',art:['.....n.n.n....','...nnnnnnnn...','..nnknnnknnn..','.nnnnnnnnnnnt.','.nnknnnnnnttt.','.nnnnnnnnttkt.','.nnnnnnnntttk.','..nnnnnnntt...','...t.t..t.t...','..............','.gggggggggggg.']},
];
// The picture as a full 14×14 grid of colour keys, centred.
function blanketGrid(b){const H=b.art.length,W=b.art[0].length,top=Math.floor((14-H)/2),left=Math.floor((14-W)/2);
  return [...Array(14)].map((_,y)=>[...Array(14)].map((_,x)=>{const r=b.art[y-top];const ch=r&&r[x-left];return ch&&ch!=='.'?ch:(b.bg||'.')}))}
