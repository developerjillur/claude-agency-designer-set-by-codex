// The cue table: global frames at 30 fps, from the voice-over's word timings (src/data/words.ts).
export const FPS = 30;
export const at = (seconds: number): number => Math.round(seconds * FPS);

// scene cuts land 3 frames before the phrase that opens the scene; the close starts while the phone leaves, so
// its title is rising when the voice says "আজই" (19.0 s)
export const CUT = {phone: 87, rule1: 180, rule2: 294, rule3: 423, phoneOut: 541, end: 559, total: 720} as const;

export const CUE = {
	khata: at(1.4), // "খাতায়?"
	tinta: at(4.1), // "তিনটা"
	prottekta: at(7.1), // "প্রতিটা"
	porpori: at(7.9), // "পরপরই"
	felun: at(8.8), // "ফেলুন।"
	mot: at(12.1), // "মোট"
	nin: at(13.2), // "নিন।"
	mash: at(15.1), // "মাস"
	beshi: at(17.2), // "বেশি"
	ajker: at(20.0), // "আজকের"
} as const;
