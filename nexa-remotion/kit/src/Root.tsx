// The kit's own compositions: one demo per component. `npx remotion studio` in the kit (or `nrk.py demos`)
// shows them. A project made with `nrk.py new` gets its own Root from starter/.
import React from 'react';
import {Composition, Folder} from 'remotion';
import {demos as core} from './demos/core';
import {demos as design} from './demos/design';
import {demos as edit} from './demos/edit';
import {demos as fx} from './demos/fx';
import {demos as graphics} from './demos/graphics';
import {demos as maps} from './demos/maps';
import {demos as motion} from './demos/motion';
import {demos as three} from './demos/three';
import {demos as type} from './demos/type';
import {demos as ui} from './demos/ui';
import type {DemoDef} from './kit/core';

const MODULES: [string, DemoDef[]][] = [
	['core', core],
	['motion', motion],
	['type', type],
	['design', design],
	['graphics', graphics],
	['ui', ui],
	['maps', maps],
	['three', three],
	['fx', fx],
	['edit', edit],
];

export const RemotionRoot: React.FC = () => (
	<>
		{MODULES.map(([name, list]) => (
			<Folder key={name} name={name}>
				{list.map((d) => (
					<Composition
						key={d.id}
						id={d.id}
						component={d.component}
						width={d.width ?? 1920}
						height={d.height ?? 1080}
						fps={d.fps ?? 30}
						durationInFrames={d.durationInFrames}
					/>
				))}
			</Folder>
		))}
	</>
);
