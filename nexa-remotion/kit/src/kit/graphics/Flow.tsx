// <FlowDiagram>: boxes and the connectors between them, choreographed as a flow: a node arrives, its arrow draws
// to the next node, that node arrives when the arrow gets there. Nodes are placed by col/row, by x/y, or laid out
// automatically in layers from the edges. <OrgChart> lays out a tree from parent links.
import React, {useMemo} from 'react';
import {useCurrentFrame} from 'remotion';
import {at30, curves, useStage, useTheme} from '../core';
import {ramp} from '../motion';
import {withOpacity} from './color';
import {ArrowPath} from './Arrow';
import {ChartLabel, ChartRoot, useChartBox} from './chart';
import {Icon} from './Icon';
import type {IconName} from './icons';
import {pathPose} from './paths';
import {buildFrames, useGraphicExit, type GraphicExitProps} from './timing';

export type FlowNode = {
	id: string;
	label: React.ReactNode;
	sub?: React.ReactNode; // a smaller second line
	icon?: IconName;
	col?: number; // grid placement (fractions allowed)
	row?: number;
	x?: number; // or a position as a share of the box (0 to 1)
	y?: number;
	tone?: 'surface' | 'accent' | 'outline';
};

export type FlowEdge = {from: string; to: string; label?: React.ReactNode; dashed?: boolean};

export type FlowDiagramProps = GraphicExitProps & {
	nodes: FlowNode[];
	edges: FlowEdge[];
	direction?: 'right' | 'down' | 'auto'; // the way the flow reads (auto: down in 9:16)
	route?: 'curve' | 'elbow' | 'straight';
	width?: number; // px at 1080
	height?: number;
	nodeWidth?: number; // px at 1080 (default from the grid)
	nodeHeight?: number;
	highlight?: string[]; // node ids shown in the accent
	pulse?: boolean; // dots keep travelling along drawn connectors
	delay?: number;
	nodeDuration?: number; // frames a node takes to arrive (default 14 at 30 fps)
	edgeDuration?: number; // frames a connector takes to draw (default 18)
	stagger?: number; // frames between nodes that no connector leads to
	labelSize?: number; // px at 1080
	style?: React.CSSProperties;
};

type Placed = FlowNode & {cx: number; cy: number; w: number; h: number; order: number};

/** Layers from the edges: a node sits one layer after the latest node that points to it. */
const layered = (nodes: FlowNode[], edges: FlowEdge[]): Map<string, {rank: number; slot: number}> => {
	const preds = new Map<string, string[]>();
	nodes.forEach((n) => preds.set(n.id, []));
	edges.forEach((e) => preds.get(e.to)?.push(e.from));
	const rank = new Map<string, number>();
	const visiting = new Set<string>();
	const rankOf = (id: string): number => {
		const hit = rank.get(id);
		if (hit !== undefined) {
			return hit;
		}
		if (visiting.has(id)) {
			return 0; // a cycle: break it here
		}
		visiting.add(id);
		const ps = (preds.get(id) ?? []).filter((p) => preds.has(p));
		const r = ps.length ? Math.max(...ps.map(rankOf)) + 1 : 0;
		visiting.delete(id);
		rank.set(id, r);
		return r;
	};
	nodes.forEach((n) => rankOf(n.id));
	const counts = new Map<number, number>();
	const out = new Map<string, {rank: number; slot: number}>();
	nodes.forEach((n) => {
		const r = rank.get(n.id) ?? 0;
		const s = counts.get(r) ?? 0;
		counts.set(r, s + 1);
		out.set(n.id, {rank: r, slot: s});
	});
	// centre short layers against the tallest one
	const tallest = Math.max(...counts.values());
	out.forEach((v) => {
		v.slot += (tallest - (counts.get(v.rank) ?? 1)) / 2;
	});
	return out;
};

const edgePath = (a: Placed, b: Placed, route: FlowDiagramProps['route'], down: boolean, clear = 0): string => {
	const f = (v: number) => +v.toFixed(2);
	const forward = down ? b.cy > a.cy + a.h / 2 : b.cx > a.cx + a.w / 2;
	if (!forward) {
		// going back: leave from the far side and loop round outside every node in between (`clear` is the far edge
		// of those nodes), with rounded corners
		const r = 18;
		if (down) {
			const x1 = a.cx + a.w / 2;
			const x2 = b.cx + b.w / 2;
			const out = Math.max(x1, x2, clear) + 40;
			const dir = b.cy < a.cy ? -1 : 1;
			const k = Math.min(r, Math.abs(b.cy - a.cy) / 2);
			return `M${f(x1)} ${f(a.cy)}H${f(out - r)}Q${f(out)} ${f(a.cy)} ${f(out)} ${f(a.cy + dir * k)}V${f(b.cy - dir * k)}Q${f(out)} ${f(b.cy)} ${f(out - r)} ${f(b.cy)}H${f(x2)}`;
		}
		const y1 = a.cy + a.h / 2;
		const y2 = b.cy + b.h / 2;
		const out = Math.max(y1, y2, clear) + 40;
		const dir = b.cx < a.cx ? -1 : 1;
		const k = Math.min(r, Math.abs(b.cx - a.cx) / 2);
		return `M${f(a.cx)} ${f(y1)}V${f(out - r)}Q${f(a.cx)} ${f(out)} ${f(a.cx + dir * k)} ${f(out)}H${f(b.cx - dir * k)}Q${f(b.cx)} ${f(out)} ${f(b.cx)} ${f(out - r)}V${f(y2)}`;
	}
	const [sx, sy] = down ? [a.cx, a.cy + a.h / 2] : [a.cx + a.w / 2, a.cy];
	const [ex, ey] = down ? [b.cx, b.cy - b.h / 2] : [b.cx - b.w / 2, b.cy];
	if (route === 'straight') {
		return `M${f(sx)} ${f(sy)}L${f(ex)} ${f(ey)}`;
	}
	if (route === 'elbow') {
		const r = 16;
		if (down) {
			const my = (sy + ey) / 2;
			if (Math.abs(ex - sx) < 1) {
				return `M${f(sx)} ${f(sy)}L${f(ex)} ${f(ey)}`;
			}
			const dir = ex > sx ? 1 : -1;
			const k = Math.min(r, Math.abs(ex - sx) / 2, Math.abs(my - sy));
			return `M${f(sx)} ${f(sy)}V${f(my - k)}Q${f(sx)} ${f(my)} ${f(sx + dir * k)} ${f(my)}H${f(ex - dir * k)}Q${f(ex)} ${f(my)} ${f(ex)} ${f(my + k)}V${f(ey)}`;
		}
		const mx = (sx + ex) / 2;
		if (Math.abs(ey - sy) < 1) {
			return `M${f(sx)} ${f(sy)}L${f(ex)} ${f(ey)}`;
		}
		const dir = ey > sy ? 1 : -1;
		const k = Math.min(r, Math.abs(ey - sy) / 2, Math.abs(mx - sx));
		return `M${f(sx)} ${f(sy)}H${f(mx - k)}Q${f(mx)} ${f(sy)} ${f(mx)} ${f(sy + dir * k)}V${f(ey - dir * k)}Q${f(mx)} ${f(ey)} ${f(mx + k)} ${f(ey)}H${f(ex)}`;
	}
	if (down) {
		const dy = (ey - sy) * 0.5;
		return `M${f(sx)} ${f(sy)}C${f(sx)} ${f(sy + dy)} ${f(ex)} ${f(ey - dy)} ${f(ex)} ${f(ey)}`;
	}
	const dx = (ex - sx) * 0.5;
	return `M${f(sx)} ${f(sy)}C${f(sx + dx)} ${f(sy)} ${f(ex - dx)} ${f(ey)} ${f(ex)} ${f(ey)}`;
};

export const FlowDiagram: React.FC<FlowDiagramProps> = ({
	nodes,
	edges,
	direction = 'auto',
	route = 'curve',
	width,
	height,
	nodeWidth,
	nodeHeight,
	highlight = [],
	pulse = false,
	delay,
	nodeDuration,
	edgeDuration,
	stagger,
	labelSize = 30,
	style,
	exit = 'none',
	outDuration,
	outAt,
}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const {fps, unit, vertical} = useStage();
	const box = useChartBox(width, height, delay);
	const q = useGraphicExit({exit, outDuration, outAt});
	const W = box.width;
	const H = box.height;
	const down = direction === 'down' || (direction === 'auto' && vertical);
	const nodeIn = nodeDuration ?? buildFrames('node', fps);
	const edgeIn = edgeDuration ?? buildFrames('edge', fps);
	const gapStep = stagger ?? at30(8, fps);
	const fade = exit === 'none' ? 1 : 1 - q;

	const placed: Placed[] = useMemo(() => {
		const auto = layered(nodes, edges);
		const grid = nodes.map((n) => {
			const a = auto.get(n.id) ?? {rank: 0, slot: 0};
			const col = n.col ?? (down ? a.slot : a.rank);
			const row = n.row ?? (down ? a.rank : a.slot);
			return {col, row};
		});
		const cols = Math.max(...grid.map((g) => g.col)) + 1;
		const rows = Math.max(...grid.map((g) => g.row)) + 1;
		const cellW = W / cols;
		const cellH = H / rows;
		const anyIcon = nodes.some((n) => n.icon);
		const nw = nodeWidth ?? Math.min(cellW * (down ? 0.84 : 0.7), 380);
		const nh = nodeHeight ?? Math.min(cellH * (down ? 0.6 : 0.7), anyIcon ? 190 : 128);
		const list = nodes.map((n, i) => ({
			...n,
			cx: n.x !== undefined ? n.x * W : (grid[i].col + 0.5) * cellW,
			cy: n.y !== undefined ? n.y * H : (grid[i].row + 0.5) * cellH,
			w: nw,
			h: nh,
			order: i,
		}));
		// reading order: along the flow, then across it
		const sorted = [...list].sort((a, b) => (down ? a.cy - b.cy || a.cx - b.cx : a.cx - b.cx || a.cy - b.cy));
		sorted.forEach((p, k) => (p.order = k));
		return list;
	}, [nodes, edges, down, W, H, nodeWidth, nodeHeight]);

	const byId = new Map(placed.map((p) => [p.id, p]));
	// choreography: when each node arrives and each connector draws
	const timing = useMemo(() => {
		const appear = new Map<string, number>();
		const edgeStart = new Map<number, number>();
		const inOrder = [...placed].sort((a, b) => a.order - b.order);
		let last = box.delay - gapStep;
		inOrder.forEach((nd) => {
			const incoming = edges
				.map((e, i) => ({e, i}))
				.filter(({e}) => e.to === nd.id && appear.has(e.from));
			let at: number;
			if (incoming.length) {
				at = Math.max(
					...incoming.map(({e, i}) => {
						const s = (appear.get(e.from) ?? 0) + Math.round(nodeIn * 0.6);
						edgeStart.set(i, s);
						return s + edgeIn;
					}),
				);
			} else {
				at = last + gapStep;
			}
			appear.set(nd.id, at);
			last = Math.max(last, at);
		});
		// connectors that point back to an earlier node draw once both ends are there
		edges.forEach((e, i) => {
			if (!edgeStart.has(i)) {
				edgeStart.set(i, Math.max(appear.get(e.from) ?? 0, appear.get(e.to) ?? 0) + nodeIn);
			}
		});
		return {appear, edgeStart};
	}, [placed, edges, box.delay, gapStep, nodeIn, edgeIn]);

	if (!nodes.length) {
		return null;
	}
	const svg: React.ReactNode[] = [];
	const html: React.ReactNode[] = [];
	edges.forEach((e, i) => {
		const a = byId.get(e.from);
		const b = byId.get(e.to);
		if (!a || !b) {
			return;
		}
		// the far edge of nodes between the two ends, for connectors that loop back round them
		const lo = down ? Math.min(a.cy, b.cy) : Math.min(a.cx, b.cx);
		const hi = down ? Math.max(a.cy, b.cy) : Math.max(a.cx, b.cx);
		const clear = Math.max(
			0,
			...placed.filter((p) => (down ? p.cy : p.cx) >= lo - 1 && (down ? p.cy : p.cx) <= hi + 1).map((p) => (down ? p.cx + p.w / 2 : p.cy + p.h / 2)),
		);
		const d = edgePath(a, b, route, down, clear);
		const s = timing.edgeStart.get(i) ?? 0;
		const p = ramp(frame, s, edgeIn, curves.inOut);
		const hot = highlight.includes(e.from) && highlight.includes(e.to);
		const col = hot ? t.colors.accent : withOpacity(t.colors.text, 0.55);
		svg.push(
			<ArrowPath
				key={`e${i}`}
				d={d}
				progress={p * (exit === 'undraw' ? 1 - q : 1)}
				head="filled"
				headSize={17}
				strokeWidth={hot ? 4.5 : 3.5}
				color={col}
				dash={e.dashed ? '2 12' : undefined}
				opacity={exit === 'undraw' ? 1 : fade}
			/>,
		);
		if (pulse && p >= 1) {
			const period = at30(46, fps);
			const tt = (((frame - s - edgeIn) % period) + period) % period / period;
			const pose = pathPose(d, tt);
			svg.push(<circle key={`p${i}`} cx={pose.x} cy={pose.y} r={7} fill={hot ? t.colors.accent : t.colors.accent2} opacity={Math.sin(Math.PI * tt) * fade} />);
		}
		if (e.label) {
			const mid = pathPose(d, 0.5);
			const lp = ramp(frame, s + edgeIn * 0.7, at30(10, fps), curves.out) * fade;
			html.push(
				<ChartLabel
					key={`el${i}`}
					x={mid.x}
					y={mid.y}
					anchor="center"
					style={{
						opacity: lp,
						scale: `${0.9 + 0.1 * lp}`,
						padding: `${5 * unit}px ${14 * unit}px`,
						borderRadius: 999,
						background: t.colors.bg,
						border: `${2 * unit}px solid ${t.colors.line}`,
						fontFamily: t.type.body,
						fontWeight: t.weights.strong,
						fontSize: labelSize * 0.72 * unit,
						color: t.colors.muted,
					}}
				>
					{e.label}
				</ChartLabel>,
			);
		}
	});
	placed.forEach((nd) => {
		const at = timing.appear.get(nd.id) ?? 0;
		const pop = ramp(frame, at, nodeIn, curves.outBack);
		const op = ramp(frame, at, Math.round(nodeIn * 0.6), curves.out) * fade;
		// highlighted: an accent ring; tone 'accent': a solid accent box (use it for one node at most)
		const hot = highlight.includes(nd.id);
		const solid = nd.tone === 'accent';
		const outline = nd.tone === 'outline';
		const bg = solid ? t.colors.accent : outline ? 'transparent' : t.colors.surface;
		const fg = solid ? t.colors.onAccent : t.colors.text;
		const border = solid ? 'none' : `${(hot ? 3.5 : 2.5) * unit}px solid ${hot ? t.colors.accent : outline ? t.colors.text : t.colors.line}`;
		html.push(
			<div
				key={`n${nd.id}`}
				style={{
					position: 'absolute',
					left: (nd.cx - nd.w / 2) * unit,
					top: (nd.cy - nd.h / 2) * unit,
					width: nd.w * unit,
					height: nd.h * unit,
					boxSizing: 'border-box',
					borderRadius: Math.min(t.radius * 0.8, 22) * unit,
					background: bg,
					border,
					boxShadow: !t.dark && !outline ? `0 ${8 * unit}px ${24 * unit}px rgba(15, 23, 42, ${hot || solid ? 0.14 : 0.07})` : undefined,
					display: 'flex',
					flexDirection: 'column',
					alignItems: 'center',
					justifyContent: 'center',
					gap: 8 * unit,
					padding: `${10 * unit}px ${16 * unit}px`,
					textAlign: 'center',
					opacity: op,
					scale: `${0.86 + 0.14 * pop}`,
				}}
			>
				{nd.icon ? <Icon name={nd.icon} size={Math.min(56, nd.h * 0.34)} color={solid ? t.colors.onAccent : t.colors.accent} delay={at + Math.round(nodeIn * 0.4)} duration={at30(18, fps)} /> : null}
				<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: labelSize * unit, lineHeight: 1.15, color: fg}}>{nd.label}</div>
				{nd.sub ? <div style={{fontFamily: t.type.body, fontWeight: t.weights.body, fontSize: labelSize * 0.72 * unit, lineHeight: 1.2, color: solid ? t.colors.onAccent : t.colors.muted, opacity: solid ? 0.85 : 1}}>{nd.sub}</div> : null}
			</div>,
		);
	});
	return (
		<ChartRoot width={W} height={H} svg={svg} style={style}>
			{html}
		</ChartRoot>
	);
};

export type OrgPerson = {id: string; label: React.ReactNode; sub?: React.ReactNode; parent?: string; icon?: IconName; tone?: FlowNode['tone']};

export type OrgChartProps = Omit<FlowDiagramProps, 'nodes' | 'edges' | 'direction' | 'route'> & {people: OrgPerson[]};

/** A tree from parent links, top down: leaves spread evenly, each parent centred over its children. */
export const OrgChart: React.FC<OrgChartProps> = ({people, ...rest}) => {
	const {nodes, edges} = useMemo(() => {
		const kids = new Map<string, string[]>();
		const roots: string[] = [];
		people.forEach((p) => {
			if (p.parent && people.some((x) => x.id === p.parent)) {
				kids.set(p.parent, [...(kids.get(p.parent) ?? []), p.id]);
			} else {
				roots.push(p.id);
			}
		});
		const pos = new Map<string, {col: number; row: number}>();
		let slot = 0;
		const place = (id: string, depth: number): number => {
			const ch = kids.get(id) ?? [];
			let col: number;
			if (!ch.length) {
				col = slot++;
			} else {
				const cs = ch.map((c) => place(c, depth + 1));
				col = (cs[0] + cs[cs.length - 1]) / 2;
			}
			pos.set(id, {col, row: depth});
			return col;
		};
		roots.forEach((r) => place(r, 0));
		return {
			nodes: people.map((p) => ({id: p.id, label: p.label, sub: p.sub, icon: p.icon, tone: p.tone, ...(pos.get(p.id) ?? {col: 0, row: 0})})),
			edges: people.filter((p) => p.parent && pos.has(p.parent)).map((p) => ({from: p.parent as string, to: p.id})),
		};
	}, [people]);
	return <FlowDiagram nodes={nodes} edges={edges} direction="down" route="elbow" {...rest} />;
};
