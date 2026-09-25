---
name: nexa-remotion-styles
description: "A catalogue of named video looks for Remotion, each a complete recipe: keynote minimal, dark SaaS launch, clean product explainer, bright consumer app, kinetic typography, Swiss grid, editorial magazine, data journalism, Vox collage, flat illustrated explainer, whiteboard sketch, corporate, luxury, cinematic trailer, neon, eighties retro and VHS, terminal and developer, brutalist, Bangla-first, lyric video, audiogram, captioned talking-head short, documentary and news, map story, 3D product hero, paper stop-motion and glitch. Each gives the kit theme, ground, type, motion character, composition, signature moves, transitions, sound and what to avoid. Use it to choose or match a style ('ei style e banao', 'Apple er moto', 'Vox style', 'cinematic trailer look'). Part of the nexa-remotion family."
---

# Styles catalogue

A look is a set of decisions that belong together: ground, type, colour, motion, composition, transitions and sound.
Pick the entry closest to the brief, apply its theme with `ThemeProvider` (brand it with `makeTheme`), and follow its
motion and composition notes. Part of the nexa-remotion family (the director skill is `nexa-remotion`; every theme
named here is in the kit's core, and `nrk.py demos --module core` shows them all on one sheet).

## Fast path

1. Read the brief for signals: audience, product category, energy, platform, brand colours, the words the client
   uses about themselves ("premium", "friendly", "bold", "trusted").
2. Choose one entry below (two at most, blended: one for structure, one for colour). When nothing fits, start from
   `studio` or `midnight` and design the dials yourself.
3. Brand it: `makeTheme('<theme>', {colors: {accent: brand}, fonts: {display: ...}})`. Keep the entry's motion
   character unless the brand says otherwise.
4. Check the look early: one scene, stills, compare with the entry's notes, then build the rest.
5. Never mix two looks' motion characters in one film (a bouncy pop in a luxury film reads as a mistake).

## The looks

| Look | Theme | One line |
|---|---|---|
| Keynote minimal | `keynote`, `keynoteLight` | huge quiet type, slow blur-in, lots of space, one product at a time |
| SaaS launch, dark | `midnight` | real UI in motion, a camera over the product, cursor clicks, cool accents |
| Clean product explainer | `studio` | off-white stage, near-black type, one blue, calm rises |
| Bright consumer app | `fresh` | white, green and coral, springy pops, phone UI, friendly rounded sans |
| Kinetic typography | `kinetic` | black, condensed capitals, acid accent, fast masked hits on a rhythm |
| Swiss grid | `swiss` | white, black, one red, flush-left grotesk, hard wipes on a visible grid |
| Editorial magazine | `editorial` | white page, big serif headlines, editorial red, masked reveals, photos with captions |
| Data journalism | `data` | charts that draw, serif headlines, sourced numbers, restrained colour |
| Vox collage | `vox` | warm paper with grain, halftone cut-outs, marker strokes, counters, newspapers |
| Flat illustrated | `playful` | sky blue, coral and sun, rounded shapes, bouncy pops, simple characters |
| Whiteboard sketch | `whiteboard` | white board, marker lines drawing on, hand lettering, arrows and circles |
| Corporate and finance | `corporate` | cool grey, navy, teal, calm motion, clear charts, trustworthy |
| Luxury and fashion | `luxury` | warm black, gold, spaced serif capitals, slow blur and long holds |
| Cinematic trailer | `trailer` | black, letterbox, spaced serif, slow fades, light leaks, grain |
| Neon night | `neon` | ink blue, cyan and magenta light, glow with restraint, wide display type |
| Eighties retro and VHS | `retro` | purple night, pink and cyan, chunky display, stepped motion, tape artefacts |
| Terminal and developer | `terminal` | GitHub-dark, monospace, typed commands, code that highlights |
| Brutalist | `brutalist` | flat grey, black rules, loud colour blocks, heavy capitals, snapping slides |
| Bangla-first | `dhaka` | deep green, red and marigold, Anek Bangla headlines, Bengali digits |
| Lyric video | `kinetic` or `editorial` | lines revealed on the beat, one word emphasised per line |
| Audiogram | `midnight` or `studio` | waveform, captions, title, the speaker's photo |
| Captioned talking-head short | any | the face untouched, bold captions with an active word, b-roll punches |
| Documentary and news | `corporate` or `trailer` | lower thirds, maps, archive photos, quiet type |
| Map story | `data`, `neon` or `studio` | routes drawing, pins, zooms from the world to a place |
| 3D product hero | `keynote` | one object turning under studio light, a name over calm space |
| Paper stop-motion | `vox` or `playful` | cut paper on a textured ground, motion on twos, slight boil |
| Glitch and cyber | `neon` or `kinetic` | RGB splits and slices in bursts, scanlines, hard cuts |

Full recipes for every look: `references/looks.md`. How to build a new look when none fits:
`references/make-a-look.md`.

## Rules that keep a look coherent

- One palette, one type voice (two families at most), one light language across the film.
- The motion character belongs to the look: durations, curves and springs come from the theme's `motion` block.
- Texture is a dial per look (grain, paper, vignette), never a default on everything.
- Adjacent scenes change composition system, not look.
- Brand colours override the palette, but keep the look's contrast and its one-accent budget.
- Check every look against the anti-slop list in `nexa-remotion/references/quality.md`.

## References

- `references/looks.md`: every look as a recipe: when to use it, theme and overrides, ground, type, motion, composition
  systems, signature moves and kit components, transitions, sound, what to avoid.
- `references/make-a-look.md`: building a look from a brand or a reference video: the dials, measuring a reference,
  writing the theme.
