# Code and terminals

Code on screen works when it is short, readable at a glance and walked through: one idea, the lines that matter lit,
the rest dimmed. This file covers the kit's `CodeBlock` and `Terminal`, the tokenizer behind them, timing budgets,
and alternatives.

## 1. What to show

- At most about 12 lines and 70 characters per line at 26 px in a 1100 px window (the block does not wrap lines).
  Cut a longer file down to the fragment that carries the point; `firstLine` keeps the real line numbers.
- One walkthrough step per idea: highlight 1 to 4 lines, hold at least 2 s per step, never while typing.
- Real code from the product or a plausible, compiling fragment; never fake API keys or secrets (mask them as
  `sk-live-...` style placeholders only if the brief requires the shape).

## 2. `CodeBlock`

```tsx
<CodeBlock code={SRC} lang="ts" title="ship.ts" typing="char" startAt={6} cps={50}
  focus={[{lines: '5-6', at: 150}, {lines: [7], at: 192}]} width={1060} fontSize={28} />
```

- **Typing modes.** `'char'` types like an editor: even speed (jitter 0.2), tiny beats after spaces and punctuation
  (a fifth of prose), leading indentation appears at once, a caret follows and blinks for about 1.3 s after the last
  character. `'line'` slides each line in from the left every `lineEvery` frames (5 at 30 fps). `'none'` fades the
  whole block in.
- **Budget.** Frames for `'char'` = characters / cps x fps + about 10%. 200 characters at 50 cps: 120 + 12 = 132
  frames. 330 characters at 45 cps is 240 frames: too long for most beats, so type a fragment by character and let the
  rest arrive by line, or use `'line'`.
- **Walkthrough.** `focus` steps light lines with an accent band (13% alpha) and a 4 px accent bar at the left, turn
  their line numbers to the accent, and dim every other line to `dim` (0.38); each step moves over 9 frames with ease
  in-out. Lines are the displayed line numbers (they start at `firstLine`, 1 by default): `[3, 4]` or `'3-6'` or
  `'2,5-7'`.
- **Scrolling.** With a fixed `height`, the view follows the caret while typing and brings the focused lines into the
  upper middle after typing, eased over a few frames (a moving average of the target, so it is deterministic).
- **Look.** A title bar with window controls and the file name (`chrome`, `title`), line numbers (`lineNumbers`,
  `firstLine`), the theme's mono font, light or dark by the theme or `mode`.

## 3. Colours and the tokenizer

`tokenizeCode(src, lang)` splits source into tokens of kind `plain`, `kw`, `str`, `num`, `com`, `fn`, `type`, `prop`,
`punc`, `op`, `tag`, `attr`, `var`, `const`. `tokenLines(src, lang)` cuts them into lines (multi-line comments and
strings split at new lines). It is a set of ordered patterns, not a parser: good for short snippets.

| Language | What it colours |
|---|---|
| ts, js | line and block comments, all three string forms, numbers, keywords, `true/false/null/undefined`, calls (`fn`), types (capitalised names), properties after `.`, object keys |
| tsx, jsx | the above plus tag names (`tag`) and attributes (`attr`) inside `<...>` |
| py | `#` comments, triple-quoted and prefixed strings (`f"..."`), decorators, `def` and `class` names, `self`/`cls`, builtins |
| json | keys (`prop`), strings, numbers, `true/false/null` |
| bash | comments, strings, `$VAR`/`${...}`, `--flags` (`attr`), the command word after a line start, `|`, `&&`, `;` |
| text | nothing |

Known limits: no highlighting inside template-literal `${...}`, no regex literals, no heredocs, generics in `.tsx`
may be read as tags.

`codePalette(dark, bg)` gives the colours: dark (keywords coral `#FF8C8C`, strings mint `#A1E3A9`, numbers amber
`#FFBA73`, functions sky `#7DC5FF`, types gold `#F3D77A`, properties lavender `#C9B6FF`, comments slate `#7F899B`) and
light (magenta keywords, green strings, orange numbers, blue functions, brown types, purple properties, grey comments).
Override any kind with `palette={{kw: '#...'}}`. For a brand-coloured editor, keep keyword and string hues apart
(at least 90 degrees) and comments clearly dimmer than code.

Fonts: JetBrains Mono (most themes) draws `=>`, `!==` and similar as ligatures; that is normal in editors. Comments in
non-Latin scripts are set upright (a synthesised italic ruins Bangla); the mono stacks fall back to the theme's Bangla
font for Bengali text.

## 4. `Terminal`

```tsx
<Terminal startAt={8} path="~/team-notes" lines={[
  {cmd: 'npm create driftnote@latest team-notes'},
  {out: 'Templates copied', tone: 'ok', icon: 'check'},
  {cmd: 'cd team-notes && npm install'},
  {progress: 'Installing', frames: 46},
  {cmd: 'npm run deploy'},
  {spinner: 'Deploying to the edge', frames: 40, done: 'Live at team-notes.driftnote.example'},
]} />
```

- Timeline (`terminalTimeline(lines, fps, startAt, cps)`): a command types at `cps` (24, with short beats), the
  output starts 9 frames after the last character (the Enter), output lines appear 2 frames apart, a progress line
  fills over `frames` (40) with an ease out and a tabular percentage, a spinner spins for `frames` (36) and becomes a
  check with its `done` text, `{gap: n}` waits.
- Tones: `plain`, `muted` (logs), `ok` (green), `warn` (the highlight colour), `err`, `accent`, `info` (accent2).
- The prompt is `path` (accent2) + `symbol` (accent); an idle prompt with a blinking block caret closes the session.
- When the lines outgrow the window it scrolls up smoothly, one line height per new line.
- Dark in every theme (the neutral dark palette with the theme's accents); `mode="light"` for a light terminal.
- Real timings: keep `added 214 packages in 6s` style outputs plausible; never print real tokens, emails or IPs.

## 5. Beyond the kit

- Animated changes between two versions of a snippet (moving tokens, morphing lines): the official Code Hike template
  (`npx create-video@latest --code-hike`) does token-level transitions.
- A diff view: build it from `tokenLines` with a `+` or `-` gutter and green or red line backgrounds at 12% alpha; animate
  removed lines collapsing with the grid-row trick and added lines growing in.
- A custom editor (tabs, a file tree, a minimap): lay it out in a `MacWindow`, type with `useUiTyping(text, start, {cps,
  pause: 0.2, instantIndent: true})` and colour with `tokenizeCode`.
- Highlighting a word in prose (not code): `@remotion/rough-notation` `<Highlight>` with a translucent colour.

## 6. Faults and fixes

| Fault | Cause | Fix |
|---|---|---|
| The walkthrough lights half-typed code | focus steps inside the typing time | budget the typing and start steps after it |
| Typing feels sluggish | prose rhythm on code, or cps under 30 | the kit's code rhythm (`pause: 0.2`) at 40 to 60 cps |
| Lines run out of the window | long lines (no wrapping) | shorter lines, a wider block or a smaller font |
| Bangla comment looks slanted and broken | synthetic italic | the kit sets non-Latin comments upright; do the same in custom code |
| Colours wrong after a template string with `${}` | the tokenizer does not parse inside it | keep template expressions simple, or override with a custom render |
| Terminal lines jump | lines of different heights (icons, Bangla) | the kit gives every line a fixed height; keep custom rows the same |
