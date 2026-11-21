# Trick trial: evo1-gen1
_2026-11-20 20:12 · 300 seeds per trick · foe HP ×2.5 · smart bot · eager on 100 · 7900 runs in 599s · ideas from C:\Users\basti\repos\The-Puzz\tools\evolution\evo1-gen1.json_
**Run:** sim 1.5.0 · page rules 682064970763 · commit edd5be0 + local changes · rerun: `git checkout scrawl-sim-v1.5.0` then `py tools/scrawl_sim.py evolve --gens 3 --pop 6 -n 300 --eager-n 100 --hard-scale 2.5 --tag evo1`

Baseline (Quill + Nudge + Flip): win 46.7%, 8.16 turns. Live tricks set the bar: median lift +31.0 pts, best +43.3.

| trick | new? | verdict | win | lift | turns saved | used on turns | uses/run | gain/use | eager hurt | what it does |
|---|---|---|---|---|---|---|---|---|---|---|
| twin | live | keeper | 90.0% | +43.3 | +0.82 | 76% | 5.5 | +11.9 | 0% | Copy a tile (the copy has no enchantment). |
| respell | live | keeper | 88.7% | +42.0 | +0.74 | 80% | 6.0 | +14.9 | 0% | A consonant becomes any consonant you like. |
| mimic | live | keeper | 87.0% | +40.3 | +0.68 | 69% | 7.8 | +9.7 | 15% | A tile takes the letter of another of its kind, vowel to vowel or consonant to consonant (×2). |
| double | live | keeper | 85.3% | +38.7 | +0.74 | 41% | 5.9 | +7.4 | 0% | Copy a tile, twice a foe (the copy has no enchantment). |
| g1x1 | idea | keeper | 83.3% | +36.7 | +0.44 | 66% | 5.1 | +10.6 | 9% | A tile takes another tile's letter (same kind only). |
| g1x3 | idea | keeper | 82.7% | +36.0 | +0.52 | 68% | 8.0 | +7.2 | 19% | A tile changes by its table (×2 a turn). |
| echo | live | keeper | 82.0% | +35.3 | +0.41 | 70% | 5.4 | +10.9 | 7% | A tile takes another tile's letter. Pick the tile to change, then the one to copy. |
| g1x4 | idea | keeper | 78.3% | +31.7 | +0.49 | 62% | 6.9 | +7.8 | 23% | One of b d p q n u m w s z h y turns by shape, your pick (×2 a turn). |
| sprout | live | keeper | 78.3% | +31.7 | +0.45 | 69% | 5.3 | +6.7 | 0% | A tile sprouts an E beside it. |
| back | live | keeper | 77.7% | +31.0 | +0.50 | 67% | 7.8 | +7.6 | 14% | One step back: C→B, A→Z. |
| g1x6 | idea | weak | 74.7% | +28.0 | +0.40 | 65% | 5.0 | +9.3 | 14% | A tile moves 3 steps back. |
| g1x5 | idea | weak | 72.0% | +25.3 | +0.22 | 68% | 5.4 | +8.3 | 9% | A consonant becomes any of ETAOINSRHL. |
| leap | live | weak | 71.7% | +25.0 | +0.36 | 67% | 5.2 | +8.5 | 11% | Two steps on: B→D, Y→A. |
| slip | live | weak | 71.7% | +25.0 | +0.35 | 60% | 4.7 | +8.3 | 14% | One key right on a keyboard: Q→W, L→A, M→Z. |
| whisper | live | weak | 71.3% | +24.7 | +0.37 | 54% | 5.6 | +7.1 | 23% | Voice swap: B↔P, D↔T, G↔K, F↔V, S↔Z, M↔N. |
| g1x2 | idea | weak | 70.3% | +23.7 | +0.31 | 64% | 5.0 | +6.6 | 20% | A consonant becomes any vowel. |
| upend | live | weak | 69.0% | +22.3 | +0.31 | 58% | 4.5 | +8.6 | 22% | Turn or flip it by shape, your pick: b d p q · n u · m w · s z · h y. |
| recast | live | weak | 66.7% | +20.0 | +0.28 | 38% | 3.0 | +9.7 | 0% | A tile becomes any letter you like, once a foe. |
| revowel | live | weak | 60.0% | +13.3 | +0.17 | 55% | 4.4 | +6.5 | 14% | A vowel becomes any vowel you like. |

Rules: dud = under +2 pts and under 0.2 turns saved; overpowered = 3+ pts above the best live trick; keeper = at least the median live lift and used on 15%+ of turns; niche = strong but rarely used; weak = below the median live trick; trap = the eager bot makes its turn worse with it 25%+ of the time.