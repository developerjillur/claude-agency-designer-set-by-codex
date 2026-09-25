// Settings measured on a Mac Studio (M4 Max, 2026-09-25): angle was faster and lighter on memory for footage,
// JPEG quality 90 costs almost nothing, and YouTube expects BT.709 for SDR. nvc.py passes the same values on the
// command line, so they also hold for renders started from code.
import { Config } from "@remotion/cli/config";

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(90);
Config.setOverwriteOutput(true);
Config.setColorSpace("bt709");
Config.setChromiumOpenGlRenderer("angle");
