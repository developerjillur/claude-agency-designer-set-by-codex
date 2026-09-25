# D3-lambda-cloud: rendering Remotion in the cloud (Lambda, Cloud Run, Vercel Sandbox)

Knowledge file for the skill authors. Built from the 150 docs pages in `assign-D3-lambda-cloud.txt`, each read in full,
cross-checked against the option definitions of the installed `@remotion/renderer` 4.0.528 and against the Lambda and
Vercel code in `repo/packages/template-*` and `examples/github-unwrapped`.

---

## 1. Scope and coverage

- Assigned: 150 pages. Read fully: 150. Logged one path per line in `kb/D3-lambda-cloud.coverage.txt`; verified with
  `diff` that the coverage list equals the assignment list.
  - `mirror/docs/lambda/**`: 102 pages (17 CLI pages incl. overview, 6 troubleshooting, 2 "without IAM", 77 API,
    concept, guide, SDK and advisory pages; 2 of them are pure redirects: `downloadvideo.md`, `rendervideoonlambda.md`).
  - `mirror/docs/cloudrun/**`: 40 pages (15 CLI pages incl. overview, 25 API and concept pages).
  - `mirror/docs/vercel/**`: 8 pages.
- Nothing was unreadable. Limitation of the mirror: MDX components are not expanded, so some values only appear as tags
  (`<DefaultMemorySize/>`, `<DefaultTimeout/>`, `<DefaultLogRetention/>`, `<MinimumFramesPerLambda/>`,
  `<LambdaRegionList/>`, `<GcpRegionList/>`, `<UserPolicy/>`, `<RolePolicy/>`, `<SAPermissionList/>`,
  `<SAPermissionTable/>`, `<ConcurrencyCalculator/>`, `<WebhookTest/>`, and every `<Options id="..."/>`). Resolved as follows:
  - Lambda defaults (memory 2048 MB, timeout 120 s, log retention 14 days): stated in page prose and the example output of
    `functions deploy`.
  - Minimum `framesPerLambda`: stated as 5 in `concurrency.md` (see Open questions for a contradiction).
  - Region lists: printed in `lambda/cli/regions.md` and `cloudrun/cli/regions.md`.
  - `<Options id>` descriptions and defaults: read from
    `nexa-media/remotion-broll/node_modules/@remotion/renderer/dist/options/*.js` (version 4.0.528), so the defaults
    quoted here are the ones on our machine.
  - Not resolvable offline: the literal JSON of the Lambda user/role policies and the GCP service-account permission list.
    The Lambda permission table (every action and why) is in prose and is summarised below. Get the JSON at runtime with
    `npx remotion lambda policies user|role` and `npx remotion cloudrun permissions`.
- Cross-reference reads outside the assignment (not in the coverage file, used for context only): `docs/compare-ssr.md`,
  `docs/vercel-sandbox.md`, `docs/lambda.md`, `docs/config.md` (first lines), `docs/transparent-videos.md` (Lambda
  section), a grep of `docs/5-0-migration.md`, the templates `template-next-app-tailwind`, `template-react-router`,
  `template-vercel`, `template-render-server`, the examples `github-unwrapped`, `template-prompt-to-motion-graphics-saas`,
  `cloudflare-containers-demo`, and `~/.claude/skills/remotion-saas/rendering.md`.
- Version lens: installed Remotion is 4.0.528, so everything documented up to v4.0.517 is available (cancellation 4.0.515,
  China regions 4.0.510, `concurrency: 1` 4.0.517, `deploySiteFromBundle` 4.0.497, Vercel detached renders 4.0.469).
  Many pages also describe Remotion 5.0 defaults (disk 10240 MB, `overwrite: true`, `x264Preset: 'veryfast'`,
  Cloud Run `maxInstances` 5, render APIs only in `@remotion/lambda/client`). Those are NOT active on 4.0.528. The v4
  defaults are given below and our skills should set the good v5 values explicitly.

---

## 2. Mental model

### 2.1 Remotion Lambda: three objects, one region

| Object | What it is | Name | Redeploy when |
|---|---|---|---|
| Function | A Remotion-owned binary (Chrome + FFmpeg + orchestrator). Contains none of your code. The same code runs for every Remotion user. | `remotion-render-4-0-528-mem2048mb-disk10240mb-240sec` (version, memory, disk, timeout) | Remotion upgrade, or new memory/disk/timeout |
| Bucket | One S3 bucket per region per account, with `sites/` and `renders/` folders | `remotionlambda-<region without dashes>-<random>`, e.g. `remotionlambda-apsouth1-3ysk0nyazp` | Never |
| Site | Your bundled project uploaded to `sites/<siteName>/`, public over HTTPS. Its URL is the Serve URL | `https://remotionlambda-xxx.s3.<region>.amazonaws.com/sites/<siteName>/index.html`, shorthand: `<siteName>` | Any code or asset change, or a Remotion upgrade |

Render flow (architecture since v4.0.165):
1. `renderMediaOnLambda()` invokes one function: the main (launch) function.
2. It opens the Serve URL in headless Chrome, finds the composition and runs props resolution (`calculateMetadata()`), which
   fixes duration, size and fps.
3. It splits the frames into chunks and invokes one renderer function per chunk. With `concurrency: 1` (v4.0.517+) it
   renders everything itself.
4. Renderers stream progress and binary chunks back with AWS Lambda Response Streaming.
5. The main function merges progress into `renders/<renderId>/progress.json` in S3, periodically.
6. `getRenderProgress()` reads that file (through a Lambda invocation by default, or directly from S3 with
   `skipLambdaInvocation`).
7. When all chunks arrived, the main function concatenates them seamlessly (algorithm not public), uploads
   `renders/<renderId>/out.<ext>` and exits.

What an agent must internalise:
- Video/audio renders are asynchronous: the call returns `{renderId, bucketName}` quickly; you poll or receive a webhook.
  Stills (`renderStillOnLambda()`) are synchronous.
- Chunks render independently in separate browsers, each starting at its own first frame. A frame must be a pure function
  of `useCurrentFrame()` and props, or chunk boundaries glitch.
- Every chunk downloads the assets it references over HTTP. Big assets are paid once per chunk (S3 egress applies even
  inside one region) and can trip rate limits on third-party hosts.
- Version lock: the `@remotion/lambda` client, the function and the site should all be the same Remotion version.
- One function serves all projects, clients and environments. Separate environments with site names, not with functions or
  buckets. Duplicate identical functions achieve nothing (the concurrency limit is per region and account, not per function).
- The Serve URL is public. Never put secrets in the bundle; pass them as `inputProps` or `envVariables` (never public).
- Rendered files are public by default (`privacy: 'public'`).

### 2.2 "Concurrency" means different things (a frequent trap)

| Term | On Lambda | Locally, on Cloud Run, on Vercel |
|---|---|---|
| `concurrency` | Number of renderer functions for one render, 1 to 200 (v4.0.322). `1` = render on the main function (v4.0.517) | Browser tabs on one machine (`"50%"`, `8`) |
| `framesPerLambda` | Frames per chunk; functions = ceil(frames / framesPerLambda) | n/a |
| `concurrencyPerLambda` | Browser tabs inside each function, default 1 (v3.0.30) | n/a |
| Account limit | Concurrent executions per region per account: 1000 default, can be 10 on new accounts | Cloud Run: max instances; Vercel: concurrent sandboxes |

Also two `--timeout` flags: on `lambda functions deploy` it is the function timeout in seconds; on `lambda render`,
`still` and `compositions` it is the `delayRender()` timeout in milliseconds.

### 2.3 Cost model

Lambda bill = sum over all invocations (main, renderers, progress calls) of duration x memory (GB) x regional
GB-second price, plus request fees, plus ephemeral storage (under 1 percent even at 10 GB), plus S3 egress for every asset
the headless browsers fetch, plus S3 storage for sites and renders, plus CloudWatch logs. Companies with more than 3 people
also need Remotion cloud rendering seats (Company License). Levers: less memory is linearly cheaper; lower concurrency has
less overhead (cheaper, slower); more memory gives more vCPU (faster, pricier).

### 2.4 The render targets side by side

| | Local Mac (`npx remotion render`, `renderMedia()`) | Remotion Lambda | Vercel Sandbox (`@remotion/vercel`) | Cloud Run (`@remotion/cloudrun`) |
|---|---|---|---|---|
| Status | Stable | Stable; Remotion's default recommendation | Experimental since v4.0.426 (breaking changes allowed) | Alpha, not actively developed |
| Parallelism | One machine, tabs | Distributed chunks, up to 200 functions | One VM (default 4 vCPU, 8 GB) | One instance per render |
| Speed | Machine bound | Fastest | Slower; VM cold start (snapshots help) | One instance |
| Length limit | None | About 80 min Full HD (15 min function limit); output about half the disk (10 GB disk: about 2 h 40 min 1080p) | Sandbox 45 min (Hobby) or 5 h (Pro/Enterprise); function 800 s unless detached | Service timeout up to 3600 s; output bounded by memory |
| Codecs | All, incl. AV1 and PDF stills | No AV1, no PDF stills | Renderer codecs | API: h264, vp8, prores, mp3, aac, wav (CLI also lists h265, png) |
| GPU | Possible | None (WebGL uses software `swangle`) | None | Untested |
| Fonts | Mac system fonts plus web fonts | Small Noto set only (section 3.6) | Undocumented | Undocumented |
| Progress | Callbacks | `getRenderProgress()`, webhooks | Callbacks; `getRenderProgress()` for detached | Callback, progress webhook |
| Cancel | Abort the process | `enableCancellation` + `cancelRenderOnLambda()` (v4.0.515) | `sandbox.stop()` | Not documented |
| Compute price | Machine you already own | Highest per render, pay per use | Pay per VM time | Cheaper than Lambda, pay per use |
| Best for | Client deliverables, max fidelity, long renders | Personalised video at scale, SaaS, batches, fast long renders | Apps already on Vercel, no AWS | Only when a client mandates GCP |

---

## 3. API digest

Conventions: "v" is the version a feature appeared in. Import render-time functions from `@remotion/lambda/client`
(light, bundleable, and the only place they exist in v5). Import infrastructure functions (`deployFunction`,
`deploySiteFromBundle`, `getOrCreateBucket`, `deleteFunction`, `getUserPolicy`, `estimatePrice`, `simulatePermissions`,
`downloadMedia`) from `@remotion/lambda`.

### 3.1 Credentials, regions and environment variables

| Variable | Scope | Notes |
|---|---|---|
| `REMOTION_AWS_PROFILE` or `AWS_PROFILE` | CLI + Node | Profile from `~/.aws/credentials` (v3.3.9). Checked first |
| `REMOTION_AWS_ACCESS_KEY_ID` + `REMOTION_AWS_SECRET_ACCESS_KEY` | CLI + Node | Preferred; wins over `AWS_*` if both are set |
| `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` (+ `AWS_SESSION_TOKEN` for roles) | CLI + Node | Reserved on Vercel; inside Lambda/Vercel functions these hold the platform's own credentials |
| `REMOTION_AWS_REGION` (or `AWS_REGION` locally) | CLI only | Default `us-east-1`. Node APIs ignore it: pass `region` every time |
| `REMOTION_SKIP_AWS_CREDENTIALS_CHECK` | v4.0.160 | Lets the SDK use instance metadata or role credentials; the client is then cached for the process lifetime |
| `REMOTION_S3_OUTPUT_PROVIDER_ACCESS_KEY_ID` / `_SECRET_ACCESS_KEY` | CLI | Credentials for `--s3-output-provider-endpoint` |
| `REMOTION_GCP_REGION` | Cloud Run CLI | Default `us-east1` |
| `BLOB_READ_WRITE_TOKEN` | Vercel | Vercel Blob read/write token |

- The CLI loads `.env` automatically (`--env-file` for another path). Node APIs never do: load it with `dotenv`.
- `remotion.config.ts` has no effect on SSR/Node APIs (confirmed in `docs/config.md`). The Lambda CLI respects it
  (Webpack override and caching are honoured when deploying from the CLI since Sept 2021; `compositions` accepts `--config`).
- AWS clients are cached per credentials + region. Rotating accounts = setting the `REMOTION_AWS_*` variables before the
  next call (documented pattern, used in production by GitHub Unwrapped).

### 3.2 Lambda infrastructure APIs

**`deployFunction(options)`** (`@remotion/lambda`). Creates the function; idempotent (returns the existing one when
version, memory, disk and timeout match).
- `region` (required), `timeoutInSeconds` (required, up to 900; docs recommend 120 or less and raising concurrency instead),
  `memorySizeInMb` (required, 512 to 10240, docs recommend 2048), `createCloudWatchLogGroup?` (recommended true),
  `cloudWatchLogRetentionPeriodInDays?` (14), `diskSizeInMb?` (512 to 10240; default 2048 on v4, 10240 on v5),
  `customRoleArn?` (default `arn:aws:iam::<account>:role/remotion-lambda-role`), `enableLambdaInsights?` (v4.0.61),
  `runtimePreference?` (v4.0.205: `'default'` = `'cjk'`, `'apple-emojis'`, `'cjk'`), `customLayerArns?` (v4.0.510,
  ordered non-empty list of versioned layer ARNs in the same region and partition; replaces all Remotion layers; required
  in China; not combinable with a non-default `runtimePreference`).
- Returns `{functionName, alreadyExisted}`.
- Gotchas: Insights and VPC settings are not applied to a function that already existed (delete, redeploy). Inside a
  serverless function it only works if the Remotion Lambda deployment files are shipped with it; run deploys from a
  script or CI instead.

```ts
import {deployFunction} from '@remotion/lambda';
const {functionName, alreadyExisted} = await deployFunction({
  region: 'us-east-1',
  memorySizeInMb: 2048,
  diskSizeInMb: 10240,
  timeoutInSeconds: 240,
  createCloudWatchLogGroup: true,
});
```

**`speculateFunctionName({memorySizeInMb, diskSizeInMb, timeoutInSeconds})`** (v3.3.75, light client): returns
`remotion-render-<version with dashes>-mem<M>mb-disk<D>mb-<T>sec` using the installed package version. Saves the
`getFunctions()` round trip (up to 1 s) and is required for `skipLambdaInvocation`. If unsure the function exists, call
`getFunctionInfo()` and catch.

**`getFunctions({region, compatibleOnly, logLevel?})`** (light client): `[{functionName, memorySizeInMb, diskSizeInMb,
version, timeoutInSeconds}]`. With `compatibleOnly: true` it is empty after an upgrade until a new function is deployed.
**`getFunctionInfo({region, functionName, logLevel?})`**: same fields, throws if missing. **`deleteFunction({region,
functionName})`**: resolves to nothing, rejects on failure. (`logLevel` on both: v4.0.115.)

**`getOrCreateBucket({region, enableFolderExpiry?, forcePathStyle?})`** (`@remotion/lambda`): `{bucketName,
alreadyExisted}` (`alreadyExisted` v3.3.78). `enableFolderExpiry` (v4.0.32): `true` installs the lifecycle rules used by
`deleteAfter`, `false` removes them, default `null` leaves them alone. `onBucketEnsured` was removed in v4.

**`deploySiteFromBundle(options)`** (v4.0.497): uploads an existing bundle. Recommended over `deploySite()` because build
and deploy are separate steps (bundle once, deploy from CI or Docker).
- `bucketName`, `region`, `bundleDir` (must hold `index.html` and `bundle.js`; `npx remotion bundle` writes `./build`;
  `bundle()` returns the directory), `siteName?` (random if omitted; chars `0-9 a-z A-Z - ! _ . * ' ( )`),
  `options?.onUploadProgress({totalFiles, filesUploaded, totalSize, sizeUploaded})`,
  `options?.onDiffingProgress(bytes, done)`, `options?.bypassBucketNameValidation` (false), `privacy?` (`'public'` default
  or `'no-acl'`; the site must stay publicly readable), `throwIfSiteExists?` (false), `forcePathStyle?` (false),
  `requestHandler?`, `logLevel?`.
- Returns `{serveUrl, siteName, stats: {uploadedFiles, deletedFiles, untouchedFiles}}`. Incremental: uploads changed
  files and deletes stale ones.
- Gotchas: the bundle must be relocatable (default for `npx remotion bundle` from v4.0.497). Symlinked files are followed
  and uploaded; symlinked directories are rejected. Deploy only trusted artifacts. Not for serverless functions.

```ts
import path from 'path';
import {bundle} from '@remotion/bundler';
import {deploySiteFromBundle, getOrCreateBucket} from '@remotion/lambda';
const {bucketName} = await getOrCreateBucket({region: 'us-east-1', enableFolderExpiry: true});
const bundleDir = await bundle({entryPoint: path.resolve('src/index.ts')});
const {serveUrl} = await deploySiteFromBundle({bucketName, bundleDir, region: 'us-east-1', siteName: 'acme-promo-prod'});
```

**`deploySite(options)`**: deprecated, still works; bundles and uploads in one step (incremental since v3.3.7).
`entryPoint` (absolute), `bucketName` (created by Remotion Lambda), `region`, `siteName?`, `logLevel?` (v4.0.140),
`privacy?` (v3.3.97), `throwIfSiteExists?` (v4.0.141), `forcePathStyle?`, and `options`: `onBundleProgress(0..100)`,
`onUploadProgress`, `webpackOverride` (ignored when `rspack`), `bundlerOverride` and `rspackOverride` (v4.0.498),
`enableCaching`, `publicDir` and `rootDir` (v3.2.17), `ignoreRegisterRootWarning` (v3.3.55), `keyboardShortcutsEnabled`
and `askAIEnabled` (v4.0.407), `rspack` (v4.0.426). Returns `{serveUrl, siteName, stats}`.
- Gotcha: Node deploys do not read `remotion.config.ts`; pass the same Webpack override the project uses (the Next.js
  template passes `options: {webpackOverride}`), or bundle with the CLI and use `deploySiteFromBundle()`.
- Gotcha: sites live in a subdirectory, so absolute asset paths like `/logo.png` break. Use `staticFile()`.

**`getSites({region, forceBucketName?, compatibleOnly?})`** (light client since v3.3.42): `{sites: [{id, bucketName,
lastModified, sizeInBytes, serveUrl, version}], buckets: [{region, name, creationDate}]}`; `compatibleOnly` and `version`
since v4.0.435; `forceBucketName` since v3.3.102. **`deleteSite({region, bucketName, siteName, forcePathStyle?})`**:
`{totalSizeInBytes}`.

**`getRegions({enabledByDefaultOnly?})`**: regions supported by this release (`enabledByDefaultOnly` v3.3.11).

**`getUserPolicy({partition?})`** and **`getRolePolicy({partition?})`**: policy JSON for the IAM user and for
`remotion-lambda-role`. `partition`: `'aws'` (default) or `'aws-cn'` (v4.0.510). In serverless code import them from
`@remotion/lambda/policies`.

**`simulatePermissions({region, onSimulation?})`**: validates the user policy only (never the role policy) through the AWS
policy simulator; resolves `{results: [{decision: 'allowed' | 'implicitDeny' | 'explicitDeny', name}]}`; does not throw
for missing permissions. CLI: `npx remotion lambda policies validate`.

**`getAwsClient({region, service, customCredentials?, forcePathStyle?})`**: the AWS SDK v3 client and module Remotion
uses. `service`: `lambda`, `cloudwatch`, `iam`, `servicequotas`, `s3`, `sts`. Returns `{client, sdk}`; reuse `client` to
save memory. From `@remotion/lambda/client` since v4.0.60 (light-client list says v4.0.82). Uses: bucket CORS
(`PutBucketCorsCommand`), streaming an output (`GetObjectCommand` on `progress.outKey`), bulk cleanup, updating layers.

**Permissions (what the policies grant and why)**
- User policy: `iam:SimulatePrincipalPolicy` (validate), `iam:PassRole` on `remotion-lambda-role`; S3 on
  `arn:aws:s3:::remotionlambda-*`: `GetObject`, `DeleteObject`, `PutObjectAcl`, `PutObject`, `CreateBucket`,
  `ListBucket`, `GetBucketLocation`, `PutBucketAcl`, `DeleteBucket`, `PutBucketOwnershipControls`,
  `PutBucketPublicAccessBlock`, `PutBucketPolicy` (v4.0.418 default bucket policy); `s3:ListAllMyBuckets` on all;
  `lambda:GetLayerVersion` on Remotion's layer account `678892195805`; `lambda:ListFunctions`, `GetFunction` on `*`;
  `InvokeAsync`, `InvokeFunction`, `DeleteFunction`, `PutFunctionEventInvokeConfig`, `CreateFunction`,
  `PutRuntimeManagementConfig`, `TagResource` on `function:remotion-render-*`; `logs:CreateLogGroup`,
  `PutRetentionPolicy` on `/aws/lambda/remotion-render-*`; `servicequotas:GetServiceQuota`,
  `GetAWSDefaultServiceQuota`, `RequestServiceQuotaIncrease`, `ListRequestedServiceQuotaChangeHistoryByQuota` on `*` for
  `lambda quotas`;
  `s3:PutLifecycleConfiguration` for auto-delete (v4.0.32).
- Role policy (the function itself): list buckets, CRUD on `remotionlambda-*` objects, `lambda:InvokeFunction` on
  `remotion-render*` (the main function invokes renderers), log stream writes.
- Only buckets prefixed `remotionlambda-` and functions prefixed `remotion-render-` are reachable with default policies.
  That is why renaming functions or buckets is discouraged.

### 3.3 Lambda render APIs

**`renderMediaOnLambda(options)`** (light client). Starts a video or audio render and returns quickly.
Required: `region`, `functionName`, `serveUrl` (full URL or site name), `composition`, `codec`.

| Option | Default / values | Since | Notes |
|---|---|---|---|
| `codec` | `h264`, `h265`, `vp8`, `vp9`, `gif`, `prores`, `mp3`, `aac`, `wav` | | No `av1` on Lambda. `h264-mkv` became `h264` (v3.3.34) |
| `inputProps` | `{}` | optional since v3.2.27 | JSON object. Large props are uploaded to S3 automatically by the JS client |
| `privacy` | `'public'`, `'private'`, `'no-acl'` | `no-acl` v3.1.7 | `no-acl` for buckets without ACLs (R2, Supabase, locked S3 buckets) |
| `framesPerLambda` | by length (5.2) | | Minimum 5 (4 until v4.0.331); never more than 200 functions |
| `concurrency` | none | v4.0.322 | 1 to 200; `1` = main function only (v4.0.517); exclusive with `framesPerLambda` |
| `concurrencyPerLambda` | 1 | v3.0.30 | Tabs per function |
| `enableCancellation` | false | v4.0.515 | Each renderer does one S3 HEAD per second |
| `frameRange` | all | `[n, null]` v4.0.421 | Number, `[a, b]` or `[a, null]` |
| `imageFormat` | `jpeg` for video | optional since v3.2.27 | `png` for alpha, `none` for audio-only |
| `jpegQuality` | 80 | | JPEG frames only |
| `crf`, `pixelFormat` (`yuv420p`), `proResProfile`, `videoBitrate`, `audioBitrate` | renderer defaults | | Same as `renderMedia()` |
| `x264Preset` | `medium` on v4 (`veryfast` on v5) | | Speed and cost lever for h264 |
| `gopSize` | encoder decides | v4.0.466 | Max GOP per chunk; extra keyframes at every chunk boundary |
| `bufferSize`, `maxRate` | none | v4.0.78 | FFmpeg `-bufsize`, `-maxrate` |
| `audioCodec` | per codec | v3.3.41 | Chunks may use uncompressed audio then encode once; `pcm-16` for uncompressed |
| `muted` | false | | |
| `sampleRate` | 48000 | v4.0.448 | Match source audio |
| `colorSpace` | `'default'` (= bt601) | v4.0.28 | `'bt709'`, `'bt2020-ncl'`, `'bt2020-cl'`; real conversion since v4.0.83 |
| `preferLossless` | false | v4.0.123 | |
| `scale` | 1 | | Output scale factor |
| `forceWidth`, `forceHeight` | | v3.2.40 | |
| `forceFps`, `forceDurationInFrames` | | v4.0.424 | |
| `everyNthFrame`, `numberOfGifLoops` | | v3.1 | GIF only |
| `envVariables` | `{}` | | Private at render time |
| `metadata` | `{}` | v4.0.216 | Container metadata |
| `outName` | `out.<ext>` in `renders/<id>/` | | String, or `{key, bucketName, s3OutputProvider?}` (4.8). Regex `^([0-9a-zA-Z-!_.*'()/]+)$` |
| `overwrite` | false on v4 (true on v5) | v3.2.25 | Existing custom key throws unless true; true also skips a check (faster) |
| `downloadBehavior` | `{type: 'play-in-browser'}` | v3.1.5 | `{type: 'download', fileName: 'x.mp4' or null}` adds Content-Disposition |
| `timeoutInMilliseconds` | 30000 | | `delayRender()` timeout, not the function timeout |
| `maxRetries` | 1 | | Chunk retries, only for errors on Remotion's flaky list |
| `chromiumOptions` | | | `disableWebSecurity`, `ignoreCertificateErrors`, `gl` (Lambda default `swangle`) |
| `rendererFunctionName` | main function | v3.3.38 | Different memory for chunks; same region, account, version |
| `webhook` | none | v3.2.30 | `{url, secret: string or null, customData?}`; `customData` max 1024 bytes (v4.0.25) |
| `forceBucketName` | auto-discovered | v3.3.42 | Multi-bucket setups only |
| `logLevel` | `info` | | `trace`, `verbose`, `info`, `warn`, `error`; `verbose` keeps artifacts (no cleanup) |
| `mediaCacheSizeInBytes` | half of memory | v4.0.352 | Budget for `@remotion/media` decoded frames |
| `offthreadVideoCacheSizeInBytes` | half of memory | v4.0.23 | |
| `offthreadVideoThreads` | 2 | v4.0.261 | Raise carefully |
| `deleteAfter` | none | v4.0.32 | `'1-day'`, `'3-days'`, `'7-days'`, `'30-days'`; bucket needs lifecycle rules |
| `storageClass` | STANDARD | v4.0.305 | S3 storage class of the output |
| `forcePathStyle` | false | v4.0.202 | S3-compatible endpoints |
| `licenseKey` | null | v4.0.409 | Remotion usage reporting |
| `isProduction` | true | v4.0.409 | `false` for test renders (not billed on remotion.pro) |
| `requestHandler` | | v4.0.315 | Proxy agent for all AWS calls |
| `apiKey`, `dumpBrowserLogs`, `quality` | deprecated | | Use `licenseKey`, `logLevel`, `jpegQuality` |

Returns `{renderId, bucketName, cloudWatchLogs (v3.2.10), cloudWatchMainLogs (v4.0.174), lambdaInsightsLogs (v4.0.61),
folderInS3Console (v3.2.43), progressJsonInConsole (v4.0.182)}`.

```ts
import {renderMediaOnLambda, speculateFunctionName} from '@remotion/lambda/client';
const {renderId, bucketName} = await renderMediaOnLambda({
  region: 'us-east-1',
  functionName: speculateFunctionName({memorySizeInMb: 2048, diskSizeInMb: 10240, timeoutInSeconds: 240}),
  serveUrl: 'acme-promo-prod',
  composition: 'Promo',
  inputProps: {headline: 'Summer sale'},
  codec: 'h264',
  colorSpace: 'bt709',
  downloadBehavior: {type: 'download', fileName: 'acme-promo.mp4'},
});
```

**`getRenderProgress({renderId, bucketName, functionName, region, customCredentials?, forcePathStyle?,
skipLambdaInvocation?})`** (light client). `skipLambdaInvocation` (v4.0.218) reads S3 directly: lower latency, no
invocation per poll; needs `s3:GetObject` (in the default user policy) and a conventionally named function.
Response: `overallProgress` (0 to 1), `chunks`, `done`, `encodingStatus` (`null` or `{framesEncoded}`), `renderId`,
`renderMetadata` (`frameRange`, `startedDate`, `totalChunks`, `estimatedTotalLambdaInvokations`,
`estimatedRenderLambdaInvokations`, `compositionId`, `codec`, `dimensions` v4.0.222, `inputProps`), `bucket`,
`outputFile` (URL when done), `outKey`, `timeToFinish` (ms), `errors[]`, `fatalErrorEncountered`, `currentTime`,
`renderSize` (slightly under-reported since v4.0.165), `outputSizeInBytes` (v3.3.9), `lambdasInvoked`, `framesRendered`
(v3.3.8, multiples of 5), `costs {accruedSoFar, currency, displayCost, disclaimer}` (Lambda compute only, best effort),
`estimatedBillingDurationInMilliseconds` (v4.0.74), `mostExpensiveFrameRanges` (top 5 chunks once done: `chunk`,
`timeInMilliseconds`, `frameRange`), `artifacts` (v4.0.176).
- Stop polling on `done` or `fatalErrorEncountered`. A cancelled render has `fatalErrorEncountered: true`, `done: false`
  and an error named `CancelledError` (no dedicated field; `fatalErrorEncountered` is derived, not stored in `progress.json`).
- Never call it for stills.

**`renderStillOnLambda(options)`** (light client). Synchronous: resolves when the image is in S3.
- Required: `region`, `functionName`, `serveUrl`, `composition`, `inputProps`, `privacy` (default `'public'`).
- Optional: `frame` (0; negative from v3.2.27, `-1` = last), `imageFormat` (`png` default, `jpeg`, `webp`; `pdf` not on
  Lambda), `jpegQuality` (browser default 80), `onInit({renderId, cloudWatchLogs, lambdaInsightsUrl})` (v4.0.6; get log
  links even if it fails), `maxRetries` (1), `envVariables`, `forceWidth/Height` (v3.2.40), `forceFps/DurationInFrames`
  (v4.0.424), `scale`, `outName`, `timeoutInMilliseconds` (30000), `downloadBehavior`, cache options, `deleteAfter`,
  `chromiumOptions` (incl. `userAgent` v3.3.83, `darkMode` v4.0.381), `forceBucketName`, `logLevel`, `forcePathStyle`,
  `storageClass`, `licenseKey`, `isProduction`.
- Returns `{bucketName, url, outKey (v4.0.141), estimatedPrice, sizeInBytes, renderId, cloudWatchLogs, artifacts}`.
  Cannot be cancelled.

**`cancelRenderOnLambda({region, bucketName, renderId, forcePathStyle?, requestHandler?})`** (v4.0.515). Writes a cancel
signal to S3 and resolves when written (renderers stop at their next 1 s poll). Throws if the render was not started with
`enableCancellation: true`. Does not delete files (use `deleteRender()` afterwards) and does not invalidate an already
finished output. A failing or timed-out main function sends the same signal to the remaining renderers.

**`getCompositionsOnLambda({functionName, region, serveUrl, inputProps, envVariables?, timeoutInMilliseconds? (30000),
chromiumOptions?, forceBucketName?, logLevel?, cache options})`** (v3.3.2): lists compositions from a machine without
Chrome. Returns `[{id, width, height, fps, durationInFrames, defaultProps}]`.

**`downloadMedia({region, bucketName, renderId, outPath, onProgress?, customCredentials?, signal?})`**
(`@remotion/lambda`, not for serverless): saves the output locally, returns `{outputPath, sizeInBytes}`; `onProgress`
gets `{totalSize, downloaded, percent}`; `signal` (AbortSignal) v4.0.406. For end-user downloads use `downloadBehavior`.

**`presignUrl({region, bucketName, objectKey, expiresInSeconds, checkIfObjectExists})`** (light client since v3.3.42):
signed URL for a private object; `expiresInSeconds` integer 1 to 604800 (7 days). `checkIfObjectExists: true` returns
`null` for missing objects; `false` (default) is documented to throw for them.

**`deleteRender({region, bucketName, renderId, customCredentials?, forcePathStyle?})`**: `{freedBytes}` (light client
since v4.0.84).

**`estimatePrice({region, durationInMilliseconds, memorySizeInMb, diskSizeInMb, lambdasInvoked})`**: estimated USD for
Lambda compute (docs example 20 000 ms, 2048 MB, 2048 MB disk, 1 lambda, us-east-1 = 0.00067). Excludes S3 and license.
`durationInMilliseconds` is the sum over all functions.

**Webhooks** (v3.2.30). Remotion POSTs JSON to `webhook.url` when a render succeeds, errors or times out.
- Headers: `X-Remotion-Mode: production | demo`, `X-Remotion-Signature: sha512=<hex HMAC-SHA512 of the body with the
  secret>` or `NO_SECRET_PROVIDED`, `X-Remotion-Status: success | timeout | error`.
- Body: always `{renderId, expectedBucketOwner, bucketName, customData}`, plus `type: 'success'` with `lambdaErrors[]`
  (non-fatal, each with `type: renderer | browser | stitcher`, `chunk`, `frame`, `attempt`, `willRetry`, `tmpDir`...),
  `outputUrl`, `outputFile`, `timeToFinish`, `costs`; or `type: 'error'` with `errors[] {message, name, stack}`; or
  `type: 'timeout'` with nothing else.
- `validateWebhookSignature({secret, body, signatureHeader})` (v3.2.30) throws on mismatch; `body` is the parsed JSON
  object, `signatureHeader` the `X-Remotion-Signature` value.
- Helpers from `@remotion/lambda/client`, each taking `{secret, testing, extraHeaders, onSuccess, onError, onTimeout}`:
  `expressWebhook()` (mount on POST and OPTIONS), `appRouterWebhook()` (export as `POST` and `OPTIONS`, v4.0.246),
  `pagesRouterWebhook()` (default export, v4.0.246). `testing: true` accepts requests from the remotion.dev tester, which
  needs CORS for `https://www.remotion.dev`; use `false` in production.
- The endpoint must be reachable from AWS (tunnel with ngrok or tunnelmole for localhost).

**Light client** `@remotion/lambda/client` (re-exports npm `@remotion/lambda-client`): `renderMediaOnLambda`,
`renderStillOnLambda`, `getRenderProgress`, `cancelRenderOnLambda`, `getCompositionsOnLambda`, `getFunctions`,
`getSites`, `presignUrl`, `speculateFunctionName`, `validateWebhookSignature`, webhook helpers, `getAwsClient` (v4.0.82),
`deleteRender` (v4.0.84), types `AwsRegion`, `RenderProgress`, `WebhookPayload`, `PresignUrlInput`, `CustomCredentials`
(v4.0.60), `DeleteRenderInput`, `RequestHandler`, `RenderStillOnLambdaInput`, `RenderMediaOnLambdaOutput`. No renderer
dependency, so Next.js and ESBuild can bundle it. Not supported on edge runtimes (Vercel Edge, Cloudflare Workers). Deno
works: Supabase Edge Functions import `npm:@remotion/lambda-client@<exact version>` (v4.0.265). Never call from a browser.

**Proxy** (v4.0.315): every AWS-touching light-client API accepts `requestHandler`, e.g.
`{httpsAgent: new HttpsProxyAgent(process.env.HTTPS_PROXY)}`; type `RequestHandler`.

### 3.4 Lambda CLI (`npx remotion lambda ...`)

Global flags: `--region`, `--yes`/`-y`, `--quiet`/`-q`, `--env-file`.

| Command | Flags | Notes |
|---|---|---|
| `policies role`, `policies user`, `policies validate` | `--region=cn-...` selects the aws-cn partition | `validate` checks the user policy only; `| pbcopy` on macOS |
| `functions deploy` | `--memory` (2048), `--disk` (2048 on v4), `--timeout` (120 s), `--disable-cloudwatch`, `--retention-period` (14), `--enable-lambda-insights` (v4.0.61), `--custom-role-arn`, `--custom-layer-arns` (v4.0.510), `--vpc-subnet-ids`, `--vpc-security-group-ids` (v4.0.160), `--runtime-preference` (v4.0.205), `-q` | Prints the existing name if identical |
| `functions ls` | `--compatible-only` (v4.0.164), `-q` (prints `()` if none) | |
| `functions rm <names...>`, `functions rmall` | `-y` | Destructive |
| `sites create [entry]` | `--site-name`, `--force-bucket-name` (v3.3.42), `--privacy` (`public`/`no-acl`, v3.3.97), `--public-dir` (v4.0.140), `--enable-folder-expiry` (v4.0.32), `--throw-if-site-exists` (v4.0.141), `--disable-git-source` (v4.0.182), `--force-path-style` (v4.0.202) | Uses `remotion.config.ts` for bundling |
| `sites ls` | `-q`, `--compatible-only` (v4.0.435) | |
| `sites rm <ids...>`, `sites rmall` | `-y`, `--force-bucket-name` | Destructive |
| `render <serve-url or site> [comp] [out]` | see below | Without `[out]` the file stays in S3; the picker needs a full URL |
| `still <serve-url or site> [comp] [out]` | `--frame`, `--image-format`, `--privacy`, `--max-retries`, `--out-name`, `--s3-output-provider-*`, `--delete-after`, `--storage-class`, `--scale`, `--jpeg-quality`, `--license-key` | `pdf` unsupported |
| `compositions <serve-url>` (v3.3.2) | `--props`, `--config`, `--timeout` (30000), `--log`, `-q`, `--force-bucket-name`, cache flags | For machines without Chrome |
| `regions` | `--default-only` (v3.3.11) | For scripts |
| `quotas`, `quotas increase` | `--region`, `--yes`, `--force` | Increase requests only work for root accounts |

`render` flags: `--props` (JSON string or file; use a file on Windows shells), `--log=verbose` (CloudWatch, S3 folder and
`progress.json` links), `--privacy`, `--max-retries` (1), `--frames-per-lambda`, `--concurrency` (v4.0.322; `1` v4.0.517;
not with `--frames-per-lambda`), `--concurrency-per-lambda` (v3.0.30), `--codec` (default h264), `--audio-codec`
(v3.3.42), `--audio-bitrate`/`--video-bitrate` (v3.2.32), `--crf`, `--x264-preset`, `--gop` (v4.0.466), `--pixel-format`,
`--prores-profile`, `--image-format`, `--jpeg-quality`, `--scale`, `--frames`, `--every-nth-frame` and
`--number-of-gif-loops` (v3.1.0), `--muted` (v3.2.1), `--timeout` (delayRender ms, 30000), `--out-name`, `--overwrite`
(v3.2.25), `--webhook` + `--webhook-secret` (v3.2.30), `--webhook-custom-data` (v4.0.25, JSON or file), `--width`/`--height`
(v3.2.40), `--fps`/`--duration` (v4.0.424), `--function-name` and `--renderer-function-name` (v3.3.38),
`--force-bucket-name`, `--gl`, `--user-agent` (v3.3.83), `--dark-mode` (v4.0.381), `--ignore-certificate-errors`,
`--disable-web-security`, `--media-cache-size-in-bytes` (v4.0.352), `--offthreadvideo-cache-size-in-bytes` (v4.0.23),
`--offthreadvideo-video-threads` (v4.0.261), `--delete-after` (v4.0.32), `--color-space` (v4.0.28), `--prefer-lossless`
(v4.0.110 on the CLI page), `--metadata` (v4.0.216), `--sample-rate` (v4.0.448), `--force-path-style` (v4.0.202),
`--storage-class` (v4.0.305), `--license-key` (v4.0.409), `--enable-cancellation` (v4.0.515),
`--s3-output-provider-endpoint`, `--s3-output-provider-region`, `--s3-output-provider-force-path-style` (use with
`--force-bucket-name`, `--out-name`, `--privacy=no-acl`).

```bash
npx remotion lambda render acme-promo-prod Promo out/promo.mp4 \
  --props=props.json --color-space=bt709 --log=verbose --enable-cancellation
```

### 3.5 SDKs for other languages (versions must equal the deployed function exactly)

| SDK | Since | Install | Payload notes | Cancel (v4.0.515) |
|---|---|---|---|---|
| Python `remotion-lambda` | v4.0.15 | `pip install remotion-lambda==4.0.528` | Large props auto-uploaded to S3 from v4.0.315 (about 194 KB video, 4.9 MB still). v4.0.380 added `session`/`config` (boto3 session recommended). v4.0.82 renamed to `input_props`, `RenderMediaParams`, `render_id`, `bucket_name` | `cancel_render_on_lambda` |
| PHP `remotion/lambda` (Composer) | v3.3.96 | pin exact version (remove `^`) | Typed fields and JSON props since v4.0.15; reads `AWS_*` env vars | `cancelRenderOnLambda` |
| Go `lambda_go_sdk` | experimental | match version | Props over 200 KB unsupported; response shape changed in v4.0.6 | `CancelRenderOnLambda` |
| Ruby gem `remotion_lambda` | v4.0.232 | match version | Input about 60 KB max (no S3 workaround); input keys snake_case, nested keys camelCase, responses camelCase; experimental | `cancel_render_on_lambda` |

### 3.6 Lambda runtime on 4.0.528

- Architecture: arm64 only (x86_64 layers discontinued).
- Chrome 149.0.7790.0 (from v4.0.452); earlier 144.0.7559.20 (v4.0.415), 133.0.6943.141 (v4.0.274), 123.0.6312.86
  (v4.0.245), 114.0.5731.1 (v4.0.0). Built with proprietary codecs, so MP4 inputs work.
- FFmpeg: the `@remotion/renderer` build, lean: no AV1 encoder (AV1 decoding works). Same lean set on Linux ARM64 GNU.
- Node runtime: table says 24.x from v4.0.415, 20.x from v4.0.379, 22.x from v4.0.376, 20.x from v4.0.246, 18.x before;
  the prose says Lambda stays on 20.x for stability (see Open questions). With `lambda:PutRuntimeManagementConfig` in the
  user policy (default for setups after Nov 2023) the runtime is locked to a known ARN; otherwise a warning is printed.
- vCPU by memory: 128 to 3008 MB = 2; 3009 to 5307 = 3; 5308 to 7076 = 4; 7077 to 8845 = 5; 8846 and up = 6.
- Built-in fonts: Noto Color Emoji; Noto Sans Black, Bold, Regular, SemiBold, Thin; Noto Sans Arabic, Devanagari, Hebrew,
  Tamil, Thai (Regular only); arm64 only: Noto Sans Simplified Chinese, Traditional Chinese, Korean, Japanese (Regular and
  Bold). Nothing else: no Bengali, no brand fonts, no Apple emoji unless `runtimePreference: 'apple-emojis'`.
- Layers: default (`cjk`) chromium 196 MB + Google emoji 9.9 MB + fonts 1.9 MB + CJK 16 MB = 223.8 MB;
  `apple-emojis`: chromium + Apple emoji 45 MB + fonts = 242.9 MB (drops CJK and Google emoji). Layers must stay under
  250 MB extracted. The docs flag these numbers as outdated after the last Chromium update.
- Disk (ephemeral storage) 512 MB to 10 GB; chunks and the final file must fit together, so output is about half the disk.

### 3.7 Lambda limits and regions

- Per render: 200 functions max; `framesPerLambda` 5 min.
- Per account and region: 1000 concurrent executions by default (as low as 10 for some new accounts); burst 1000 new
  executions per 10 s (500 in some regions). Errors: `TooManyRequestsException: Rate Exceeded`,
  `ConcurrentInvocationLimitExceeded`.
- Function: 15 min max runtime, 10 GB RAM, 10 GB disk.
- Webhook `customData`: 1024 bytes. Go props 200 KB, Ruby about 60 KB.
- Regions: eu-central-1, eu-west-1, eu-west-2, eu-west-3, eu-south-1, eu-north-1, us-east-1, us-east-2, us-west-1,
  us-west-2, af-south-1, ap-south-1, ap-east-1, ap-southeast-1, ap-southeast-2, ap-northeast-1, ap-northeast-2,
  ap-northeast-3, ca-central-1, sa-east-1, plus cn-north-1 and cn-northwest-1 (v4.0.510: China account, custom layers,
  `aws-cn` policies, `amazonaws.com.cn` URLs, costs reported in CNY). Some regions are disabled by default in new accounts.
- Price per GB-second (docs table, may be stale): 0.0000133334 for most regions; eu-south-1 0.0000156138; af-south-1
  0.00001768; ap-east-1 0.0000183.

### 3.8 Cloud Run (`@remotion/cloudrun`, alpha, not actively developed)

Every Cloud Run page carries an Alpha badge; `status.md` says only critical bugs are fixed and Remotion plans to rebuild
Cloud Run on the Lambda runtime. Missing vs Lambda: distributed rendering, completion webhooks, Apple emoji, cost
estimation, expiring renders, PHP/Go/Python SDKs.

- Setup (human, in GCP): create project, enable billing, open Cloud Shell, run Remotion's installer
  (`curl -L https://github.com/remotion-dev/remotion/raw/main/packages/cloudrun/src/gcpInstaller/gcpInstaller.tar | tar -x -C . && node install.mjs`;
  option 1 = set up or update the project; the key option generates a new `.env` or manages keys, numbered 2 in
  `setup.md` but 3 in `generate-env.md`), answer `yes` to apply the plan and to generate `.env`, copy it locally,
  delete it from the VM. Max 10 keys per service account. Validate: `npx remotion cloudrun permissions` or
  `testPermissions({onTest?})` (returns `{results: [{decision: boolean, permissionName}]}`).
- `deployService({projectID, region, memoryLimit?, cpuLimit?, minInstances?, maxInstances?, timeoutSeconds?,
  performImageVersionValidation?, onlyAllocateCpuDuringRequestProcessing?})`: memory 512 MiB to 32 GiB (default 2 GiB,
  CPU minimums apply), CPU default 1.0, `minInstances` 0 (anything above 0 is billed while idle), `maxInstances` 100 on
  v4 (5 on v5; GCP max 100 without a quota increase), `timeoutSeconds` default 300, max 3600, image validation default
  true, `onlyAllocateCpuDuringRequestProcessing` (v4.0.221) sets `cpu_idle` for cost savings. Idempotent. Returns
  `{fullName, shortName, uri, alreadyExists}`. Name pattern `remotion--4-0-528--mem2gi--cpu1-0--t-300`.
- `speculateServiceName({memoryLimit, cpuLimit, timeoutSeconds})`, `getServices({region, compatibleOnly})`,
  `getServiceInfo({region, serviceName})` (fields `serviceName, memoryLimit, cpuLimit, remotionVersion, timeoutInSeconds,
  uri, region, consoleUrl`), `deleteService({region, serviceName})`.
- Storage: `getOrCreateBucket({region, updateBucketState?})` creates `remotioncloudrun-*` (one per region);
  `deploySite({entryPoint, bucketName, siteName?, logLevel?, options?})` has no `region` argument and the same bundling
  options as Lambda's `deploySite`; Serve URL `https://storage.googleapis.com/remotioncloudrun-xxx/sites/<site>/index.html`;
  `getSites(region)` takes a plain string (`'all regions'` allowed) and returns `bucketRegion` per site;
  `deleteSite({bucketName, siteName})`.
- `renderMediaOnCloudrun({cloudRunUrl xor serviceName, region, serveUrl, composition, codec, ...})`: a single HTTP request
  lasting the whole render. Documented API codecs: `h264`, `vp8`, `prores`, `mp3`, `aac`, `wav`. Specific options:
  `updateRenderProgress(progress, error)`, `renderStatusWebhook {url, headers, data, webhookProgressInterval}` (interval
  default 0.1, range 0.01 to 1; POSTs `{progress, renderedFrames, encodedFrames, renderId, ...data}`), `renderIdOverride`
  (you guarantee uniqueness or files get overwritten), `concurrency` (tabs, default `"50%"`, was `"100%"` before v4.0.76),
  `delayRenderTimeoutInMilliseconds` (30000), `downloadBehavior` (v4.0.176), `enforceAudioTrack`, `outName` (string only),
  `privacy` (`public` or `private`, no `no-acl`), `frameRange` (one range only). Returns `{type: 'success', publicUrl,
  renderId, bucketName, privacy: 'public-read' | 'project-private', cloudStorageUri, size (KB)}` or `{type: 'crash',
  cloudRunEndpoint, message, requestStartTime, requestCrashTime, requestElapsedTimeInSeconds}`.
- `renderStillOnCloudrun(...)`: same shape, `frame` (negative allowed), `imageFormat`.
- Light client `@remotion/cloudrun/client` (v4.0.84): the delete, get, render and speculate functions plus
  `RenderMediaOnCloudrunInput`, `RenderStillOnCloudrunInput`, `UpdateRenderProgress` types.
- CLI (camelCase flags on deploy): `services deploy --memoryLimit --cpuLimit --minInstances --maxInstances --timeoutSeconds
  --onlyAllocateCpuDuringRequestProcessing`, `services ls/rm/rmall`, `sites create/ls/rm/rmall` (`--all-regions` on ls and
  rmall, `--disable-git-source` v4.0.182), `render` and `still` (`--cloud-run-url` xor `--service-name`, `--privacy`,
  `--force-bucket-name`, `--webhook`, `--render-id-override`, `--concurrency`, codec and encoding flags), `permissions`,
  `regions`.
- Limits: one request per instance (docs say "0 concurrency" in one place and "concurrency of 1" in another); `503 service
  unavailable` beyond max instances (queue with Cloud Tasks); memory 32 GB; execution 60 min; output limited by memory minus
  the runtime.
- Regions: asia-east1, asia-east2, asia-northeast1, asia-northeast2, asia-northeast3, asia-south1, asia-south2,
  asia-southeast1, asia-southeast2, australia-southeast1, australia-southeast2, europe-central2, europe-north1,
  europe-southwest1, europe-west1, europe-west2, europe-west3, europe-west4, europe-west6, europe-west8, europe-west9,
  me-west1, northamerica-northeast1, northamerica-northeast2, southamerica-east1, southamerica-west1, us-central1,
  us-east1, us-east4, us-east5, us-south1, us-west1, us-west2, us-west3, us-west4. Two pricing tiers.

### 3.9 Vercel Sandbox (`@remotion/vercel`, experimental since v4.0.426)

Peer dependency `@vercel/sandbox`. Each render gets an ephemeral Linux VM with Chrome, the compositor and system libraries.

- `createSandbox({onProgress?, resources?, timeoutInMilliseconds?})`: `resources` default `{vcpus: 4}` (2048 MB per vCPU),
  `timeoutInMilliseconds` (v4.0.452) caps creation, default 300000. `onProgress({progress, message})`. Returns
  `VercelSandbox` (`Sandbox` + `AsyncDisposable`: `await using` stops it automatically). Otherwise call `sandbox.stop()`.
- `addBundleToSandbox({sandbox, bundleDir})`: copies a local bundle (path relative to cwd) into the sandbox. Returns void.
- `renderMediaOnVercel({sandbox, compositionId, inputProps, codec? ('h264'), outputFile? ('/tmp/video.mp4'), onProgress?,
  detached? (v4.0.469), vercelBlob? (v4.0.469; required when detached: {blobToken, access, blobPath?}),
  detachedSandboxTimeoutInMilliseconds? (1800000), ...renderMedia options})`. The renderMedia options include `crf`,
  `imageFormat`, `pixelFormat`, `envVariables`, `frameRange`, `everyNthFrame`, `proResProfile`, `chromiumOptions`, `scale`,
  `preferLossless`, `enforceAudioTrack`, `disallowParallelEncoding`, `concurrency`, `metadata`, `logLevel`,
  `timeoutInMilliseconds`, bitrates, `audioCodec`, `encodingMaxRate`, `encodingBufferSize`, `muted`, `numberOfGifLoops`,
  `x264Preset`, `gopSize`, `colorSpace`, `jpegQuality`, `forSeamlessAacConcatenation`, `separateAudioTo`,
  `hardwareAcceleration`, cache options, `licenseKey`. Returns `{sandboxFilePath, contentType}`, or
  `{sandboxId, cmdId, outputFile}` when detached. `onProgress` stages: `opening-browser`, `selecting-composition`,
  `render-progress` (with `progress: RenderMediaProgress`), each with `overallProgress`.
- `renderStillOnVercel({sandbox, compositionId, inputProps, imageFormat?, outputFile? ('/tmp/still.png'), frame?,
  jpegQuality?, envVariables?, chromiumOptions?, scale?, logLevel?, timeoutInMilliseconds?, cache options, licenseKey?,
  onProgress?})`: `{sandboxFilePath, contentType}`.
- `uploadToVercelBlob({sandbox, sandboxFilePath, contentType, blobToken, access, blobPath?})`: `{url, size}`;
  `access` `'public'` or `'private'`; random `blobPath` if omitted.
- `getRenderProgress({sandboxId, cmdId})` (v4.0.469) for detached renders: stages `starting`, `opening-browser`,
  `selecting-composition`, `render-progress`, `uploading`, `done {url, size, contentType}`, `error {message}`,
  `expired`. On `done`/`error` drop the stored handle; the sandbox lives until its timeout unless you stop it.
- Limits (from `vercel-sandbox.md`): sandbox 45 min on Hobby, 5 h on Pro/Enterprise; 10 concurrent sandboxes on Hobby,
  2000 on Pro/Enterprise; Vercel functions max 800 s, so longer renders must be detached.

---

## 4. Recipes

Written for an autonomous agent in a client project on Remotion 4.0.528.

### 4.1 First-time Lambda setup (human does the console, agent does the rest)

1. Agent: `npx remotion add @remotion/lambda` (installs the version matching the project).
2. Human, AWS console (agent prints exact steps, never handles secrets): policy `remotion-lambda-policy` from
   `npx remotion lambda policies role`; role `remotion-lambda-role` (use case Lambda) with that policy; IAM user without
   console access; inline policy from `npx remotion lambda policies user`; access key of type "Application running on an
   AWS compute service". Names must be exact.
3. Human puts `REMOTION_AWS_ACCESS_KEY_ID` and `REMOTION_AWS_SECRET_ACCESS_KEY` in `.env`. Agent only checks they exist.
4. Agent: `npx remotion lambda policies validate` (wait 2 to 3 minutes if it fails right after creation), then
   `npx remotion lambda quotas`. If the limit is tiny, the human requests an increase (`quotas increase` works for root
   accounts; otherwise Service Quotas console; answer template on `limits.md`), and renders use `--concurrency=1` meanwhile.
5. Agent: deploy function, bucket, site (4.2) and a test render (4.3).

### 4.2 Idempotent deploy per client project

Keep one config file with region, site name, memory, disk and timeout (the templates' `config.mjs` pattern). Bundle with
the CLI (reads `remotion.config.ts`), then deploy:

```ts
// deploy.ts: run after `npx remotion bundle` (writes ./build)
import 'dotenv/config';
import {deployFunction, getOrCreateBucket, deploySiteFromBundle} from '@remotion/lambda';
import {REGION, SITE_NAME, RAM, DISK, TIMEOUT} from './render.config';
const {functionName} = await deployFunction({region: REGION, memorySizeInMb: RAM, diskSizeInMb: DISK, timeoutInSeconds: TIMEOUT, createCloudWatchLogGroup: true});
const {bucketName} = await getOrCreateBucket({region: REGION, enableFolderExpiry: true});
const {serveUrl, stats} = await deploySiteFromBundle({bucketName, region: REGION, bundleDir: './build', siteName: SITE_NAME});
console.log({functionName, bucketName, serveUrl, stats});
```

Re-run after: template code or asset changes (site), config changes (function), Remotion upgrades (both). Site names:
`<client>-<project>-<env>` (e.g. `acme-promo-prod`, `acme-promo-staging`).

### 4.3 Render one video and wait

```ts
import {renderMediaOnLambda, getRenderProgress, speculateFunctionName} from '@remotion/lambda/client';
const region = 'us-east-1';
const functionName = speculateFunctionName({memorySizeInMb: 2048, diskSizeInMb: 10240, timeoutInSeconds: 240});
const {renderId, bucketName} = await renderMediaOnLambda({region, functionName, serveUrl: 'acme-promo-prod', composition: 'Promo', codec: 'h264', inputProps: props});
while (true) {
  await new Promise((r) => setTimeout(r, 1000));
  const p = await getRenderProgress({renderId, bucketName, functionName, region, skipLambdaInvocation: true});
  if (p.fatalErrorEncountered) throw new Error(p.errors.map((e) => e.message).join('\n'));
  if (p.done) { console.log(p.outputFile, p.costs.displayCost); break; }
}
```

Then `downloadMedia({region, bucketName, renderId, outPath: 'out/promo.mp4'})` if the file must land on disk. One-off CLI
equivalent: `npx remotion lambda render acme-promo-prod Promo out/promo.mp4 --props=props.json`.

### 4.4 Batches and personalised video within the concurrency budget

- Executions per video = renderer functions + 1 main (+1 short one per progress poll without `skipLambdaInvocation`).
  Default renderers at 30 fps: 15 (10 s), 45 (30 s), 82 (60 s), 90 (2 min), 113 (5 min), 150 (10 min and longer).
- Simultaneous videos about `floor((accountLimit - headroom) / (renderers + 1))`: with 1000, about 11 one-minute videos or
  about 21 thirty-second videos at once.
- For large batches set a lower per-video `concurrency` (e.g. 20 to 40): more videos in flight, lower total cost, each video
  slower.
- Queue in your app: count in-flight renders, release a slot on `done`/`fatalErrorEncountered` or on the webhook. The
  documented SQS guide releases the queue slot when the render is triggered, not when it finishes, so it does not throttle
  (the page itself flags this flaw). SQS setup there: `batchSize: 1`, `maxBatchingWindow: 5 min`,
  `reportBatchItemFailures: true`.
- Stagger starts: burst limit is 1000 new executions per 10 s (500 in some regions).
- Scale out: quota increase, the same function and site deployed to several regions, several AWS accounts rotated per
  render (set `REMOTION_AWS_ACCESS_KEY_ID/SECRET` before the call; GitHub Unwrapped chooses a random account and region
  per render and stores both with the render record for later progress calls).
- Rate-limit end users; any public render button is a direct line to the AWS bill.

### 4.5 Completion by webhook (Next.js App Router)

```ts
// app/api/remotion-webhook/route.ts
import {appRouterWebhook} from '@remotion/lambda/client';
export const POST = appRouterWebhook({
  secret: process.env.REMOTION_WEBHOOK_SECRET!,
  testing: false,
  onSuccess: async ({renderId, outputFile, customData}) => { /* mark job done, notify client */ },
  onError: async ({renderId, errors}) => { /* log, maybe retry */ },
  onTimeout: async ({renderId}) => { /* retry with lower load or longer timeout */ },
});
export const OPTIONS = POST;
```

Start renders with `webhook: {url: 'https://app.example.com/api/remotion-webhook', secret: process.env.REMOTION_WEBHOOK_SECRET!,
customData: {jobId}}`. `customData` must stay under 1 KB; store more in `inputProps` and read `renderMetadata.inputProps`
through `getRenderProgress()`. CLI: `--webhook`, `--webhook-secret`, `--webhook-custom-data`.

### 4.6 Private client deliverables

- `privacy: 'private'`; share `presignUrl({region, bucketName, objectKey: progress.outKey, expiresInSeconds: 604800,
  checkIfObjectExists: true})` (7 days is the AWS maximum).
- `downloadBehavior: {type: 'download', fileName: 'acme-summer-sale-1080p.mp4'}` for a clean saved filename.
- Buckets created on v4.0.418+ with `s3:PutBucketPolicy` get a policy (objects readable only by exact URL, bucket not
  listable). Older buckets keep a `public-read` ACL: anyone can list them. Fix: S3 console, Permissions, ACL, remove List for
  Everyone.
- Optional hardening: `robots.txt` with `Disallow: /` at the bucket root, long site names.

### 4.7 Auto-delete renders

1. User policy needs `s3:PutLifecycleConfiguration` (automatic for setups after v4.0.32; older setups add it under the
   `"Sid": "Storage"` statement).
2. `getOrCreateBucket({region, enableFolderExpiry: true})` or `sites create --enable-folder-expiry` (4 lifecycle rules
   appear under the bucket's Management tab).
3. Render with `deleteAfter: '7-days'`: the render id gets a prefix, keys become `renders/7-days-<id>/...`. AWS deletes by
   last-modified date, not at the exact minute.

### 4.8 Send the output elsewhere

- Other bucket, same region: `outName: {bucketName: 'client-deliveries', key: 'acme/promo.mp4'}`; extend the role policy
  (not the user policy) with write access (`s3:PutObject` on `arn:aws:s3:::client-deliveries/*`). Bucket name must match
  AWS naming rules (regex in `custom-destination.md`). Node API only, per that page.
- Other region or account: add `s3OutputProvider: {endpoint: 'https://s3.us-west-1.amazonaws.com', accessKeyId,
  secretAccessKey, region: 'us-west-1'}` (v4.0.112).
- Cloudflare R2 (no egress fees): `s3OutputProvider: {endpoint: 'https://<account>.r2.cloudflarestorage.com',
  accessKeyId, secretAccessKey}` with `privacy: 'no-acl'` (API key with Object Read & Write). Supabase Storage (v4.0.259):
  endpoint `https://<project>.supabase.co/storage/v1/s3`, `region`, `forcePathStyle: true`. DigitalOcean Spaces works.
  Google Cloud Storage works with HMAC keys (`gcloud storage hmac create <service-account-email>`), uniform access and no
  underscores in the bucket name. Azure Blob does not (not S3-compatible).
- Later calls (`getRenderProgress`, `downloadMedia`, `deleteRender`) still take the AWS site bucket as `bucketName`, plus
  the same credentials as `customCredentials`.
- CLI (`cli/render.md`): `--force-bucket-name`, `--out-name`, `--privacy=no-acl`, `--s3-output-provider-endpoint`,
  `--s3-output-provider-region`, credentials in `REMOTION_S3_OUTPUT_PROVIDER_*`.

### 4.9 Thumbnails, OG images, story frames

`renderStillOnLambda({region, functionName, serveUrl, composition: 'Thumbnail', inputProps, privacy: 'public',
imageFormat: 'jpeg', jpegQuality: 95, frame: 0})` returns `url` directly. GitHub Unwrapped starts the video render and two
still renders (OG image, Instagram story) together with `Promise.all`. `png` for transparency, `webp` also works, `pdf` does
not on Lambda.

### 4.10 Accounts with a tiny concurrency limit

`concurrency: 1` (v4.0.517+) renders on the main function (one short extra invocation for progress). With a limit of 10
the docs suggest `--concurrency=8` (8 renderers + 1 main + 1 spare). Inference, not stated in the docs: a single-function
render must finish within the function timeout (max 900 s), so deploy a long-timeout function for this mode.

### 4.11 Cancel a render

Start with `enableCancellation: true`; call `cancelRenderOnLambda({region, bucketName, renderId})`; detect with
`progress.errors.some((e) => e.name === 'CancelledError')`; clean with `deleteRender()`. Worst-case polling cost (200
functions for 15 min) is about $0.072. CLI: `--enable-cancellation` then Ctrl+C (twice to exit without waiting for the
signal). Without the flag Ctrl+C only stops the CLI; the render and its bill continue.

### 4.12 Zero-downtime upgrade

1. `npx remotion upgrade` (every Remotion package).
2. Re-apply `npx remotion lambda policies user` and `policies role` if the release notes mention new permissions
   (examples: `s3:PutBucketPolicy` in v4.0.418, `s3:PutLifecycleConfiguration` in v4.0.32,
   `lambda:PutRuntimeManagementConfig`, S3 ownership permissions in v3.3.87).
3. Deploy the new function (old keeps serving) and a new site name (overwriting may break old functions).
4. Ship the app with the new package, function name and serve URL.
5. When no old renders are in flight, `functions rm` the old function and remove the old site.
List versions with `functions ls`, `sites ls --compatible-only`.

### 4.13 Heavy compositions

- 3009 MB memory is the cheapest step to 3 vCPUs (the Next.js and SaaS templates use 3009 MB, 10240 MB disk, 240 s);
  combine with `concurrencyPerLambda: 2`.
- Or keep a lean main function and route chunks to a bigger one with `rendererFunctionName` (same region, account, version).
- Replace `<OffthreadVideo>` with `<Video>`/`<Audio>` from `@remotion/media` (range requests, decoding starts early).
- Precompute data once and pass it in `inputProps` instead of fetching in every chunk.
- After a render, read `mostExpensiveFrameRanges` to find the slow section.

### 4.14 Assets for cloud renders

- Files used through `staticFile()` travel with the site upload and are fetched over HTTP by each chunk that uses them.
- Big footage: Cloudflare R2 behind a custom domain with a Cache Rule (the `r2.dev` URL cannot cache; check the
  `CF-Cache-Status` header: `HIT`/`MISS` = cached path, `DYNAMIC` = not cached), Bot Fight Mode disabled, sources re-encoded
  with short keyframe intervals.
- On `@remotion/media` components set `delayRenderTimeoutInMilliseconds` below the function timeout, plus
  `delayRenderRetries`, so a stalled range request fails fast and retries instead of timing out the render.
- Third-party hosts see up to 200 parallel browsers: expect rate limits, use a CDN.
- VPC endpoints for S3 avoid egress but need a redeployed function, cost a per-request fee, may block other traffic and
  have no official configuration (see linked GitHub issue).
- If your web app (not the Lambda browser) reads files from the Remotion bucket, add CORS via `getAwsClient`
  (`PutBucketCorsCommand`, GET/HEAD); GitHub Unwrapped does this in its deploy script.

### 4.15 Fonts and emoji in the cloud (critical for Bangla clients)

- Bengali, and every script outside the Noto list in 3.6, has no system font on Lambda. A video that looks right on the
  Mac (macOS ships Bangla fonts) can render tofu boxes on Lambda. Always load fonts as web fonts in the composition:
  `@remotion/google-fonts/NotoSansBengali`, `HindSiliguri`, `AnekBangla`, `BalooDa2`, `TiroBangla` (all present in the
  installed package), or a bundled `.woff2` via `staticFile()` + FontFace + `delayRender()`.
- Brand Latin fonts must also be web fonts; the only system family is Noto Sans.
- Emoji default to Google Noto Color Emoji on Lambda, Apple Color Emoji on the Mac. For Apple emoji deploy with
  `runtimePreference: 'apple-emojis'` (removes CJK and Google emoji; Apple emoji licensing is your responsibility). For the
  same look everywhere, render emoji as images.
- CJK: Regular and Bold only, arm64 only.
- Custom layers (clone `remotion-dev/lambda-binaries`, edit `fonts/.fonts/...`, `sh size.sh`, `sh make.sh`, create the
  layer in each region, deploy with `customLayerArns` (v4.0.510) or swap it with `UpdateFunctionConfiguration`, which needs
  `lambda:GetFunctionConfiguration`, `lambda:UpdateFunctionConfiguration`, `lambda:GetLayerVersion`) only when web fonts
  are impossible. Stay under 250 MB and rebuild on Remotion updates.
- Vercel Sandbox and Cloud Run font sets are undocumented: treat them like Lambda (web fonts only).

### 4.16 Render calls from AWS compute without long-term keys

- IAM role route (`without-iam.md`): create policy `remotion-executionrole-policy` from the user policy JSON, attach it
  (plus `AWSLambdaBasicExecutionRole`) to the calling function's execution role; the runtime injects `AWS_ACCESS_KEY_ID`,
  `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`. To write into another bucket add `s3:PutObject` on it.
- EC2 route (`ec2.md`): role `remotion-ec2-executionrole` trusting both `lambda.amazonaws.com` and the EC2 role; the app
  calls STS AssumeRole and sets the temporary keys as env vars before `renderMediaOnLambda()`. Or set
  `REMOTION_SKIP_AWS_CREDENTIALS_CHECK=1` and let the SDK use instance metadata.
- Serverless Framework, CDK + Cognito + API Gateway, and SQS reference projects: `alexfernandez803/remotion-serverless`
  (third-party, older Remotion versions; read for architecture only).

### 4.17 Render on Vercel Sandbox

Synchronous (under 800 s):

```ts
import {createSandbox, addBundleToSandbox, renderMediaOnVercel, uploadToVercelBlob} from '@remotion/vercel';
await using sandbox = await createSandbox({resources: {vcpus: 8}});
await addBundleToSandbox({sandbox, bundleDir: '.remotion'});
const {sandboxFilePath, contentType} = await renderMediaOnVercel({sandbox, compositionId: 'Promo', inputProps});
const {url} = await uploadToVercelBlob({sandbox, sandboxFilePath, contentType, blobToken: process.env.BLOB_READ_WRITE_TOKEN!, access: 'public'});
```

- Detached (long renders): `renderMediaOnVercel({..., detached: true, vercelBlob: {blobToken, access: 'public'}})` returns
  `{sandboxId, cmdId}`; poll `getRenderProgress({sandboxId, cmdId})`; on `done`/`error` stop the VM with
  `Sandbox.get({sandboxId}).then((s) => s.stop())`; treat `expired` as failure.
- Template pattern against cold starts (`template-vercel`): at build time create a sandbox, add the bundle,
  `sandbox.snapshot({expiration: 0})`, store `snapshotId` in Blob keyed by `VERCEL_DEPLOYMENT_ID`; per request
  `Sandbox.create({source: {type: 'snapshot', snapshotId}})`. Stream progress to the browser as SSE, run the job in
  `waitUntil()`, always `sandbox.stop()` in `finally`.
- Blob files and snapshots persist forever unless deleted; set Vercel Spend Management and add rate limiting.

### 4.18 Cloud Run (only if a client requires GCP)

`npx remotion cloudrun services deploy --memoryLimit=2Gi --cpuLimit=2 --timeoutSeconds=900`, then
`npx remotion cloudrun sites create src/index.ts --site-name=acme-promo`, then
`npx remotion cloudrun render acme-promo Promo --service-name=<name> --region=us-east1`. In Node use
`@remotion/cloudrun/client`, branch on `result.type`, and on `crash` compare `requestElapsedTimeInSeconds` with the service
timeout and read the logs at `consoleUrl`. Queue anything beyond max instances yourself (Cloud Tasks). Keep min instances
at 0 unless the client pays for warm instances.

### 4.19 Debug a failed Lambda render

1. Reproduce: `npx remotion lambda render <site> <comp> --props=props.json --log=verbose` and let it finish or fail.
2. Read the error; open the printed links. CloudWatch filters: renderers `method=renderer,renderId=<id>`, one chunk
   `method=renderer,renderId=<id>,chunk=12`, main `method=launch,renderId=<id>`. In code, use `cloudWatchLogs`,
   `cloudWatchMainLogs` and `folderInS3Console` from the render call (`logLevel: 'verbose'` while debugging only).
   With `concurrency: 1` there are no renderer logs.
3. Open `renders/<id>/progress.json`: missing entries in `chunks` are the failed chunks.
4. Classify: React error (the CLI symbolicates stack traces), `delayRender()` timeout (a bug or a slow asset; raise
   `timeoutInMilliseconds` only after checking), chunk function timeout, main function timeout (raise `--timeout` on
   deploy, optimise, or find the stuck chunk).
5. Fix, redeploy the site, re-render. For a bug report share `progress.json` and complete CloudWatch logs.

### 4.20 Transparent video from Lambda

Transparent WebM (`vp8`/`vp9` + `yuva420p`) can flicker in the alpha channel at chunk boundaries because VP8/VP9 alpha
depends on previous frames. On Lambda prefer ProRes with alpha: `codec: 'prores'`, `proResProfile: '4444'`,
`pixelFormat: 'yuva444p10le'`, `imageFormat: 'png'` (from `transparent-videos.md`). If WebM is required, render it locally
in one pass, or raise `framesPerLambda` to reduce boundaries.

### 4.21 Encoding parity with our local pipeline

`renderMediaOnLambda()` ignores `remotion.config.ts`, so pass every setting the local config applies: `codec`, `crf`,
`pixelFormat`, `colorSpace` (our `remotion-broll` standard is bt709), `audioCodec`, `audioBitrate`, `sampleRate`,
`x264Preset`, `imageFormat`, `jpegQuality`, `scale`, `muted`. Composition-level defaults returned by
`calculateMetadata()` (e.g. `defaultCodec`, `defaultPixelFormat`) travel inside the bundle; check precedence against the
required `codec` argument before relying on them.

### 4.22 Price check before a batch

Render one representative video; read `costs.accruedSoFar` and `estimatedBillingDurationInMilliseconds` from the final
progress (or `costs` in the webhook); multiply by batch size; add S3 egress for assets and storage. Reference numbers from
`cost-example.md` (2048 MB, 10 GB disk, us-east-1, v4.0.381): Hello World $0.001 (7.6 s warm, 11 s cold); 1 min video
with an embedded local video file $0.017 to $0.021 (15 to 19 s); 10 min remote HD video $0.103 to $0.108 (56 to 61 s);
10 s remote 4K video $0.013 to $0.014 (45 to 53 s). Video inside video and 4K dominate cost.

---

## 5. Performance and render stability

### 5.1 What breaks chunked (distributed) rendering
- State carried between frames: accumulators in `useState`/`useRef`, per-frame physics integration, "previous value"
  logic. Chunk N starts at its first frame without rendering the earlier frames. Derive everything from
  `useCurrentFrame()`.
- Non-determinism: `Math.random()` (use `random(seed)`), `Date.now()`, data fetched per chunk that may change between
  chunks (fetch once in `calculateMetadata()` or before the render and pass as props).
- Wall-clock animation: CSS transitions or animations, Lottie or GSAP playing in real time, autoplaying video. Drive them
  from the frame.
- Encoder boundaries: every chunk starts a new GOP (`gopSize` caps GOP length per chunk); transparent WebM alpha flicker;
  audio is encoded per chunk then combined (Remotion avoids lossy seams by using uncompressed audio in chunks where needed).
- Per-chunk setup cost: fonts, big images and video seeks at the start of each chunk are paid once per chunk; with 150
  chunks they are paid 150 times.

### 5.2 Default chunking (code from `concurrency.md`)

```ts
const concurrency = interpolate(frameCount, [0, 18000], [75, 150], {extrapolateRight: 'clamp'});
const fpl = Math.max(frameCount / concurrency, 20);
const framesPerLambda = Math.ceil(frameCount / Math.ceil(frameCount / fpl));
```

Computed at 30 fps: 3 s = 18 frames x 5 functions; 5 s = 19 x 8; 10 s = 20 x 15; 30 s = 20 x 45; 60 s = 22 x 82;
90 s = 32 x 85; 2 min = 40 x 90; 3 min = 56 x 97; 5 min = 80 x 113; 10 min and longer = 150 functions. Leaving
`framesPerLambda` unset (null) always stays within bounds.

### 5.3 Speed levers, in rough order of impact
1. Concurrency up (lower `framesPerLambda`) until orchestration overhead dominates; no gain beyond 200, and more cost.
2. Memory up for vCPU (3009 MB = 3 vCPUs); then `concurrencyPerLambda` 2 or 3. Counter-productive if the function is
   already saturated.
3. `@remotion/media` `<Video>`/`<Audio>` (partial downloads, earlier decoding).
4. Disk 10240 MB (Chrome gets more disk cache; costs under 1 percent more).
5. `x264Preset: 'veryfast'` (the v5 default, chosen to cut encode time and cost).
6. `audioCodec: 'mp3'` makes the combine stage much faster (v4.0.16 tip; QuickTime will not play it; slightly larger).
7. `speculateFunctionName()` instead of `getFunctions()` (up to 1 s saved).
8. `overwrite: true` skips an existence check.
9. `skipLambdaInvocation` for faster polling (latency only).
10. Region-named buckets (created after Dec 2022) avoid per-bucket region lookups.

### 5.4 Cost levers
Less memory (linear); lower concurrency (less warm-up, browser start and asset download overhead); `@remotion/media`
tags; cheaper regions; precomputed props; general render performance; cancellation only when needed; `deleteAfter` and
lifecycle rules; R2 for assets and outputs; CloudWatch retention; `skipLambdaInvocation` (one less invocation per poll).

### 5.5 Memory and disk
- Output about half the disk. v4 default disk 2048 MB = about 32 min of 1080p; 10240 MB = about 2 h 40 min.
- `offthreadVideoCacheSizeInBytes` and `mediaCacheSizeInBytes` default to half the memory; lower them if a 2048 MB
  function struggles with heavy video.
- `logLevel: 'verbose'` disables artifact cleanup: debugging only.

### 5.6 Timeouts
- `timeoutInMilliseconds` (delayRender, default 30000) versus function `timeoutInSeconds` (default 120, max 900).
  Parallel renders rarely need more than 120 s; `concurrency: 1` renders need much more.
- A 2021 changelog entry: renders not complete 20 s after the main function's timeout are marked failed (no stuck renders).
- Cloud Run service timeout default 300 s, max 3600 s. Vercel: function 800 s, sandbox 45 min or 5 h, creation 5 min.

### 5.7 WebGL and GPU
Lambda's default `gl` is `swangle` (software rendering). Three.js, shaders and heavy canvas are CPU-bound in the cloud:
give more memory, lower resolution, or render locally with a GPU. Neither Lambda nor Vercel Sandbox has a GPU; Cloud Run
with GPU is untested.

### 5.8 Cold starts and warm functions
Cold starts add seconds (Hello World 7.6 s warm vs 11 s cold). One function per configuration stays warmer than several;
extra regions add redundancy and capacity but can hit cold functions. Vercel Sandbox cold start includes VM provisioning,
dependency install and browser download unless you restore a snapshot.

---

## 6. Errors and fixes

| Symptom | Cause | Fix |
|---|---|---|
| `TooManyRequestsException: Rate Exceeded` or `ConcurrentInvocationLimitExceeded` | Account concurrency or burst limit | `npx remotion lambda quotas`; request an increase; lower per-render `concurrency`; queue and stagger; spread across regions or accounts; `concurrency: 1` while waiting |
| `Too many functions: This render would cause [X] functions to spawn. We limit this amount to 200 functions...` | `framesPerLambda` too low | Leave it null, or keep functions at 200 or fewer and `framesPerLambda` at 5 or more |
| `The security token included in the request is invalid` | Region not enabled in the account | Enable the region (account menu, Account); or `getRegions({enabledByDefaultOnly: true})` |
| `UnrecognizedClientException: The AWS credentials provided were probably mixed up.` | Called inside Lambda or a Vercel function where `AWS_*` hold the platform's credentials | Use `REMOTION_AWS_ACCESS_KEY_ID` / `REMOTION_AWS_SECRET_ACCESS_KEY` |
| `AccessControlListNotSupported: The bucket does not allow ACLs` | Output bucket has ACLs disabled | `privacy: 'no-acl'` |
| `InvalidBucketAclWithObjectOwnership: Bucket cannot have ACLs set with ObjectOwnership's BucketOwnerEnforced setting` or `AccessDenied` creating a bucket or site | AWS blocks public buckets by default (since April 2023) | Remotion 3.3.87 or later; add `s3:PutBucketOwnershipControls` and `s3:PutBucketPublicAccessBlock` to the user policy; redeploy function and site |
| `You have multiple buckets [a,b,c] in your S3 region [us-east-1] starting with "remotionlambda-"` | Extra prefixed buckets | Delete the extras, or pass `forceBucketName` / `--force-bucket-name` everywhere (then `sites ls`, `getSites()`, `getOrCreateBucket()` cannot be used) |
| Generic AWS permission errors | `.env` not loaded in Node; user and role policies swapped; propagation delay; a new version needs new permissions; other credentials (AWS CLI) picked up | Load dotenv; re-check both policies; wait 2 to 3 min; re-copy policies after upgrades; log which variables are set; `policies validate` (user only) |
| `delayRender()` timed out | `continueRender()` never called, or a font, fetch or asset is too slow from AWS | Fix the code; host assets on a cached CDN; raise `timeoutInMilliseconds` (render), not the function timeout |
| Main function timed out | Render longer than the function timeout, a bottleneck, or one stuck chunk | Raise the function timeout (redeploy), increase concurrency, optimise, find the stuck chunk in `progress.json` and CloudWatch |
| One chunk runs far longer than the rest | Uncached or slow range requests to remote media (often R2 `r2.dev`), long GOP sources | Custom domain + Cloudflare Cache Rule, shorter keyframe interval, `delayRenderTimeoutInMilliseconds` + `delayRenderRetries` on `@remotion/media` components |
| `getFunctions({compatibleOnly: true})` returns `[]`, version mismatch warning, or protocol errors | Client, function and site versions differ | Deploy a function for the installed version; redeploy the site; pin every Remotion package to one version (also Python/PHP/Go/Ruby SDKs) |
| Render errors because a file exists at the custom `outName` | `overwrite` is false by default on v4 | `overwrite: true`, or unique keys |
| `cancelRenderOnLambda()` throws | Render not started with `enableCancellation` | Start renders with `enableCancellation: true` when they may need cancelling |
| Ctrl+C in the CLI, costs keep running | No `--enable-cancellation` | Use the flag, or call `cancelRenderOnLambda()` |
| Error enabling Lambda Insights | Region `ap-southeast-4`, `ap-southeast-5` or `eu-central-2` | Deploy without Insights there |
| Insights or VPC config missing | Function already existed | Delete the function and redeploy |
| Webhook signature invalid | Secret mismatch, body passed as a string, or `NO_SECRET_PROVIDED` | Same secret both sides, pass the parsed body, always set a secret |
| Error about webhook `customData` | Over 1024 bytes serialized | Put data in `inputProps`, send only an id |
| Tofu boxes or wrong fonts in cloud output | Script or family not installed (Bengali, brand fonts) | Load web fonts in the composition |
| Emoji look different from local | Lambda uses Noto Color Emoji | `runtimePreference: 'apple-emojis'` or emoji images |
| Flicker in transparent WebM alpha | VP8/VP9 alpha across chunk boundaries | ProRes 4444 on Lambda, or WebM rendered locally in one pass, or larger `framesPerLambda` |
| `av1` codec or `pdf` still rejected | Not in the lean Lambda binaries | Render locally |
| Historical: `Error: expected to launch` / `Failed to launch the browser process!` (SIGBUS, Feb 2023) | AWS Node 14 runtime update | Fixed in Remotion 4.0; runtime locking needs `lambda:PutRuntimeManagementConfig` |
| Historical: `relocation error: /lib64/librt.so.1: symbol __pthread_attr_copy...` (Feb 2022) | AWS micro-VM change vs a bundled libpthread | Fixed; the old `--architecture=x86_64` workaround is obsolete (x86 discontinued) |
| Cloud Run `503 service unavailable` | Max instances reached | Raise `maxInstances` or the GCP quota; queue with Cloud Tasks |
| Cloud Run result `type: 'crash'` | Service died without a response (timeout or memory) | Compare `requestElapsedTimeInSeconds` with the service timeout; read logs at `consoleUrl`; raise memory or timeout |
| Cloud Run `You have multiple buckets [...] starting with "remotioncloudrun-"` | Extra buckets | Delete extras in the GCP console |
| GCP key creation fails | 10 keys per service account max | Delete an old key (installer key-management option) |
| Vercel template: `BLOB_READ_WRITE_TOKEN is not set` | No Blob store linked | Create a Blob store, link it, `vercel env pull .env.local` |
| Vercel template: `No sandbox snapshot found. Run bun run create-snapshot...` | Snapshot step missing from the build | Build command `turbo run build create-snapshot` (see `vercel.json`) |
| Vercel function times out | Render longer than 800 s | `detached: true` + `getRenderProgress()` |
| Vercel progress stage `expired` | Sandbox reached its timeout | Raise `detachedSandboxTimeoutInMilliseconds`; handle as a failure |
| Go or Ruby SDK rejects big props | SDK payload limits (Go 200 KB, Ruby about 60 KB) | Store data elsewhere and pass an id, or use the JS or Python client |
| Supabase sample fails with `speculateFunctionName is not defined` | Doc sample forgets the import | Import it from `npm:@remotion/lambda-client@<version>` |

---

## 7. What our skills must teach

### 7.1 Where to render (decision table)

| Situation | Choose |
|---|---|
| One or a few client deliverables, highest fidelity, the Mac Studio is available | Local render (full codec set, Mac fonts, GPU, no cloud bill). Default for our agency work |
| Needs AV1 output or PDF stills | Local |
| Bangla or other non-Noto scripts and fonts are not yet loaded as web fonts | Local, or add web fonts first and verify one cloud render |
| Many personalised videos, a SaaS feature, a batch, or fast turnaround on long videos | Lambda |
| Client app already on Vercel and wants no AWS | Vercel Sandbox (experimental: pin versions, test every upgrade) |
| Client mandates GCP | Cloud Run, with a written warning that it is alpha and unmaintained |
| Over about 80 min Full HD or output over about 5 GB | Local or a long-running server (`template-render-server`) |
| WebGL/3D heavy | Local with GPU, or Lambda with more memory after a cost test |

### 7.2 Safety and consent rules
- Never ask for, print, paste or type AWS, GCP or Vercel secrets. The human creates accounts, IAM users, keys and `.env`.
  The agent only checks that the variables exist.
- Before the first deploy in an account, and before any batch, state what will be created and the expected cost, and wait
  for a yes. Cloud resources are billable.
- `functions rmall`, `sites rmall`, anything with `-y`, `deleteSite`, `deleteRender`, bucket deletion and
  `services rmall`: destructive, need explicit confirmation naming the exact targets. Never run uninstall steps unasked.
- Never call Lambda APIs from browser code. Render endpoints must be authenticated and rate-limited.
- Do not run the Cloud Run installer (downloads and executes a script in the user's GCP Cloud Shell); give the human the steps.
- License reminder: companies with more than 3 people need Remotion cloud rendering seats; set `licenseKey`, and
  `isProduction: false` for test renders.

### 7.3 Our defaults on 4.0.528 (set them explicitly)
- One region close to the client's assets and audience (default `us-east-1`); function, bucket and site in that region.
- Function: `memorySizeInMb: 2048` for motion graphics, `3009` for video-in-video, 4K or heavy scenes; `diskSizeInMb:
  10240`; `timeoutInSeconds: 240`; `createCloudWatchLogGroup: true`; retention 14 days. Keep the triple in one config file
  and derive the name with `speculateFunctionName()` everywhere (no hardcoded names).
- Site: `npx remotion bundle` then `deploySiteFromBundle()`; `siteName: '<client>-<project>-<env>'`.
- Render: import from `@remotion/lambda/client`; `codec: 'h264'`; `colorSpace: 'bt709'`; leave `framesPerLambda` unset
  unless budgeting; `downloadBehavior` with a clean filename; `privacy: 'private'` + presigned links for unreleased client
  work; `deleteAfter` for temporary renders (bucket with folder expiry); `overwrite: true` when reusing keys;
  `enableCancellation: true` for user-facing jobs; a webhook for batches and anything over a minute.
- Progress: poll every 1 s with `skipLambdaInvocation: true`; stop on `done` or `fatalErrorEncountered`; surface
  `errors[0].message` plus the CloudWatch links.

### 7.4 Pre-flight checklist before any cloud render
1. Composition is deterministic: frame-pure, seeded random, no wall clock, no per-chunk network data.
2. Every font is a web font loaded before the frame renders; non-Latin scripts (Bengali) checked in a cloud test render.
3. Assets use `staticFile()` or public HTTPS URLs reachable from AWS; big media on a cached CDN; no `localhost` URLs, no
   absolute `/path` asset URLs.
4. `inputProps` are JSON-serializable; secrets in `envVariables`, never in the bundle.
5. Versions equal: `remotion`, `@remotion/lambda`, deployed function, deployed site (`functions ls`,
   `sites ls --compatible-only`).
6. Function, bucket and site in the same region.
7. `npx remotion lambda quotas` leaves headroom for the planned functions (table 5.2).
8. Expected output below half the disk.
9. Codec supported on Lambda (no AV1, no PDF).
10. Encoding options copied from the local config (the Node API ignores `remotion.config.ts`).
11. One test render reviewed (visual check and cost) before a batch.

### 7.5 Production checklist (condensed from both platforms' checklists)
Memory tuned down to the lowest stable value; maximum output length vs disk, and user-requested lengths capped;
least-privilege credentials in environment variables; concurrency within bounds; output privacy decided; per-user rate
limiting; function timeout measured; license in place. Cloud Run also: instance limits (503 beyond), 1 request per
instance, memory-bound output. Vercel also: Spend Management, cleanup of Blob files and snapshots.

### 7.6 Debug procedure (always in this order)
CLI repro with `--log=verbose` and `--props=<file>`; read the final error; CloudWatch (renderer, chunk, launch filters);
`progress.json` chunk list; classify (code error, delayRender timeout, chunk timeout, main timeout); fix; redeploy the site;
re-render.

### 7.7 Never assume
- That a local render proves a cloud render (fonts, emoji, GPU, codecs, config file, asset reachability all differ).
- That `concurrency` or `--timeout` mean the same thing in every context.
- That Ctrl+C stops a Lambda render.
- That renders are private, or that pre-v4.0.418 buckets are unlistable.
- That v5 defaults apply on 4.0.528 (disk 10240, `overwrite: true`, `veryfast`, Cloud Run max instances 5).
- That Cloud Run or `@remotion/vercel` APIs are stable.

---

## 8. Best examples to learn from

- `repo/packages/template-next-app-tailwind/config.mjs`, `deploy.mjs`, `src/app/api/lambda/render/route.ts`,
  `src/app/api/lambda/progress/route.ts`: canonical deploy, render and progress loop from one config triple (3009 MB,
  10240 MB, 240 s) with `speculateFunctionName()`; passes `webpackOverride` to `deploySite()`; env checks with clear errors.
- `examples/template-prompt-to-motion-graphics-saas/src/app/api/lambda/render/route.ts` and `progress/route.ts`: the same
  pattern in a SaaS product (`framesPerLambda: 60`, download filename).
- `repo/packages/template-react-router/app/lib/render-video.server.ts` and `app/progress.tsx`: Lambda from React Router
  actions, with `metadata` and `downloadBehavior`, progress mapped to `{type: progress | done | error}`.
- `examples/github-unwrapped/deploy.ts`, `delete.ts`, `src/server/render.ts`, `src/server/make-og-image.ts`,
  `src/helpers/set-env-for-key.ts`, `src/helpers/get-account-count.ts`, `src/config.ts`: production scale on Lambda: every
  account times every region deployed, random account and region per render, render records in a database (no duplicate
  renders), `deleteAfter: '30-days'`, bucket CORS via `getAwsClient`, OG and story stills in parallel with the video,
  batch cleanup of `renders/` with `p-limit`, lean 1200 MB functions.
- `repo/packages/template-vercel/create-snapshot.ts`, `src/app/api/render/route.ts`,
  `src/app/api/render/restore-snapshot.ts`, `src/app/api/render/helpers.ts`, `vercel.json`: Vercel Sandbox with a
  build-time snapshot, SSE progress, `waitUntil()`, Blob upload and `sandbox.stop()` in `finally`.
- `repo/packages/template-render-server/` (`README.md`, `server/`, `Dockerfile`): self-hosted Express render server with
  start, progress and cancel endpoints, the non-Lambda option.
- `examples/cloudflare-containers-demo/`: rendering on Cloudflare Containers with R2 output (paid Workers plan needed).
- Docs to re-read: `mirror/docs/lambda/setup.md` (full setup), `rendermediaonlambda.md` (every option),
  `troubleshooting/debug.md` (debug method), `concurrency.md` (chunk maths), `cost-example.md` (real prices),
  `data-transfer-cost.md` (asset costs, R2 caching), `custom-destination.md` (outputs), `webhooks.md` (payloads, signing),
  `separate-environments.md` and `upgrading.md` (operations), `runtime.md` (fonts, Chrome, vCPU), `custom-layers.md`
  (layer sizes), `mirror/docs/vercel/render-media-on-vercel.md` and `types.md` (Vercel stages).

---

## 9. Open questions

1. Minimum `framesPerLambda` on 4.0.528: `concurrency.md` says 5 (4 until 4.0.331), but the `concurrency` option says
   "must result in framesPerLambda >= 4". Test before using 4.
2. Lambda Node runtime: the table says 24.x from v4.0.415, the prose says Lambda stays on 20.x. Which runtime ARN does
   4.0.528 lock?
3. Region list: `cli/regions.md` lacks `ap-southeast-4`, `ap-southeast-5` and `eu-central-2`, yet `insights.md` discusses
   deploying there. Run `npx remotion lambda regions` on 4.0.528.
4. `custom-destination.md` says custom buckets and other clouds are "not supported from the CLI", but `cli/render.md`
   documents `--s3-output-provider-*` flags without a version. Since which version, and does 4.0.528 have them?
5. `presignUrl()` with `checkIfObjectExists: false` is documented to throw for missing objects, which is unusual for
   presigning. Verify.
6. `uploadToVercelBlob()` lists `access` as required and also "Default: private". Treat it as required.
7. Cloud Run docs contradict themselves on per-instance concurrency ("0" vs "1") and the validate command
   (`cloudrun permissions` vs `cloudrun policies validate`); the uninstall page writes `cloudRun`.
8. Fonts and emoji inside Vercel Sandbox and Cloud Run images are undocumented. Test Bangla, emoji and CJK before
   promising parity.
9. `examples/github-unwrapped/deploy.ts` passes `enableV5Runtime: true` to `deployFunction()`, an option not in the docs
   read here. Does 4.0.528 accept it and what changes?
10. Does `npx remotion lambda render` apply every encoding setting from `remotion.config.ts` (colorSpace, crf, x264 preset)
    like `npx remotion render` does? Likely (config support is documented for bundling and `--config` exists); test once.
11. Exact `inputProps` size at which the JS client switches to S3 upload (Python mirrors "the same logic": about 194 KB for
    video, 4.9 MB for stills).
12. Webhook retry behaviour on non-200 responses and timeouts is not documented.
13. Precedence between `calculateMetadata()` default encoding fields (`defaultCodec`, `defaultPixelFormat`) and the
    explicit `codec` that `renderMediaOnLambda()` requires.
14. Cost examples were measured on v4.0.381 with a 10 GB disk. Re-measure our typical compositions on 4.0.528.
15. Vercel Sandbox pricing and its concurrency numbers (10 Hobby, 2000 Pro) come from Remotion's page, not Vercel's; confirm
    before quoting to a client.
