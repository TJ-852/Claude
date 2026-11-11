# Palindrome

A one-tap arcade game in a single self-contained HTML file. No build, no
dependencies, no server — open `index.html` in any browser and play.
*(Formerly PULSE; saved progress carries over.)*

## How to play

- **Desktop:** click or press Space. **Mobile & Apple Watch:** tap.
- A dot orbits the ring. Tap while it's inside the **glowing arc**.
- **Where you tap writes your direction** — the palindrome rule:
  - Tap **before the arc's midpoint** (the white notch) → the dot **bounces back**
    the way it came.
  - Tap **after the midpoint** → the dot **carries on**.
  - Tap **dead centre** → the dot **⧉ SPLITS** into two dots orbiting in
    opposite directions. Play continues with both until a bad tap costs you a
    dot — with two dots live, mistakes lose a dot instead of the run.
- **Exit speed is proportional to your distance from the midpoint**: centre
  taps leave calm and slow, edge taps leave hot and fast. Precision is the
  brake; sloppiness is the accelerator.
- With one dot, a near-miss spends a **shield** 🛡 (regenerate every 25 hits);
  a wild miss ends the run.
- Rising ticks telegraph each strike; the dot grows and brightens as it closes in.

## Scoring

| Mechanic | Effect |
|---|---|
| Combo (every 5 hits) | +0.5× multiplier |
| Perfect / split (arc centre) | 2× — and freezes time for a beat |
| Gold arc (14%) | 3× |
| Mystery chest (every 8–15 hits) | +points, +shield, GOLD RUSH ×6, or a 5% JACKPOT (×2 for 10 hits) |
| Phase shift (every 50 hits) | Palette rotates — long runs travel somewhere |
| OVERCLOCK (every ~35–45 hits) | ×1.6 speed, ×1.5 arc, ×2 pay for 3 targets |
| ☄ COMET (rare, once per run) | The dot streaks for one lap — that hit pays ×10 |
| ECLIPSE (very rare, once per run) | The world goes dark and silent; one silver target, big bounty |

## Progression

- **Tiers** — NOVICE → ROOKIE → SHARPSHOOTER → MARKSMAN → SNIPER → LEGEND
- **Skins** — unlocked at best-score 25 / 60 / 120 / 250
- **Daily run** — a date-seeded deterministic layout with its own best; pays 2× lifetime
- **Streak** — consecutive days played (runs of 10+ points count)
- **Ascension** — lifetime score unlocks ranks at 500 / 1000 / 2000 / 4000 / 8000 / 16000
  with real perks: rank 1 = exclusive *Ascendant* skin, rank 2 = start with 3 shields,
  rank 3 = dot trail
- **Share** — a rendered PNG score card, copied to the clipboard

Everything persists in `localStorage`.

## Surprise & delight

- **Quests** — a rotating micro-goal always on the HUD (hit 3 golds, reverse
  3 times, 15 hits without a graze…), each paying a bonus; daily runs share
  the same quest sequence for everyone.
- **Revenge** — your last run's score is a rival; pass it for a "⚔ REVENGED" bonus.
- **Melodic combos** — each hit plays the next note of a rising pentatonic
  scale, so a long combo literally composes a tune.
- **Epitaphs** — the death screen has opinions: "Greed is a hell of a drug.",
  "It reads the same backwards."
- **Haptics** — hits, perfects, splits, and deaths vibrate where supported.
- **Record theater** — near your best, a gold ghost dot appears; break the record
  mid-run and it dissolves, time dilates, and your score runs gold to the end.
- **FLAWLESS** — 8 consecutive perfects shatter the ring in a supernova.
- **Palindrome scores** — the namesake: palindrome/repdigit scores (121, 222…)
  earn a "✦ PALINDROME ✦" flourish, and 404 has an opinion.
- **Near-milestone drama** — within 3 points of a milestone, its number ghosts
  at ring center, and a NEXT-goal chip always names your next target.
- **A secret skin** exists. Its trigger is not documented here.
- The dot blinks mid-run and fidgets if you leave it waiting.

## Apple Watch

The page declares `disabled-adaptations: watch`, so watchOS Safari renders it
at native size instead of a shrunken desktop view. On watch-class screens
(≤290 px) the layout compacts, effects slim down for the GPU, and target arcs
widen ~15% because a finger covers half the display. Open the game URL from a
Message/Mail link on the watch to play. (watchOS may not support WebAudio —
the game degrades silently to visual-only feedback.)

## How it was designed

Built across seven iterations by an agent-council design loop: three tester
agents (fun, challenge, reward) critique each build independently, an
orchestrator synthesizes a ranked plan, the next build implements it, and
every build is verified end-to-end in a real browser before committing.
Council scores across rounds: Fun 6.5 → 8+, Challenge 4 → 7.5, Reward 4 → 7.5.
The v7 redesign (the palindrome rule: player-written direction, splits, and
distance-proportional exit speed) replaced the old pre-announced forced
reversals. Each round's plan is recorded in the commit history.
