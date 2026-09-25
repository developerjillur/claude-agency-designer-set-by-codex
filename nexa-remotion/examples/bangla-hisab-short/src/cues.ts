// The cue table: global frames at 30 fps, from the voice-over's word timings (src/data/words.ts).
export const FPS = 30;
export const at = (seconds: number): number => Math.round(seconds * FPS);

// scene cuts land a few frames before the phrase that opens the scene; the close starts while the phone leaves, so
// its title is rising when the voice says "আজই" (19.0 s)
export const CUT = {phone: 93, rule1: 183, rule2: 297, rule3: 426, phoneOut: 541, end: 559, total: 720} as const;

export const CUE = {
	khata: at(1.5), // "খাতায়?"
	tinta: at(4.2), // "তিনটা"
	prottekta: at(7.2), // "প্রতিটা"
	porpori: at(8.0), // "পরপরই"
	felun: at(8.9), // "ফেলুন।"
	mot: at(12.2), // "মোট"
	nin: at(13.2), // "নিন।"
	mash: at(15.2), // "মাস"
	beshi: at(17.3), // "বেশি"
	ajker: at(20.1), // "আজকের"
} as const;
