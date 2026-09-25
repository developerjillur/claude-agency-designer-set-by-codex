// Settings for `npx remotion studio` and `npx remotion render` in a kit project. The Node render APIs
// (renderMedia, renderStill) ignore this file: pass the same options to them. nrk.py passes its own flags.
import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(95);
Config.setColorSpace('bt709');
// WebGL (effects, 3D, shader transitions) draws nothing on the default renderer; angle uses the GPU.
Config.setChromiumOpenGlRenderer('angle');
Config.setOverwriteOutput(true);
