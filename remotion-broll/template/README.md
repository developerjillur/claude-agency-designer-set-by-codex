# Explainer B-roll (remotion-broll kit)

A Remotion 4 project for 1920x1080, 30 fps explainer B-roll: code-drawn characters, UI scenes, charts, captions and an
end card, with sound effects. It was started from the remotion-broll skill.

- Every word on screen: `src/copy.ts`. The charts' numbers: `GROWTH` in the same file.
- Font and colours: `src/theme.ts`. Scene lengths: `src/Part2.tsx` and `src/BrollDemo.tsx`.
- Pictures: `public/presenter-pip.png` and `public/creator-cutout.png` (stand-ins until you add your own).

```console
npm run dev                                            # Studio: scrub the timeline, each scene on its own
npx remotion render BrollMinute out/BrollMinute.mp4    # the whole minute, about 45 s
```

With the skill installed, `python3 ~/.claude/skills/remotion-broll/scripts/broll.py check|stills|render|review .`
checks the copy, makes a contact sheet, renders with QA and runs the Gemini review.

Remotion is free for individuals and companies of up to three people; larger teams need a company licence
(remotion.pro/license).
