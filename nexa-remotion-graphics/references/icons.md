# Icons: the kit's set, rules, adding your own, motion

## 1. The set (49, drawn for this kit)

24 x 24 grid, 2 px strokes, round caps and joins, no fills, every icon made of strokes listed in the order a hand
would draw them (so `mode="sequence"` draws them like a pen).

| Group | Names |
|---|---|
| Actions and arrows | check, x, plus, minus, arrow-right, arrow-left, arrow-up, arrow-down, trend, download, link, search |
| Media | play, pause, camera |
| Data | chart-up, chart-down, chart-bar, target |
| People | user, users, chat, bell, mail, phone |
| Commerce | cart, money, gift, trophy |
| Places and time | home, pin, globe, clock, calendar, flag |
| Tech | code, file, settings, cloud, lock, shield, bolt |
| Ideas and moods | star, heart, spark, bulb, rocket, leaf, eye |

`ICONS[name]` is the path data; `ICON_NAMES` lists the names; `IconName` is the type.

## 2. Using them

```tsx
<Icon name="rocket" size={96} delay={10} />                         // draws on in 26 f
<Icon name="check" size={64} color={t.colors.positive} draw={false} />  // still
<IconBadge name="shield" size={140} delay={20} />                   // tinted disc pops, then the icon draws
<IconBadge name="bolt" size={120} solid tint={t.colors.accent2} />  // solid disc, on-accent icon
<svg viewBox="0 0 24 24"><path d={ICONS.globe} fill="none" stroke="currentColor" strokeWidth={2} /></svg>
```

Sizes (px at 1080): 48 to 64 inline with text, 84 to 120 in lists and flow nodes, 140 to 220 as a scene's hero.
Stroke: 2 at 64 to 140 px; 1.5 for big hero icons (above 180 px) so the line does not look heavy; 2.5 for small
icons on busy grounds.

## 3. Motion

- Draw on: 20 to 30 f, in-out, `'sequence'` (pen order). Lists of icons: a 3 to 6 f stagger.
- Badge: the disc pops (14 f, overshoot), the icon starts drawing 6 f later.
- Exit: `exit="undraw"` erases the strokes from their start, `'fade'`, `'shrink'`.
- A state change (play to pause, plus to check): cross-fade two icons over 8 f, or morph two single-outline icons
  with `MorphPath mode="points"` (outline icons with several strokes do not morph well).
- Keep icons still once drawn; if an icon must live during a long hold, a 2 to 3 degree `Float` on the badge, never
  on the strokes.

## 4. Adding an icon

1. Draw on the 24 grid with a 2 px margin (keep points between 2 and 22), strokes only.
2. Use the builders in `icons.ts` (`circle(cx, cy, r)`, `rrect(x, y, w, h, r)`, `gear`, `star`) and plain `M L H V
   A C Q Z` commands. One subpath per stroke a hand would draw; order them as a hand would (outline first, details
   after).
3. Dots are zero-length strokes (`M12 12L12 12`): the round cap draws them, and the draw-on shows them whole when the
   pen reaches them.
4. Check it at 84 px and at 220 px in the icons demo (`nrk.py demos --module graphics --only Icons`, then a
   full-size still) before using it.
5. Rules that keep the set consistent: optical size (a circle icon at radius 9, a square at 16 to 18 wide), 2 px
   gaps between strokes that do not touch, corners rounded 2 on rectangles, no fills, no strokes thinner than 2.

## 5. Other icon sources

- A brand's own icons (SVG): paste the path data into `DrawPath` (it computes the viewBox) or add them to a
  project-level map; keep their stroke width.
- Lucide, Tabler, Phosphor and similar sets are open source (check each licence) and share the 24 grid and 2 px
  stroke, so they sit well next to the kit's icons; they are not bundled.
- Emoji: `@remotion/animated-emoji` (Noto animated emoji videos; the assets are not bundled).
- Lottie icons: `@remotion/lottie` with the JSON in `public/` (memoise `animationData`).
