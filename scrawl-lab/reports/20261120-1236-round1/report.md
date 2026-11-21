# Trick trial: round1
_2026-11-20 12:36 · 600 seeds per trick · foe HP ×2.5 · smart bot · eager on 150 · 11850 runs in 762s · ideas from C:\Users\basti\repos\The-Puzz\tools\ideas\r1.py_
**Run:** sim 1.2.0 · page rules d9a80b459f96 · commit 57a55a6 + local changes · rerun: `git checkout scrawl-sim-v1.2.0` then `py tools/scrawl_sim.py trial --round 1 -n 600 --eager-n 150 --hard-scale 2.5`

Baseline (Quill + Nudge + Flip): win 46.2%, 8.20 turns. Live tricks set the bar: median lift +10.6 pts, best +41.7.

| trick | new? | verdict | win | lift | turns saved | used on turns | uses/run | gain/use | eager hurt | what it does |
|---|---|---|---|---|---|---|---|---|---|---|
| twin | live | keeper | 87.8% | +41.7 | +0.82 | 75% | 5.5 | +11.7 | 0% | Copy a tile. |
| sprout | idea | keeper | 78.7% | +32.5 | +0.46 | 69% | 5.4 | +7.6 | 0% | A tile sprouts an E beside it. |
| echo | idea | keeper | 76.2% | +30.0 | +0.43 | 69% | 5.3 | +10.8 | 5% | A tile takes another tile's letter. |
| back | idea | keeper | 73.5% | +27.3 | +0.46 | 65% | 7.6 | +7.6 | 13% | One step back: C→B (×2). |
| smudge | idea | keeper | 70.3% | +24.2 | +0.32 | 66% | 5.2 | +7.4 | 24% | Make a blank, once a turn (Ink Blot is once a foe). |
| slip | idea | keeper | 68.7% | +22.5 | +0.32 | 60% | 4.7 | +8.5 | 13% | Slip one key right on a keyboard: Q→W, L→A. |
| leap | idea | keeper | 68.5% | +22.3 | +0.32 | 66% | 5.2 | +8.3 | 10% | Two steps on: B→D. |
| whisper | idea | keeper | 67.2% | +21.0 | +0.36 | 52% | 5.6 | +7.4 | 24% | Voice swap: B↔P, D↔T, G↔K, V↔F, Z↔S, M↔N (×2). |
| split | live | keeper+trap | 66.7% | +20.5 | +0.24 | 37% | 2.9 | +6.9 | 54% | A 4+ tile breaks into E and A. |
| soften | idea | keeper+trap | 58.3% | +12.2 | +0.14 | 39% | 3.1 | +5.1 | 40% | Consonant → nearest vowel: D→E, N→O. |
| vshift | live | keeper+trap | 57.3% | +11.2 | +0.15 | 39% | 4.2 | +4.4 | 33% | A→E→I→O→U→A (×2). |
| inkblot | live | weak+trap | 56.2% | +10.0 | +0.18 | 35% | 2.8 | +5.0 | 35% | Make a blank (once a foe). |
| rotate | live | weak+trap | 54.8% | +8.7 | +0.14 | 35% | 2.8 | +5.2 | 41% | Turn by shape: b→d→p→q, n↔u, m↔w. |
| harden | idea | weak+trap | 50.5% | +4.3 | +0.11 | 26% | 2.1 | +5.2 | 63% | Vowel → next consonant: A→B, E→F, O→P. |
| swap | live | weak | 50.0% | +3.8 | +0.04 | 14% | 1.2 | +8.5 | 0% | Two tiles trade letters. |

Rules: dud = under +2 pts and under 0.2 turns saved; overpowered = 3+ pts above the best live trick; keeper = at least the median live lift and used on 15%+ of turns; niche = strong but rarely used; weak = below the median live trick; trap = the eager bot makes its turn worse with it 25%+ of the time.