# The research behind the nexa-remotion family

Notes made on 2026-09-25 and 26 by reading, in full, every page of the Remotion docs (1,103 pages), the rest of
remotion.dev (182 pages: Elements, prompts, templates, blog, learn, experts), the Remotion monorepo's plugins, skills,
evals, MCP server, example project, the team's own videos and the 20 templates, 32 example repositories of the Remotion
organisation, and the wider community (tutorials, agent skills, discussions, issues, competing tools, motion craft).
Each file has a coverage list of what was read (kept in the research folder, not here).

They are written in our own words, with code snippets under 15 lines. The installed Remotion is **4.0.528**; the docs
describe 4.0.529 and later in places, so every API has a version tag: anything above 4.0.528 is not available here.
Where the docs, the official skills or templates are wrong, the notes say so.

Every file follows the same sections: 1 scope and coverage, 2 mental model, 3 API digest, 4 recipes, 5 performance
and render stability, 6 errors and fixes, 7 what our skills must teach, 8 best examples, 9 open questions.

| File | Covers |
|---|---|
| `D1-core-a.md` | interpolate, Easing, interpolateColors, spring, measureSpring, Composition, calculateMetadata, AbsoluteFill, Loop, Freeze, props and schemas, Interactive, delayRender, assets and images, fonts, effects overview, config, codecs, GL, CLI, Docker, HDR, migrations |
| `D2-core-b.md` | hooks, Sequence and Series with the timing model, assets and loading, the three video tag families, audio, 3D and ThreeCanvas, props and visual editing, rendering and output, integrations, licensing terms |
| `D3-lambda-cloud.md` | Lambda (functions, sites, renders, concurrency, costs, webhooks, privacy, debugging), Cloud Run, Vercel Sandbox |
| `D4-render-studio-player.md` | renderer APIs, CLI, the encoding matrix, the Studio as an editor, the Studio protocol, the Player, preload, browser bundler, client-side rendering, HtmlInCanvas, codemods, licensing |
| `D5-effects-canvas.md` | all 74 @remotion/effects with parameters, ranges and cost; createEffect; canvas components; HtmlInCanvas; light leaks; starburst; motion blur; noise; animation-utils |
| `D6-graphics-text.md` | paths, shapes, transitions (including the shader ones and pushCut), fonts, layout-utils, rough-notation, rounded-text-box, Lottie, GSAP, Rive, GIF, animated emoji, cursors |
| `D7-media-audio-captions.md` | @remotion/media Video and Audio, trims and speed, volume, captions and paging, sound effects and their licences, Whisper (cpp, web, WebGPU), ElevenLabs and OpenAI transcripts, video matting, the Recorder template |
| `D8-parser-webcodecs-editor-ai.md` | media parser, WebCodecs, Mediabunny, the editor starter, AI features, MCP, prompt-to-video systems |
| `S1-site.md` | remotion.dev: the 41 Elements with their motion and visual language, the prompt showcase with a prompt style guide, templates, blog lessons |
| `R1-skills-plugins.md` | the 12 official skills, the Claude Code, Codex, Cursor and Kimi plugins, evals, the MCP server, gaps |
| `R2-team-videos.md` | the Remotion team's own video productions and their code patterns |
| `R3-templates-examples.md` | every template and example repository, with a technique index and the trailers' motion language |
| `C1-community.md` | community libraries and agent skills, measured motion craft, sound arithmetic, competing tools, the 25 most useful external resources |

Use the skills first (they hold the decisions); come here for depth, a version question or an error the skills do not
list. The official `remotion-best-practices` skills (installed separately) are the other API reference; these notes
say where they are wrong for 4.0.528.
