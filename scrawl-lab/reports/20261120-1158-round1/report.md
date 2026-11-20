# Trick trial: round1
_2026-11-20 11:57 · 600 seeds per trick · foe HP ×2.5 · smart bot · eager on 150 · 11850 runs in 654s · ideas from tools/ideas/r1.py_
**Run:** sim 1.1.0 · page rules d9a80b459f96 · commit 047d0fe + local changes · rerun: `git checkout scrawl-sim-v1.1.0` then `py tools/scrawl_sim.py trial --round 1 -n 600 --eager-n 150 --hard-scale 2.5`

Baseline (Quill + Nudge + Flip): win 46.3%, 8.19 turns. Live tricks set the bar: median lift +10.8 pts, best +41.5.

| trick | new? | verdict | win | lift | turns saved | used on turns | uses/run | gain/use | eager hurt | what it does |
|---|---|---|---|---|---|---|---|---|---|---|
| twin | live | keeper | 87.8% | +41.5 | +0.82 | 75% | 5.5 | +11.7 | 0% | Copy a tile. |
| sprout | idea | keeper | 78.7% | +32.3 | +0.46 | 69% | 5.4 | +7.5 | 0% | A tile sprouts an E beside it. |
| echo | idea | keeper | 76.2% | +29.8 | +0.42 | 69% | 5.3 | +10.8 | 5% | A tile takes another tile's letter. |
| back | idea | keeper | 73.5% | +27.2 | +0.46 | 65% | 7.6 | +7.6 | 13% | One step back: C→B (×2). |
| smudge | idea | keeper | 70.2% | +23.8 | +0.32 | 66% | 5.2 | +7.4 | 24% | Make a blank, once a turn (Ink Blot is once a foe). |
| slip | idea | keeper | 68.7% | +22.3 | +0.32 | 60% | 4.7 | +8.5 | 13% | Slip one key right on a keyboard: Q→W, L→A. |
| leap | idea | keeper | 68.5% | +22.2 | +0.31 | 66% | 5.2 | +8.4 | 10% | Two steps on: B→D. |
| whisper | idea | keeper | 67.3% | +21.0 | +0.36 | 52% | 5.6 | +7.4 | 24% | Voice swap: B↔P, D↔T, G↔K, V↔F, Z↔S, M↔N (×2). |
| split | live | keeper+trap | 66.7% | +20.3 | +0.24 | 37% | 2.9 | +6.8 | 54% | A 4+ tile breaks into E and A. |
| soften | idea | keeper+trap | 58.2% | +11.8 | +0.13 | 39% | 3.1 | +5.1 | 40% | Consonant → nearest vowel: D→E, N→O. |
| vshift | live | keeper+trap | 57.2% | +10.8 | +0.15 | 39% | 4.2 | +4.4 | 33% | A→E→I→O→U→A (×2). |
| inkblot | live | weak+trap | 56.2% | +9.8 | +0.17 | 35% | 2.8 | +5.0 | 35% | Make a blank (once a foe). |
| rotate | live | weak+trap | 55.0% | +8.7 | +0.13 | 34% | 2.8 | +5.2 | 41% | Turn by shape: b→d→p→q, n↔u, m↔w. |
| harden | idea | weak+trap | 50.3% | +4.0 | +0.10 | 26% | 2.1 | +5.2 | 63% | Vowel → next consonant: A→B, E→F, O→P. |
| swap | live | weak | 50.2% | +3.8 | +0.04 | 14% | 1.2 | +8.5 | 0% | Two tiles trade letters. |

Rules: dud = under +2 pts and under 0.2 turns saved; overpowered = 3+ pts above the best live trick; keeper = at least the median live lift and used on 15%+ of turns; niche = strong but rarely used; weak = below the median live trick; trap = the eager bot makes its turn worse with it 25%+ of the time.