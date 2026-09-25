# Vox-style explainer: style bible

Version 1, compiled 2026-09-25 for a Remotion-based explainer tool.
Every source was accessed on 2026-09-25. Bracketed IDs such as [S4] point to the source list at the end, which gives each URL with its access date.

---

## 0. Read this first

### 0.1 What "Vox style" means here

The look of Vox.com's YouTube explainers (2014 onward) and the genre they seeded: paper and collage explainers, map-led geopolitics (Vox Atlas, Vox Borders, Johnny Harris), archival photo forensics (Vox Darkroom, Missing Chapter), music breakdowns (Earworm) and video essays. Not Kurzgesagt's flat vector world.

### 0.2 Evidence grades used on every claim

- **(A)** Vox staff or the creator describing their own work: interviews, talks, their own tutorials. "(A, reported)" means a journalist paraphrasing them.
- **(B)** Either measured by me from public YouTube data (method in Appendix A), or a named practitioner tutorial. Tutorial values are that tutor's recreation choices, not confirmed Vox settings.
- **(C)** Secondary, marketing or AI-looking articles and packs. Leads only.
- **(H)** House default proposed for our tool. Not sourced. Tune by eye.
- **UNVERIFIED** marks common claims I could not confirm from a primary source.

### 0.3 Honest limits

- No public Vox video style guide exists that I could find. The look varies by producer, series and year, and art direction is set per story [S1] (A) [S41] (A).
- Design press coverage is thin: I found no substantive Vox-specific pieces on It's Nice That, Motionographer or Creative Bloq. School of Motion's interview with Estelle Caswell is the main design-press source [S6]. Reddit was reachable only through an archive API and had little of substance [S47].
- I did not download any video, so shot lengths and on-screen colours were not measured frame by frame. Pace numbers come from caption timings and player metadata (Appendix A).

---

## 1. The style in twelve rules

1. **Only make it a video if the story is visual.** Joe Posner's founding philosophy for the Vox team: narration with b-roll or stock photos slapped on top does not qualify [S14] (A, reported).
2. **Visual evidence first, context second.** Johnny Harris calls his formula "anchor, bridge": real, pointable evidence ("visual anchors") first, short context bridges between them. He says the fancy camera moves are only the icing; the anchors are the substance [S4] (A). An analysis of his Venezuela border piece found the first three minutes of eight were almost all anchors, and its author notes Harris learned the structure at Vox under mentors such as Joss Fong [S5] (B).
3. **Write to the picture.** Harris writes in three columns (narration, visual, source) and does not write a paragraph without a planned visual; Vox narration points at what is on screen ("this is...") while the animation circles it [S4] (A). Fong keeps direct phrases such as "This is" and "Look at this" that print editors would cut, because viewers need room to look [S10] (A).
4. **Picture and voice match exactly and arrive together.** Fong says tight correspondence between what the animation shows and what the voice says boosts comprehension and retention [S12] (A). This is Mayer's temporal contiguity and signaling principles [S48].
5. **One anchor visual per video.** Fong hunts for the single visual with the most explanatory power and reuses it, for example a Venn diagram that carries a whole piece [S11] (A). Art director Joey Sendaydiego builds each video on an "anchor" motif [S1] (A).
6. **Imperfect on purpose.** Sendaydiego: a perfect finish makes a video read like an ad instead of editorial [S1] (A). Practitioners sum the look up as analog: screens look like screens, paper looks like paper [S23] (B).
7. **Information over decoration.** Caswell: transitions carry no information, so jump cut to the next thing; slightly rough (B+) animation is fine if the story is served [S6] (A). The point of video is to talk about the thing on screen [S8] (A).
8. **The denser the idea, the flatter the design**, and repeated motifs keep viewers oriented (observed in Christophe Haubursin and Amanda Northrop's work) [S34] (C).
9. **Each video gets its own visual world inside the brand.** A unique visual language per episode while respecting Vox branding [S41] (A); construction paper for a schools story, protest-poster styling for history, flying text for an AI story [S1] (A).
10. **Accuracy is part of the look.** Harris marks every assertion red until it has a sourced hyperlink in the third column, then green, and a colleague proofs them at the end [S4] (A). On serious topics, accuracy and respect beat beauty [S1] (A).
11. **Tactile, found evidence beats generic stock:** archival magazines and instrument manuals [S7] (A), vinyl and tape decks [S9] (A), charts printed on paper (Fong, now at Howtown) [S13] (A).
12. **Long is fine if you earn it.** Front-load the best anchors in the first 10 to 15 seconds as a promise, then deliver it [S4] (A).

---

## 2. Format defaults (measured and reported)

| Parameter | Evidence | Default for the tool |
|---|---|---|
| Frame rate | All 18 sampled uploads (17 Vox from 2016 to 2025, plus one Johnny Harris) report 24 fps [S62] (B). YouTube: upload at the rate you recorded [S50]. | 24 fps (H) |
| Resolution | Sampled Vox uploads topped out at 1080p in the player data I could read [S62] (B). Harris builds map comps at 1920x1080 [S3] (A); Boone rebuilt a Vox map at 4K [S19] (B). | Master 1920x1080; source art at 2x for push-ins (H) |
| Length | Sample: 5:43 to 15:52, median about 9:40 [S62] (B). Vox went from 2 to 4 minute videos (2015) to 6 to 10 minutes after its 6:46 Syria explainer drew about 100 million Facebook views [S4] (A). Atlas pieces run about 10 minutes [S16] (A). | 6 to 12 min for YouTube; 60 to 120 s cutdowns (H) |
| Narration speed | Median 148 words per minute over full runtime (range 104 to 163) and about 170 wpm inside speech [S62] (B). Vox's planning rule: word count divided by 160 wpm [S4] (A). | Time scripts at 150 to 160 wpm (H) |
| First words | Median narration onset 1.9 s (range 0.1 to 9.2 s) [S62] (B). | Voice or anchor visual within 2 s (H) |
| Breaths | Speech gaps of 1.5 s or more: median 0.75 per minute, median length 3.2 s, 90th percentile about 11 s; the Borders documentary had 1.9 per minute [S62] (B). | One music breath every 60 to 90 s, 2 to 5 s long; longer only at act breaks (H) |
| Music changes | Fong changes music about every 20 s in a dense explainer [S10] (A). | New cue or music edit every 20 to 40 s (H) |
| Retention | Vox averages about four minutes of watch time [S1] (A); Harris reports about 70% of viewers finishing Borders episodes [S4] (A). | n/a |
| Production time | Two to three weeks at most per video, one or two uploads a week [S1]; Earworm about 3.5 weeks [S9]; Caswell: 4 to 5 days of reporting and script, then a week to ten days of animation, voice and assembly [S8]; one Atlas video took five weeks [S16]; a Borders season: about six weeks of pre-reporting, 10 to 11 days on location, about eight weeks of post for five films [S4][S17] (all A). | Lock the script before animation (H) |
| Team | About 25 to 30 full-time video staff plus freelancers [S6] (A). | n/a |

### 2.1 The production workflow behind the look

- Pitch with visuals already found: Caswell pitches only after building her dataset [S8] (A); Phil Edwards starts from striking archive assets and researches backward [S43] (A).
- Script in three columns (voice, visual, source), colour-coded for fact-checking [S4] (A).
- Early rough cut ("shame draft") with scratch voice, music and placeholder text for missing animation, shown to editors before animation starts [S43] (A); editors call these placeholders temp graphics [S47] (C).
- Harris builds the story structure in the edit first, then adds b-roll [S64] (A, per his course description). His animators get a list of animations with key directions and discuss duration and pacing per shot [S21] (B).
- Voice is recorded during the animation phase, as part of final assembly [S8] (A).
- Edit in Premiere, animate in After Effects, maps with GEOlayers or Google Earth Studio [S3][S7][S15] (A).

---

## 3. Visual system

### 3.1 Canvas: paper, grain and texture

Principle: nothing is pure digital white; everything has a material [S23] (B).

| Element | What sources show | Default (1080p, 24 fps) |
|---|---|---|
| Background colour | Never pure white; warm it slightly, because paper picks up the room's light [S23] (B). Off-white or light grey-stone solid under texture [S27] (B). | Paper #F2EEE6 or #EFE9DD; dark variant #151515 (H) |
| Paper texture | Scanned paper blended Screen at 40 to 50%, plus a Texturize pass (contrast 0.2) with a slowly moving light [S27] (B). A tutor recommends texturelabs.org as free and commercially usable [S23] (B); confirm its licence before client work. | One real scanned plate: Multiply 25 to 40% on light grounds, Screen 30 to 50% on dark (H) |
| Halftone overlay | Halftone grunge in Overlay for a newsprint feel [S23] (B); halftone at 25% Overlay [S25] (B); dot texture at 10 to 20%, because more looks fake [S27] (B). | 12 to 20% (H) |
| Grain | Monochrome noise about 5% [S27] (B); heavy grain (size about 1.4) over mixed archival [S23] (B); grain plus unsharp mask [S28] (B). | 4 to 8% mono grain, re-seeded every stepped frame (H) |
| Boiling texture | Five or six textures cycling so two or three appear each second, looped over 10 s [S2] (B); textures jumped with hold keyframes and looped [S59] (B). | Six plates, swap every 8 to 12 frames (H) |
| Light leak | Add-mode leak for slight paper discolouration [S23] (B). | Optional, 5 to 15% (H) |
| Vignette and edge blur | Lumetri vignette [S23]; lens-blur vignette about 4 through a 300 px feathered ellipse [S25]; Gaussian 3.5 inside a circular mask feathered 50 [S2] (all B). | Darken edges 10 to 20%; 2 to 4 px edge blur (H) |
| Chromatic aberration | About 0.8 on graphics (transcribed as "8" after 1.5 was judged too strong), 1.2 on screens, 2 on archival; too much looks amateur [S23] (B). | 0.5 to 1 px channel offset on graphics, 1 to 2 px on archive and screens (H) |

### 3.2 Colour

- **Brand yellow:** vox.com's live CSS uses #FFF200 (inspected 2026-09-25) [S37] (B). A third-party token scan of the site calls it the masthead and highlight colour and lists ink #131313, soft ink #4A4A4A, muted #636363, link blue #6AAAE4 and hairline #E9E9E9 [S38] (C).
- **Yellow highlighting** is widely treated as a Vox video trademark [S42] (C). Recreations use a standard yellow marker in Multiply [S29] (B).
- **Palette per story:** each episode gets its own visual language within Vox branding [S41] (A); topic-led treatments such as 1980s fluorescent gradients [S34] (C) or protest-poster styling [S1] (A).
- **Map palette** sampled by Jason Boone from a 2019 Vox map (Strait of Hormuz): land RGB 21,21,21 (#151515), water RGB 47,71,111 (#2F476F), highlighted countries RGB 44,44,44 (#2C2C2C), a yellow dashed route, labels in capitals with one country label in white [S19] (B).
- **Johnny Harris maps:** a bluish solid for water, land recoloured with hue and saturation, white borders, orange country highlight [S3] (A); recreations blend the orange in Multiply [S22] (B).
- **Few colours:** "three to four colours" is a common claim [S57] (C). House rule (H): paper base, ink, one accent (yellow marker), one topic colour; red only for harm, conflict or loss.
- **Photos:** grade everything into one family (black and white or sepia, then one tint) [S26][S28] (B).

House palette (H): Paper #F2EEE6, Ink #131313, Marker #FFF200 (Multiply on paper), Signal red #D7392B, Map water #2F476F, Map land dark #151515 or light #E6DFD2, Neutral grey #8A8A8A, Accent blue #6AAAE4.

### 3.3 Typography

Facts:

- vox.com (2026) declares three families: Balto, Harriet and Roboto Mono [S37] (B). The token scan assigns Balto to headlines, navigation and buttons (11 to 70 px, weights 400 to 700, about -0.7 px tracking at display sizes), Harriet to body text, and Roboto Mono to uppercase kickers and labels at 11 to 12 px with about 1.1 px tracking [S38] (C).
- The 2014 launch system was Harriet (display), Balto and Alright Sans [S35] (C).
- **Balto:** American gothic sans by Tal Leming for Type Supply (2013 to 2014), modelled on Morris Fuller Benton's ATF gothics, eight weights with italics [S39] (C); available on Adobe Fonts [S61]. Commercial font: license it for client work.
- **Harriet:** Jackson Showalter-Cavanaugh, Okay Type, 2012; Text and Display optical sizes with five weights each; a Baskerville and Scotch Roman descendant [S40].
- **In video:** a font-identification forum answer names Balto Medium for Vox on-screen text [S36] (C). Medium confidence; UNVERIFIED by Vox.
- Tutorials use other faces for mock newspapers and timelines (Caslon Pro Bold and Bebas Neue [S25]; Palatino Linotype Bold at 90 px with -35 tracking for years [S27]; Poppins ExtraBold labels [S28]) (B). These are not Vox choices.

House rules (H):

- Labels and headlines: an American gothic sans at Medium to Bold. License Balto for client work, or use a free Franklin-style gothic as the fallback.
- Quotes and documents: a Scotch or Baskerville style serif (Harriet-like).
- Kickers, sources, dates, coordinates: monospace capitals tracked about +0.1 em (the web tokens use 1.1 px at 11 to 12 px).
- Capitals only for labels of three words or fewer (map countries, kickers). Sentences stay in sentence case.
- Display tracking -1 to -2%; body 0.
- Sizes at 1080p: headlines 72 to 120 px; labels 36 to 56 px; kickers and sources 22 to 28 px. Nothing the viewer must read below 28 px.
- Never put the narration on screen as full sentences. Show keywords, names and numbers (redundancy principle) [S48].

### 3.4 Photos: cut-outs, borders, shadows, halftone

- Cut with irregular, hand-drawn masks, not boxes, and roughen the cut edge [S28] (B).
- Unify mixed photos: black and white or sepia first, then one tint. One tutor generates all AI art in sepia so it grades identically [S26][S28] (B).
- Halftone the photo for newsprint; one tutor's image prompts ask for a black and white newspaper photo with halftone texture and grain [S25] (B).
- Drop shadow in one recreation: black at 15 to 18% opacity, straight down (180 degrees), distance 75, softness about 120 on a 2500x1500 precomp [S27] (B). In other words, a large, soft, faint shadow, never a hard offset.
- Stutter portrait: cut between several photos of the same subject every few frames, each with a slightly different mask, so the image flickers like a stack of prints [S28] (B).
- White "sticker" keyline around cut-outs: common in third-party guides [S56] (C). UNVERIFIED as a Vox rule.
- House (H): keyline 6 to 10 px in paper white; shadow y-offset 8 to 16 px, blur 24 to 48 px, black at 15 to 25%; each cut-out rotated 1 to 4 degrees off square; one keyline style per video.

### 3.5 Torn paper, tape, stamps, string

- Vox uses real craft when the story suits it: the video "Teaching in the US vs. the rest of the world" was built entirely from construction paper [S1] (A); Fong, now at Howtown, printed data visualisations on paper and walked through them [S13] (A); Earworm uses vinyl and tape decks to feel tactile [S9] (A).
- Masking tape, torn edges, rubber stamps and red string appear in third-party "Vox style" packs [S58] (C). UNVERIFIED as Vox staples.
- House (H): at most one or two tape pieces per frame; torn edges only where one paper layer meets another; stamps only for dates or verdicts.

### 3.6 Collage layering and 2.5D parallax

- Design the final layout first, then push layers into depth and animate the camera backward from that end state. One tutor spreads layers from Z 0 to Z 10,000 px, rescales each to fit, and runs an 8 s pull-back on a camera null [S25] (B).
- Stagger: start each element as the previous one finishes, so there is always exactly one new thing to look at [S25] (B).
- A 24 mm camera with a 12 s push reads as a documentary opener [S60] (B); 35 mm for documents [S29] (B).
- Subtle float: position wiggle about 1 Hz and 5 px [S28] (B); a camera wiggle like a hovering helicopter [S59] (B).
- House (H): three to five depth planes; parallax ratio about 1.0 front, 0.6 middle, 0.3 back; one camera move per beat.

### 3.7 Archival footage and screens

- Footage from everywhere (archive.org, YouTube, phones, fair-use clips) never matches, so run it all through one shared treatment: black and white, heavy grain, blurred edges, a slight CRT or pixel texture, a small exposure flicker [S23] (B). One recipe: edge blur radius about 6 through an inverted feathered radial mask; CC Ball Action at grid spacing 0; chromatic aberration about 2; exposure flicker 24 times a second by about 0.05; grain size about 1.4 [S23] (B).
- Screens and websites are never flat screenshots: add a screen treatment and move the camera smoothly across them, as if discovering with the narrator [S23] (B). Recipe: Venetian Blinds at 5% completion rotated 90 degrees, width 8, feather 1, over a black Solid Composite; aberration about 1.2; vignette; exposure flicker [S23] (B).
- Vintage map sequences: desaturate, vignette, 16 mm grain in Overlay at 35%, stepped to 10 fps [S45] (B).
- Law and sourcing: Harris cuts three newscasters saying the same thing to show a topic was part of the public conversation, relying on US fair use, and licenses anything else [S4] (A). Caswell checks with Vox's legal team, and record labels still push takedowns of short clips [S6][S4] (A). Phil Edwards mines AP Archive [S43] (A); Caswell uses public-domain archives, old music magazines and instrument manuals [S7], plus Billboard and the Library of Congress registry [S6] (A).

### 3.8 Documents, headlines, screenshots and quote cards

- Sam Ellis says he would usually show headlines or a news article to establish where a story began, and reached for a 3D Earth Studio flyover only when it added more [S15] (A). Phil Edwards animates dusty documents, period reports and old charts so the archive keeps momentum [S44] (A, reported).
- Page move: 35 mm camera with depth of field travelling across the page, focus pulled to the active line [S29] (B).
- Zoom and mark: scale and position into the line over about 1 s with eased keys, then a highlight sweeps behind the words [S30] (B).
- Mock newspaper assets: serif headline, thin double rules above and below, roughened edges [S25] (B).
- Quote cards (H): serif quote at 56 to 72 px; attribution in mono capitals; outlet and date line; paper card with a faint shadow; highlight only the three to six words the voice reads.

### 3.9 Annotations: highlighter, underline, circles, arrows, handwriting

- Narration and annotation are written together: the voice says "this is..." while a circle draws on [S4] (A). Ellis draws lines and arrows straight onto Earth Studio footage [S15] (A). Caswell's pieces play handwriting against typeset text [S34] (C).
- **Highlighter** recipe: a yellow stroke along a hand-drawn mask path, Multiply so the paper grain shows through, brush hardness about 85%, revealed over about 1 s, several lines drawn one after another [S29] (B). Alternative: a rectangle scaling from 0 to 100% on X from a left anchor, Multiply, roughened edges [S30] (B).
- **Circles:** a stroke revealed by trim path, starting about 6 frames into the shot and completing in a little over a second, eased [S26] (B).
- **Hand-drawn lines:** 2 to 4 s draw-ons with a tapered leading end, staggered [S25] (B).
- **Boiling edges:** roughen the stroke edge and re-randomise it three times a second [S26] (B).
- House (H): strokes 8 to 14 px at 1080p; circles draw in 12 to 20 frames, underlines in 8 to 14, highlights in 12 to 24 per line; arrowheads appear in the last 3 or 4 frames; yellow for highlights, red or ink for circles and arrows.

### 3.10 Maps

Evidence from Vox and Harris:

- **Why animate:** a static map only shows where. Explanation needs zooming out to the players and in to the ground, drawing old and new borders, labelling buildings, and spatial datasets, which Ellis calls "visual gold" [S15] (A).
- **Vox Atlas:** a master world map in After Effects. Google Earth Studio supplies close-ups with slow, drone-like orbits and spirals, exported as JPEG sequences and linked to the master map; lines and arrows are drawn on top [S15] (A). Most animation stays at high altitude [S15] (A). For history, Ellis traced maps from old books [S16] (A).
- **Syria explainer (6:46):** essentially one camera floating over a map while the players move in; it became Vox's most-viewed video of its time [S4] (A).
- **Harris, original workflow:** a detailed, layered Illustrator world file imported as vector footage with continuous rasterisation, parented to one controller null; anchor point over the target, then scale and position keyframes; highlights are colour solids masked by the country path pasted from Illustrator and wiped on during the move [S3] (A).
- **Harris, current workflow:** a custom Mapbox style with place labels, provincial and disputed boundaries switched off, loaded into GEOlayers. Keyframes on latitude, longitude, zoom, bearing and pitch; for example start wide, zoom to Iraq over about 7 s, hold about 4 s with a slight pitch, then fly to Basra. Delay the bearing keys for an orbit. Country shapes from Natural Earth; labels as 3D text pinned to the map anchor; fade the highlight as the camera travels on [S3] (A).
- **Boone's frame-matched rebuild of a Vox map:** labels, roads, rivers and minor borders off; simple fills (palette in 3.2); labels in capitals pinned so they scale with the map; countries flicker on; labels fade in over a few frames; a dashed yellow route (30 px stroke, 30 dash, 30 to 35 gap at 4K) that draws on with trim paths, later trims away from its start, with a feathered mask fading its tail; a zoom out over about 5 s, then further; speed curves sharpened so moves kick [S19] (B).
- **Historic map montage:** 5 to 10 old map scans (for example from the David Rumsey collection) aligned on one landmark, 3 frames each, hard cuts, looped to 3 to 5 s, with a sped-up stopwatch tick [S20] (B).
- **Spread or occupation:** a shape or track matte grows across the map while the camera pulls out [S46] (B).
- **Accuracy:** an animator who worked for Harris recalls a history episode corrected after a historian's response video; the historian then co-wrote the next episodes [S21] (B).

Rules for our tool (H unless cited):

- Strip the base map to coastlines, the countries in play and very few labels [S3][S19].
- Projection: world views in an equal-area or compromise projection (Equal Earth or Natural Earth), regional zooms in Mercator to match web maps viewers know, an orthographic globe for "where on Earth" openers. d3-geo supports all three families [S53]; Natural Earth data is public domain [S54].
- Zoom grammar: wide establishing shot (3 to 4 s), eased travel (4 to 7 s), hold while the place is labelled (3 to 4 s), then detail [S3].
- Borders draw along their path (1 to 2 s per country); fills flicker or wipe on; disputed lines dashed.
- Routes: dashed for movement or trade, solid for borders; draw speed matched to the sentence.
- Pins: dot, leader line, label; pop with a small overshoot.
- Show one scale bar or a familiar comparison whenever distance matters.

### 3.11 Charts

- Charts are visual evidence in their own right (Harris's chart of refugee intake by country) [S4] (A); Fong prints charts on paper at Howtown [S13] (A); Sendaydiego turned paper clocks into pie charts [S1] (A).
- Recreation values: baseline 3 px, gridlines 1 px; bars grow by trim path over 1 to 1.5 s with front-loaded easing, each bar 3 frames after the last; axis labels slide in over about 20 frames, 2 frames apart, through a feathered matte (30 px); a highlight band at 50% opacity with a 100 px feather marks the key bars [S31] (B).
- Behind a chart: a darkened, desaturated, blurred photo with vignette and grain; the chart revealed by a moving track matte; stepped camera [S32] (B).
- A fast line move gets a whoosh plus a faint stopwatch tick [S24] (B).
- House (H): direct labels, not legends; one highlighted series in the accent colour, others in ink at 30 to 50%; tabular numerals; a source line under every chart; bar axes start at zero; never animate a number faster than the voice can say it.

### 3.12 Timelines

- Recreation: 24 fps; years in a bold serif (Palatino Linotype Bold, 90 px, tracking -35); event boxes in bright yellow scaling from their left edge; photos as framed cards that slide up with blur 25 to 0 and a fade; the previous card blurs back to 25 as the next arrives; the camera null steps along X with ease-in-out curves; shadows as in 3.4 [S27] (B).
- Sound: a stopwatch tick for timeline travel [S33] (B).
- House (H): one date per beat; the spine line draws just ahead of the camera; past events desaturate.

### 3.13 Counters and big numbers

No Vox-specific source found (UNVERIFIED). House (H): the display sans with tabular numerals; count up over 18 to 36 frames with a strong ease-out, stepped at 12 fps; unit and source in mono capitals; one tick sound on the final value only; for comparisons, show a physical proxy (dots, stacks, areas) instead of a spinning number.

### 3.14 Lower thirds, captions and source citations

- Lower third recreation: a rough texture strip revealed by a mask stepped frame by frame in a jagged, uneven way, with the text arriving a few frames later [S2] (B).
- Credits and references are tucked into frames without crowding them (Caswell's J Dilla video) [S34] (C). Sources also go in the description: Phil Edwards lists dissertations and old medical articles there [S44] (A, reported); Vox's Gaza explainer links a source spreadsheet [S63] (B).
- Harris uploads caption files rather than burning subtitles in, so community translations can reach other markets [S4] (A).
- House (H): source line bottom-left in mono capitals, 22 to 26 px, ink at 60 to 70%; names in the sans (Medium) with the role in mono capitals beneath; hold long enough to read twice (at least 2.5 s).

### 3.15 The finishing stack (over everything)

Order used by several tutors (B): paper and halftone textures, chromatic aberration, vignette, light leak, flicker, then frame stepping on top [S23][S25][S27]. Flicker recipe: a Curves lift on an adjustment layer whose opacity is stepped at 6 fps and wiggled, reading like projected film [S25] (B). Variants add displacement from a paper texture (plus or minus 0.5) and 5% monochrome noise [S27] (B), or vignette, unsharp mask, aberration and an S-curve on maps [S22] (B).

---

## 4. Motion language

### 4.1 Frame stepping ("on twos")

- The most widely taught signature: build graphics at 12 fps inside a 24 fps edit so moves stutter slightly like hand animation [S2][S23][S25][S27] (B). Consistent across independent tutors, but UNVERIFIED by Vox staff.
- 8 fps ("on threes") for a more collage feel [S23]; 6 fps for deliberate jitter [S60]; 10 fps for period maps [S45] (B).
- Motion blur: one tutor says Vox-style work usually leaves it off [S26]; others switch it on [S28][S30] (B). House (H): off for stepped graphics, on for smooth camera travel over live footage.
- House (H): step graphics, type, maps and camera moves over graphics; never step live-action footage or talking heads.

### 4.2 Easing

- Fast start, slow settle: pull the keyframe handle so a move starts quickly and eases into place [S25] (B); bar growth weighted to the start [S31] (B); Circ-type curves [S26] (B).
- Camera travel: ease in and out with the speed peak mid-move [S27] (B); map moves sharpened so they kick [S19] (B).
- House curves (H): entrances cubic-bezier(0.16, 1, 0.3, 1); camera cubic-bezier(0.65, 0, 0.35, 1); exits cubic-bezier(0.7, 0, 0.84, 0), short.

### 4.3 Entrance and exit timings

| Move | Source value | House value at 24 fps |
|---|---|---|
| Text in (fade plus blur) | Opacity 0 and blur 15 resolving over 2 s, keys offset by a third of a second [S25] (B) | 12 to 18 frames (H) |
| Highlight a line | About 1 s [S29] (B) | 12 to 24 frames per line (H) |
| Circle draw | Starts 6 frames in, a little over 1 s [S26] (B) | 12 to 20 frames (H) |
| Hand-drawn line | 2 to 4 s, staggered, tapered [S25] (B) | 12 to 36 frames (H) |
| Bars grow | 1 to 1.5 s, 3-frame stagger [S31] (B) | 18 to 30 frames, 3-frame stagger (H) |
| Axis labels | About 20 frames, 2-frame stagger [S31] (B) | Same (H) |
| Photo card slide | Blur 25 to 0 plus fade [S27] (B) | 10 to 16 frames (H) |
| Pop or slap-in | Scale from 0 with the anchor at an edge [S28]; hold-keyframe jump zooms [S26] (B) | 4 to 8 frames with 5 to 8% overshoot (H) |
| Map highlight | Opacity flicker over a few frames [S19][S22] (B) | 6 to 10 frames (H) |
| Map montage frame | 3 frames per map [S20] (B) | Same (H) |
| Exit | Mostly cut away [S6] (A); routes trim away from their start [S19] (B) | Cut, or a 6 to 8 frame fade (H) |

### 4.4 Camera

- Slow push or pull across a collage, 8 to 12 s per move [S25][S60] (B).
- Over documents: 35 mm, depth of field, focus following the line being read [S29] (B).
- Maps: fly to a place and hold; delayed bearing for an orbit; slight pitch during holds [S3] (A); Earth Studio orbits and spirals [S15] (A); a continuous floating camera over one map [S4] (A).
- Tilt from a low angle to top-down over a map [S22] (B); helicopter-style wiggle [S59] (B).
- House (H): one move per beat; hold still while the voice delivers the key fact; start the move slightly before the sentence so the frame arrives on the key word.

### 4.5 Transitions

- The default is the cut: transitions for their own sake carry no information [S6] (A).
- Tracking transition: a camera push that starts several frames before the cut and continues after it, with a brief blur peaking on the cut [S2] (B).
- Paper or ink luma-matte wipes to reveal layers [S25] (B).
- Match cuts on shape or motion, for example a line crossing a face becoming the next scene's line [S26] (B); sound can sell a match cut [S33] (B).
- Music endings and entrances mark topic shifts [S10] (A); music drop-outs create dramatic pauses and hide music edits [S33] (B).
- House (H): at most one designed transition per act; everything else is a hard cut or a camera move that carries through.

### 4.6 Pacing

- Narration: about 150 wpm on average and about 170 wpm inside sentences [S62] (B).
- Anchors dominate; context bridges stay short and alternate rhythmically with them [S4] (A) [S5] (B).
- Delayed reveal works for science: Fong's black hole video opens on the telescopes (via Google Earth Studio) and shows the actual photo only midway, with a choir under the reveal [S10] (A).
- A hosted format (Glad You Asked) allowed more breathers and emotional moments than dense explainers [S12] (A).
- Return to the opening image at the end so viewers reread it with new knowledge (Phil Edwards) [S43] (A).
- Derived house targets (H): one beat per spoken sentence (5 to 10 s); a new visual event (cut, reveal, annotation or camera move) every 2 to 4 s; 6 to 12 beats per minute; 2 to 4 annotations per minute; a music breath every 60 to 90 s.

### 4.7 Syncing motion to words

- Plan the visual first, then write the sentence that points at it [S4] (A).
- Keep picture and voice simultaneous and matching [S12] (A); cue the essential material (signaling) [S48].
- Editors' advice: lock the voice first, keep it inside the animation project so cues are visible, and storyboard one or two lines per frame [S47] (C).
- Sound effects need not be frame-exact in stepped animation; placing them a few frames early (a J-cut) primes the eye [S24] (B).
- House (H): every reveal is bound to a word from forced alignment and lands 2 to 4 frames before the stressed syllable; highlights sweep while their words are spoken.

---

## 5. Sound

### 5.1 Narration

- Conversational, the producer's own voice, closer to talking to a friend than to broadcast neutrality [S6] (A).
- Pointing phrases ("this is", "look at this") are used, but sparingly: a median of about 2 to 3 regex matches per video in my sample [S62] (B).
- The final voice is recorded during the animation phase [S8] (A); scratch voice goes into early drafts [S43] (A). Harris records in a booth, speaking to visuals he has already planned [S4] (A).
- Rate: see 4.6.

### 5.2 Music

- Fong (2019): Vox Media licenses APM Music; she searches by keyword for tracks with the right minimalism and energy, slices together the sections she likes, fakes endings with reverb tails, and changes music about every 20 s; starts and ends of songs work as attention cues; finding and editing music can take a full day [S10] (A).
- Harris uses big, synth-heavy music to keep fact-dense sections energetic [S4] (A); his channel's music is composed by Tom Fox [S3] (A).
- Caswell says she spends about 70% of her time editing audio [S7] (A).
- Practitioner tip: let the opening question land dry, then start the music; place cuts on the track's rises and falls [S33] (B).

### 5.3 Sound effects

Keep them barely noticeable: better that a viewer misses one than that it covers the voice [S33] (B). Organise the library by family: mechanical, tech, tactile, ambience, whooshes, miscellaneous [S24] (B).

| On screen | Sound (practitioner mapping) |
|---|---|
| Photo or cut-out lands | Camera shutter, relay click, paper movement [S24][S33] (B) |
| Paper or newspaper moves | Paper rustle; a book sliding across a table [S24] (B) |
| Highlighter or underline | Marker; pencil for sketches and arrows [S24][S33] (B) |
| Timeline travel, map montage | Stopwatch tick, sped up [S20][S33] (B) |
| Map marker or dot | Soft bubble pop [S33] (B) |
| Text typing on | Keyboard or typewriter [S33] (B) |
| Websites and windows | Mouse click, laptop keys, cloth for windows collapsing [S24] (B) |
| Camera push or fast chart line | Low whoosh plus a faint tick [S24] (B) |
| Archival film | Projector run or hum [S24][S33] (B) |
| Big reveal | Bell ding, rarely [S33] (B) |

Rules: in a busy frame, sound only the most important motion [S24]; vary repeats by rate or pitch [S24]; avoid cliché samples [S33] (all B).

### 5.4 Mix and delivery

- Practitioner levels: dialogue peaking around -6 dB, music around -20 dB, effects -10 to -20 dB; carve a vocal pocket in the music (about -20 dB in the voice band) [S24] (B).
- YouTube normalises playback to about -14 LUFS and does not turn quieter uploads up [S49]. Upload AAC-LC or Opus at 48 kHz in MP4 with fast start [S50].
- House (H): voice around -16 LUFS short-term; music -26 to -22 LUFS under the voice; duck 6 to 10 dB with 150 to 300 ms attack and release; true peak at or below -1 dBTP; final mix -14 LUFS integrated.

---

## 6. Sub-styles and what each needs

| Sub-style | Example | Visual core | Motion and pace | Sound | Needs |
|---|---|---|---|---|---|
| Animated explainer | Vox channel staple [S14] | Paper canvas, cut-outs, labels, one anchor diagram [S11] | Stepped graphics, 150 to 160 wpm, many small reveals | Library music, new cue every 20 to 40 s [S10] | Script with visual column; asset list |
| Map-led geopolitics | Vox Atlas, Syria explainer [S15][S4] | Master world map, highlights, routes, Earth close-ups | One continuous camera; zoom, hold, label | Low pulses, ticks, whooshes | Verified borders; Natural Earth or custom tiles [S54] |
| Field documentary | Vox Borders [S17] | Walk-and-talk, drone, anchors, then maps | Anchor then bridge; more breaths (1.9 per minute) [S62] | Synth score for energy [S4]; location sound under it (H) | Weeks of pre-reporting, a fixer, appearance releases [S4][S17] |
| Data-led science | Joss Fong [S10][S13] | Clean or printed charts, one repeated diagram | Build step by step; hold on the key number | Minimal music | Clean data; one highlighted series |
| Collage or cut-out | Sendaydiego's construction-paper video [S1] | Real or simulated paper, textures, stutter | 12 or 8 fps stepping, parallax | Paper, shutter, relay | Scanned textures; unified photo grade |
| Archival and photo forensic | Vox Darkroom, Missing Chapter [S63] | One photograph examined: zooms, circles, comparisons | Slow push, hold, annotate | Projector, room tone | Archive licences, fair-use review [S4][S6] |
| Music explainer | Earworm [S9] | Beat breakdowns, vinyl, magazines, handwriting | Cut on the beat; stepped graphics | Songs as evidence; heavy audio editing [S7] | Legal review of clips [S6] |
| Video essay | Every Frame a Painting [S55] | Clips plus voice, few graphics | Rhythm set by clip editing | Audio reworked to fit fair use [S55] | Thesis script; clip-rights strategy [S55] |
| Kinetic type | Flying-text motif in an AI video [S1] | Type as image, highlights | Word-synced, stepped | Tight effects per word group | Forced alignment of the voice |
| Rapid response | Fong's black hole video, published about an hour after the announcement [S10] | Pre-built map and chart kits | Short, dense | Library cues | Templates ready before the news |

---

## 7. What makes it look amateur, and the professional fix

1. **Too polished** (silky 60 fps glides, perfect vectors): reads as an ad [S1] (A). Fix: textures, stepping, rough edges [S23] (B).
2. **Decorative transitions** that carry no information [S6] (A). Fix: cut, and spend the time finding evidence.
3. **Narration over generic b-roll or stock** [S14] (A). Fix: a visual anchor for every claim [S4] (A).
4. **Evidence arrives late** after long context [S4] (A) [S5] (B). Fix: open on the strongest anchor within seconds.
5. **Texture and aberration cranked** until they look fake [S23][S27] (B). Fix: halftone 10 to 20%, aberration about 1 px.
6. **Pure white backgrounds** [S23] (B). Fix: a warm paper tone.
7. **Raw archival of mixed quality** [S23] (B). Fix: one homogenising treatment.
8. **Everything animating at once** [S25] (B). Fix: stagger so one new thing appears at a time.
9. **Sound on every motion, cliché samples, music fighting the voice** [S24][S33] (B). Fix: hierarchy, restraint, ducking.
10. **Heavy-handed music and indulgent shots.** Harris's story editor pushes back on exactly this [S4] (A). Fix: an editor with no attachment to the footage.
11. **Cluttered maps** with default labels, roads and admin lines [S3][S19]. Fix: strip the base map.
12. **Factual or map errors** [S21] (B). Fix: a source column and a red-to-green check on every assertion [S4] (A).
13. **Full sentences on screen repeating the voice** [S48]. Fix: keywords and numbers only.
14. **One music bed for ten minutes** [S10] (A). Fix: change or edit music at topic turns.
15. **Stepping live-action footage or talking heads** (H). Fix: step graphics only.
16. **Holds with nothing new, or cuts faster than the voice** (H, from 4.6). Fix: one visual event every 2 to 4 s, tied to words.

---

## 8. Building it in Remotion (notes, not code)

### 8.1 Architecture

- Treat the script as data: each beat holds its voice text, word ids, visual type, assets, annotations and sound effects. Drive every reveal from word timestamps (H).
- `@remotion/install-whisper-cpp`: `transcribe()` with `tokenLevelTimestamps: true`, then `toCaptions()`, returns Caption objects with `startMs` and `endMs` per token; convert with `frame = Math.round(startMs / 1000 * fps)` [S51c].
- Composition 1920x1080 at 24 fps; one `Sequence` per beat; `TransitionSeries` only where a designed transition is wanted [S51b].

### 8.2 Time stepping and determinism

- `const stepped = Math.floor(frame / 2) * 2` gives 12 fps motion at 24 fps; feed it to `interpolate` and `spring` for graphics, and keep the raw frame for live footage (H).
- Seeded randomness only: Remotion's `random(seed)` returns the same value for the same seed [S51d]; `noise2D` and `noise3D` from `@remotion/noise` return values between -1 and 1 for a seed and coordinates [S51a]. Seed with element id plus the stepped frame so boil and jitter render identically every time (H).

### 8.3 Paper, grain, boil, finish

- Paper: full-frame scanned JPGs as `Img` layers with CSS `mix-blend-mode: multiply` or `screen` (H).
- Grain: an SVG `feTurbulence` (type fractalNoise, high baseFrequency, two octaves) whose `seed` changes every stepped frame, blended at 4 to 8% [S52b] (values H).
- Boil: cycle six texture images with `Math.floor(frame / 10) % 6` at 24 fps, which matches two to three swaps a second [S2] (mapping H).
- Vignette: a radial-gradient overlay; edge blur from a masked, blurred duplicate (H).
- Aberration: red and blue copies isolated with `feColorMatrix`, offset about 1 px, Screen-blended (H).
- Flicker: `brightness(1 + 0.03 * noise)` updated at 6 fps (H, after [S25]).

### 8.4 Cut-outs, keylines, shadows, torn edges, tape

- Sticker keyline: SVG `feMorphology` with operator dilate (radius 6 to 10) on the alpha, flooded with paper white and placed under the image; then a soft shadow (`feDropShadow` or a blurred offset copy) [S52a] (values H).
- Scissor-cut or torn edge: `feTurbulence` feeding `feDisplacementMap` (scale 3 to 8) applied to the alpha only, so the photo itself does not warp; displacement follows the channel formula documented on MDN [S52b][S52c] (values H). For tears, a `clip-path` polygon whose edge points are pushed by `noise2D`, plus a thin pale fibre edge from a dilated copy (H).
- Tape: a translucent pale-yellow rectangle (55 to 75% opacity, Multiply) with zigzag `clip-path` ends, rotated 2 to 8 degrees (H).

### 8.5 Halftone

- Pre-process once per image, not per frame: greyscale, then a dot grid rotated 45 degrees where dot area follows darkness (radius = cell / 2 * sqrt(1 - luminance)), cell 6 to 10 px at 1080p; cache as PNG in a pre-render step (H). Canvas 2D or WebGL both work.

### 8.6 Annotations

- Draw-on: `evolvePath(progress, path)` from `@remotion/paths` returns `strokeDasharray` and `strokeDashoffset` for any SVG path [S51e].
- Hand-made feel: nudge control points 1 to 3 px with `noise2D` every stepped frame (H).
- Highlighter over live text: wrap words in spans and grow a `linear-gradient` background from 0 to 100% width with `mix-blend-mode: multiply`; over images, use a thick round-cap SVG stroke (H).

### 8.7 Camera and parallax

- Either CSS `perspective` with `translateZ` per layer, or manual parallax (`x = camX * depthFactor` with scale compensation); animate a single camera object with eased keys (H).
- Depth of field: blur far layers and ease it as focus shifts (H).

### 8.8 Maps

- d3-geo projection plus Natural Earth or world-atlas TopoJSON; `fitExtent` to frame a region; animate `center`, `scale` and `rotate` per frame [S53][S54].
- Borders: country outlines from `geoPath`, drawn with `evolvePath` [S51e]; fills fade or wipe through a clip mask (H).
- Routes: a dashed stroke inside a mask that is itself drawn with `evolvePath`, so the dashes stay put while the route grows (H).
- Labels: positioned with `projection([lon, lat])`; scale with zoom up to a cap; capitals and tracking for countries (H).
- Satellite and 3D: Google Earth Studio exports image sequences plus tracking data; Boone's pipeline turns the track points into an After Effects camera and label nulls [S18] (B). In Remotion, play the sequence and place labels from exported screen positions (H). Check Earth Studio's attribution terms before client use (UNVERIFIED here).

### 8.9 Charts, timelines, counters

- SVG plus d3 scales; bars grow from the baseline with a 3-frame stagger; labels slide in over about 20 frames [S31] (B).
- Counters: `interpolate` with ease-out, `Math.round`, `Intl.NumberFormat`, CSS `font-variant-numeric: tabular-nums`, stepped at 12 fps (H).

### 8.10 Transitions

- `@remotion/transitions`: `TransitionSeries` with built-in presentations (for example slide, clockWipe, iris) and timings (`linearTiming`, `springTiming`), plus custom presentations for paper or ink luma wipes [S51b].
- Tracking transition: move the camera across the cut and add a blur that peaks on the cut frame (H, after [S2]).

### 8.11 Audio

- `Audio` accepts a per-frame volume callback; use it to duck music under the voice [S51f].
- Place effects in Sequences 2 to 4 frames before their visual event (H, after [S24]).
- Normalise the final mix to -14 LUFS integrated with a two-pass loudness filter (H; target from [S49]).

### 8.12 Delivery and performance

- 1080p24, BT.709, AAC 48 kHz, MP4 with fast start, about 8 Mbps for 1080p SDR [S50].
- Full-frame SVG filters are slow: pre-render textures, halftones and heavy filter passes (H).

### 8.13 Component inventory for the tool (H)

Build these once, each driven by props and word cues:

| Component | Does | Bible section |
|---|---|---|
| `PaperCanvas` | Base tone, paper plate, halftone, grain, boil | 3.1 |
| `FinishStack` | Aberration, vignette, edge blur, flicker, stepping | 3.15, 4.1 |
| `CameraRig` | 2.5D layers, eased push, pan, wiggle, depth of field | 3.6, 4.4 |
| `CutoutPhoto` | Mask, keyline, shadow, tint, halftone, stutter set | 3.4 |
| `ArchivalClip` and `ScreenGrab` | Homogenised footage; screen treatment | 3.7 |
| `DocumentPage` and `QuoteCard` | Page move, zoom to line, highlight, citation | 3.8 |
| `Highlighter`, `DrawOn`, `Arrow`, `Circle` | Annotations bound to words | 3.9 |
| `MapScene` | Projection, fly-to, borders, fills, routes, pins, labels | 3.10 |
| `BarChart`, `LineChart` | Axes, staggered growth, highlight band, source line | 3.11 |
| `Timeline` | Spine, date boxes, photo cards, camera steps | 3.12 |
| `Counter` | Stepped count-up with tabular numerals | 3.13 |
| `LowerThird`, `SourceLine` | Jagged reveal names; citations | 3.14 |
| `SfxCue` | Sound placed a few frames before its visual | 5.3, 4.7 |

---

## 9. Open questions and unverified items

- The exact on-screen typefaces in 2024 to 2026 Vox videos (Balto Medium is a community identification) [S36].
- Whether Vox animators literally work at 12 fps; the claim is practitioner consensus [S2][S23].
- Keyline and shadow specifications for Vox cut-outs; torn paper, tape and stamps as Vox staples [S56][S58].
- Shot length, holds and visual changes per second: not measured (no downloads). A frame-level pass over five to ten Vox videos would settle cut rate, hold length and palette.
- Today's music library: APM is confirmed for 2019 [S10].

---

## 10. Checklist

**Pre-production**

- [ ] The story is visual; every claim has a visual anchor [S14][S4].
- [ ] Three-column script: voice, visual, source; red until sourced, green when checked [S4].
- [ ] One anchor visual or motif for the whole piece [S11][S1].
- [ ] Opening promise inside 10 to 15 s, strongest anchors first [S4].
- [ ] Script timed at 150 to 160 wpm [S4][S62].
- [ ] Palette chosen: paper, ink, yellow marker, one topic colour; fonts licensed or fallbacks picked.

**Visual**

- [ ] No pure white; paper texture; halftone 10 to 20%; grain 4 to 8%.
- [ ] Photos unified (black and white or sepia plus one tint), irregular masks, soft faint shadows.
- [ ] Archival and screens homogenised; screens look like screens.
- [ ] Maps stripped of clutter; borders, labels and routes verified; projection chosen on purpose.
- [ ] Charts: baseline, direct labels, one highlighted series, source line.
- [ ] On-screen text limited to keywords, names and numbers; nothing under 28 px at 1080p.

**Motion**

- [ ] Graphics stepped at 12 fps; live footage not stepped.
- [ ] Entrances fast-in, slow-settle, staggered; one new thing at a time.
- [ ] One camera move per beat; holds on the key facts.
- [ ] Cuts by default; at most one designed transition per act.
- [ ] Every reveal tied to a word timestamp, landing 2 to 4 frames early.
- [ ] A new visual event every 2 to 4 s; 6 to 12 beats per minute.

**Sound**

- [ ] Voice clean, conversational, about 150 wpm.
- [ ] Music edited to the story; cue changes every 20 to 40 s; breaths at act turns.
- [ ] Effects only on the most important motion; varied; slightly early.
- [ ] Voice on top, music ducked 6 to 10 dB; final -14 LUFS integrated, true peak at or below -1 dBTP.

**QA and delivery**

- [ ] Fact-check pass on every number, date, border and name.
- [ ] Licence or fair-use note for every archival clip and song.
- [ ] Sources on screen where each claim appears and in the description.
- [ ] 1080p24, BT.709, MP4, AAC 48 kHz; captions uploaded as a file, not burned in.

---

## Appendix A: measurement method and data

Method (2026-09-25): for each video I read the public YouTube watch page and the Innertube player response (Android client) for title, date, length, frame rate and the English caption track (manual captions in all cases), then computed words per minute over the full runtime and over captioned speech time (overlapping spans merged), the onset of the first spoken caption, and gaps of at least 1.5 s between non-empty captions. Pointing phrases were counted with a regex for "look at", "this is", "here's", "here is", "right here", "see this", "take a look", "notice".

Caveats: manual captions include interview soundbites and some lyrics; caption display durations can overlap real pauses, so gap counts are approximate; the reported maximum resolution may be capped by the client used. The Earworm rap video was excluded from the gap analysis because of its lyric captions.

| Video ID | Published | Title (short) | Length (s) | Words | wpm (runtime) | wpm (speech) |
|---|---|---|---|---|---|---|
| cUBg6Qp_N98 | 2019-08-22 | US and Iran over a tiny waterway | 563 | 1334 | 142 | 153 |
| JFpanWNgfQY | 2017-04-07 | Syria's war: who is fighting and why | 406 | 1027 | 152 | 170 |
| pAoEHR4aW8I | 2019-04-10 | Why this black hole photo is a big deal | 388 | 1054 | 163 | 183 |
| QWveXdj6oZU | 2016-05-19 | Rapping, deconstructed | 763 | 1322 | 104 | 168 |
| 4WvKeYuwifc | 2017-10-17 | Divided island (Borders) | 952 | 2095 | 132 | 194 |
| _c7AuSQdvow | 2019-07-02 | Why Iraq's great rivers are dying (Atlas) | 596 | 1442 | 145 | 172 |
| 5HRU5yonyK8 | 2019-05-31 | This photo almost started a nuclear war (Darkroom) | 343 | 910 | 159 | 164 |
| 3tEn0hfVkeA | 2025-12-31 | 2025, in 8 minutes | 515 | 1167 | 136 | 154 |
| 2XkV-AMhBvo | 2025-01-10 | Should fluoride be in our water? | 612 | 1643 | 161 | 186 |
| UGqWRyBCHhw | 2019-10-14 | How the US stole Native American children (Missing Chapter) | 821 | 1802 | 132 | 143 |
| iRYZjOuUnlU | 2016-01-20 | Israel-Palestine: a brief, simple history | 619 | 1619 | 157 | 172 |
| lv1SpwwJEW8 | 2023-10-27 | Gaza, explained | 951 | 2108 | 133 | 170 |
| 62tIvfP9A2w | 2018-11-12 | The most feared song in jazz (Earworm) | 649 | 1664 | 154 | 188 |
| Bxz6jShW-3E | 2017-08-18 | A recording-studio mishap shaped 80s music (Earworm) | 509 | 1231 | 145 | 147 |
| tWcV94G4rRI | 2019-02-08 | Cocaine and the migrant crisis (Atlas) | 396 | 987 | 150 | 153 |
| g9bkQ7OiEdQ | 2019-03-01 | How the Hindenburg killed an industry (Darkroom) | 349 | 886 | 152 | 171 |

Summary: median wpm 148 (runtime) and 170 (speech). Onset median 1.9 s (15 videos). Gaps of 1.5 s or more: median 0.75 per minute, median 3.2 s, 90th percentile about 11 s (15 videos). Frame rate: 24 fps for all of the above plus gK6MD_8S01o ("How Trump's second term will be different") and Johnny Harris's GsojLuJpe_0.

---

## Appendix B: default parameter sheet (1920x1080, 24 fps)

All values are house defaults (H) distilled from the sections named; tune by eye per story.

| Area | Default | From |
|---|---|---|
| Frame rate and stepping | 24 fps master; graphics stepped every 2 frames (12 fps); 3-frame steps for heavy collage; live footage unstepped | 2, 4.1 |
| Base colours | Paper #F2EEE6; ink #131313; marker #FFF200 in Multiply; one topic colour; red only for harm | 3.2 |
| Textures | Paper plate 25 to 40% Multiply; halftone 12 to 20%; mono grain 4 to 8% re-seeded per step; six-plate boil, swap every 8 to 12 frames | 3.1 |
| Finish | Aberration 0.5 to 1 px (1 to 2 px on archive); vignette 10 to 20%; flicker about 3% at 6 fps | 3.1, 3.15 |
| Cut-outs | Irregular mask; keyline 6 to 10 px; shadow y 8 to 16 px, blur 24 to 48 px, 15 to 25% black; tilt 1 to 4 degrees | 3.4 |
| Type | Gothic sans Medium or Bold for labels (36 to 56 px) and headlines (72 to 120 px); serif for quotes; mono caps +0.1 em for kickers and sources (22 to 28 px); nothing essential under 28 px | 3.3 |
| Strokes | 8 to 14 px; circles 12 to 20 frames; underlines 8 to 14; highlights 12 to 24 per line | 3.9 |
| Entrances | Text 12 to 18 frames; pops 4 to 8 frames with 5 to 8% overshoot; cards 10 to 16 frames; bars 18 to 30 frames with 3-frame stagger | 4.3 |
| Easing | Enter cubic-bezier(0.16, 1, 0.3, 1); camera cubic-bezier(0.65, 0, 0.35, 1); exit cubic-bezier(0.7, 0, 0.84, 0) | 4.2 |
| Camera | One move per beat; collage push 8 to 12 s; map travel 4 to 7 s then a 3 to 4 s labelled hold | 4.4, 3.10 |
| Pace | 150 to 160 wpm; new visual event every 2 to 4 s; 6 to 12 beats per minute; 2 to 4 annotations per minute; music breath every 60 to 90 s; music cue every 20 to 40 s | 2, 4.6 |
| Sync | Reveals land 2 to 4 frames before the stressed syllable; sound effects 2 to 4 frames early | 4.7, 5.3 |
| Mix | Voice about -16 LUFS short-term; music -26 to -22 LUFS under voice; 6 to 10 dB duck; master -14 LUFS integrated, true peak -1 dBTP or lower | 5.4 |
| Delivery | 1080p24, BT.709, MP4 fast start, AAC 48 kHz, about 8 Mbps; captions as a file | 8.12, 3.14 |

---

## Sources (all accessed 2026-09-25)

- [S1] Storybench, Q&A with Vox art director Joey Sendaydiego, "How Vox uses animation to make complicated topics digestible for everyone". https://www.storybench.org/how-vox-uses-animation-to-make-complicated-topics-digestible-for-everyone/ (accessed 2026-09-25)
- [S2] Lewis McGregor, PremiumBeat, "5 Breakdowns on Replicating the VOX Motion Graphic Look", 2021-03-08. https://www.premiumbeat.com/blog/replicating-vox-motion-graphic/ (accessed 2026-09-25)
- [S3] Johnny Harris, "How I Make My Maps", YouTube, 2020-12-11 (transcript and description read). https://www.youtube.com/watch?v=GsojLuJpe_0 (accessed 2026-09-25)
- [S4] Johnny Harris (then Vox), workshop "The Power of Visuals", Jerusalem Press Club, published 2019-07-08 (full transcript read). https://www.youtube.com/watch?v=lRq6rIiGFAU (accessed 2026-09-25)
- [S5] David Mora, "Why every Johnny Harris video goes viral", YouTube, 2022-03-05 (transcript and description read). https://www.youtube.com/watch?v=dIKsEhX-vyU (accessed 2026-09-25)
- [S6] School of Motion, "Vox Earworm Storytelling: A Chat with Estelle Caswell" (podcast page and transcript). https://schoolofmotion.com/blog/estelle-caswell-vox-podcast (accessed 2026-09-25)
- [S7] Uses This, interview with Estelle Caswell, 2018-12-04. https://usesthis.com/interviews/estelle.caswell/ (accessed 2026-09-25)
- [S8] Film Independent, "Explainer: An Interview with Vox Pop Video Essayist Estelle Caswell". https://www.filmindependent.org/blog/explainer-an-interview-with-vox-pop-video-essayist-estelle-caswell/ (accessed 2026-09-25)
- [S9] TNW, "Vox' Estelle Caswell on creating Earworm", 2019-05-21 (transcript read). https://www.youtube.com/watch?v=aPwi5rNKpMk (accessed 2026-09-25)
- [S10] The Open Notebook, "Videogram: How a Vox Video Explains the Science behind the First Photo of a Black Hole", 2020-01-07. https://www.theopennotebook.com/2020/01/07/videogram-how-a-vox-video-explains-the-science-behind-the-first-photo-of-a-black-hole/ (accessed 2026-09-25)
- [S11] "Production Process - Joss Fong | KC Highlight", clip from NYU's 2019 "Vidsplaining" event (transcript read). https://www.youtube.com/watch?v=Zk1hePS5J5I (accessed 2026-09-25)
- [S12] Video Consortium, "Episode 1: Joss Fong". https://videoconsortium.org/mag/episode-1-joss-fong (accessed 2026-09-25)
- [S13] Storybench, "Learning for a Living: Howtown's Joss Fong...". https://www.storybench.org/learning-for-a-living-howtowns-joss-fong-is-on-a-mission-to-reinvent-science-explainer-videos/ (accessed 2026-09-25)
- [S14] Simon Owens, The Long Story, "Why the best journalists on YouTube are all former Vox employees", 2025-06-03. https://thelongstory.substack.com/p/why-the-best-journalists-on-youtube (accessed 2026-09-25)
- [S15] Google Earth (Medium), "How Vox Video uses Earth Studio for dynamic visual storytelling", interview with Sam Ellis. Read via an Internet Archive snapshot because Medium blocked direct access. https://medium.com/google-earth/how-vox-video-uses-earth-studio-for-dynamic-visual-storytelling-703fc871766e (accessed 2026-09-25)
- [S16] Storybench, "Vox Atlas: Producer Sam Ellis on his distinctive map animations". https://www.storybench.org/vox-atlas-producer-sam-ellis-on-his-map-animations/ (accessed 2026-09-25)
- [S17] Storybench, "Behind the scenes of the Vox web series Borders". https://www.storybench.org/behind-the-scenes-of-the-vox-web-series-borders/ (accessed 2026-09-25)
- [S18] Jason Boone, PremiumBeat, "How I Got a Gig Making Maps for Johnny Harris". https://www.premiumbeat.com/blog/making-maps-for-johnny-harris/ (accessed 2026-09-25)
- [S19] Boone Loves Video (Jason Boone), "Make Maps Like VOX in Adobe After Effects - Strait of Hormuz", 2021-02-15 (transcript read; recreates Vox video cUBg6Qp_N98). https://www.youtube.com/watch?v=yj-yi7mdwNI (accessed 2026-09-25)
- [S20] Boone Loves Video, "Create a Johnny Harris Style Animated Map Montage", 2026-06-01 (transcript read). https://www.youtube.com/watch?v=wfgMiZDTvxE (accessed 2026-09-25)
- [S21] Minds Behind Maps, "Visual Effects with Maps, Working with Johnny Harris... - Jason Boone MBM56" (transcript read). https://www.youtube.com/watch?v=TOPsRdJgBhc (accessed 2026-09-25)
- [S22] Flat Pack FX, "Johnny Harris Style Map Animation - After Effects", 2025-03-17 (transcript read). https://www.youtube.com/watch?v=QU0tdH-dlIA (accessed 2026-09-25)
- [S23] Chris Moran, "How VOX breaks the Digital Feel with Motion Graphics", 2026-01-17 (transcript read). https://www.youtube.com/watch?v=sACZlG7z35Q (accessed 2026-09-25)
- [S24] Chris Moran, "The VOX Sound Design System", 2026-02-07 (transcript read). https://www.youtube.com/watch?v=UgVgzSZVu-8 (accessed 2026-09-25)
- [S25] createdaley, "How To Edit VOX Style like a PRO (After Effects Tutorial)", 2026-03-02 (transcript and description read). https://www.youtube.com/watch?v=5eVyoHFzBEY (accessed 2026-09-25)
- [S26] createdaley, "Animate Collages Like Vox, Part 2" (2025-02-17) and "Part 3" (2025-02-24) (transcripts read). https://www.youtube.com/watch?v=GUybR6jSbbY and https://www.youtube.com/watch?v=AbFmCpfGmus (accessed 2026-09-25)
- [S27] Editing Snapped, "How VOX Makes Documentary Timelines (After Effects Tutorial)", 2026-07-01 (transcript read). https://www.youtube.com/watch?v=W-W6UItToJw (accessed 2026-09-25)
- [S28] Flat Pack FX, "Create VOX Style Collage Animation", 2024-07-08 (transcript read). https://www.youtube.com/watch?v=V_x5e5wsZ4Q (accessed 2026-09-25)
- [S29] Flat Pack FX, "How to Create Vox Highlighter Effect", 2019-07-15 (transcript read). https://www.youtube.com/watch?v=a0T3kcizcOY (accessed 2026-09-25)
- [S30] Robel Muhammed, "Vox-Style Documentary Text Highlight Animation in After Effects", 2025-07-29 (transcript read). https://www.youtube.com/watch?v=xW7RLiJBNcU (accessed 2026-09-25)
- [S31] Marius, "How to make animated charts like Vox in After Effects", 2023-11-12 (transcript read). https://www.youtube.com/watch?v=61vR3DHV8Eg (accessed 2026-09-25)
- [S32] Flat Pack FX, "UNIQUE Vox Style Graph Animation", 2025-03-04 (transcript read). https://www.youtube.com/watch?v=-rAcCCnwixI (accessed 2026-09-25)
- [S33] Lilly's Tech Tips, "How to SOUND DESIGN your Documentary - Vox Style", 2025-05-07 (transcript read). https://www.youtube.com/watch?v=pVRW1GGTNZc (accessed 2026-09-25)
- [S34] viewinder, "Film School: The Motion Design of Vox". https://viewinder.com/vox-motion-design/ (accessed 2026-09-25)
- [S35] Fonts In Use, "Vox website" (2014). https://fontsinuse.com/uses/6828/vox-website (accessed 2026-09-25)
- [S36] dafont forum thread identifying Balto Medium in a Vox video. https://www.dafont.com/forum/read/437583/what-is-this-font?highlight=937956 (accessed 2026-09-25)
- [S37] vox.com homepage HTML and CSS, inspected for colour and font declarations (#fff200; --font-balto, --font-harriet, --font-roboto-mono). https://www.vox.com/ (accessed 2026-09-25)
- [S38] shadcn.io, "Vox Design System" (third-party token extraction of vox.com). https://www.shadcn.io/design/vox (accessed 2026-09-25)
- [S39] Typographica, "Balto" review, and Typewolf, "Balto". https://typographica.org/typeface-reviews/balto/ and https://www.typewolf.com/balto (accessed 2026-09-25)
- [S40] Okay Type, "Harriet". https://okaytype.com/harriet (accessed 2026-09-25)
- [S41] John McColgan, "Vox Explained, Season 1" (portfolio). https://www.mcmotion.art/vox-explained (accessed 2026-09-25)
- [S42] Jasper Pictures, "Analyzing Vox' Explained: A Video Content Case Study". https://jasperpictures.com.au/blog/vox-explained-a-case-study/ (accessed 2026-09-25)
- [S43] Brendan Miller, "Phil Edwards of Vox talks explainers". https://brendanmiller.co.uk/phil-edwards-of-vox-talks-explainers/ (accessed 2026-09-25)
- [S44] The Explainers, "Making the trivial nontrivial: How Phil Edwards makes attention-getting videos". https://theexplainers.substack.com/p/making-the-trivialnontrivial-how (accessed 2026-09-25)
- [S45] No Film School, "How to Create Vox Style Maps in Adobe After Effects". https://nofilmschool.com/how-create-vox-style-map-animations-after-effects (accessed 2026-09-25)
- [S46] Adobe Community thread, "How does Johnny Harris do this mask reveal animation in After Effects?" https://community.adobe.com/questions-529/how-does-johnny-harris-do-this-mask-reveal-animation-in-after-effects-59396 (accessed 2026-09-25)
- [S47] Reddit r/motiongraphics, "Vox Editting Style" (2019), post and comments retrieved through the PullPush archive API because reddit.com blocked access. https://www.reddit.com/r/motiongraphics/comments/b5ei72/vox_editting_style/ (accessed 2026-09-25)
- [S48] Devlin Peck, "Mayer's 12 Principles of Multimedia Learning" (summarising Mayer, Multimedia Learning, 3rd ed., Cambridge University Press, 2021). https://www.devlinpeck.com/content/mayers-principles-of-multimedia-learning (accessed 2026-09-25)
- [S49] MeterPlugs, "YouTube Changes Loudness Reference to -14 LUFS", 2019-09-18. https://www.meterplugs.com/blog/2019/09/18/youtube-changes-loudness-reference-to-14-lufs.html (accessed 2026-09-25)
- [S50] YouTube Help, "Recommended upload encoding settings". https://support.google.com/youtube/answer/1722171?hl=en (accessed 2026-09-25)
- [S51] Remotion documentation (accessed 2026-09-25): (a) noise2D https://www.remotion.dev/docs/noise/noise-2d ; (b) transitions, presentations and timings https://www.remotion.dev/docs/transitions/presentations and https://www.remotion.dev/docs/transitions/presentations/clock-wipe and https://www.remotion.dev/docs/transitions/timings/springtiming ; (c) toCaptions https://www.remotion.dev/docs/install-whisper-cpp/to-captions ; (d) random https://www.remotion.dev/docs/random ; (e) evolvePath https://www.remotion.dev/docs/paths/evolve-path ; (f) audio volume https://www.remotion.dev/docs/audio/volume
- [S52] MDN Web Docs (accessed 2026-09-25): (a) feMorphology https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/feMorphology ; (b) feTurbulence https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/feTurbulence ; (c) feDisplacementMap https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/feDisplacementMap
- [S53] d3-geo, "Projections". https://d3js.org/d3-geo/projection (accessed 2026-09-25)
- [S54] Natural Earth, "Terms of use" (public domain). https://www.naturalearthdata.com/about/terms-of-use/ (accessed 2026-09-25)
- [S55] Wikipedia, "Every Frame a Painting". https://en.wikipedia.org/wiki/Every_Frame_a_Painting (accessed 2026-09-25)
- [S56] FCPX Full Access, "How to Get the Vox / Johnny Harris Documentary Style in Final Cut Pro" (secondary). https://fcpxfullaccess.com/blogs/blog/vox-johnny-harris-documentary-style-final-cut-pro (accessed 2026-09-25)
- [S57] DEmotion blog, "Why Your Motion Graphics Never Look Like Vox" (secondary). https://trydemotion.com/blog/motion-graphics-like-vox (accessed 2026-09-25)
- [S58] Third-party AI style packs (secondary): Cele-san, "vox-style-animation" (cream paper, halftone dots, heavy ink type, one yellow highlighter, hand-drawn annotations, paper slap-ins) https://github.com/Cele-san/vox-style-animation ; Alisa0808, "vox-director" (torn edges, tape, halftone, clippings; seen in search results only) https://github.com/Alisa0808/vox-director (accessed 2026-09-25)
- [S59] ilkin, "Create a Vox Style Collage Animation in 5 Minutes", 2026-08-30 (transcript read). https://www.youtube.com/watch?v=gkslh4m3PGA (accessed 2026-09-25)
- [S60] Motion Nations, "Vox Style Documentary Opener Animation in After Effects | 3D Parallax Effect", 2026-07-04 (transcript read). https://www.youtube.com/watch?v=IJTewZ7lIGM (accessed 2026-09-25)
- [S61] Adobe Fonts, "Balto" (Type Supply). https://fonts.adobe.com/fonts/balto (accessed 2026-09-25)
- [S62] My measurements from public YouTube metadata and caption tracks, method and data in Appendix A. Video pages: https://www.youtube.com/watch?v= followed by each ID in the table, plus gK6MD_8S01o and GsojLuJpe_0 (accessed 2026-09-25)
- [S63] Vox YouTube descriptions (accessed 2026-09-25): Borders credits (producer Christina Thornell, story editor Joss Fong, animation Sam Ellis, executive producer Joe Posner) https://www.youtube.com/watch?v=4WvKeYuwifc ; Darkroom series line (stories of the past, one photograph at a time) https://www.youtube.com/watch?v=5HRU5yonyK8 ; Missing Chapter series line (overlooked moments from the past) https://www.youtube.com/watch?v=UGqWRyBCHhw ; Vox Atlas series line (conflicts shown on a map) https://www.youtube.com/watch?v=_c7AuSQdvow ; Gaza explainer source spreadsheet link https://www.youtube.com/watch?v=lv1SpwwJEW8
- [S64] Bright Trip, "Visual Storytelling" course page (Johnny Harris organises footage and builds the story structure first, then adds b-roll). https://www.brighttrip.com/courses/visual-storytelling (accessed 2026-09-25)
