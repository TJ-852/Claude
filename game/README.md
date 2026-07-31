# PULSE

A one-tap timing arcade game in a single self-contained HTML file. No build, no
dependencies, no server — open `index.html` in any browser and play.

## How to play

- **Desktop:** click or press Space. **Mobile:** tap.
- A white dot orbits the ring. Tap the instant it crosses the **glowing arc**.
- The dot grows, brightens, and plays rising ticks as the strike approaches —
  that crescendo is your timing cue.
- **Miss the arc** and the run ends. A *near*-miss spends a **shield** 🛡
  instead ("SO CLOSE"). Shields regenerate every 25 hits.
- A **gold-tinted ring** warns that the next hit will reverse the dot's
  direction. The warning is a contract: it always executes.

## Scoring

| Mechanic | Effect |
|---|---|
| Combo (every 5 hits) | +0.5× multiplier |
| Perfect (center of arc) | 2× — and freezes time for a beat |
| Gold arc (14%) | 3× |
| Mystery chest (every 8–15 hits) | +points, +shield, GOLD RUSH ×6, or a 5% JACKPOT (×2 for 10 hits) |
| Phase shift (every 50 hits) | Palette rotates — long runs travel somewhere |
| OVERCLOCK (every ~35–45 hits) | ×1.6 speed, ×1.5 arc, ×2 pay for 3 targets |
| ☄ COMET (rare, once per run) | The dot streaks for one lap — that hit pays ×10 |
| ECLIPSE (very rare, once per run) | The world goes dark and silent; one silver target, big bounty |

## Surprise & delight

- **Record theater** — near your best, a gold ghost dot appears; break the record
  mid-run and it dissolves, time dilates, and your score runs gold to the end.
- **FLAWLESS** — 8 consecutive perfects shatter the ring in a supernova.
- **Palindrome winks** — palindrome/repdigit scores sparkle (404 has an opinion).
- **Near-milestone drama** — within 3 points of a milestone, its number ghosts
  at ring center.
- **A secret skin** exists. Its trigger is not documented here.
- The dot fidgets if you leave it waiting.

## Apple Watch

The page declares `disabled-adaptations: watch`, so watchOS Safari renders it
at native size instead of a shrunken desktop view. On watch-class screens
(≤290 px) the layout compacts, effects slim down for the GPU, and target arcs
widen ~15% because a finger covers half the display. Open the game URL from a
Message/Mail link on the watch to play. (watchOS may not support WebAudio —
the game degrades silently to visual-only feedback.)

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

## How it was designed

The game was built in four iterations by an agent council loop:

1. Define the qualities of a viral, sticky, addictive game; build the simplest
   game that can carry all of them.
2. Convene three tester agents — one each for **fun**, **challenge**, and
   **reward** — who critique the build independently.
3. An orchestrator synthesizes their reports into a ranked improvement plan.
4. Build, verify in a real browser, and reconvene.

Council scores across rounds: Fun 6.5 → 7.5 → 8.0, Challenge 4 → 6 → 7,
Reward 4 → 6 → 7.5. Each round's plan is recorded in the commit history.
