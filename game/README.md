# SATIE

A one-tap arcade game in a single self-contained HTML file. No build, no
dependencies, no server — open `index.html` in any browser and play.
It plays Erik Satie's *Gymnopédie No. 1* as you play, and is named for him.
*(Formerly Palindrome, and before that PULSE; saved progress carries over.)*

## How to play

- **Desktop:** click or press Space. **Mobile & Apple Watch:** tap.
- A dot orbits the ring. Tap while it's inside the **glowing arc**.
- **Where you tap writes your direction** — the palindrome rule:
  - Tap **before the arc's midpoint** (the white notch) → the dot **bounces back**
    the way it came.
  - Tap **after the midpoint** → the dot **carries on**.
  - Tap **dead centre** → the dot **⧉ SPLITS** into two dots orbiting in
    opposite directions. Split play runs faster on tighter arcs and pays ×1.5.
    A near-miss costs a dot; a wild tap costs a dot and a life.
- **Exit speed is proportional to your distance from the midpoint**: centre
  taps leave calm and slow, edge taps leave hot and fast. Precision is the
  brake; sloppiness is the accelerator.
- **Lives are hearts** ❤️. You start with three. With one dot, any miss, near
  or wild, costs a heart; the run ends when the last one goes. A heart grows
  back every 25 hits (four at most), and chests can hold one.
- **Your first runs are gentler**: until your best reaches 25, the first ten
  hits of a run cannot split the dot, and your first run of the day is an
  ordinary one rather than the daily.
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
- **SATIE!** Play the tune's first eight notes straight through and the run
  pays an 88-point bonus, one for each key of the piano, over a rolled D
  major seventh. A slip starts the phrase again, so it can still be earned
  later in the run; it pays once per run.
- Rising ticks telegraph each strike; the dot grows and brightens as it closes in.
- **The ring closes in.** Every lap that lets the arc go by untapped pulls
  the ring in a notch and turns it redder. Timing is unchanged (everything
  is measured in angles), but there is less to read. It stays closed in
  until you hit the arc or lose a life; at its tightest, one more wasted
  lap takes that life itself. Either way it then springs back to full size.
  It is billed fairly: a late tap is a miss, never a miss *and* a wasted
  lap; an arc that appears on top of the dot is a free pass; with two dots
  only the one you are judged on counts. It starts once a run's first hit
  lands, waits out an eclipse, and tightens less on watch-sized screens.

## Scoring

| Mechanic | Effect |
|---|---|
| Combo (every 5 hits) | +0.5× multiplier, shown live beside the score |
| Reverse (tap before the midpoint) | ×1.3 on that hit |
| Perfect / split (arc centre) | 2× — and freezes time for a beat |
| Gold arc (14%) | 3× |
| Mystery chest (every 8–15 hits) | +points, +1 life, GOLD RUSH ×6, or a 5% JACKPOT (×2 for 10 hits) |
| Phase shift (every 50 hits) | Palette rotates — long runs travel somewhere |
| OVERCLOCK (every ~35–45 hits) | ×1.6 speed, ×1.5 arc, ×2 pay for 3 targets |
| ☄ COMET (rare, once per run) | The dot streaks for one lap — that hit pays ×10 |
| ECLIPSE (very rare, once per run) | The world goes dark and silent; one silver target, big bounty |

## Progression

- **Tiers** — NOVICE → ROOKIE (150) → SHARPSHOOTER (400) → MARKSMAN (750) →
  SNIPER (1200) → LEGEND (2000) → PALINDROME (3003). The rungs are spaced by
  how far players really get: a first run lands near 150, an expert near 2000.
- **Skins** — unlocked at best-score 150 / 400 / 750 / 1200 / 2000 / 3003.
  Skins earned under the earlier, lower thresholds are kept.
- **Daily run** — a date-seeded deterministic layout with its own best; pays 2× lifetime
- **Streak** — consecutive days played (runs of 10+ points count)
- **Ascension** — lifetime score unlocks ranks at 500 / 1000 / 2000 / 4000 / 8000 / 16000
  with real perks: rank 1 = exclusive *Ascendant* skin, rank 2 = one more starting
  life (not on the daily), rank 3 = dot trail
- **Share** — a rendered PNG score card, copied to the clipboard

Everything persists in `localStorage`.

The in-play HUD is set in *Press Start 2P*, a 1980s arcade face loaded from
Google Fonts; offline it falls back to a plain monospace and the game is
otherwise unaffected.

## Surprise & delight

- **Quests** — a rotating micro-goal always on the HUD (hit 3 golds, reverse
  3 times, 15 hits without a graze…), each paying a bonus; daily runs share
  the same quest sequence for everyone.
- **Revenge** — your last run's score is a rival; pass it for a +10 bonus
  (not on the daily, where no one starts ahead).
- **Epitaphs** — the death screen has opinions: "Greed is a hell of a drug.",
  "It reads the same backwards."
- **Haptics** — hits, perfects, splits, and deaths vibrate where supported.
- **Record theater** — near your best, a gold ghost dot appears; break the record
  mid-run and it dissolves, time dilates, and your score runs gold to the end.
- **FLAWLESS** — 8 consecutive perfects shatter the ring in a supernova.
- **Palindrome scores** — after the rule the game is built on: repdigit and
  four-digit mirror scores (222, 1221…) earn a "✦ PALINDROME ✦" flourish,
  and 404 has an opinion.
- **Near-milestone drama** — within 3 points of a milestone, its number ghosts
  at ring center, and a NEXT-goal chip always names your next target.
- **Secret skins** exist, and other things besides. See the spoilers below.
- The dot blinks mid-run and fidgets if you leave it waiting.

## Easter eggs

None of these is explained in the game.

<details>
<summary>Spoilers</summary>

- **Lent et douloureux** — the tempo marking on the score ("slow and
  sorrowful"). Land all of the first eight notes near dead centre and the
  SATIE! bonus pays double, 176, under that title.
- **Gymnopédiste** — play the whole piece, all 116 notes, without a slip:
  888 points, the last chord held, and the hidden **Ivory** skin.
- **The Velvet Gentleman** — Satie bought seven identical velvet suits and
  wore nothing else. Seven perfects in a row unlocks the hidden **Velvet** skin.
- **Umbrellas** — he left a great many behind. Every hundred hits without
  losing a heart earns a ☂ and 100 points; the count is kept.
- **Dates** — a score of exactly 1866 (his birth), 1888 (the Gymnopédies)
  or 1925 (his death) gets its own flourish.
- **17 May** — on his birthday the title wishes him well and every burst
  of particles is confetti.
- **His markings** — most ordinary epitaphs are performance directions
  Satie wrote on his Gnossiennes ("Open your head.", "Very lost.", "Arm
  yourself with clairvoyance."), with the French and the piece beneath.
  They are taken from the Mutopia Project engravings; the English for
  Nos. 2 and 3 is our own translation.
- **Furniture music** — Satie's *musique d'ameublement* was written to be
  ignored. Leave the game-over screen alone for a minute and the left hand
  of the Gymnopédie plays quietly to itself. (Sound has to have been
  switched on by a tap first, so it will not start on a fresh title screen.)
- **Vexations** — a piece to be played 840 times in a row. Your 840th run
  is acknowledged.
- **Phantom** — the older secret skin: three perfects landed while split.

</details>

## Leaderboard & ghosts

Once your best reaches 25, the first run of each day defaults to the
**daily**, which is built to be a fair contest: it is keyed to the UTC day,
and gold arcs, comets, eclipses and overclocks are rolled from the seed and
the hit number before anything else, so every player meets the same events
at the same hit whatever path they take. Perks, the newcomer's grace, the
revenge bonus and small-screen arc widening are all off. (What a chest
gives can still depend on whether you have room for another life.)

When hosted as a claude.ai artifact (with the `db` and `user` capabilities),
daily runs post to a **shared leaderboard**: today's top five on the title
screen and behind MORE on the death screen, your own rank if you're outside
it, and a countdown to the reset. Rank is an event: the next player above
you becomes a target on the HUD once the chase is close, passing someone
on the way into the top five is announced, the death screen shows your
rank change, and the title screen tells you if you slipped while away (and
sets up a daily run to answer it). All of it counts the score you have
already posted, so you are never told you passed someone you were already
ahead of. Each row keeps a seven-day history, so yesterday's
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
REVERSES, SATIE!, CHESTS, QUESTS, ZEN, ECLIPSE, REVENGE count up line by line (rising note per line)
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

Built across eighteen iterations by an agent-council design loop: three tester
agents (fun, challenge, reward) critique each build independently, an
orchestrator synthesizes a ranked plan, the next build implements it, and
every build is verified end-to-end in a real browser before committing.
Council scores across rounds: Fun 6.5 → 8.5, Challenge 4 → 7, Reward 4 → 8.5
(the scale was reset at the v7 redesign).
The v7 redesign (the palindrome rule: player-written direction, splits, and
distance-proportional exit speed) replaced the old pre-announced forced
reversals. Each round's plan is recorded in the commit history.
