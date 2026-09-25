# The design module's API at a glance

Import from `./kit/design` (or `./kit` when the kit index exports design). Full prop tables, examples and gotchas:
`src/kit/design/README.md` in a project (the kit's copy lives in `~/.claude/skills/nexa-remotion/kit/src/kit/design/`).
Sizes are px at 1080 (multiplied by `unit`); colours default to the theme's.

## Grounds
```
<Ground kind="lit|spot|band|solid" color color2 light={[x,y]} intensity=1 split=0.64 direction="horizontal|vertical"
        seam="soft|hard" drift=0.05 grain vignette dither=true>{scene}</Ground>
<Gradient kind="linear|radial|conic" colors stops angle center drift=0 space="oklab|oklch|srgb" dither=0.035 grain vignette />
<Mesh colors base speed=1 wander=0.16 size=1 seed grain(>=0.05) vignette />
<EffectGround kind="blueprint|liquid|waves|starburst|contours|floor" colors={[ground, pattern]} contrast speed=1 scale=1
              seed=4 loop=false pixelDensity grain vignette />
<Paper color amount=0.5 fibers=0.2 crumples=0.1 folds=0.05 roughness=0.22 scale=0.8 seed=6 boil=0 grid rules margin
       lineColor lineWeight=1.7 engine="auto|webgl|css" grain light=1 />
<Finish grain vignette dither />            // the theme's vignette + grain, last in a custom scene
```

## Texture and light
```
<Grain amount(theme) rate=12 size=1.25 blend="auto|signed|overlay|soft-light" seed />
<Vignette amount(theme) color center={[0.5,0.46]} size=1 />
<Pattern kind="grid|dots|cross|stripes|rules|checker|halftone" size weight color opacity angle fade drift={[x,y]} />
<Spotlight at to radius=300 | rect toRect corner  moveAt=30 moveFrames feather dim=0.62 color(bg) glow delay fade exit />
<LightSweep at=8 duration=28 angle=-18 width=0.3 intensity=0.6 color blend radius>{card}</LightSweep>
grainTile(kind) grainUrl(kind) useGrainUrl(kind) hasWebGL2()
```

## Surfaces
```
<Card variant="solid|outline|glass|paper|tonal" elevation radius padding=44 width height color blur=28 tilt />
<Pill variant="soft|solid|outline|glass" color size=30 caps dot icon>Label</Pill>
<Badge variant="solid|soft|outline|glass" color size=28>+24%</Badge>
<Scrim side="bottom|top|left|right|center|full" size=0.62 strength=0.72 color />
<Frame variant="mat|polaroid|line|bare" width=720 height=480 mat color radius elevation=3 tilt caption>{img}</Frame>
<Border kind="rule|double|corners|brackets" inset="safe" color weight length=64 delay duration=24 />
<Panel width=1100 height=680 title bar="dots|title|none" tone="auto|light|dark" elevation=4 radius padding=0>{ui}</Panel>
<OnTone dark>{chips on a dark picture}</OnTone>    useOnDark()
elevation(level, theme, unit)  surfaceAt(level, theme)  hairline(theme)  tonal(theme, color?)  SPACE  space(step, unit)
```

## Layout
```
const {shape, wide, tall, pick, safe, width, height, unit} = useLayout();   // shape: wide|square|portrait|tall
pick({wide: 3, tall: 1}, shape)   shapeOf(aspect)   Responsive<T> = T | {wide?, square?, portrait?, tall?}
<Grid columns={{wide:3,square:2,portrait:2,tall:1}} rows gap={{wide:32,tall:24}} rowGap align fill area>{cells}</Grid>
<Cell span rowSpan />
<Stack dir="column" gap=24 align justify wrap fill area />
<Center area="safe" maxWidth={{wide:0.72,...}} optical align="center" gap=28 />
<Split ratio=0.5 dir gap=72 area="safe|full" seam="none|line|hard" grounds align justify>{a}{b}</Split>
<StatSplit value sample label note color ratio size align="bottom" />
<FullBleed src|background focus={[x,y]} push=0.04 place scrim="auto" strength=0.72 maxWidth tone="light|dark"
           area="safe|box" pad=44>{text}</FullBleed>
useTextEm(text, {fontFamily, fontWeight, letterSpacing, textTransform})   estimateEm(text, digitEm)
```

## Shapes
```
blobPath({width, height, points=7, wobble=0.16, seed, time}) -> "M ... Z"
<Blob size=520 height color gradient outline points wobble seed speed=0.25 delay grow opacity>{child}</Blob>
<BlobMask width=560 height=640 points wobble=0.12 seed speed=0.2>{img}</BlobMask>
<Ring size=360 weight=6 color progress delay duration=30 start=-90 dashed>{child}</Ring>
<Sparkle size=64 color delay rotate twinkle />
<Squiggle width=420 amplitude=12 waves=5 weight=7 color delay duration=18 seed />
```

## Colour and brand
```
mix(a, b, t)  lighten(c, d)  darken(c, d)  saturate(c, k)  oklch(l, c, h, a?)  toOklch(c)
parseColor(c)  toHex(c)  withAlpha(c, a)  luminance(c)  contrast(fg, bg)  isReadable(fg, bg, 'AA'|'AAA', large?)
readableOn(bg, light?, dark?)  ensureContrast(fg, bg, min=4.5)  isDark(c)  shadowTint(ground)
brandTheme({primary, secondary, dark, base, neutral, fonts, radius, name, grain, vignette}) -> ThemeSpec
```

## Demos (rendered by `nrk.py demos --module design`)
DemoDesignGrounds, DemoDesignGroundsTall (9:16 tiles), DemoDesignGradients, DemoDesignMesh, DemoDesignEffects
(WebGL grounds), DemoDesignTextures, DemoDesignPaper (shader against CSS at true size), DemoDesignGrain (amounts by
tone), DemoDesignPatterns, DemoDesignCards, DemoDesignElevation, DemoDesignSurfaces, DemoDesignMore (bento grid, scrim sides,
FullBleed placements, brackets, full-frame sweep, blob and ring variants), DemoDesignLayouts (16:9),
DemoDesignLayoutsTall (9:16), DemoDesignLayoutsSquare (1:1), DemoDesignLayoutsFeed (4:5), DemoDesignShapes,
DemoDesignColor.
