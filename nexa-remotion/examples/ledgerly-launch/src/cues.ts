// The music (110 BPM) sets the cuts: every whip is centred on a downbeat of the fitted track (music_fit.json).
// The fitted track is the song's first 8 bars, then its last 4 (the loud middle is cut at the 17.55 s downbeat, under
// the third whip), so it ends on the song's own stop at 26.1 s and rings out to 27.0 s.
export const DOWNBEAT = [3, 68, 134, 199, 265, 330, 396, 461, 527, 592, 658, 723, 788];
export const T = 12; // transition frames
// scene starts so that each 12-frame whip is centred on its downbeat: 134, 330, 527, 658
export const START = [0, 128, 324, 521, 652];
export const DURATION = [140, 208, 209, 143, 158]; // mounted frames, overlaps included (sum - 4 x 12 = 810)
export const TOTAL = 810;
export const PAID_NOTE = DOWNBEAT[11] - START[4]; // the payment arrives on the last bar's downbeat (24.1 s)
export const STAMP = 774 - START[4]; // and the Paid stamp lands on the song's last kick (25.8 s), before it rings out
