import type {LonLat} from './kit/maps';
import {CUE} from './cues';

// A typical container route by sea from Chattogram to Rotterdam, through the Suez Canal. The waypoints keep the
// line on water (round Sri Lanka, through Bab-el-Mandeb and the canal, off the coast of Tunisia and Algeria, round
// Iberia and up the Channel).
export const PLACE = {
	chattogram: [91.78, 22.33] as LonLat,
	colombo: [79.85, 6.93] as LonLat,
	suez: [32.55, 29.97] as LonLat,
	gibraltar: [-5.6, 35.95] as LonLat,
	rotterdam: [4.05, 51.95] as LonLat,
};

// Each segment starts on its word and lands on the place's name; frames per leg are split by distance.
export const SEGMENTS: {stops: LonLat[]; delay: number; legs: number[]}[] = [
	// "leaves" to "Colombo": the ship is moving from the first second
	{stops: [PLACE.chattogram, [88.6, 15.8], [82.2, 5.6], [80.3, 5.25], [79.55, 6.1], PLACE.colombo], delay: CUE.leaves, legs: [64, 108, 17, 12, 9]},
	// "Then" to "Suez"
	{stops: [PLACE.colombo, [65.0, 11.2], [48.2, 12.4], [43.4, 12.6], [38.4, 20.2], PLACE.suez], delay: CUE.then, legs: [55, 61, 17, 33, 41]},
	// "Suez" to "Gibraltar": a slow canal transit while the camera is close, then the Mediterranean
	{stops: [PLACE.suez, [32.3, 31.3], [20.0, 34.3], [12.3, 36.9], [9.6, 37.8], [4.5, 37.5], [-1.5, 36.3], PLACE.gibraltar], delay: CUE.suez, legs: [24, 48, 27, 10, 17, 19, 14]},
	// "up the coast" to "Rotterdam", arriving just before the word so the port gets its moment
	{stops: [PLACE.gibraltar, [-9.5, 36.6], [-10.2, 43.6], [-5.3, 48.6], [1.6, 51.0], PLACE.rotterdam], delay: CUE.europe - 33, legs: [10, 20, 18, 13, 7]},
];
