# Writing a precise video brief

Use this when turning a vague request into a buildable plan, when briefing a sub-agent to build a scene, or when a
user wants to write their own prompt. Numbers beat adjectives; the frames must add up.

## The skeleton (fill every line, delete what does not apply)

```text
Skills: nexa-remotion + <sub-skill>; kit modules <list>
Canvas: <W>x<H>, <fps> fps, <seconds> s (<frames> frames), composition "<Id>", ground <theme ground or hex>
Story: Scene 1 (<frames> f): <what appears; copy verbatim> / Scene 2 (...) ... (frames add up to the total)
Style: theme <name> (+ makeTheme overrides: colours with roles, fonts per role); look anchors (1 to 3)
Motion: entrances <reveal, frames, distance>; exits <...>; stagger <frames>; transitions <type, frames>; camera <path>
Assets and data: <public/ paths, data JSON, captions JSON, screenshots>
Audio: <voice file and cue table, music file and volume, effects on which cues>
Props to expose: <list, with a Zod schema if a client will edit them>
Constraints: deterministic; fonts loaded; safe area for <platform>; <layering rules>
Output: <preset (web, master, alpha), path>; stills sheet per act before the render
Done when: <observable checklist: "title readable at frame 0", "counter lands on 'three'", "nothing on the last frame">
```

## Two detail levels that work

- **Short prompt plus iteration** for exploratory or effect-driven pieces: a clear anchor ("a route drawing from
  Dhaka to London on a dark globe"), then precise corrections after each look.
- **A long numeric spec** for production pieces with fixed content and a brand: every scene with frames, copy,
  colours and motion values.

## Briefing a sub-agent to build scenes

Give one heavy task per agent, the shared parts by path (theme file, cue tables, the kit), and the checks it must
run (stills sheet, what to look for). Ask it to report the frames it looked at and what it could not verify. Keep
design notes away from the reviewer agent.

## Anti-patterns

No canvas numbers; adjective piles without values; asking to "analyse the uploaded video" without a video tool (use
agy-watch-video); hand-rolled random hashes instead of `random(seed)`; real people and brands without permission;
"make it pop" without saying what the viewer should notice first.
