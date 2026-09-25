# Studio, Player, client-side rendering and codemods

## The Studio as an editor (4.0.475+)

Start it for a person with `npx remotion studio --no-open` (it prints the URL; if one already runs for the project it
says so; `--force-new` starts another). Visual edits are written back to the source: drag to move (`translate`),
edges to scale, corners to rotate, keyframes and easing on the timeline, effects dropped on layers, `Cmd+Shift+D`
splits at the playhead (4.0.527).

Code stays editable only when:
- layers are `Interactive.*` elements (or `Img`, `@remotion/media` `Video`) with a literal `name`;
- `style` is one inline object literal (no constants, spreads, maths or memoised objects);
- animation is an inline `interpolate(frame, [literal range], [literal values], {literal options})` per property
  (the input range may use `fps`, `durationInFrames`, `2 * fps`, `durationInFrames - 1`);
- transforms use `translate`, `scale`, `rotate` and `opacity` properties, not `transform` strings or `top`/`left`;
- Composition metadata and `defaultProps` are inline (no casts, no extracted constant);
- effects arrays are inline with a stable shape;
- custom components use `Interactive.withSchema({Component, componentName, schema: {...Interactive.baseSchema,
  ...}})` and forward `controls` (and `outlineRef` with `layout="none"`).
Editable easings: `linear`, `step1`, `bezier`, `spring({static})`, `ease`, `quad`, `cubic`, `back`, `poly(1 to 3)`.
After a person edits in Studio, read the source again before changing it.

The kit's components take props; scene code written with inline keyframes and `Interactive.*` stays editable. Use
that style for client projects a person will fine-tune.

Useful `@remotion/studio` functions (Studio only): `getStaticFiles`, `watchStaticFile`, `writeStaticFile`,
`saveDefaultProps`, `restartStudio`, `seek`, `play`, `goToComposition`, `reevaluateComposition` (re-runs
`calculateMetadata`). Keyboard: Space, J/K/L, `T` checkerboard (check transparency), `R` render dialog, `Shift+R`
rulers and guides. `Config.setDefaultEditor('cursor')` for open-in-editor.

## The Player in apps

`<Player component durationInFrames fps compositionWidth compositionHeight inputProps controls />` (never a
`<Composition>`). Keep the component that renders it from re-rendering on time updates; memoise `inputProps`; put
controls in siblings with a `playerRef` (`play(e)`, `pause`, `seekTo`, events `frameupdate`, `timeupdate`, `ended`,
`error`, `waiting`); pass the click event into `play(e)` for audio; mount-only props (`initialFrame`, `sampleRate`,
`numberOfSharedAudioTags`) need a remount with a new `key`. Buffering: `@remotion/media` tags buffer by default;
`useBufferState().delayPlayback()` for your own loading (in `useEffect`, unblock in cleanup). Premounting
(`premountFor`) is for the Player and Studio only. Embedding a Player counts as automation for licensed companies.

## Client-side rendering (`@remotion/web-renderer`)

`renderMediaOnWeb()` redraws the DOM onto a canvas in the user's browser: single-threaded, needs CORS on every asset,
only `@remotion/media` media, no z-index (order the DOM), no blend modes, no backdrop-filter, no perspective, no
inset shadows; supported: layout, overflow, `object-fit`, 2D transforms, `opacity`, linear gradients, borders and
radius, most text properties, basic shadows, `filter`, `clip-path`. Check with `canRenderMediaOnWeb()` first. Use
`useDelayRender()` and `useRemotionEnvironment()` (not the global functions). Server rendering stays the choice for
client work.

## Codemods (`@remotion/codemods`, draft on 4.0.528)

The Studio's editing engine as functions over an in-memory project `{rootDir, files}`: inspect nodes and props
(static, keyframed, computed), add, duplicate, rename and move compositions, set default props, add media and
components, split sequences, detach audio, edit props and keyframes, add and reorder effects; each returns file
changes (apply with `applyCodemodChanges`; undo by swapping previous and next). They refuse computed values, spreads
and dynamic timing: the same static-code rules as the Studio.

## Licence facts to surface

Free for individuals, organisations of up to 3 people, non-profits and evaluation. A Company License for 4 or more:
seats for people writing Remotion code (agents included), per-render pricing for automation (calling render
functions, the CLI render in a pipeline, cloud rendering, an embedded Player); Enterprise from $500 a month. An agency
delivering only files counts only its own headcount. Codec patent fees are not covered.
