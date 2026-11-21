# Trick trial: evo1-gen3
_2026-11-20 20:36 · 300 seeds per trick · foe HP ×2.5 · smart bot · eager on 100 · 7900 runs in 848s · ideas from C:\Users\basti\repos\The-Puzz\tools\evolution\evo1-gen1.json, C:\Users\basti\repos\The-Puzz\tools\evolution\evo1-gen2.json, C:\Users\basti\repos\The-Puzz\tools\evolution\evo1-gen3.json_
**Run:** sim 1.5.0 · page rules 682064970763 · commit edd5be0 + local changes · rerun: `git checkout scrawl-sim-v1.5.0` then `py tools/scrawl_sim.py evolve --gens 3 --pop 6 -n 300 --eager-n 100 --hard-scale 2.5 --tag evo1`

Baseline (Quill + Nudge + Flip): win 46.7%, 8.16 turns. Live tricks set the bar: median lift +31.0 pts, best +43.3.

| trick | new? | verdict | win | lift | turns saved | used on turns | uses/run | gain/use | eager hurt | what it does |
|---|---|---|---|---|---|---|---|---|---|---|
| g3x6 | idea | keeper | 92.3% | +45.7 | +1.24 | 44% | 8.8 | +7.6 | 0% | A tile becomes itself + a copy, 3× a foe. |
| twin | live | keeper | 90.0% | +43.3 | +0.82 | 76% | 5.5 | +11.9 | 0% | Copy a tile (the copy has no enchantment). |
| respell | live | keeper | 88.7% | +42.0 | +0.74 | 80% | 6.0 | +14.9 | 0% | A consonant becomes any consonant you like. |
| mimic | live | keeper | 87.0% | +40.3 | +0.68 | 69% | 7.8 | +9.7 | 15% | A tile takes the letter of another of its kind, vowel to vowel or consonant to consonant (×2). |
| double | live | keeper | 85.3% | +38.7 | +0.74 | 41% | 5.9 | +7.4 | 0% | Copy a tile, twice a foe (the copy has no enchantment). |
| echo | live | keeper | 82.0% | +35.3 | +0.41 | 70% | 5.4 | +10.9 | 7% | A tile takes another tile's letter. Pick the tile to change, then the one to copy. |
| sprout | live | keeper | 78.3% | +31.7 | +0.45 | 69% | 5.3 | +6.7 | 0% | A tile sprouts an E beside it. |
| back | live | keeper | 77.7% | +31.0 | +0.50 | 67% | 7.8 | +7.6 | 14% | One step back: C→B, A→Z. |
| leap | live | weak | 71.7% | +25.0 | +0.36 | 67% | 5.2 | +8.5 | 11% | Two steps on: B→D, Y→A. |
| slip | live | weak | 71.7% | +25.0 | +0.35 | 60% | 4.7 | +8.3 | 14% | One key right on a keyboard: Q→W, L→A, M→Z. |
| whisper | live | weak | 71.3% | +24.7 | +0.37 | 54% | 5.6 | +7.1 | 23% | Voice swap: B↔P, D↔T, G↔K, F↔V, S↔Z, M↔N. |
| upend | live | weak | 69.0% | +22.3 | +0.31 | 58% | 4.5 | +8.6 | 22% | Turn or flip it by shape, your pick: b d p q · n u · m w · s z · h y. |
| g3x3 | idea | weak | 67.7% | +21.0 | +0.23 | 50% | 8.2 | +4.2 | 22% | A tile moves 1 step on (×3 a turn). |
| g3x4 | idea | weak+trap | 67.0% | +20.3 | +0.21 | 54% | 4.3 | +6.3 | 29% | One of b d p q n u m w s z h y becomes any vowel. |
| recast | live | weak | 66.7% | +20.0 | +0.28 | 38% | 3.0 | +9.7 | 0% | A tile becomes any letter you like, once a foe. |
| g3x1 | idea | weak | 65.3% | +18.7 | +0.23 | 62% | 4.9 | +6.8 | 12% | A vowel becomes any of AEIOUY. |
| g3x2 | idea | weak | 64.0% | +17.3 | +0.20 | 36% | 2.9 | +7.1 | 9% | A tile takes another tile's letter, 1× a foe. |
| revowel | live | weak | 60.0% | +13.3 | +0.17 | 55% | 4.4 | +6.5 | 14% | A vowel becomes any vowel you like. |
| g3x5 | idea | weak | 57.3% | +10.7 | +0.19 | 37% | 3.0 | +4.5 | 5% | A tile becomes any of AEIOUY, 1× a foe. |

Rules: dud = under +2 pts and under 0.2 turns saved; overpowered = 3+ pts above the best live trick; keeper = at least the median live lift and used on 15%+ of turns; niche = strong but rarely used; weak = below the median live trick; trap = the eager bot makes its turn worse with it 25%+ of the time.