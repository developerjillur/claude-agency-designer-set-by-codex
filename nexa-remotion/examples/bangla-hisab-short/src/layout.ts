// The 9:16 layout: the words sit in the top band of the safe area, the stage (notebook, then phone) below it and
// running past the safe area's bottom (only decoration goes there; every word stays inside the safe area).
export const WORDS_TOP = 280; // captions and the hook title
export const STAGE_TOP = 500;
export const PHONE_W = 600;
export const PHONE_LEFT = (1080 - PHONE_W) / 2;
export const K = PHONE_W / 380; // UI inside the phone was sized for a 380 px phone
