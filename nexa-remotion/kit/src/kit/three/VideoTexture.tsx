// Video on 3D surfaces, the 4.0.528 way: @remotion/media's <Video headless onVideoFrame> draws each frame into a
// canvas behind a CanvasTexture. Frame extraction is async and finishes after ThreeCanvas has drawn the frame, so
// the callback redraws with advance() while rendering (invalidate() does nothing when frameloop is 'never'; the
// official template's invalidate() can leave stale frames).
import type {ThreeElements} from '@react-three/fiber';
import {Video} from '@remotion/media';
import React, {useCallback, useEffect, useMemo, useState} from 'react';
import * as THREE from 'three';
import {useRedraw} from './hooks';
import {roundedPlaneGeometry} from './RoundedBox';

const sourceSize = (s: CanvasImageSource): [number, number] => {
	const v = s as Partial<VideoFrame & HTMLVideoElement & HTMLImageElement & {width: number; height: number}>;
	if (v.displayWidth && v.displayHeight) {
		return [v.displayWidth, v.displayHeight];
	}
	if (v.videoWidth && v.videoHeight) {
		return [v.videoWidth, v.videoHeight];
	}
	if (v.naturalWidth && v.naturalHeight) {
		return [v.naturalWidth, v.naturalHeight];
	}
	return [Number(v.width) || 1, Number(v.height) || 1];
};

/**
 * A texture that video frames are drawn into, cropped to cover `width` x `height` px. Render
 * `<Video src headless muted onVideoFrame={onVideoFrame} />` from @remotion/media next to the mesh (inside the
 * ThreeCanvas) and use `texture` as the material's map (toneMapped false keeps the video's colours).
 */
export const useVideoFrameTexture = (width = 1080, height = 1920, fit: 'cover' | 'fill' = 'cover') => {
	const [state] = useState(() => {
		const canvas = document.createElement('canvas');
		canvas.width = Math.max(2, Math.round(width));
		canvas.height = Math.max(2, Math.round(height));
		const ctx = canvas.getContext('2d') as CanvasRenderingContext2D;
		const texture = new THREE.CanvasTexture(canvas);
		texture.colorSpace = THREE.SRGBColorSpace;
		return {canvas, ctx, texture};
	});
	useEffect(() => () => state.texture.dispose(), [state]);
	const redraw = useRedraw();
	const onVideoFrame = useCallback(
		(frame: CanvasImageSource) => {
			const {canvas, ctx, texture} = state;
			const [fw, fh] = sourceSize(frame);
			const W = canvas.width;
			const H = canvas.height;
			if (fit === 'fill') {
				ctx.drawImage(frame, 0, 0, W, H);
			} else {
				const k = Math.max(W / fw, H / fh);
				const sw = W / k;
				const sh = H / k;
				ctx.drawImage(frame, (fw - sw) / 2, (fh - sh) / 2, sw, sh, 0, 0, W, H);
			}
			texture.needsUpdate = true;
			redraw();
		},
		[state, fit, redraw],
	);
	return {texture: state.texture, onVideoFrame};
};

export type VideoPlaneProps = Omit<ThreeElements['group'], 'children'> & {
	src: string;
	/** World size of the plane; the video is cropped to cover it. */
	width?: number;
	height?: number;
	radius?: number;
	loop?: boolean;
	trimBefore?: number;
	playbackRate?: number;
	/** Texture px per world unit. */
	density?: number;
	children?: React.ReactNode;
};

/** A rounded screen in 3D space showing a video (muted: lay audio separately with <Audio>). */
export const VideoPlane: React.FC<VideoPlaneProps> = ({
	src,
	width = 3.2,
	height = 1.8,
	radius = 0.12,
	loop = true,
	trimBefore,
	playbackRate,
	density = 400,
	children,
	...group
}) => {
	const {texture, onVideoFrame} = useVideoFrameTexture(Math.min(2048, width * density), Math.min(2048, height * density));
	const geo = useMemo(() => roundedPlaneGeometry(width, height, radius, 16), [width, height, radius]);
	useEffect(() => () => geo.dispose(), [geo]);
	return (
		<group {...group}>
			<Video src={src} headless muted loop={loop} trimBefore={trimBefore} playbackRate={playbackRate} onVideoFrame={onVideoFrame} />
			<mesh geometry={geo}>
				<meshBasicMaterial map={texture} toneMapped={false} />
			</mesh>
			{children}
		</group>
	);
};
