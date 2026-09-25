# Rendering in the cloud: Lambda, Vercel Sandbox, Cloud Run

## Where to render

| Situation | Choose |
|---|---|
| One or a few client deliverables, highest fidelity | the local Mac (default for agency work) |
| AV1 output or PDF stills | local |
| Bangla or other scripts without cloud fonts | local, or load web fonts and verify one cloud render first |
| Many personalised videos, a batch, a SaaS feature, fast turnaround on long videos | Lambda |
| The client's app lives on Vercel and wants no AWS | Vercel Sandbox (experimental: pin versions, test every upgrade) |
| The client mandates GCP | Cloud Run, with a written warning: alpha and no longer developed |
| Over about 80 minutes of Full HD, or outputs over about 5 GB | local or a long-running render server |
| Heavy WebGL or 3D | local with a GPU (Lambda has none: WebGL runs in software) |

## Safety and consent (non-negotiable)

- Never ask for, print, paste or type AWS, GCP or Vercel secrets. The person creates accounts, IAM users, keys and
  `.env` files; the agent only checks that the variables exist.
- Before the first deploy in an account, and before any batch, say what will be created and the expected cost, and
  wait for a yes. Cloud resources cost money.
- Destructive commands (`functions rmall`, `sites rmall`, anything with `-y`, deleting sites, renders or buckets,
  `services rmall`) need explicit confirmation naming the exact targets.
- Never call Lambda from browser code; render endpoints are authenticated and rate-limited.
- Licence: companies of 4 or more need cloud render seats; set `licenseKey`, and `isProduction: false` for tests.

## Lambda defaults on 4.0.528 (set them explicitly; the v5 defaults are not active)

- One region near the client's assets and audience (`us-east-1` by default); function, bucket and site together.
- Function: `memorySizeInMb` 2048 for motion graphics, 3009 for video-in-video, 4K or heavy scenes; `diskSizeInMb:
  10240` (the default is only 2048); `timeoutInSeconds: 240`; CloudWatch logs with 14 days retention. Keep the triple
  in one config file and derive the name with `speculateFunctionName()`.
- Site: `npx remotion bundle`, then `deploySiteFromBundle()` (4.0.497); name it `<client>-<project>-<env>`.
- Render from `@remotion/lambda/client`: `codec: 'h264'`, `colorSpace: 'bt709'`, `privacy: 'private'` with presigned
  links (7 days at most) for unreleased work, `downloadBehavior` for a clean file name, `deleteAfter` for temporary
  renders, `overwrite: true` when reusing keys, `enableCancellation: true` (4.0.515) for user-facing jobs, a webhook for
  batches and anything over a minute (HMAC-SHA512 signed, `customData` at most 1 KB).
- Progress: poll every second with `skipLambdaInvocation: true`; stop on `done` or `fatalErrorEncountered`; show
  `errors[0].message` and the CloudWatch links.
- Concurrency: the AWS limit is 1000 per region by default (as low as 10 on new accounts); default split at 30 fps is
  about 15 functions for 10 s, 45 for 30 s, 82 for 60 s, 150 for 10 minutes or more; at most 200 functions and at
  least 4 or 5 frames each; `concurrency: 1` (4.0.517) for tiny accounts.
- Everything the same version: the npm package, the deployed function and the site (4.0.528 here).
- Outputs are public by default; buckets created before 4.0.418 may even be listable.

## Pre-flight before any cloud render

1. Frame-pure composition: seeded randomness, no wall clock, no per-chunk network data (chunks render in separate
   browsers).
2. Every font a web font loaded before the frame; Bengali checked in a cloud test render (Lambda ships Noto for Latin,
   Arabic, Devanagari, Hebrew, Tamil, Thai and CJK on arm64, not Bengali). Emoji render as Noto, not Apple.
3. Assets via `staticFile()` or public HTTPS URLs reachable from AWS; big media on a cached CDN (each chunk downloads
   again); `@remotion/media` tags fetch only the parts they need; no localhost URLs.
4. JSON-serialisable `inputProps`; secrets in environment variables, never in the bundle.
5. Same versions everywhere; function, bucket and site in one region; quotas leave headroom.
6. Output under half the disk; codec supported (no AV1, no PDF).
7. Encoding options copied from the local config (the Node API ignores `remotion.config.ts`).
8. One test render reviewed (picture and cost) before a batch.

## Debugging, in this order

Reproduce with `npx remotion lambda render --log=verbose --props=props.json`; read the final error; CloudWatch
filtered by `method=renderer,renderId=X,chunk=N` or `method=launch,renderId=X`; the `chunks` list in `progress.json`;
classify (code error, delayRender timeout, chunk timeout, main timeout); fix; redeploy the site; render again. Two
different timeouts exist: `delayRender` in milliseconds and the function's in seconds. Ctrl+C in the CLI does not stop
a Lambda render unless it started with `--enable-cancellation`.

## Vercel Sandbox and Cloud Run

- Vercel Sandbox: experimental; 4 vCPU by default; Vercel functions stop at 800 s, so long renders run detached
  (4.0.469); snapshots cut cold starts; stop sandboxes when done; fonts undocumented (test Bangla).
- Cloud Run: alpha and no longer developed; one instance per render; 503 errors past the instance limit; do not run
  its installer for the user (it downloads and executes a script in their Cloud Shell): give them the steps.

Depth: `~/.claude/skills/nexa-remotion/references/kb/D3-lambda-cloud.md`.
