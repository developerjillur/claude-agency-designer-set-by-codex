// Named curves and springs. Pick by role: `out` family for arrivals, `in` family for departures, `inOut` for
// anything that moves while on screen and for the camera, linear only for clocks (typewriters, tickers).
import {Easing} from 'remotion';

export type Ease = (t: number) => number;

export const curves = {
	linear: Easing.linear,
	// arrivals
	out: Easing.bezier(0.16, 1, 0.3, 1), // expo-like: the default entrance
	outCubic: Easing.bezier(0.33, 1, 0.68, 1), // gentler; better for short moves (strong curves freeze at the end)
	outQuart: Easing.bezier(0.25, 1, 0.5, 1),
	outQuint: Easing.bezier(0.22, 1, 0.36, 1),
	outBack: Easing.bezier(0.34, 1.56, 0.64, 1), // about 10% overshoot: pops, badges, dots
	decelerate: Easing.bezier(0, 0, 0, 1), // Material standard decelerate
	emphasized: Easing.bezier(0.05, 0.7, 0.1, 1), // Material emphasized decelerate
	// departures
	in: Easing.bezier(0.7, 0, 0.84, 0),
	inCubic: Easing.bezier(0.32, 0, 0.67, 0),
	accelerate: Easing.bezier(0.3, 0, 0.8, 0.15), // Material emphasized accelerate
	anticipate: Easing.bezier(0.36, 0, 0.66, -0.56), // pulls back before it goes
	// moves on screen, wipes, camera
	inOut: Easing.bezier(0.65, 0, 0.35, 1),
	inOutQuart: Easing.bezier(0.76, 0, 0.24, 1),
	inOutExpo: Easing.bezier(0.87, 0, 0.13, 1),
	standard: Easing.bezier(0.2, 0, 0, 1), // Material standard
	sine: Easing.bezier(0.37, 0, 0.63, 1),
	snap: Easing.bezier(0.2, 0.9, 0.1, 1), // quick settle, UI feel
} satisfies Record<string, Ease>;

export type CurveName = keyof typeof curves;

export type SpringSpec = {damping: number; stiffness: number; mass: number};

/**
 * A spring from a perceived duration (seconds) and a bounce (0 = no overshoot, 0.15 subtle, 0.3 playful, above
 * 0.4 exaggerated), the model Apple uses. Remotion's spring works in seconds too, so it maps one to one.
 */
export const appleSpring = (duration: number, bounce = 0): SpringSpec => ({
	mass: 1,
	stiffness: ((2 * Math.PI) / duration) ** 2,
	damping: bounce >= 0 ? ((1 - bounce) * 4 * Math.PI) / duration : (4 * Math.PI) / (duration * (1 + bounce)),
});

export const springs = {
	calm: {damping: 200, stiffness: 100, mass: 1}, // no overshoot: the safe default
	smooth: appleSpring(0.5, 0),
	settle: {damping: 18, stiffness: 140, mass: 1}, // a hint of settle
	snappy: {damping: 20, stiffness: 200, mass: 1},
	pop: {damping: 12, stiffness: 180, mass: 1}, // visible overshoot, one hero at a time
	bouncy: {damping: 9, stiffness: 150, mass: 0.7},
	heavy: {damping: 22, stiffness: 90, mass: 2},
} satisfies Record<string, SpringSpec>;

export type SpringName = keyof typeof springs;

/** A spring as an easing curve for interpolate(): the curve is stretched over the segment it is used on. */
export const springEase = (spec: SpringName | SpringSpec = 'calm', allowTail = false): Ease =>
	Easing.spring({...(typeof spec === 'string' ? springs[spec] : spec), allowTail});
