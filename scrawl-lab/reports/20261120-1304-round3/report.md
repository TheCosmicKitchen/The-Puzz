# Trick trial: round3
_2026-11-20 13:04 · 600 seeds per trick · foe HP ×2.5 · smart bot · eager on 150 · 14850 runs in 868s · ideas from C:\Users\basti\repos\The-Puzz\tools\ideas\r1.py, C:\Users\basti\repos\The-Puzz\tools\ideas\r2.py, C:\Users\basti\repos\The-Puzz\tools\ideas\r3.py_
**Run:** sim 1.2.0 · page rules d9a80b459f96 · commit 57a55a6 + local changes · rerun: `git checkout scrawl-sim-v1.2.0` then `py tools/scrawl_sim.py trial --round 3 -n 600 --eager-n 150 --hard-scale 2.5`

Baseline (Quill + Nudge + Flip): win 46.2%, 8.20 turns. Live tricks set the bar: median lift +10.6 pts, best +41.7.

| trick | new? | verdict | win | lift | turns saved | used on turns | uses/run | gain/use | eager hurt | what it does |
|---|---|---|---|---|---|---|---|---|---|---|
| twin | live | keeper | 87.8% | +41.7 | +0.82 | 75% | 5.5 | +11.7 | 0% | Copy a tile. |
| echo2 | idea | keeper | 85.2% | +39.0 | +0.69 | 71% | 8.1 | +9.5 | 13% | A tile takes another tile's letter (×2). (Echo, buffed) |
| respell | idea | keeper | 84.7% | +38.5 | +0.74 | 81% | 6.0 | +15.3 | 0% | A consonant becomes any consonant, once a turn. (Recast, narrowed) |
| echo_kin | idea | keeper | 82.5% | +36.3 | +0.68 | 68% | 7.6 | +9.3 | 15% | A tile takes the letter of another of its kind, vowel to vowel or consonant to consonant (×2). (Echo, narrowed) |
| twin_f2 | idea | keeper | 81.0% | +34.8 | +0.70 | 41% | 5.8 | +7.4 | 0% | Copy a tile, twice a foe. (Twin, rationed) |
| sprout | idea | keeper | 78.7% | +32.5 | +0.46 | 69% | 5.4 | +7.6 | 0% | A tile sprouts an E beside it. |
| echo | idea | keeper | 76.2% | +30.0 | +0.43 | 69% | 5.3 | +10.8 | 5% | A tile takes another tile's letter. |
| upend2 | idea | keeper | 73.5% | +27.3 | +0.51 | 60% | 6.5 | +8.2 | 21% | Turn or flip by shape: b d p q, n u, m w, s z, h y (×2). (Upend, buffed) |
| back | idea | keeper | 73.5% | +27.3 | +0.46 | 65% | 7.6 | +7.6 | 13% | One step back: C→B (×2). |
| twin_foe | idea | keeper | 67.5% | +21.3 | +0.35 | 38% | 3.0 | +7.6 | 0% | Copy a tile, once a foe. (Twin, rationed) |
| split | live | keeper+trap | 66.7% | +20.5 | +0.24 | 37% | 2.9 | +6.9 | 54% | A 4+ tile breaks into E and A. |
| upend | idea | keeper | 65.3% | +19.2 | +0.36 | 57% | 4.4 | +8.7 | 19% | Turn or flip by shape: b d p q, n u, m w, s z, h y. (Rotate, evolved) |
| recast | idea | keeper | 64.0% | +17.8 | +0.31 | 38% | 3.0 | +10.2 | 0% | A tile becomes any letter, once a foe. (Ink Blot, evolved: keeps points) |
| revowel2 | idea | keeper | 63.7% | +17.5 | +0.21 | 58% | 6.0 | +6.4 | 18% | A vowel becomes any vowel (×2). (Revowel, buffed) |
| revowel | idea | keeper | 61.7% | +15.5 | +0.16 | 54% | 4.4 | +7.2 | 15% | A vowel becomes any vowel you like. (Vowel Shift, evolved) |
| vshift | live | keeper+trap | 57.3% | +11.2 | +0.15 | 39% | 4.2 | +4.4 | 33% | A→E→I→O→U→A (×2). |
| inkblot | live | weak+trap | 56.2% | +10.0 | +0.18 | 35% | 2.8 | +5.0 | 35% | Make a blank (once a foe). |
| rotate | live | weak+trap | 54.8% | +8.7 | +0.14 | 35% | 2.8 | +5.2 | 41% | Turn by shape: b→d→p→q, n↔u, m↔w. |
| swap | live | weak | 50.0% | +3.8 | +0.04 | 14% | 1.2 | +8.5 | 0% | Two tiles trade letters. |

Rules: dud = under +2 pts and under 0.2 turns saved; overpowered = 3+ pts above the best live trick; keeper = at least the median live lift and used on 15%+ of turns; niche = strong but rarely used; weak = below the median live trick; trap = the eager bot makes its turn worse with it 25%+ of the time.