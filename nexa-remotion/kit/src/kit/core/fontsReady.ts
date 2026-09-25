import {useEffect, useState} from 'react';
import {useDelayRender} from 'remotion';
import {waitForKitFonts} from './fonts';

/**
 * False until every kit font requested so far has loaded, and holds the render meanwhile. Use it before measuring
 * text (fitText, measureText, getBoundingClientRect): a measurement taken with a fallback font stays wrong.
 */
export const useFontsReady = (): boolean => {
	const {delayRender, continueRender, cancelRender} = useDelayRender();
	const [handle] = useState(() => delayRender('Waiting for the kit fonts'));
	const [ready, setReady] = useState(false);
	useEffect(() => {
		let alive = true;
		waitForKitFonts()
			.then(() => {
				if (alive) {
					setReady(true);
				}
				continueRender(handle);
			})
			.catch((err: unknown) => cancelRender(err instanceof Error ? err : new Error(String(err))));
		return () => {
			alive = false;
		};
	}, [continueRender, cancelRender, handle]);
	return ready;
};
