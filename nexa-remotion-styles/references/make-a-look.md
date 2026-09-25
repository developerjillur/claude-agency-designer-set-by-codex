# Making a new look

When no entry fits, or a client brings a reference video or a brand book.

## From a brand

1. Colours: the brand's primary becomes `accent`; pick `accent2` from the brand's secondary or a complementary hue;
   derive `bg`, `surface`, `text`, `muted`, `faint` and `line` as tinted neutrals (a hint of the accent's hue). Check
   text on ground at 4.5:1 or more; darken the accent for small text on light grounds.
2. Type: the brand's fonts if they are on Google Fonts (add them to the kit's font table with their real weights) or
   as files through `@remotion/fonts`; otherwise the closest free family. One display, one body, a Bangla family when
   the audience needs it.
3. Motion character from the brand's words: "premium, calm" long blur-ins and no bounce; "friendly, playful" pops and
   bouncy springs; "bold, confident" masks and snaps; "trusted, clear" rises on `outCubic`.
4. Texture from the medium: print brands grain and paper; tech brands clean or a faint grid; cinema grain and vignette.
5. Write it with `makeTheme(base, overrides)` in one `theme.ts`.

## From a reference video

Measure, do not guess (the Vox look in `nexa-video-creator` was built this way):

1. Watch it with `agy-watch-video` (`watch VIDEO --goal motion`) and pull frames at the moments that define the look
   (`frames VIDEO --at ...`).
2. Measure colours from frames (sample flat areas), sizes of type and margins at 1080, the grain (luma spread on a flat
   area), line widths.
3. Time the motion: count frames of entrances, holds, exits and transitions from a dense frame sheet (`--fps 10`).
4. Note the composition systems and the signature moves.
5. Rebuild one scene, render stills at the same moments, compare side by side, adjust, then write the theme and a
   recipe entry like the ones in `looks.md`.

Never copy a reference's logos, characters, footage or text; the look (colour, type classification, rhythm,
composition) is what you rebuild.

## The dials

| Dial | Low | High |
|---|---|---|
| Energy | long holds, blur-ins, dissolves | fast masks, punch-ins, cuts on the beat |
| Density | one thing per shot | several elements, layered |
| Ground | flat colour | textured, lit, parallax world |
| Depth | flat | camera moves, parallax, 3D |
| Type | text as caption | text as the image |
| Texture | clean | grain, paper, halftone, film |
| Colour | one accent | several, saturated |
| Sound | a bed | effects on every event, music-driven cuts |

Three directions for a client differ on at least four dials.
