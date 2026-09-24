# R8: GPT Image 2.5 — region editing, references, typography, sizes and access paths

Prepared 2026-09-23 for the NexaLance "single-prompt, full-capability" design route on `gpt-image-2.5-sunburst` / `gpt-image-2.5-flare` (snapshots 2026-09-08).

**Relation to earlier notes.** This note extends `design-research/R3-gpt-image-design-prompting.md` (R3) and `~/.claude/skills/codex-imagegen/references/master.md` §3 and §9. It does not repeat what R3 already verified: the size constraints, the quality→token ladder, the four-size cost table, the official exact-text rules and the edit/outpaint recipes. Where this note corrects R3 or master.md, the correction is listed in §C.

**Evidence tags.** Every claim carries a tag and a source number [n] that resolves in the Sources list at the end. All web sources were accessed on 2026-09-23.

| Tag | Meaning |
|---|---|
| OFF | Official OpenAI documentation, announcement, model page, API reference or an OpenAI staff/support reply |
| SRC | Source code we read ourselves (file and commit cited) |
| COM | Community report (forum, GitHub issue, HN, practitioner blog). Anecdotal |
| VEN | Vendor or marketing blog. Numbers not reproducible by us |
| DER | Our own derivation from the cited inputs |
| **UNVERIFIED** | Could not be confirmed. Do not hard-code a rule on it |

---

## Summary: 12 findings that change our design

1. **No API has pins, comments, boxes, sketches or templates.** The only spatial control in the API is an alpha mask applied to the first input image (`mask` on `/v1/images/edits`, `input_image_mask` on the Responses tool). OpenAI calls it prompt-based guidance [1][4][6] OFF. ChatGPT's Select, Comment, Markup, Erase, Sketch and Templates are UI features, and how they reach the model is undocumented [13][15] OFF / UNVERIFIED. **Design change:** we build our own "comment layer". Each click or box becomes region words plus percent coordinates in the prompt, an alpha mask made from the same coordinates, an optional guide image, a crop window when the target is small, and a deterministic composite back. A practitioner who built exactly this on the 2.5 API reports the same conclusion [35] COM.
2. **The Codex route cannot be turned into a 2.5 route.**
   - Source (SRC): `IMAGE_MODEL = "gpt-image-2"` is still hard-coded in `codex-rs/ext/image-generation/src/tool.rs` in stable 0.156.1, in pre-release 0.158.0-alpha.2 and on main at `8f1490eab` (2026-09-23). The quality enum has no `xhigh`/`max`, the edit request has no mask field, and the tool takes at most 5 references [22][23].
   - Backend (COM): the ChatGPT/Codex endpoints overwrite the model, size and quality a client sends. The hosted tool echoes `gpt-image-2-codex`, and deliberately invalid model ids still return HTTP 200 [29][33][34].
   - **Design change:** Sunburst or Flare selection, `xhigh`/`max`, masks and exact sizes exist only on the API (or Higgsfield, §6.5). Treat every Codex output as an unknown 2.x model at about 1.57 MP.
3. **Preservation outside the edit is much better on 2.5, but never exact.**
   - Flare, one prompt-only edit: 0.22 % of pixels outside the edit box changed, with face SSIM 0.889 [42] COM.
   - Three chained edits drift 9–10 %, against 11.4 % on gpt-image-2 [45] VEN.
   - On gpt-image-2, tiny regions are over-edited 50–1,400× their area [53].
   - OpenAI still says: composite any region that must stay pixel-identical [2] OFF.
   - **Design change:** composite-back stays mandatory. Small targets are edited in a crop window.
4. **The editor sees a downsampled copy of every input.** Inputs to `/v1/images/edits` are budgeted to about 1,536 patches of 32 px; a 1248×1248 image uses 1,521 tokens, so sending a larger file adds no detail [21] COM. **Design change:** small text, fingers and logo marks in a big design are low-resolution to the editor. Fix them by cropping a window of 1.5 MP or less around the target, editing it and pasting it back [35][36] COM.
5. **Annotated-image editing works as a hint, not a guarantee.** No success rate is published for gpt-image-2 or 2.5.
   - OpenAI's own `hatch-pet` skill tells the model "do not draw the guide", yet its QA still rejects outputs with "copied guide marks" [27] OFF/SRC.
   - Vendors report arrows rendered as physical objects and annotation colour bleeding into the output [48] VEN.
   - Numeric coordinates are weakly followed: gpt-image-2 scores 17.5 % mIoU or lower on position-exact geometric edits [53].
   - **Design change:** send the clean original as Image 1 and the marked-up copy as Image 2, add a mask built from the same coordinates, and always composite.
6. **Quality labels were remapped; do not port `high` from gpt-image-2 configs.**
   - 2.5 `high` spends the tokens gpt-image-2 spent on `medium`; 2.5 `max` equals gpt-image-2 `high` [21] COM, [44][45] VEN. R3 §1.3 has the table.
   - **Design change:** for text-heavy finals, start at `high` and test `xhigh` and `max`. OpenAI's generic "compare medium or high for small text" advice [2] predates the remap. DER.
7. **Sunburst leads on text, with caveats.**
   - LMArena Text Rendering (2026-09-21): Sunburst 1466 ± 14, Flare 1436 ± 13, gpt-image-2 (medium) 1423 ± 7. Flare is statistically tied with gpt-image-2 [52].
   - One poster test: Sunburst switched the copy to all capitals and added unrequested elements, while Flare stayed literal [42] COM (n = 1).
   - Small "micro-glyphs" look worse on 2.5 [47] COM.
   - No new evidence exists for Bengali, Arabic or Hindi on 2.5.
   - **Design change:** use Sunburst for text finals under strict casing and element constraints. Keep Bengali on the hybrid route, as R3 §8 already sets.
8. **2.5 adds grain and repetitive texture to flat areas.**
   - Persistent fine grain appears in skies, studio backdrops and solid backgrounds, even when the prompt forbids it [41] COM (TechRadar test) and [21] COM.
   - Large textured areas repeat "clone-stamp" motifs [36] COM.
   - **Design change:** flat colour fields, gradients and background panels come from CSS or vector, or are cleaned in post. Add a flat-area noise check to QA.
9. **References: 16 on the API, 5 on Codex.**
   - The API reference explicitly lists the 2.5 models with "up to 16 images" [5] OFF. This corrects master.md, which called 16 undocumented.
   - Images enter the context before the text, and the mask applies to image 1 [20] OFF (OpenAI Support). Name each image's role by index [2][17][18] OFF.
   - The model re-renders every logo; it never keeps the input pixels. **Design change:** the vector logo is composited, never trusted to the model.
10. **Reference images are re-billed on every edit.**
    - `/v1/images/edits` does not apply cached-input pricing when the same reference is reused; cached-image billing applies only to the Responses tool [20] OFF.
    - Each reference costs at most about 1.5k image-input tokens, roughly $0.012 [21] COM → DER.
    - A 6-reference `xhigh` render at 1088×1360 costs about $0.16. Batch does not support 2.5 [9] OFF.
11. **Exact valid sizes exist for most deliverables** (§5.2):
    - 1088×1360 → 1080×1350; 1152×2048 or 1440×2560 for exact 9:16; 1280×720 or 2560×1440 for exact 16:9; 2384×1248 → 1200×628;
    - 1824×2560 for A5 with 3 mm bleed at about 300 ppi (experimental);
    - A4 at 300 ppi is impossible natively (above 8.29 MP);
    - 2048×2048 counts as "experimental" under the pixel rule, even though the guide lists it as a common size. DER from [1][4].
12. **Throughput budget.**
    - Both 2.5 models allow 5 images per minute at Tier 1 (then 20/50/150/250 by tier) [7][8] OFF.
    - Organization verification may be required [1][16] OFF.
    - Measured latency: Flare about 20–34 s and Sunburst about 28–60 s at about 2 MP, rising from `high` to `max` [44] VEN; at 1920×1088 `high`, Flare about 29 s and Sunburst about 42 s [21] COM.
    - **Design change:** schedule parallel jobs within the IPM limit and budget about 1 minute per Sunburst `max` render.

---

## 1. Region / pointer / comment-based editing

### 1.1 What ChatGPT Images 2.5 ships (UI only)

| Feature | How it works | Surface | Evidence |
|---|---|---|---|
| **Select** | Highlight an area with the selection brush. On mobile the brush size has a slider and there is undo/redo. Then describe the change. OpenAI: "Highlights are not always precise, and edits may extend beyond the area you selected." | Web and mobile editor | OFF [15] |
| **Comment** | Click any element and type an instruction ("remove this", "change this to blue"). Comments are points for ChatGPT to act on when you press Send. On mobile, the full-screen view lets you "edit the image or add comments". | Web Edit toolbar, mobile | OFF [13][15]; COM hands-on [40] |
| **Markup** | Draw marks on the image. Reported as a toolbar item; its mechanics are not documented. | Web Edit toolbar | COM [40]; **UNVERIFIED** |
| **Erase** | Brush roughly over an object and it is removed. | Web Edit toolbar | COM [40] |
| **Remove BG** | Keeps the foreground; the download is a transparent PNG. | Web toolbar; mobile "Remove" | COM [40]; OFF [15] |
| **Resize / Aspect ratio** | Regenerates the image at another ratio (presets include 3:4, 16:9, 4:3). | Web, mobile | OFF [15]; COM [40] |
| **Version history** | Each edit is kept as a separate file; scroll through them in Edit mode. | Web | COM [40] |
| **Sketch** | Documented flow: type `@` and pick Sketch, draw with colour, erase and undo, confirm, then add instructions (for example "Turn this sketch into a watercolor painting…"). A web entry point via Images → Sketch is reported, and there is a public entry at `chatgpt.com/sketch`. | Mobile (documented); web (reported) | OFF [13][15]; COM [40] |
| **Templates** | Open the sidebar, pick Images → Templates → a category → a template. ChatGPT asks follow-up questions (style, setting) and may offer a reference upload. Named examples: Poster, Merch, Logo, flyers, product photos (styles Clean Studio, Editorial, Lifestyle, Dramatic). Not available in Work mode. | ChatGPT only | OFF [13][15]; COM [40] |
| **Shared prompts** | Share → Prompt template → Copy link; someone else runs the same prompt with their own photos. | ChatGPT | OFF [13][15] |
| **Codex app Canvas comments** | In Canvas view, use Comment on one or more images, select them with Multi-select, and send the comments with any extra instructions in the same chat. | Codex desktop app | OFF [17] |

TechRadar reports that the Edit toolbar (Markup, Comment, Remove BG, Erase, Resize) rolled out quietly during August 2026, before the 2.5 launch [40] COM.

### 1.2 How comments and selections reach the model — UNVERIFIED

- OpenAI documents no mechanism: not whether ChatGPT turns a pin into coordinates, a mask, an annotated image or plain text [13][15].
- The Codex built-in tool has no mask field [22][23]. A Codex-app comment can therefore reach the image model only as text and/or reference images (DER).
- ChatGPT may use an internal mask path; this cannot be checked from outside.
- **Practitioner reconstruction on the 2.5 API** [35] COM, 2026-09-16:
  - comment pins: the full image plus a text instruction containing the click's percentage coordinates;
  - brush: an alpha mask;
  - markup: the clean original plus an annotated reference image.
  - "These approaches worked for many requests, but small, densely packed features remained challenging." (A ring landed on the neighbouring finger.)
  - The fix was a local pipeline:
    1. Turn the click or strokes into a selection in original-image coordinates.
    2. Crop the selection with surrounding context.
    3. Resize the crop to a 1024×1024 working image.
    4. Send a clean crop, a selection-guide image and an alpha mask, all built from the same coordinate transform.
    5. Resize the result back.
    6. Composite only the selection.
  - An optional vision step first clarifies which object is the target.
  - The author notes that a selection must be big enough for the complete addition (for example, both lenses of a pair of glasses).

### 1.3 API equivalents

| Capability | Images API `/v1/images/edits` | Responses `image_generation` tool | Codex built-in `image_gen` |
|---|---|---|---|
| Region mask | `mask`: PNG with alpha, transparent = edit, applied to the first image [1][4][5] OFF | `input_image_mask: {file_id \| image_url}` inside the tool config [1][6] OFF | None [22][23] SRC |
| References | Up to 16: multipart `image[]`, or JSON `images:[{image_url \| file_id}]` (JSON supported since 2026-02-09) [4][5][10] OFF | `input_image` content items (URL, base64 data URL or `file_id` with Files purpose `vision`) [1] OFF. Cap undocumented | At most 5, via `referenced_image_paths` or `num_last_images_to_include`, in path order [22] SRC |
| Multi-turn | Stateless: re-send the image | `previous_response_id`, or an input item `{"type":"image_generation_call","id":"ig_…"}` [1][3] OFF | Conversation context |
| Force edit | By choosing the endpoint | `action: "auto" \| "generate" \| "edit"`; forcing `edit` with no image in context returns an error [1][6] OFF | Implicit |
| Pins, boxes, points, annotation objects, sketch objects | **None** | **None** | **None** |
| Templates | None | Responses "reusable prompts" (a dashboard prompt `id` plus `variables`, which may include images; since 2025-06-13) [10] OFF. These are text-prompt templates, not ChatGPT image templates (DER) | None |
| Model, quality, size | Explicit; 2.5 adds `xhigh` and `max` [4] | Explicit in the tool config. The tool's `model` **defaults to `gpt-image-1`**, so always set it [6] OFF | Hard-coded `gpt-image-2`, `auto`, `auto` [22] SRC |
| Prompt rewriting | None | The mainline model rewrites the prompt (`revised_prompt`) [1][3] OFF | The Codex agent writes the prompt (R3 §1.1) |

The practitioner's wish list [35] — "First-class editor inputs: Support comment pins, brush strokes, bounding boxes, and segmentation information as explicit editing inputs" — confirms these do not exist today. COM.

### 1.4 Hard limits (API)

| Limit | Value | Evidence |
|---|---|---|
| Input images per edit | At most 16; png/webp/jpg, each under 50 MB | OFF [5] |
| Mask format | PNG with an alpha channel; "fully transparent areas (e.g. where alpha is zero)" are edited | OFF [1][5] |
| Mask size | Same dimensions as the first image. The SDK reference says "less than 4MB" [5]; the guide says image and mask "same format and size (less than 50MB)" [1]. Conflict — keep masks under 4 MB. | OFF (conflicting) |
| Prompt | At most 32,000 characters for GPT image models | OFF [5] |
| `n` | 1–10 | OFF [5] |
| Output | base64; png by default, or jpeg/webp with `output_compression` 0–100 (default 100) | OFF [1][5] |
| Streaming | `partial_images` 0–3; each partial costs +100 output tokens | OFF [1] |
| Context order | "the images come before the text prompt, and a mask applies to the first image" | OFF (OpenAI Support, 2026-09-22) [20] |
| Effective input resolution | About 1,536 patches of 32 px per input image; 1248×1248 → 1,521 tokens; a larger upload adds nothing | COM [21] |
| Endpoints for 2.5 | `/v1/images/generations` and `/v1/images/edits`; in Responses only as the tool model; no Batch | OFF [7][8][9] |

### 1.5 How faithfully unmasked areas are preserved — measurements

| Test | Model | Result | Tag |
|---|---|---|---|
| Clothing swap. Prompt-only (no mask stated), images resized to match, light blur, a pixel counts as "changed" if any channel differs by more than 30/255, measured outside a collar-down rectangle | 2.5 Flare | 0.22 % of outside pixels changed; outside-region SSIM 0.938; face-crop SSIM 0.889; a new collar covered a neck mole (n = 1) | COM/VEN [42] |
| Three chained edits, method not disclosed | gpt-image-2 / Sunburst / Flare | 11.4 % / 9.9 % / 9.2 % pixel drift | VEN [45] |
| PaintBench: 1,920 deterministic precise edits, default API settings | gpt-image-2 | 16.3 % mIoU overall (Nano Banana 2: 17.1 %). Changed pixels are 1–8× the edit region for large regions and 50–1,400× for regions under 32² px. mIoU rises from 1.7 % (under 32² px) to 24.1 % (at least 256² px). Removal is the easiest operation (50.6 %) | Paper [53] |
| Mask test ("remove the marked cats") | gpt-image-2 | "High accuracy in retaining image details outside of mask", but an unmasked yarn thread was edited (n = 1) | COM [37] |
| Professional architectural patch work | 2.5 (ChatGPT) | Preservation of geometry, perspective and crop is "extremely strong"; used as a crop → fix → reinsert retoucher | COM [36] |
| Claim | 2.5 | "better at editing only what you've asked for"; chained edits "without degrading image quality over time" | OFF claim [13] |

**Takeaways (DER).**

- 2.5 plausibly reduces spill to around 1 % of the canvas or less for a single well-specified edit.
- Small regions remain the failure zone: fixed per-edit spill is large relative to a small target. So enlarge the target via a crop window: aim for the target to cover at least about 256 px in the working image, which is where gpt-image-2's mIoU recovers [53].
- Always composite; a mask by itself is never a lock [1][2].

### 1.6 What OpenAI says about `input_fidelity` on 2.5

- **The 2.5 parameter table omits `input_fidelity` entirely** [2] OFF.
- The guide says only: "For `gpt-image-2`, omit this parameter; the API doesn't allow changing it because the model processes every image input at high fidelity automatically" [1] OFF.
- The SDK edit reference: "supported for GPT image models that support input fidelity. `gpt-image-2` and `gpt-image-2-2026-04-21` ignore this parameter" [5] OFF.
- The Responses tool reference still says it is "only supported for `gpt-image-1` and `gpt-image-1.5` and later models… Defaults to `low`" [6]. This reads as stale and contradicts the lines above.
- A community test in April 2026 got an API error when sending the field to gpt-image-2 [37] COM.
- A user who compared bills found image-input usage on both 2.5 models "completely identical to gpt-image-2" [21] COM. That is consistent with always-high-fidelity input.
- **Rule:** omit `input_fidelity` for 2.5 (master.md already says so). Whether 2.5 accepts it, ignores it or errors is **UNVERIFIED**.

### 1.7 Design implication: our "comment layer" (DER, from [1][2][20][35][53])

1. **Capture.** The UI or agent emits pins `{x%, y%, note}`, boxes `{x0, y0, x1, y1}` and brush masks, all in original-image pixels.
2. **Resolve the target.** Optionally ask a vision model to name the object under the pin ("the left glass", "the CTA pill"). The user's region stays authoritative [35].
3. **Choose the working window.** If the target is under about 256 px, or the design is larger than about 1.5 MP, crop a context window (target plus 1–2× margin) and resize it to a valid size of about 1.0–1.5 MP. Otherwise edit the full canvas at its native size.
4. **Build the inputs from the same transform:**
   - Image 1 = clean window;
   - Image 2 (optional) = the same window with a thin box in a colour absent from the design;
   - mask = alpha 0 inside the box, dilated 12–24 px (polarity: master.md §9.3).
5. **Prompt:** describe the target in words, give the percent box as a secondary cue, say "change only…", list what must stay, and say "do not reproduce any marks from Image 2" (§2.3).
6. **Composite.** Resize back and composite only the selection (feather 4–8 px) onto the original. Run the checks: a diff outside the selection must be 0; OCR if text changed; look for the annotation colour.
7. **Stop rule.** After two failed attempts, fall back to hybrid (HTML) or a manual fix. This is R3's rule.

---

## 2. Visual prompting with annotations

### 2.1 Evidence

| Source | What it shows | Tag |
|---|---|---|
| OpenAI `hatch-pet` skill (openai/skills) | Layout-guide images are attached as "layout-only" inputs. Wording: "Use the attached layout guide only for slot count, spacing, centering, and padding; do not draw the guide." Role label: "layout guide for N frame slots; use for spacing only, do not copy guide lines". QA must "Fail rows with … copied guide marks", which shows leakage happens in practice | OFF/SRC [27] |
| OpenAI 2.5 prompting guide | Sketch-to-render is an official edit pattern, shown with 2.5 outputs: "Preserve the exact layout, proportions, and perspective… Do not add new elements or text." It also says that for precise local edits you should name the "saturation, contrast, arrows, camera angle, and surrounding objects that must remain unchanged" | OFF [2] |
| VIBE benchmark (arXiv 2602.01851v2, 2026-05-21) | Visual-instruction editing with boxes, arrows, sketches and force vectors. gpt-image-1: 44.21 overall, **58.56 on "deictic" (boxes and arrows)**. Nano Banana Pro: 65.15 overall, 84.83 deictic. gpt-image-2 and 2.5 were **not tested** | Paper [54] |
| Annotation-editor vendor | Sends "the clean source image and the annotated reference image" to GPT Image 2 with "Apply the red arrows, circles, freehand marks, and notes as editing instructions. Remove all annotations in the final output." No success rate | VEN [49] |
| Atlas Cloud sketch/markup guide | Reported failures: saturated strokes bleed colour into the output; overlapping lines trigger hallucinated content; "directional arrows may render as physical props". Advice: thin, low-opacity strokes and boxes instead of arrows | VEN [48] |
| Practitioner on the 2.5 API | Markup via a clean original plus an annotated reference "worked for many requests"; densely packed small targets failed until crop, mask and composite were added | COM [35] |
| ChatGPT's own selection tool | "not always precise… edits may extend beyond the area you selected" | OFF [15] |

**Verdict.**

- GPT Image 2 and 2.5 generally understand annotated references, and OpenAI's own tooling relies on that for layout guides.
- No published success rate exists for 2/2.5, and two leak modes are documented: annotation marks copied into the output, and annotation colour bleeding into it.
- The most recent measured comparison (gpt-image-1 vs Nano Banana Pro) put OpenAI well behind Google on box and arrow instructions. Whether 2.5 closed that gap is **UNVERIFIED**; it needs our own eval (§O).

### 2.2 Numeric coordinates and percentages

- **Official:** no guidance. OpenAI's examples use words: "upper-right corner", "top third", "centered in the top third", "leave the upper-right corner clear", and "72pt" as a size cue [2][17][18] OFF.
- **Measured (gpt-image-2):** PaintBench includes position-specified operations: translation, rotation about a canvas coordinate, construction "at position", and removal by canvas position. Geometric operations score at most 17.5 % mIoU and construction scores 14.3 % [53]. Tiny regions are badly over-edited.
- **Practitioner:** percentage coordinates in text worked for many comment edits but misfired on closely spaced targets [35] COM.
- **Rule (DER):**
  - Write the region in words first ("the orange CTA pill, bottom-center"), then add a secondary cue ("≈ x 30–70 %, y 84–92 % of the canvas").
  - Enforce position with a mask plus composite (API), or with a layout-guide image (both routes).
  - Never rely on coordinates to place text or a logo; typeset those in HTML (R3's hybrid route).
  - Whether percentages are honoured proportionally on 2.5 remains **UNVERIFIED**, as R3 §12 already noted.

### 2.3 Best wording (DER, assembled from [2][27][35][49])

**A. Two-image annotated edit (API or Codex).** Image 1 is the clean original; Image 2 is the same image with one thin box.

```text
Image 1 is the design to edit. Image 2 is an instruction copy of Image 1 with one thin magenta rectangle; the rectangle is a pointer only.
Edit Image 1: inside the area marked by the rectangle (the orange "Order now" button, bottom-center, about x 30–70 %, y 84–92 %), change the button colour to deep green #1F5C3A. Keep the button's shape, size, position, text, font and shadow exactly as they are.
Change nothing outside that area: same layout, text, colours, product, person, lighting and margins.
Do not reproduce anything from Image 2 — no rectangle, outline, magenta colour, arrow or handwriting may appear in the output.
```

**B. Layout guide for a new design** (the `hatch-pet` pattern [27]):

```text
Image 4 is a layout guide only: coloured blocks show zones (orange = headline zone, blue = product zone, grey = empty logo zone). Follow the zones' positions and proportions. Do not draw the guide: no blocks, borders, outlines, guide colours, labels or grid lines in the output.
```

**Rules for annotation images (DER):**

- Use a single colour absent from the design (magenta or cyan) and 2–4 px strokes.
- Prefer boxes over arrows.
- Never write text on the annotation image; put the instruction in the prompt.
- Use one mark per edit, then run a QA check that finds the annotation hue in the output.
- On the API, always send a mask built from the same box and composite afterwards.

---

## 3. Reference images at full capability

### 3.1 Counts and mechanics

| Route | Maximum references | Order and roles | Tag |
|---|---|---|---|
| Images API edits | 16 (2.5 listed explicitly) | Images precede the prompt in context; the mask applies to image 1 | OFF [5][20] |
| Responses tool | Undocumented cap; images come from the conversation context | Mask via `input_image_mask` | OFF [1] |
| Codex built-in | 5 | Order = `referenced_image_paths` order; `num_last_images_to_include` is best-effort and "may include newer unrelated images" (source comment) | SRC [22] |
| ChatGPT UI | Not documented; OpenAI advises "a small set is usually easier to manage than a large one" | — | OFF [18] |
| Official sample | The 2.5 guide itself uses 4 references (gift basket; outfit plus 3 garments) | — | OFF [1][2] |

**Per-image resolution budget.** About 1,536 patches (COM [21]). Six references are six separate downsampled images, not one shared budget (DER from the per-image patch rule [11][21]). A collage (brand sheet) shares one budget across all its tiles.

### 3.2 Assigning roles — official wording

- "Identify each input by number and purpose: subject, style, clothing, or background. Explain how the inputs should combine and which elements should move where." [2] OFF.
- "Image 1 is the product photo to edit. Image 2 is the style reference. Keep the product, camera angle, layout, and objects from image 1, but apply the clean line work, muted palette, and soft shadows from image 2…" [17] OFF.
- "Place the dog from the second image into the setting of image 1…" — the scene goes first [2] OFF.
- "Use terms like `draw` or `edit`… instead of saying `combine` or `merge`… say 'edit the first image by adding this element from the second image'" [3] OFF.
- Codex skill scaffold: `Input images: <Image 1: role; Image 2: role>`; "reference images by index and describe how they should be used" [25] OFF/SRC.
- The first image is "preserved with extra richness in texture", so faces should be combined into one composite image. This is documented only for gpt-image-1 with `input_fidelity="high"` [19] OFF (older model). For 2.5 it is **UNVERIFIED**; keep it as an ordering heuristic: the most fidelity-critical element goes first.

### 3.3 Identity and face preservation on 2.5

| Evidence | Finding | Tag |
|---|---|---|
| OpenAI | "better at preserving the subjects in your reference photos… distinctive features are more likely to carry through" | OFF claim [13] |
| LMArena Image Edit (2026-09-21) | Sunburst 1526 ± 6, Flare 1482 ± 6, gpt-image-2 (medium) 1461 ± 3, Nano Banana Pro 1390 ± 3 (2.5 scores preliminary) | COM [52] |
| Puter | Portrait relocated to a new scene: all five identifying features kept (hair, eyes, neck mole, ears, lips). Clothing edit: face-crop SSIM 0.889 (n = 1 each) | COM/VEN [42] |
| MindStudio | Four-angle character sheet: identity held "more reliably" than Nano Banana 2 or Pro (n = 1) | VEN [43] |
| HN | Kept a person's appearance while changing pose; less "fried" skin than gpt-image-2. Another user: OpenAI edits still "lose fine detail" compared with Nano Banana or Flux | COM [47] |
| Official prompt (2.5 guide) | "Do not change her face, facial features, skin tone, body shape, pose, or identity in any way. Preserve her exact likeness, expression, hairstyle, and proportions. Replace only…" | OFF [2] |

**Verdict.** 2.5 (Sunburst especially) is currently the strongest publicly ranked editor for identity. It is still generative: the face is re-rendered, and the SSIM of about 0.89 shows micro-changes. For client faces, composite the original face and hair back whenever the face should not change (master.md §9.6). DER.

### 3.4 Logo fidelity

- The model re-renders the whole image, logo included; nothing is pixel-copied. OpenAI lists brand-element drift as a known limitation [1] and requires compositing for pixel-identical regions [2] OFF.
- IMG.LY scores Flare 3.3/5 on "Logos, Icons & Vector-Style" [46] VEN (small n).
- The 2.5 announcement claims developers can "update a single element… while preserving the subject, composition, and brand treatment around it" [13]. That is a preservation claim, not pixel exactness.
- **Rule (unchanged from R3/master.md, now with 2.5 evidence):** pass the logo only for colour and shape awareness or for perspective placement (packaging, merch). Otherwise reserve an empty zone and composite the SVG. When the logo must sit in perspective on an object, let the model place it, then replace it with a warped vector (master.md §9.7).

### 3.5 Brand-kit sheet images (DER; no official guidance found)

- A single "brand sheet" (swatches, type specimen, logo lockup) saves reference slots, which matters most on Codex with its 5-image cap. The whole sheet then shares one ~1,536-patch budget, so small specimen text becomes mush [21] COM → DER.
- Text on a reference can leak into the output. This is failure 22 in R3 §6, and hex codes rendered as labels is failure 5 in R3 §6. Make brand sheets text-free: swatches only, plus a large specimen of the display face using a neutral pangram, or no letters at all. Add "do not copy any text, labels or swatches from Image N".
- The palette is better given in words plus hex in the prompt, guarded by R3's hex-guard line (R-T11).

### 3.6 Six-slot plan used in template T1 (DER)

| Slot | Role | Why here |
|---|---|---|
| Image 1 | Product (source of truth) | Most fidelity-critical; possible first-image richness [19] |
| Image 2 | Face / identity | Second most critical |
| Image 3 | Logo | Colour and shape awareness only; composited later |
| Image 4 | Layout guide (wireframe blocks) | "Do not draw the guide" [27] |
| Image 5 | Style reference | "Palette, light and texture only" [2][17] |
| Image 6 | Brand sheet (text-free) | Palette and type character |

For a person-first design, swap Images 1 and 2. On Codex (maximum 5), drop the logo.

---

## 4. Text and typography on 2.5

### 4.1 New evidence since R3 (2.5-specific)

| Source | Setting | Finding | Tag |
|---|---|---|---|
| LMArena "Text Rendering" category (2026-09-21) | Human preference | Sunburst 1466 ± 14 (2,988 votes); Flare 1436 ± 13 (2,647); gpt-image-2 (medium) 1423 ± 7; mai-image-2.6 1370; Nano Banana 2 1293; Nano Banana Pro 2k 1270; Seedream 5.0 Pro 1255 | COM [52] |
| LMArena "Product, Branding & Commercial Design" | Human preference | Sunburst 1415 ± 13 (preliminary); Flare 1395 ± 13 (preliminary); gpt-image-2 1387 ± 6 | COM [52] |
| Puter poster test | Mid-century travel poster, fixed layout, 3 text elements, `xhigh` | Flare: text correct, formatting kept. Sunburst: "correct letters, set in all capitals", added unrequested harbour elements, took about twice as long (n = 1) | COM/VEN [42] |
| Tosea deck test | 5-slide deck at 2048×1152, matched token budgets, 41 calls | Every heading, bullet and figure correct on gpt-image-2, Sunburst and Flare ("98.4 %", "4.2 to 5.6", "18:00"); "no regression" | VEN [44] |
| IMG.LY | "auto" tier, 24 text runs per model | Text accuracy 5.0/5 for both; typography category 3.7/5 (Flare) | VEN [46] |
| HN (heavy API user, UI mock-ups) | 2.5 vs 2 | References were used better, but "microglyphs" look worse | COM [47] |
| HN / press summary | — | OpenAI did not claim better text in 2.5. The announcement claims infographic accuracy, layouts and style, not text | OFF [13][14] + COM [47] |

**Net (DER).** Short and medium copy is as reliable as, or slightly better than, gpt-image-2 on Sunburst; Flare is about the same as gpt-image-2. Tiny text, decorative micro-labels and casing fidelity are the soft spots. R3's text budgets and OCR gate still apply unchanged. No string-count accuracy curve has been published for 2.5.

### 4.2 Non-Latin (Bengali, Arabic, Hindi)

- No independent 2.5 test found. The only claims are vendor pages repeating the 2.0-era "~99 %" figure without method [search results, VEN].
- R3 §8 policy stands: Bengali on the hybrid route, with at most 3 words of AI-rendered Bengali (Tier B) plus a native reviewer.

### 4.3 Fonts: by name or by description

- **Official:** describe the typography — "style, size, color, and placement"; examples "bold sans-serif, high contrast, centered, clean kerning", "handwriting-like font", "large, bold, white sans-serif letters", "72pt" [1][2][17][18] OFF. OpenAI never tells you to name a font.
- **Community / vendor:** font names are "style hints" only. Descriptive terms work best: classification, weight, width, terminals, era or medium [51] VEN. A reference image containing the target lettering plus "match the typography style of the reference image" is claimed to help [51] VEN, **UNVERIFIED**. The 2.5 guide's official style-transfer pattern ("Use the same style from the input image…") covers palette, texture and medium, not glyph-accurate fonts [2].
- **Rule (DER):**
  - For brand fonts, typeset in HTML with the real font files (hybrid).
  - In full-AI, describe the font instead of naming it: "condensed geometric grotesque, heavy weight, tight tracking, all caps, flat ink".
  - Optionally attach a large, text-light specimen as a "typographic character" reference.
  - Expect a similar style, never the same glyphs.

### 4.4 Quality settings for text

- **Official:** "Compare medium or high quality for small text, dense information, or multiple fonts" [2]. "Use `xhigh` or `max` only when they improve an unmet quality requirement… A higher setting doesn't guarantee a better result" [2] OFF.
- **The remap:** at 2048×1152, 2.5 `medium` = 367 output tokens, `high` = 1,413, `xhigh` = 2,511, `max` = 5,650. gpt-image-2 used 1,413 for `medium` and 5,650 for `high` [44] VEN, which matches R3's formula (DER).
- **Rule (DER):**
  - Never use 2.5 `low` or `medium` for text-bearing finals.
  - Start at `high`, the budget OpenAI's old "medium for text" advice assumed.
  - Use `xhigh` for dense or small copy and `max` for hero or print text.
  - Measure with the OCR gate; there is no 2.5 study of text accuracy by quality level (**UNVERIFIED**).

### 4.5 Poster and merch "templates" — can the API use them?

- In ChatGPT a template is a guided prompt builder: a starting prompt plus follow-up questions and an optional reference upload. Poster, Merch, Logo, Product photo and flyers are named [13][15][40]. They are not available in Work mode [15].
- **There is no API equivalent** [1][4][6]. The nearest API mechanism is Responses reusable prompts: a dashboard prompt `id` with `variables`, which can include images [10] OFF. That templates the mainline model's prompt, not a ChatGPT image template.
- **Rule (DER):** our own per-deliverable templates (R3 §5.4) plus a question flow is the equivalent. There is no gain in trying to reach ChatGPT's templates.

---

## 5. Sizes and aspect

### 5.1 Rules — additions to R3

- **Rule text on 2.5.** The reference wording adds "the maximum supported resolution is `3840x2160`" and "the requested size must also satisfy the model's current pixel and edge limits" [4] OFF. The guide's 4K portrait (`2160x3840`) is also listed as a common size [2].
- **The "experimental" line is a pixel count, not an edge length.** Output above 3,686,400 px is experimental. So `2048x2048` (4.19 MP) counts as experimental even though the 2.5 guide lists it as a "common size" [2]; `1920x1920` (exactly 3,686,400 px) is not (DER).
- **The API returns the size you ask for.** No mismatch was found on the API. The size mismatches in R3 (1536×864 → 1672×941) come from the ChatGPT/Codex backend, which ignores `size` and picks about 1.57 MP at its own aspect [31][34] COM.

### 5.2 Deliverable sizes (all valid; checked by script against the four rules)

| Deliverable | Request (API) | Post step | MP | Experimental? | Notes |
|---|---|---|---|---|---|
| IG portrait 1080×1350 | **1088×1360** | Downscale ×0.993 | 1.48 | No | Exact 4:5. Higher-detail options: 1536×1920 (2.95 MP), 2048×2560 (5.24 MP, experimental) |
| Square 1080×1080 | 1088×1088 or 1024×1024 | Downscale | 1.18 | No | — |
| Story/Reel 1080×1920 | **1152×2048** (×0.9375) or **1440×2560** (×0.75) | Downscale | 2.36 / 3.69 | No | Both exact 9:16. R3's 1088×1920 needs an 8 px crop |
| YouTube 1280×720 | **1280×720** directly, or 2560×1440 (×0.5) for crisper text | None / downscale | 0.92 / 3.69 | No | Exact 16:9 |
| YouTube 3840×2160 | 3840×2160 | None | 8.29 | **Yes** | Or 2560×1440 plus a non-generative upscale |
| FHD 1920×1080 | 2048×1152 (×0.9375) or 2560×1440 (×0.75) | Downscale | 2.36 / 3.69 | No | 1920×1088 needs an 8 px crop |
| Link/ad 1200×628 (1.91:1) | **2384×1248** (×0.503, crop about 0.03 %) or 1712×896 | Downscale + crop | 2.98 / 1.53 | No | 628 is not a multiple of 16, so a tiny crop is unavoidable |
| A5 trim at 300 ppi (1748×2480) | 1760×2480 (crop 12 px) or 1872×2656 (exact ratio) | Crop / downscale | 4.36 / 4.97 | **Yes** | Nothing non-experimental reaches 300 ppi |
| A5 + 3 mm bleed at 300 ppi (1819×2551) | **1824×2560** | Crop about 0.1 % | 4.67 | **Yes** | — |
| A4 at 300 ppi (2480×3508 = 8.7 MP) | **Impossible natively** (above 8,294,400 px) | — | — | — | Best: **2384×3344** ≈ A4 + 3 mm bleed at about 280 ppi (7.97 MP, experimental), or 2416×3424 ≈ 291 ppi trim only (R3). Then vector type plus a non-generative upscale of the plate |

### 5.3 Output tokens and cost at these sizes (2.5; $30 per 1M output tokens; formula from R3 / master.md §14.1)

| Size | low | medium | high | xhigh | max |
|---|---|---|---|---|---|
| 1088×1360 | 181 / $0.005 | 397 / $0.012 | 1,587 / $0.048 | 2,840 / $0.085 | 6,431 / $0.193 |
| 1536×1920 | 258 / $0.008 | 565 / $0.017 | 2,257 / $0.068 | 4,039 / $0.121 | 9,146 / $0.274 |
| 1152×2048 | 157 / $0.005 | 367 / $0.011 | 1,413 / $0.042 | 2,511 / $0.075 | 5,650 / $0.170 |
| 1440×2560 or 2560×1440 | 205 / $0.006 | 478 / $0.014 | 1,843 / $0.055 | 3,276 / $0.098 | 7,370 / $0.221 |
| 1280×720 | 106 / $0.003 | 246 / $0.007 | 947 / $0.028 | 1,683 / $0.050 | 3,787 / $0.114 |
| 2384×1248 | 160 / $0.005 | 389 / $0.012 | 1,493 / $0.045 | 2,707 / $0.081 | 5,971 / $0.179 |
| 1824×2560 (exp.) | 294 / $0.009 | 681 / $0.020 | 2,722 / $0.082 | 4,909 / $0.147 | 10,885 / $0.327 |
| 2384×3344 (exp.) | 439 / $0.013 | 1,018 / $0.031 | 4,069 / $0.122 | 7,340 / $0.220 | 16,275 / $0.488 |
| 1248×1248 (check) | — | — | — | — | **8,197** / $0.246 |

The 1248×1248 `max` figure of 8,197 tokens matches an independently billed request [21], which validates the formula (DER).

Input image tokens are extra, at $8 per 1M:

- about 1,000–1,536 tokens per reference (COM-derived);
- about $0.008–0.012 each;
- never discounted on `/images/edits` [20].

### 5.4 Does upscaling or `max` change text fidelity?

- **No 2.5 measurement exists (UNVERIFIED).**
- Tosea found text equally correct at matched budgets [44] VEN.
- OpenAI says higher quality is "not a guarantee" [2].
- DER reasoning:
  - `max` gives the model more tokens and so more detail, which should help small text. It does not fix spelling logic.
  - At 4K, 2.5 `high` gets only 3,336 tokens, versus 13,342 for gpt-image-2 `high` [44]. A 4K `high` render is therefore detail-starved; a 4K render needs `max` to have gpt-image-2's `high` token density.
  - Non-generative upscalers (Real-ESRGAN class) sharpen but cannot correct wrong glyphs; they may amplify 2.5's grain (§8).
  - Generative re-rendering ("recreate at higher resolution") redraws the text and needs a new OCR pass.
- **Rule:** get the text right at the native size (or typeset it in HTML), then upscale only text-free plates.

---

## 6. Access to 2.5 without an API key

### 6.1 Codex CLI source (SRC)

| Item | Finding | Where |
|---|---|---|
| Latest releases | Stable `0.156.1` (2026-09-23 02:41 UTC); pre-releases `0.157.0-alpha.11` (04:50 UTC) and `0.158.0-alpha.2` (13:07 UTC) | [26] |
| Model | `const IMAGE_MODEL: &str = "gpt-image-2";` at line 59 of `codex-rs/ext/image-generation/src/tool.rs`. Identical in `rust-v0.158.0-alpha.2` and on main `8f1490eab` (2026-09-23 17:08 UTC). Last change to the file: `40eac3ce8` (#47484, 2026-09-23) | [22] |
| References | `MAX_EDIT_IMAGES = 5` (line 60). Paths are loaded with `PromptImageMode::Original` and sent as data URLs in path order | [22] |
| Quality and size | `quality: Some(ImageQuality::Auto)`, `size: Some("auto")` on every generation and edit | [22] |
| Quality enum | `enum ImageQuality { Low, Medium, High, Auto }` — no `XHigh`/`Max`. Unchanged since `423488480` (2026-05-22); the last change to the file was `929389f59` (2026-09-09) | `codex-rs/codex-api/src/images.rs` [23] |
| Edit request | `ImageEditRequest { images, prompt, background, model, n, quality, size }` — **no mask, no input_fidelity** | [23] |
| Endpoint | `POST {provider base}/images/generations` and `/images/edits`; with a ChatGPT login the base is `https://chatgpt.com/backend-api/codex` | `codex-rs/codex-api/src/endpoint/images.rs` [23]; [29] |
| Transparency | PR #47484 (`transparent_background`) **first ships in `rust-v0.158.0-alpha.2`**; not in 0.156.1 or 0.157.0-alpha.11 (checked with `compare`) | [26] |
| Feature flags | Only `image_generation` (stable, default on) — an on/off switch, no model option | `codex-rs/features/src/lib.rs` [24] |
| Config | The Codex `config.toml` reference has no image-model key | [26] (config reference) |
| PRs | `gh search prs` for "gpt-image-2.5", "sunburst", "flare", "IMAGE_MODEL" finds nothing relevant. Open requests without maintainer answers: **#43965** (expose model and selector, 2026-09-09) and **#45452** (C2PA ambiguity, 2026-09-14) | [29][30] |
| Official skill fallback (with a key) | `scripts/image_gen.py`: `DEFAULT_MODEL = "gpt-image-2"`; `ALLOWED_QUALITIES = {low, medium, high, auto}`; any model other than gpt-image-2 is limited to legacy sizes (1024×1024, 1536×1024, 1024×1536, auto). **With an API key, the stock skill still cannot request 2.5 `xhigh`/`max` or custom 2.5 sizes** | [25] |

### 6.2 What the subscription backend does with a 2.5 request (COM; unofficial probes)

| Probe | Result | Source |
|---|---|---|
| Hosted tool on `/backend-api/codex/responses` with `model=gpt-image-2.5-sunburst, quality=max, size=1536x1024`; controls with an invalid model and with the bare tool | `response.tools` echo is always `model=gpt-image-2-codex quality=auto size=auto`; every call returns an image | Hermes #107233 (2026-09-10); confirmed by a Hermes maintainer, fixed in #111000 [33] |
| Native `/backend-api/codex/images/generations`, model `gpt-image-2.5-flare` vs an invalid id | Both return HTTP 200 with a 1254×1254 PNG. Server-reported `quality=low` for `auto`. No effective-model field | codex #43965, Joeywrz, 2026-09-10 [29] |
| Same, `gpt-image-2.5-sunburst` vs an invalid id, `size=1024x1024, quality=low` | 1536×1024 vs 1254×1254; no model field | codex #43965, Dr-Amp, 2026-09-14 [29] |
| Same, 21 samples, requested `quality=low, size=1024x1024` | ~1.2–1.4 MP at a server-chosen aspect (1370×1148 and others); "Neither route honors `size`"; explicit `gpt-image-2` returns a consistent shape, other ids vary | OmniRoute #14617, 2026-09-23 [34] |
| Hosted tool with `gpt-image-2`, `high`, `2160x3040` | Rewritten to `gpt-image-2-codex/auto/auto`; PNGs 1024×1536, 1054×1492, 1254×1254, 1693×929 | codex #28723, 2026-06-17 (open) [31] |
| C2PA metadata | `softwareAgent gpt-image / 2.0` on Codex **and** on API 2.5 Flare and Sunburst images, so it cannot identify the model | [21][30] |

### 6.3 A weak fingerprint (DER, UNVERIFIED)

All nine `usage.output_tokens` samples OmniRoute reported [34] fit R3's token formula exactly with granularity **G = 24**, and none fits G = 16, 48 or 96:

- 1370×1148 → 429 tokens;
- 1346×1168 → 451;
- 1333×1180, 1338×1175 and 1328×1184 → 451;
- 1310×1200, 1312×1199 and 1322×1190 → 472;
- 1286×1223 → 494.

G = 24 exists only in the 2.5 ladder (`medium`). gpt-image-2's documented ladder is 16/48/96. So the Codex route is **not** plain, documented gpt-image-2, whatever the client asks for. It runs at a budget of about 430–500 output tokens at ~1.57 MP: roughly 2.5 `medium`, and about a quarter of gpt-image-2 `medium` at that size.

Two consequences:

- the Codex backend may already run a 2.5-family model, consistent with OpenAI's statement that Images 2.5 rolled out to Codex [13];
- small or dense text on the Codex route is structurally token-starved.

This does not prove which model ran.

### 6.4 Codex app and ChatGPT desktop

- **Codex app.** It uses the same built-in tool as the CLI, whose schema is `prompt`, `referenced_image_paths`, `num_last_images_to_include` [22][29], with no model or quality selector. OpenAI's Codex doc still says "Built-in image generation uses `gpt-image-2`" [17]. The app shows an Images 2.5 promotion [29]. Canvas-view comments are available [17].
- **ChatGPT desktop / web / mobile.** Images 2.5 runs on all tiers [13][15], with no Flare/Sunburst selector and no quality or size controls. Practical output is about 1.5–1.6 k px on the long edge (about 1.57 MP) [21][36] COM. The claim that ChatGPT "defaults to Flare, escalates to Sunburst" is one forum post saying "AFAIK" — **UNVERIFIED** [21]. Comments, Sketch and Templates are usable manually. There is no API and no supported automation.

### 6.5 Routes that avoid an OpenAI key

- **Higgsfield CLI** (user's installed skills). Upstream main (2026-09-11) makes `gpt_image_2_5` the default image/design model, with "Flare/Sunburst variants and quality tiers through `max`" and reference-guided editing [55]. R1 §A.5 has the details; the local skill copy predates this. It needs a Higgsfield account and credits. Mask support is **UNVERIFIED**.
- **Third-party gateways** (fal, OpenRouter, Atlas Cloud and others) expose both models, each with its own key and billing (search results).
- **Using the ChatGPT OAuth token with non-official clients** (Hermes, OmniRoute, term-llm) is undocumented, is not an OpenAI-supported developer interface, and as §6.2 shows does not give verifiable model, size or quality control. **Not recommended.** COM.

### 6.6 Verdict

As of 2026-09-23 there is **no config key, flag, environment variable, feature toggle or PR** in openai/codex that selects 2.5. The backend would ignore such a selection anyway.

- The only verifiable route to Sunburst or Flare with `xhigh`/`max`, masks and exact sizes is the **OpenAI API with a key** (or Higgsfield's hosted 2.5).
- Keep the Codex route for concepts, text-free plates and cheap iterations.
- Watch #43965 for a model selector. Re-check `tool.rs` after every Codex update; R3 §11 already has a canary for this.

---

## 7. Prices, rate limits, verification, latency

| Item | Value | Tag |
|---|---|---|
| Token prices (both 2.5 models, same as gpt-image-2) | Image input $8 per 1M (cached $2); image output $30 per 1M; text input $5 per 1M (cached $1.25) | OFF [7][8][9] |
| Cached-input discount | **Not applied on `/v1/images/edits`** when a reference is reused; cached-image billing applies to the Responses tool (a working example is still pending) | OFF (OpenAI Support 2026-09-21/22) [20] |
| Batch | Not supported for 2.5 (only gpt-image-2 and older appear in the Batch table) | OFF [7][9] |
| Responses overhead | Mainline model tokens are added. For example, `gpt-5.4-mini` costs $0.75 in / $4.5 out per 1M and supports `image_generation`; `gpt-6-astra` costs $10 / $50 | OFF [1][12] |
| Rate limits (default; same for Sunburst and Flare) | Tier 1: 100 k TPM / **5 IPM**; Tier 2: 250 k / 20; Tier 3: 800 k / 50; Tier 4: 3 M / 150; Tier 5: 8 M / 250 | OFF [7][8] |
| Organization verification | "you may need to complete the API Organization Verification… before using GPT Image models" [1]. Identity verification needs a physical government ID and a selfie if requested; one individual can verify only one organization [16] | OFF |
| Latency: official | "Complex prompts may take up to 2 minutes" [1]; "up to 50 %" lower than Images 2.0 [13]; Flare "50 % lower latency" than gpt-image-2 [13] | OFF |
| Latency: 1920×1088 `high`, webp, n = 6 each | Flare mean 29.4 s (headers 28.8 s); Sunburst 41.9 s | COM [21] |
| Latency: 2048×1152, matched budgets, 41 calls | 1,413 tokens: gpt-image-2 `medium` 37.3 s, Sunburst `high` 27.7 s, Flare `high` 19.7 s. 5,650 tokens: gpt-image-2 `high` 82.9 s, Sunburst `max` 59.8 s, Flare `max` 33.7 s. 4K `high`: gpt-image-2 92.4 s vs 2.5 27.8–33.8 s | VEN [44] |
| Latency: "auto", about 0.79 MP, 111 images | p50: Flare 21.3 s, Sunburst 30.4 s | VEN [46] |
| Latency: heavy API user (about 50 k images) | gpt-image-2 averaged about 104 s; 2.5 about 35–40 s | COM [47] |
| Latency: Codex route | About 77 s for the first run (R3 L2); 26–87 s range, with occasional failures after 265 s | LOC (R3) / COM (codex #33050) |

**Budget example (DER).** One T1 render (6 references, 1088×1360, `xhigh`, Sunburst) costs:

- output: 2,840 × $30/M = $0.085;
- inputs: 6 × ~1.5 k × $8/M ≈ $0.074;
- prompt: about 1.2 k text tokens ≈ $0.006;
- **total ≈ $0.165**, and about $0.27 at `max`.

At Tier 1 (5 IPM) a 3-direction × 2-variant exploration needs at least 2 minutes of rate budget.

---

## 8. Known failure modes of 2.5 for designs, and mitigations

| # | Failure | Evidence | Mitigation |
|---|---|---|---|
| F1 | **Grain or sandy noise in flat areas** (skies, studio sweeps, solid panels, gradients) even when the prompt asks for smooth fills | TechRadar test (4 images) [41]; Reddit via [41]; forum "solid backgrounds still has symptoms" [21] COM | Flat fields come from CSS or vector (hybrid). Add a flat-area noise metric (local variance in low-gradient regions) to QA. If AI is required: denoise flat regions only (guided or bilateral filter within a mask), or replace them with a sampled solid colour. Compare Flare vs Sunburst vs gpt-image-2 on our own set |
| F2 | **Repetitive "clone-stamp" textures** (rocks, foliage, paving) | [36] COM | Keep hero textures photographic (a real photo plate), or regenerate the patch in a crop window; avoid large texture fields in AI plates |
| F3 | **Casing drift** (Sunburst set copy in all caps) | [42] COM | Write copy in the final casing and add "preserve upper/lower case exactly as written; do not convert to all caps". Run a case-sensitive OCR diff; try Flare for copy-literal jobs |
| F4 | **Unrequested elements and "interpretive" layout** (Sunburst added a harbour; less literal about spatial positions) | [42] COM; [45] VEN | Enumerate the elements with "no additional elements". Attach a layout-guide image (§2.3B). A/B Flare or gpt-image-2 for layout-literal jobs |
| F5 | **Micro-glyphs and small decorative text degrade** | [47] COM | Keep text in R3's Tier A/B budgets and use `xhigh`/`max`; decorative micro-labels only in hybrid |
| F6 | **Extra or invented copy; hex codes printed as labels** | R3 §6 F2/F5 (no new 2.5 data) | R3 rules (only these strings; hex guard) |
| F7 | **Logo drift or re-lettering; fake marks** | [1] OFF; [46] VEN | Composite the SVG; reserve an empty zone; "no logos except…" |
| F8 | **Detail loss in edits of dense designs** (input downsampled to about 1,536 patches) | [21][47] COM | Crop-edit-paste windows (§1.7); edit from the original, never from a chained copy |
| F9 | **Chained-edit drift** (still about 9–10 % after 3 edits; "editing a few times still gets the image messy") | [45] VEN; [50] VEN | At most 2 chained edits (R3); composite each approved change onto the master |
| F10 | **Small-region over-editing** | [53] (gpt-image-2) | Crop window so the target is at least about 256 px; mask plus composite |
| F11 | **Annotation leakage** (boxes or arrows copied, colour bleed) | [27] OFF QA rule; [48] VEN | §2.3 rules plus an annotation-hue detector in QA |
| F12 | **Prompt rewriting in Responses** (`revised_prompt`) can change the copy | [1][3] OFF | Use the Images API for exact text; if using Responses, log `revised_prompt` and diff the quoted strings |
| F13 | **Quality-remap trap** (porting `high` gives half-budget renders) | [21][44][45] | Map gpt-image-2 `medium` → 2.5 `high` and `high` → `max` (§4.4) |
| F14 | **Model and quality not honoured on subscription routes** | [29][31][33][34] COM | API for anything that needs guarantees; log requested vs reported `quality` and `size` |
| F15 | **Experimental sizes (> 3.69 MP)**: tiling or noise reports (on gpt-image-2) and no guarantee | [1][4] OFF; vendor reports (search) | Prefer ≤ 2560×1440 plus a non-generative upscale for plates; test before using 4K or A-series experimental sizes in production |
| F16 | **Transparency artefacts** (checkerboard patterns seen in downloads) | [50] VEN (Reddit) | Decode and check alpha (R3 F20) |
| F17 | **Moderation blocks on edits** (`image_generation_user_error` / `moderation_blocked`, with `moderation_stage`) | [1] OFF | Don't auto-retry; rephrase; log `moderation_details` |

---

## Recommended request templates

All three use the API. `$OPENAI_API_KEY` stays in the environment; never log it. Placeholders are in `<…>`.

### T1 — Generate with 6 reference images at 1088×1360, `xhigh` (Images API, JSON body)

A new image made from references goes through `/v1/images/edits`; the generations endpoint takes no images [1]. The JSON body has been accepted since 2026-02-09 [10].

```http
POST https://api.openai.com/v1/images/edits
Content-Type: application/json
Authorization: Bearer $OPENAI_API_KEY
```

```json
{
  "model": "gpt-image-2.5-sunburst",
  "images": [
    { "file_id": "<file-id: product packshot, clean, high-res>" },
    { "file_id": "<file-id: person portrait, identity source>" },
    { "image_url": "data:image/png;base64,<logo PNG on flat background>" },
    { "image_url": "data:image/png;base64,<layout guide 1088x1360: flat colour blocks, no text>" },
    { "image_url": "data:image/jpeg;base64,<style reference>" },
    { "image_url": "data:image/png;base64,<text-free brand sheet: swatches + large specimen>" }
  ],
  "prompt": "Use case: Instagram feed post, vertical 4:5, launch announcement for LUMEN cold brew.\nInput images:\nImage 1 = PRODUCT, source of truth for the can: keep its exact shape, proportions, colours, materials and label layout; do not redraw, restyle or re-letter the label.\nImage 2 = PERSON identity: same person as Image 2; do not beautify, age or average the face; keep skin tone, hairstyle and proportions; natural skin texture.\nImage 3 = LOGO, for colour and shape awareness only: do not draw this logo anywhere; the grey zone in Image 4 stays plain background.\nImage 4 = LAYOUT GUIDE only: orange block = headline zone (top 26 %), blue block = can (right half, lower 60 %), green block = person (left half, lower 60 %), purple block = CTA pill (bottom-center), grey block = empty logo zone (top-left). Follow the zones' positions and proportions. Do not draw the guide: no blocks, outlines, guide colours or grid lines.\nImage 5 = STYLE reference: use only its soft window light from the left, warm-neutral grade and fine film texture; do not copy its subjects, layout or any text.\nImage 6 = BRAND SHEET: use its palette (deep espresso brown, cream, burnt orange) and the character of its condensed geometric sans; do not copy any text, swatches or labels from it.\nScene: a sunlit café counter, shallow depth, the person holding a glass of cold brew toward the can, candid, unretouched camera look.\nText (render exactly, each once, preserve case):\n1) \"COLD BREW IS BACK\" in the orange zone, condensed geometric sans, heavy weight, cream on espresso, two lines, left-aligned.\n2) \"Slow-steeped for 18 hours\" under it, same family, regular weight, cream, one line.\n3) \"Order now\" centred inside a burnt-orange pill in the purple zone, espresso text.\nConstraints: no other text anywhere (no taglines, numbers, prices, extra labels, watermarks or fake logos); the can keeps only its own label from Image 1; the grey logo zone is plain background; keep 6 % margins on all sides; flat, clean background areas without grain.",
  "size": "1088x1360",
  "quality": "xhigh",
  "background": "opaque",
  "output_format": "png",
  "moderation": "auto",
  "n": 2
}
```

**After the call:**

- Log `usage`, `quality` and `size` from the response [4].
- Downscale to 1080×1350.
- Composite the SVG logo into the grey zone.
- Run R3's OCR gate and the checks for annotation hue (guide colours) and flat-area noise.

**Cost:** about $0.165 per image, so about $0.33 for `n: 2` (§7).

**Codex variant:** at most 5 references, so drop Image 3. There are no `size` or `quality` fields, so put "vertical 4:5 portrait" in the first prompt line. Expect about 1.57 MP at the server's own quality.

### T2 — Mask edit of one region (Images API, JSON body)

The source is a design from T1 at 1088×1360. The job is to change the CTA pill's text and colour inside a known box, x 380–708 and y 1188–1276 px.

1. **Mask:** a 1088×1360 RGBA PNG, opaque everywhere except **alpha 0** inside the box dilated by 16 px. Polarity and code: master.md §9.3. Keep it under 4 MB [5].
2. **Request:**

```json
{
  "model": "gpt-image-2.5-sunburst",
  "images": [
    { "image_url": "data:image/png;base64,<ORIGINAL design, 1088x1360>" }
  ],
  "mask": { "image_url": "data:image/png;base64,<MASK, 1088x1360, alpha 0 = editable>" },
  "prompt": "The same Instagram post, unchanged, except the call-to-action pill at the bottom centre: the pill is now deep green and reads exactly \"Order today\" in the same condensed geometric sans, heavy weight, cream, centred, one line, same pill size, position, corner radius and shadow. Keep every other pixel, text, colour, person, product and margin exactly as in the image. Do not add any text.",
  "size": "1088x1360",
  "quality": "high",
  "output_format": "png",
  "n": 2
}
```

Notes:

- Describe the **whole final image** in the prompt, as OpenAI's own mask example does [1].
- `size` must equal the source size, so the composite aligns without resampling.
- Alternative for a small target: crop a window (for example 544×544 around the pill), resize it to 1024×1024, make the matching mask, edit, resize back, then composite (§1.7) [35].
- Optional extra (§2.3A): add a second image, the marked-up copy, as a semantic pointer, and add the "do not reproduce the marks" line. The mask still decides the region.

3. **Composite:** feather 4–8 px and take only the masked box from the output (master.md §9.4). Outside the box, the diff against the original must be exactly 0. Then OCR "Order today".

**Multipart equivalent:** `curl -F "model=gpt-image-2.5-sunburst" -F "image[]=@design.png" -F "mask=@mask.png" -F "prompt=…" -F "size=1088x1360" -F "quality=high"` [1].

### T3 — Multi-turn edit via the Responses API

Use this when a conversational chain helps, for example review comments applied one at a time. Responses rewrites prompts (`revised_prompt`), so exact-copy edits belong in T2 [1][3].

**Turn 1:**

```http
POST https://api.openai.com/v1/responses
```

```json
{
  "model": "gpt-5.4-mini",
  "instructions": "Always call the image_generation tool exactly once. Pass the user's instruction to the tool verbatim, including quoted text and letter case. Do not add creative details.",
  "input": [
    {
      "role": "user",
      "content": [
        { "type": "input_text", "text": "Edit Image 1: move the person slightly left so her shoulder no longer touches the headline zone. Keep her identity, pose, clothing, the can, all text, colours and margins exactly the same. Do not add any text." },
        { "type": "input_image", "file_id": "<file-id: ORIGINAL design>" }
      ]
    }
  ],
  "tools": [
    {
      "type": "image_generation",
      "model": "gpt-image-2.5-sunburst",
      "action": "edit",
      "size": "1088x1360",
      "quality": "high",
      "background": "opaque",
      "output_format": "png"
    }
  ],
  "tool_choice": { "type": "image_generation" },
  "store": true
}
```

The response includes an `image_generation_call`: `{id: "ig_…", result: <base64>, revised_prompt, action, quality, size, …}` [6]. Save the PNG and log `revised_prompt`.

**Turn 2** (stateful):

```json
{
  "model": "gpt-5.4-mini",
  "previous_response_id": "<resp_… from turn 1>",
  "input": [
    { "role": "user", "content": [ { "type": "input_text", "text": "Now warm the light on the counter slightly; change nothing else, including all text and the person." } ] }
  ],
  "tools": [ { "type": "image_generation", "model": "gpt-image-2.5-sunburst", "action": "edit", "size": "1088x1360", "quality": "high", "output_format": "png" } ],
  "tool_choice": { "type": "image_generation" }
}
```

**Turn 2** (stateless alternative) — reference the previous image by id [1]:

```json
{
  "model": "gpt-5.4-mini",
  "input": [
    { "role": "user", "content": [ { "type": "input_text", "text": "Now warm the light on the counter slightly; change nothing else." } ] },
    { "type": "image_generation_call", "id": "<ig_… from turn 1>" }
  ],
  "tools": [ { "type": "image_generation", "model": "gpt-image-2.5-sunburst", "action": "edit", "size": "1088x1360", "quality": "high" } ],
  "tool_choice": { "type": "image_generation" }
}
```

Rules:

- Always set the tool `model`; its default is `gpt-image-1` [6].
- `action: "edit"` without an image in context returns an error [1].
- A mask can go in the tool config as `input_image_mask: {"file_id": "<mask>"}`. Which context image it binds to in a multi-turn chain is undocumented (**UNVERIFIED**), so put masked edits in T2.
- Cached-image billing may apply to repeated references on this route [20].
- R3's stop rule applies: at most 2 chained generations, then go back to the original plus composites.
- `gpt-6-astra` works as the host model too, at about 13× the input and 11× the output token price of `gpt-5.4-mini` [12]. Whether a cheaper host affects tool-call quality is **UNVERIFIED**.

---

## C. Corrections to R3 and master.md

1. **master.md §2.4 and §9.8.** "'16 reference image' 2.5-e undocumented" is wrong. The SDK edit reference lists the 2.5 models and says "You can provide up to 16 images" [5] OFF. Curating 2–4 references is still good practice.
2. **R3 §1.1, transparency row.** PR #47484 `transparent_background` first ships in **`rust-v0.158.0-alpha.2`** (pre-release, 2026-09-23 13:07 UTC). It is not in 0.156.1 or 0.157.0-alpha.11 [26] SRC.
3. **R3 §1.1, `quality` row, "Always `auto`".** The client sends `auto`, but the server decides. Probes saw reported `quality=low` for `auto` and `medium` when `high` was requested, and output budgets of about 430–500 tokens at ~1.57 MP [29][31][34] COM, §6.3 DER.
4. **R3 §1.1, mask row.** Add: under 4 MB (SDK) vs under 50 MB (guide) conflict; images come before the text; the mask binds to image 1 [1][5][20].
5. **R3 §1.2, Story row.** Prefer exact 9:16 `1152x2048` or `1440x2560` over `1088x1920` (§5.2).
6. **master.md §3.3.** `2048x2048` is experimental under the pixel rule; `1920x1920` sits exactly at the threshold and is not (§5.1).
7. **master.md §9.0, "the model does not see what is under the mask".** Community tests conflict. An April test on gpt-image-2 kept a masked yarn ball, suggesting the content is visible [37]. A May test found masked content could not be described [38]. Treat it as unknown, and design so it doesn't matter: describe the full final image, then composite.
8. **R3 §12, "Does Codex's backend serve 2.5?"** Still unknowable from the client. New facts: the server alias is `gpt-image-2-codex`, model strings are not validated, and the token counts fit the 2.5 ladder (§6.2–6.3).
9. **Vendor claim that 2.5 is unusable in Responses.** Wrong [45]. The model page's "Responses: Not supported" refers to using 2.5 as the top-level model; 2.5 is supported as the `image_generation` tool model [1][3][7].
10. **master.md §11.9, "Tier 1 = 5 image/min".** Confirmed for both 2.5 models [7][8].
11. **R3 §1.6.** Add the LMArena Text Rendering and Commercial Design category tables (§4.1); R3 listed text leadership as UNVERIFIED.

---

## O. Open questions

1. How ChatGPT turns Comment, Markup and Select into model input (mask, coordinates, annotated image or text). Undocumented.
2. Whether `/backend-api/codex/*` serves 2.5 weights, and whether openai/codex will expose a model or quality selector (#43965).
3. Whether 2.5 accepts, ignores or rejects `input_fidelity`.
4. The mask file limit: 4 MB or 50 MB. And is the mask billed as image input?
5. Whether the ~1,536-patch input cap is the same for Responses-tool inputs, and whether `detail: "original"` on `input_image` changes what the image model receives.
6. Whether "first image gets extra richness" holds on 2.5.
7. Our own eval of annotated-image editing on 2.5: success rate and leak rate by mark type (box vs arrow vs circle) and by route (API with mask vs Codex without).
8. Whether percentage coordinates are honoured on 2.5 (shared with R3 §12).
9. 2.5 text accuracy by quality (`high`/`xhigh`/`max`) × size × string count, for Latin and Bengali. Nothing public.
10. Grain and noise incidence by model (Flare vs Sunburst vs gpt-image-2) and by quality, on flat-background design plates.
11. Failure and artefact rates at experimental sizes (1824×2560, 2384×3344, 3840×2160) on 2.5.
12. Whether the IPM limit counts each of `n` images separately.
13. A working Responses example showing cached-image pricing [20].
14. Whether Higgsfield's `gpt_image_2_5` supports masks and explicit `xhigh`/`max`, and what it costs per render.

---

## Sources

Accessed 2026-09-23 unless marked.

**OpenAI — official documentation, announcements, staff replies**

1. Image generation guide (2.5 overview, Responses multi-turn, `action`, edits, mask requirements, sizes, limitations, moderation errors, costs; `input_fidelity` section for gpt-image-2) — https://developers.openai.com/api/docs/guides/image-generation (`.md` version read)
2. Image prompting guide, GPT Image 2.5 (model choice, parameters, fundamentals, edit examples incl. sketch-to-render, identity, combine references; GPT Image 2 tab) — https://developers.openai.com/api/docs/guides/image-prompting
3. Image generation tool (Responses): tool options, `action`, revised prompt, prompting tips, supported host models — https://developers.openai.com/api/docs/guides/tools-image-generation
4. Images API reference: Create image edit (JSON body `images`, `mask`, `input_fidelity`, `size` wording "maximum supported resolution is 3840x2160"; response `usage`) — https://developers.openai.com/api/reference/resources/images
5. Python SDK `images.edit` reference (up to 16 images incl. 2.5; mask "less than 4MB"; prompt 32,000 chars; n 1–10; `input_fidelity` ignored by gpt-image-2) — https://developers.openai.com/api/reference/python/resources/images/methods/edit
6. Responses `create` reference: `ImageGeneration` tool (`action`, `input_image_mask`, `input_fidelity` text, `model` default gpt-image-1) and `ImageGenerationCall` — https://developers.openai.com/api/reference/resources/responses/methods/create
7. Model page `gpt-image-2.5-sunburst` (snapshot 2026-09-08, endpoints, Batch not supported, rate limits per tier) — https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst
8. Model page `gpt-image-2.5-flare` (same limits) — https://developers.openai.com/api/docs/models/gpt-image-2.5-flare
9. API pricing (image-generation token rates; Batch table without 2.5) — https://developers.openai.com/api/docs/pricing
10. API changelog (2026-09-08 2.5 release; 2026-02-09 JSON requests on `/v1/images/edits`; 2025-06-13 reusable prompts) — https://developers.openai.com/api/docs/changelog
11. Images and vision guide (32-px patch tokenization; GPT Image input pricing pointer) — https://developers.openai.com/api/docs/guides/images-vision
12. Model pages `gpt-6-astra` and `gpt-5.4-mini` (supported tools incl. `image_generation`; prices) — https://developers.openai.com/api/docs/models/gpt-6-astra · https://developers.openai.com/api/docs/models/gpt-5.4-mini
13. "Introducing ChatGPT Images 2.5" (published 2026-09-08; Sketch, templates, comments, shared prompts, API models, availability incl. Codex) — https://openai.com/index/introducing-chatgpt-images-2-5/ (read via browser; direct fetch returned 403)
14. ChatGPT Images 2.5 System Card (2026-09-08) — https://deploymentsafety.openai.com/chatgpt-images-2-5
15. OpenAI Help Center, "Images in ChatGPT" (editor, selection tool, comments on mobile, Sketch steps, Templates, prompt sharing; updated about 2026-09-10) — https://help.openai.com/en/articles/11084440-images-in-chatgpt
16. OpenAI Help Center, "API Organization Verification" — https://help.openai.com/en/articles/10910291-api-organization-verification
17. learn.chatgpt.com, "Image generation" (Codex app Canvas view Comment and Multi-select; built-in uses gpt-image-2; multi-reference wording) — https://learn.chatgpt.com/docs/image-generation
18. OpenAI Academy, "Creating images with ChatGPT" (2026-04-10; multiple images by order; text specs incl. "72pt") — https://openai.com/academy/image-generation/
19. Cookbook, "Generate images with high input fidelity" (gpt-image-1; first image preserved with extra richness) — https://developers.openai.com/cookbook/examples/generate_images_with_high_input_fidelity
20. OpenAI forum, "GPT Image 2 and 2.5: zero cached image inputs despite reusing reference images" — OpenAI Support replies 2026-09-21 and 2026-09-22 (no cached pricing on `/images/edits`; images before text; mask on first image) — https://community.openai.com/t/gpt-image-2-and-2-5-zero-cached-image-inputs-despite-reusing-reference-images/1396063
21. OpenAI forum, "Introducing GPT Images 2.5 in the API and ChatGPT" (announcement plus replies 2026-09-08→22: token remap, latency test, 1,536-patch input cap, the 1248×1248 `max` = 8,197 tokens bill, C2PA "2.0", solid-background symptoms, sam.saffron's term-llm claim, ChatGPT routing claim) — https://community.openai.com/t/introducing-gpt-images-2-5-in-the-api-and-chatgpt/1395897

**Source code read (SRC)**

22. openai/codex `codex-rs/ext/image-generation/src/tool.rs` (lines 59–60 `IMAGE_MODEL`, `MAX_EDIT_IMAGES`; request builder; path order) at main `8f1490eab` (2026-09-23 17:08 UTC) and tag `rust-v0.158.0-alpha.2`; tool description `imagegen_description.md` — https://github.com/openai/codex/blob/main/codex-rs/ext/image-generation/src/tool.rs
23. openai/codex `codex-rs/codex-api/src/images.rs` (request structs; `ImageQuality` enum) and `codex-rs/codex-api/src/endpoint/images.rs` (`images/generations`, `images/edits`) — https://github.com/openai/codex/tree/main/codex-rs/codex-api/src
24. openai/codex `codex-rs/features/src/lib.rs` (`image_generation` feature flag) — https://github.com/openai/codex/blob/main/codex-rs/features/src/lib.rs
25. openai/codex imagegen system skill: `SKILL.md` (role labels, "Input images: <Image 1: role…>") and `scripts/image_gen.py` (`DEFAULT_MODEL`, allowed qualities and sizes), last change `84aa75204` (2026-09-01) — https://github.com/openai/codex/tree/main/codex-rs/skills/src/assets/samples/imagegen
26. openai/codex releases (0.156.1, 0.157.0-alpha.11, 0.158.0-alpha.2) and `compare 40eac3ce8…tags`; commit history of tool.rs and images.rs; Codex config reference (no image-model key) — https://github.com/openai/codex/releases · https://developers.openai.com/codex/config-file/config-reference
27. openai/skills `hatch-pet` (`SKILL.md` layout-guide rule and QA; `scripts/prepare_pet_run.py` role strings "do not draw the guide") — https://github.com/openai/skills/tree/main/skills/.curated/hatch-pet
28. openai/openai-imagegen-demo (2.5 model ids; `/images/edits` streaming at 1024×1536 high) — https://github.com/openai/openai-imagegen-demo

**GitHub issues (COM)**

29. openai/codex #43965 "Expose effective image model and supported model selection for built-in image_gen (Images 2.5)", 2026-09-09, open, with probe comments by Joeywrz (2026-09-10) and Dr-Amp (2026-09-14) — https://github.com/openai/codex/issues/43965
30. openai/codex #44369 (closed as a duplicate, 2026-09-10) and #45452 "C2PA provenance does not distinguish Codex, GPT Image 2.5 Flare, and Sunburst outputs" (2026-09-14) — https://github.com/openai/codex/issues/44369 · https://github.com/openai/codex/issues/45452
31. openai/codex #28723 "Codex API image_generation silently ignores size/quality and returns gpt-image-2-codex auto output" (2026-06-17, open); also #33050 (latency variance) — https://github.com/openai/codex/issues/28723
32. openai/codex #44039 "built-in image tool unavailable on Images 2.5 rollout day" (2026-09-09) — https://github.com/openai/codex/issues/44039
33. NousResearch/hermes-agent #107233 "Codex OAuth image route does not enforce the image_generation tool spec" (2026-09-10; closed via #111000, 2026-09-14) — https://github.com/NousResearch/hermes-agent/issues/107233
34. diegosouzapw/OmniRoute #14617 (2026-09-23; hosted tool pinned to `gpt-image-2-codex`; native images route ignores `size`; per-sample dimensions and `usage.output_tokens`) — https://github.com/diegosouzapw/OmniRoute/issues/14617

**OpenAI forum threads (COM)**

35. "Improving Precision Image Editing with GPT-Image 2.5 API" (2026-09-16; comment/brush/markup pipeline, crop-to-1024 plus composite) — https://community.openai.com/t/improving-precision-image-editing-with-gpt-image-2-5-api/1398022
36. "GPT Image 2.5 for Professional Architectural Workflows…" (2026-09-10; preservation strength, ChatGPT resolution about 1.5–1.6 k px, clone-stamp textures) — https://community.openai.com/t/gpt-image-2-5-for-professional-architectural-workflows-native-2k-4k-web-editing-sunburst-controls-and-fixing-repetitive-clone-stamp-ai-artifacts/1396281
37. "GPT Image 2 Masking Issue" (2026-04-22; mask test; `input_fidelity` error on gpt-image-2) — https://community.openai.com/t/gpt-image-2-masking-issue/1379510
38. "Understanding how gpt-image models on edits see 'mask' and transparency" (2026-05-25) — https://community.openai.com/t/understanding-how-gpt-image-models-on-edits-see-mask-and-transparency/1381752
39. "Image-2.5 in codex with oauth" (2026-09-19; unanswered) — https://community.openai.com/t/image-2-5-in-codex-with-oauth/1399182

**Press, reviews, vendors**

40. TechRadar, Graham Barlow, "ChatGPT Images 2.5 is out — I've been testing it for 24 hours…" (2026-09-09; Edit toolbar Markup, Comment, Remove BG, Erase, Resize; Sketch; Templates) — https://www.techradar.com/ai-platforms-assistants/chatgpt/chatgpt-images-2-5-is-out-ive-been-testing-it-for-24-hours-and-these-are-the-3-new-features-youll-actually-use
41. TechRadar, Eric Hal Schwartz, "'The noise patterns are awful'…" (2026-09-10; 4-image grain test) — https://www.techradar.com/ai-platforms-assistants/the-noise-patterns-are-awful-some-reddit-users-arent-happy-with-the-new-chatgpt-images-2-5-so-i-did-my-own-tests-and-have-to-agree
42. Puter, Reynaldi Chernando, "GPT Image 2.5 Review" (2026-09-11; 0.22 % outside-edit change, face SSIM 0.889, poster casing) — https://developer.puter.com/blog/gpt-image-2-5-review/
43. MindStudio, "GPT Image 2.5 Review: OpenAI's Flare and Sunburst Models Tested" (2026-09-10) — https://www.mindstudio.ai/blog/gpt-image-25-review
44. Tosea.ai, "How to Use GPT Image 2.5: Complete Guide" (2026-09-09; matched-budget latency, token table, deck text) — https://tosea.ai/blog/gpt-image-2-5-complete-guide
45. Pixmax, "GPT Image 2.5 Review: Flare is 47 % Faster, But Watch the Quality Trap" (undated, after 2026-09-08; chained-edit drift) — https://www.pixmax.ai/blog/gpt-image-2-5-review-flare-sunburst.html
46. IMG.LY AI benchmarks: GPT Image 2.5 Flare / Sunburst (undated) — https://img.ly/ai-benchmarks/models/gpt-image-2-5-flare/ · https://img.ly/ai-benchmarks/models/gpt-image-2-5-sunburst/
47. Hacker News, "ChatGPT Images 2.5" (2026-09-08→; latency 104 s → 35–40 s; micro-glyphs; edit detail loss) — https://news.ycombinator.com/item?id=49614720
48. Atlas Cloud blogs: "GPT Image 2.5 image comments" (2026-09-16) and "ChatGPT Image 2.5 Sketch… Canvas Workflow" (Kishi, 2026-09-14) — https://www.atlascloud.ai/blog/tips/gpt-image-2.5-image-comments · https://www.atlascloud.ai/blog/tips/gpt-image-2.5-sketch-workflow
49. image3.org, "AI Image Annotation Editor" (undated; clean-plus-annotated two-image method) — https://image3.org/ai-image-annotation-editor
50. Freyavideo, "GPT Image 2.5 noise and editing" (2026-09-09) — https://freyavideo.com/blog/gpt-image-2-5-noise-editing
51. APIYI, "GPT-image-2 API font prompt complete guide" (2026-05-06) — https://help.apiyi.com/en/gpt-image-2-api-font-prompt-typography-guide-en.html

**Benchmarks and papers**

52. LMArena leaderboards, snapshot 2026-09-21: text-to-image Overall, **Text Rendering**, **Product, Branding & Commercial Design**; Image Edit — https://arena.ai/leaderboard/text-to-image · https://arena.ai/leaderboard/text-to-image/text-rendering · https://arena.ai/leaderboard/text-to-image/commercial-design · https://arena.ai/leaderboard/image-edit
53. PaintBench: Deterministic Evaluation of Precise Visual Editing, Xu, Brown et al., NYU, arXiv 2606.00188v1 (2026-05-29) — https://arxiv.org/abs/2606.00188
54. VIBE: A Systematic Benchmark for Visual Instruction-Driven Image Editing, arXiv 2602.01851v2 (2026-05-21) — https://arxiv.org/abs/2602.01851

**Other**

55. higgsfield-ai/skills `higgsfield-generate/references/model-catalog.md` (main, 2026-09-11/14: `gpt_image_2_5` default, Flare/Sunburst, quality through `max`); see also R1 §A.5 — https://github.com/higgsfield-ai/skills/blob/main/higgsfield-generate/references/model-catalog.md
56. Local: `design-research/R3-gpt-image-design-prompting.md` (§0–§1, §6, §7, §12, §13) and `~/.claude/skills/codex-imagegen/references/master.md` (§3, §9, §14) — read 2026-09-23
