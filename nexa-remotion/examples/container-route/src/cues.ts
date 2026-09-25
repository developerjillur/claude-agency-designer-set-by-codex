// Cue table: global frames at 30 fps from the voice-over's word timings (vo/words.json).
export const at = (seconds: number): number => Math.round(seconds * 30);

export const CUE = {
	leaves: at(0.7),
	chattogram: at(1.2),
	crosses: at(5.3),
	bay: at(6.1),
	colombo: at(7.7),
	there: at(9.5),
	bigger: at(11.0),
	then: at(12.9),
	west: at(13.6),
	arabian: at(15.4),
	redSea: at(17.6),
	suez: at(19.8),
	med: at(22.5),
	gibraltar: at(25.1),
	europe: at(27.4),
	rotterdam: at(28.9),
	end: at(29.8),
} as const;

export const TOTAL = 990;
