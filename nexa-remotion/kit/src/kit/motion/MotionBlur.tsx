// Motion blur for fast moves (whips, flicks, fast slides). It renders `samples` copies of its children at
// sub-frame times, so the children must be a component that calls useCurrentFrame() itself, or nothing blurs.
// Keep samples at 5 to 8: every sample is a full extra render of the children.
import {CameraMotionBlur, Trail} from '@remotion/motion-blur';
import React from 'react';

export const MotionBlur: React.FC<{children: React.ReactNode; samples?: number; shutter?: number}> = ({
	children,
	samples = 6,
	shutter = 180,
}) => (
	<CameraMotionBlur samples={samples} shutterAngle={shutter}>
		{children}
	</CameraMotionBlur>
);

/** Echo copies that lag behind a moving element: a stylised streak rather than a camera blur. */
export {Trail};
