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
    opposite directions. Split play runs faster on tighter arcs and pays ×1.5.
    A near-miss costs a dot; a wild tap costs a dot and a shield, and only
    ends the run when you have no shields left.
- **Exit speed is proportional to your distance from the midpoint**: centre
  taps leave calm and slow, edge taps leave hot and fast. Precision is the
  brake; sloppiness is the accelerator.
- With one dot, a near-miss spends a **shield** 🛡 (regenerate every 25 hits);
  a wild miss ends the run.
- **Your first runs are gentler**: until your best reaches 25, the first ten
  hits of a run cannot split the dot and a wild tap there costs a shield
  instead of the run.
- **The run plays Satie.** Each hit sounds the next note of Erik Satie's
  *Gymnopédie No. 1* (1888, public domain; pitches transcribed from the
  Mutopia Project engraving), so playing well plays the tune: all 116 notes,
  with the repeat and both endings, then round again. The rhythm is yours,
  though notes the score holds longer ring longer. A slip (a graze, a lost
  dot, the ring closing) sends the melody back to the start of its phrase,
  so each phrase is earned. With two dots the line is doubled an octave
  below, the heartbeat rocks G to D as Satie's left hand does, and the
  approach ticks, the reverse cue and the ring's notches are tuned to the
  same key.
- Rising ticks telegraph each strike; the dot grows and brightens as it closes in.
- **The ring closes in.** Every lap that lets the arc go by untapped pulls
  the ring in a notch and turns it redder. Timing is unchanged (everything
  is measured in angles), but there is less to read. At its tightest, one
  more wasted lap costs a shield, or the run if you have none. Any hit
  springs it back to full size. It only starts once a run's first hit lands,
  and it tightens less on watch-sized screens.

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

## Leaderboard & ghosts

The first run of each day defaults to the **daily**, which is built to be a
fair contest: it is keyed to the UTC day, every roll is derived from the
seed and the hit number (so the course is the same for everyone whatever
path they take through it), and perks and small-screen arc widening are off.

When hosted as a claude.ai artifact (with the `db` and `user` capabilities),
daily runs post to a **shared leaderboard**: today's top five on the title
screen and behind MORE on the death screen, your own rank if you're outside
it, and a countdown to the reset. Rank is an event: the next player above
you is a live target on the HUD, passing them mid-run is announced, the
death screen shows your rank change, and the title screen tells you if you
were passed while away. Each row keeps a seven-day history, so yesterday's
winner and your place are remembered. Rows store only an
opaque id and a score — names are resolved per viewer at render time, never
stored. A score is written only when it beats your own best for the day.

Every daily run is also **recorded** (dot position every 150 ms, score at
each hit) and posted alongside the score, so it can be raced: the 👻 button
cycles LEADER / ME / OFF, and a small violet ghost on an inner lane shows
where that run was at this moment of yours, with a live pace chip
("👻 Sam 112 · +8") and a verdict on the death screen.

Both are optional layers: opened as a plain file, signed out, or on a watch,
the game detects the missing capabilities and plays exactly as before.
Signed-in members of the owning organization can post scores; visitors from
outside it can read the board but not write to it.

## Challenges & sharing

- **⚔ VS** — async challenges with zero backend: the daily seed *is* the
  protocol. A friend sends "DAILY 2026-11-11 — 247. Beat me."; you tap VS,
  enter 247, and play the identical daily with a 👑 pace chip. Pass them
  mid-run for a **CROWN TAKEN** celebration, a persistent 👑 crown count,
  and a pre-written counter-challenge in COPY TEXT ("Reclaim it?") — every
  resolved challenge mints the next one.
- **Share card** — draws *where you died* on the ring (the curiosity
  hook), your best superlative, and your crown count. The SHARE button
  pulses only on record-break deaths — never on ordinary ones.

## The tally

Every death ends in the run adding itself up: TAPS, PERFECTS, CHESTS,
QUESTS, ZEN, ECLIPSE, REVENGE count up line by line (rising note per line)
into the grand total, which slams in with a flash. The tally never blocks:
after a short pause that swallows a frantic last tap, one tap plays again.
The death screen itself is deliberately short — score, epitaph, play again —
with stats, the board, sharing, modes and skins behind MORE.

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
