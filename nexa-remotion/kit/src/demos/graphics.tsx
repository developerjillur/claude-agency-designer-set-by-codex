import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {SafeArea, ThemeProvider, useStage, useTheme, type DemoDef, type ThemeName} from '../kit/core';
import {Animate} from '../kit/motion';
import {
	Arrow,
	BarChart,
	BarRace,
	Callout,
	ChartFrame,
	Comparison,
	Donut,
	DrawPath,
	DrawnPath,
	FlowDiagram,
	HandMark,
	HandStroke,
	ICON_NAMES,
	Icon,
	IconBadge,
	LineChart,
	Marked,
	Morph,
	MorphPath,
	OrgChart,
	PathFollow,
	Pie,
	ProgressBar,
	ProgressRing,
	Stat,
	Sparkline,
	SvgLayer,
	Timeline,
	barRaceFrames,
	circlePath,
	smoothPath,
	starPath,
	type HandKind,
} from '../kit/graphics';

// ---------------------------------------------------------------- scaffolding

const Ground: React.FC<{children: React.ReactNode}> = ({children}) => {
	const t = useTheme();
	return <AbsoluteFill style={{background: t.colors.bg}}>{children}</AbsoluteFill>;
};

const themed = (Comp: React.FC, theme: ThemeName): React.FC => {
	const Wrapped: React.FC = () => (
		<ThemeProvider theme={theme}>
			<Ground>
				<Comp />
			</Ground>
		</ThemeProvider>
	);
	return Wrapped;
};

/** A small caption in the theme's body face. */
const Caption: React.FC<{children: React.ReactNode; x: number; y: number; delay?: number}> = ({children, x, y, delay = 0}) => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div style={{position: 'absolute', left: x, top: y, translate: '-50% 0'}}>
			<Animate in="rise" delay={delay}>
				<div style={{fontFamily: t.type.body, fontWeight: t.weights.strong, fontSize: 32 * unit, color: t.colors.muted, whiteSpace: 'nowrap'}}>{children}</div>
			</Animate>
		</div>
	);
};

// ---------------------------------------------------------------- bars

const BarsScene: React.FC = () => (
	<ChartFrame title="Referrals brought in the most new customers" subtitle="New customers by channel, 2025" source="Example data">
		<BarChart
			data={[
				{label: 'Search', value: 34200},
				{label: 'Social', value: 28900},
				{label: 'Referral', value: 51300},
				{label: 'Email', value: 12400},
				{label: 'Events', value: 8700},
			]}
			format={{compact: true}}
			highlight="Referral"
			highlightAt={96}
		/>
	</ChartFrame>
);

const BarsHorizontalScene: React.FC = () => (
	<ChartFrame title="Dhaka has nearly half of all users" subtitle="Weekly active users by city" source="Example data" exit="fade">
		<BarChart
			orientation="horizontal"
			sort="desc"
			data={[
				{label: 'Chattogram', value: 21700},
				{label: 'Dhaka', value: 48200},
				{label: 'Sylhet', value: 9800},
				{label: 'Khulna', value: 8900},
				{label: 'Rajshahi', value: 7600},
				{label: 'Barishal', value: 4100},
			]}
			values="count"
			highlight="Dhaka"
			exit="shrink"
		/>
	</ChartFrame>
);

const BarsNegativeScene: React.FC = () => (
	<ChartFrame title="Back in profit by the third quarter" subtitle="Operating profit, USD millions" source="Example data">
		<BarChart
			data={[
				{label: 'Q1 2025', value: -1.2},
				{label: 'Q2 2025', value: -0.4},
				{label: 'Q3 2025', value: 0.8},
				{label: 'Q4 2025', value: 2.1},
				{label: 'Q1 2026', value: 2.9},
			]}
			format={{prefix: '$', suffix: 'M', decimals: 1}}
			axisLabel="USD millions"
		/>
	</ChartFrame>
);

const BanglaBarsScene: React.FC = () => (
	<ChartFrame title="মোবাইল লেনদেন বেড়েই চলেছে" subtitle="মাসিক লেনদেন, টাকায়" source="উদাহরণ তথ্য">
		<BarChart
			data={[
				{label: 'জানুয়ারি', value: 1250000},
				{label: 'ফেব্রুয়ারি', value: 1480000},
				{label: 'মার্চ', value: 1720000},
				{label: 'এপ্রিল', value: 2150000},
				{label: 'মে', value: 2610000},
			]}
			format={{grouping: 'south-asian', digits: 'bengali', prefix: '৳'}}
			highlight={4}
		/>
	</ChartFrame>
);

// ---------------------------------------------------------------- bar race

const RACE = [
	{label: '2021', values: {Nimbus: 42, Kite: 35, Orbit: 30, Lumen: 22, Pixel: 18, Tandem: 12, Quill: 9, Harbor: 6}},
	{label: '2022', values: {Nimbus: 48, Kite: 44, Orbit: 31, Lumen: 30, Pixel: 26, Tandem: 21, Quill: 14, Harbor: 11}},
	{label: '2023', values: {Nimbus: 51, Kite: 57, Orbit: 33, Lumen: 41, Pixel: 30, Tandem: 34, Quill: 22, Harbor: 17}},
	{label: '2024', values: {Nimbus: 53, Kite: 66, Orbit: 34, Lumen: 58, Pixel: 33, Tandem: 49, Quill: 35, Harbor: 26}},
	{label: '2025', values: {Nimbus: 55, Kite: 71, Orbit: 35, Lumen: 74, Pixel: 36, Tandem: 63, Quill: 47, Harbor: 38}},
];

const RaceScene: React.FC = () => (
	<ChartFrame title="Lumen took the lead in 2025" subtitle="Monthly active users, millions" source="Example data">
		<BarRace snapshots={RACE} highlight="Lumen" format={{suffix: 'M'}} />
	</ChartFrame>
);

// ---------------------------------------------------------------- lines

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const LineScene: React.FC = () => (
	<ChartFrame title="The new plan overtook the old one in June" subtitle="Monthly sign-ups by plan" source="Example data">
		<LineChart
			series={[
				{name: 'Classic', points: MONTHS.map((m, i) => ({x: m, y: [420, 460, 450, 480, 470, 455, 440, 430, 410, 400, 395, 380][i]}))},
				{name: 'Plus', points: MONTHS.map((m, i) => ({x: m, y: [60, 90, 150, 230, 330, 470, 560, 640, 700, 790, 860, 930][i]}))},
			]}
			highlight={1}
			dots="end"
			callouts={[{series: 1, x: 'Jun', title: 'June', text: 'Plus passes Classic'}]}
		/>
	</ChartFrame>
);

const LineUnevenScene: React.FC = () => (
	<ChartFrame title="Readings came in at uneven times" subtitle="River level at the gauge" source="Example data" exit="fade">
		<LineChart
			data={[
				{x: new Date(Date.UTC(2026, 5, 1)), y: 2.1},
				{x: new Date(Date.UTC(2026, 5, 4)), y: 2.4},
				{x: new Date(Date.UTC(2026, 5, 12)), y: 3.8},
				{x: new Date(Date.UTC(2026, 5, 14)), y: 4.6},
				{x: new Date(Date.UTC(2026, 5, 15)), y: 5.2},
				{x: new Date(Date.UTC(2026, 5, 22)), y: 4.1},
				{x: new Date(Date.UTC(2026, 6, 6)), y: 2.9},
			]}
			format={{decimals: 1}}
			yLabel="metres"
			xLabel="June and July 2026"
			curve="linear"
			callouts={[{x: new Date(Date.UTC(2026, 5, 15)), title: 'Peak', text: '5.2 m on 15 June'}]}
			exit="undraw"
		/>
	</ChartFrame>
);

// ---------------------------------------------------------------- donut and pie

const DonutScene: React.FC = () => {
	const {safe, unit} = useStage();
	const w = safe.w / unit / 2 - 20;
	const h = safe.h / unit - 120;
	const t = useTheme();
	return (
		<SafeArea row justify="space-between" align="center">
			<div style={{display: 'flex', flexDirection: 'column', gap: 20 * unit}}>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 48 * unit, color: t.colors.text, letterSpacing: `${t.tracking.display}em`}}>A working week</div>
				<Donut
					width={w}
					height={h}
					radius={230}
					data={[
						{label: 'Focused work', value: 16},
						{label: 'Meetings', value: 10},
						{label: 'Planning', value: 6},
						{label: 'Email', value: 4},
						{label: 'Admin', value: 2},
					]}
					highlight="Focused work"
					format={{suffix: ' h'}}
					centerLabel="hours"
					show="percent"
				/>
			</div>
			<div style={{display: 'flex', flexDirection: 'column', gap: 20 * unit}}>
				<div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 48 * unit, color: t.colors.text, letterSpacing: `${t.tracking.display}em`}}>Budget split</div>
				<Pie
					width={w}
					height={h}
					radius={230}
					delay={30}
					labels="inside"
					data={[
						{label: 'Product', value: 45},
						{label: 'Marketing', value: 30},
						{label: 'Support', value: 15},
						{label: 'Other', value: 10},
					]}
				/>
			</div>
		</SafeArea>
	);
};

// ---------------------------------------------------------------- stats, progress, comparison

const StatsScene: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<SafeArea justify="center" gap={80}>
			<div style={{display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', columnGap: 60 * unit, width: '100%', alignItems: 'start'}}>
				<div style={{display: 'flex', flexDirection: 'column', gap: 28 * unit}}>
					<Stat value={12480} label="new customers this month" delta={18.2} deltaLabel="vs May" size={124} />
					<Sparkline data={[6.1, 6.8, 6.4, 7.9, 8.8, 8.1, 9.6, 10.2, 10.6, 12.48]} width={420} height={90} delay={20} />
				</div>
				<Stat value={4.2} format={{prefix: '$', suffix: 'M', decimals: 1}} label="revenue, rolled like an odometer" mode="roll" delay={16} size={124} color={t.colors.accent} />
				<Stat value={1234567} format={{grouping: 'south-asian', digits: 'bengali', prefix: '৳'}} label="মোট বিক্রি, এই বছর" delay={32} size={96} delta={-3.4} />
			</div>
			<div style={{fontFamily: t.type.body, fontSize: 28 * unit, color: t.colors.muted}}>Counts start fast and settle on the value; the width is held for the final number.</div>
		</SafeArea>
	);
};

const ProgressScene: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<SafeArea justify="center" gap={80}>
			<div style={{display: 'flex', justifyContent: 'space-between', width: '100%'}}>
				<ProgressRing value={0.72} sublabel="of the goal" delay={6} />
				<ProgressRing value={38} max={50} label="value" sublabel="stores open" delay={18} color={t.colors.accent2} />
				<ProgressRing value={0.94} sublabel="uptime" delay={30} color={t.colors.positive} />
			</div>
			<div style={{display: 'flex', flexDirection: 'column', gap: 44 * unit, width: '100%'}}>
				<ProgressBar value={0.64} label="Survey responses" width={1700} delay={40} />
				<ProgressBar value={3} max={5} segments={5} label="Step 3 of 5: shipping" showValue="none" width={1700} delay={54} color={t.colors.accent2} />
			</div>
		</SafeArea>
	);
};

const CompareScene: React.FC = () => {
	const {safe, unit} = useStage();
	const W = safe.w / unit;
	return (
		<SafeArea style={{justifyContent: 'space-evenly'}}>
			<Comparison
				width={W}
				height={420}
				a={{label: 'Old checkout', value: 94, note: 'seconds to pay, median'}}
				b={{label: 'New checkout', value: 38, note: 'seconds to pay, median'}}
				format={{suffix: ' s'}}
				lowerIsBetter
			/>
			<Comparison width={W} height={300} mode="share" delay={40} a={{label: 'Paid by phone', value: 62}} b={{label: 'Paid by card', value: 38}} />
		</SafeArea>
	);
};

// ---------------------------------------------------------------- diagrams

const FlowScene: React.FC = () => (
	<ChartFrame title="How an order moves" source="Each step starts when the one before it finishes">
		<FlowDiagram
			nodes={[
				{id: 'order', label: 'Order placed', icon: 'cart'},
				{id: 'pay', label: 'Payment', sub: 'card or mobile', icon: 'money'},
				{id: 'pack', label: 'Packed', icon: 'file'},
				{id: 'refund', label: 'Refund', sub: 'if payment fails', icon: 'arrow-left'},
				{id: 'ship', label: 'Shipped', icon: 'rocket'},
				{id: 'done', label: 'Delivered', icon: 'home', tone: 'accent'},
			]}
			edges={[
				{from: 'order', to: 'pay'},
				{from: 'pay', to: 'pack', label: 'paid'},
				{from: 'pay', to: 'refund', label: 'failed', dashed: true},
				{from: 'pack', to: 'ship'},
				{from: 'ship', to: 'done'},
			]}
			highlight={['order', 'pay', 'pack', 'ship', 'done']}
			pulse
		/>
	</ChartFrame>
);

const OrgScene: React.FC = () => (
	<ChartFrame title="Who does what" align="center">
		<OrgChart
			people={[
				{id: 'ceo', label: 'Nadia Rahman', sub: 'Founder', tone: 'accent'},
				{id: 'pd', label: 'Product', sub: 'Imran', parent: 'ceo'},
				{id: 'eng', label: 'Engineering', sub: 'Farhan', parent: 'ceo'},
				{id: 'ops', label: 'Operations', sub: 'Sumaiya', parent: 'ceo'},
				{id: 'des', label: 'Design', parent: 'pd'},
				{id: 'app', label: 'Apps', parent: 'eng'},
				{id: 'web', label: 'Web', parent: 'eng'},
				{id: 'sup', label: 'Support', parent: 'ops'},
			]}
			highlight={['eng', 'app', 'web']}
		/>
	</ChartFrame>
);

const TimelineScene: React.FC = () => (
	<ChartFrame title="From a garage to a million users" source="Gaps between dots are true to time">
		<Timeline
			events={[
				{label: '2019', title: 'Founded', text: 'Two people, one idea', at: 2019},
				{label: '2020', title: 'First 1,000 users', at: 2020.4},
				{label: '2022', title: 'Series A', text: 'USD 6M raised', at: 2022.2},
				{label: '2024', title: 'Five countries', at: 2024},
				{label: '2026', title: '1M users', text: 'and still growing', at: 2026},
			]}
			highlight={4}
		/>
	</ChartFrame>
);

// ---------------------------------------------------------------- variants (options the main demos do not show)

const MarksVariantsScene: React.FC = () => {
	const t = useTheme();
	const {unit, width, height} = useStage();
	const text: React.CSSProperties = {fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 72 * unit, lineHeight: 1.2, color: t.colors.text};
	return (
		<>
			<SafeArea justify="start" gap={40}>
				<div style={text}>
					<Marked kind="box" delay={10}>Fast</Marked>, <Marked kind="double-underline" delay={30}>cheap</Marked>, <Marked kind="cross" delay={50}>perfect</Marked>
				</div>
				<div style={text}>
					Pick <Marked kind="scribble" delay={70} color={t.colors.accent}>three</Marked> two
				</div>
				<div style={{display: 'flex', gap: 60 * unit, alignItems: 'center', marginTop: 20 * unit}}>
					{(['right', 'left', 'up', 'down'] as const).map((dir, i) => (
						<HandMark key={dir} kind="arrow" direction={dir} width={170} height={170} delay={90 + i * 8} seed={i + 5} color={t.colors.accent2} />
					))}
				</div>
			</SafeArea>
			<SvgLayer>
				<HandStroke
					points={Array.from({length: 60}, (_, i) => {
						const s = i / 59;
						// a looping signature-like line
						return [width * (0.08 + 0.3 * s) + Math.sin(s * Math.PI * 6) * 40 * unit, height * 0.84 - Math.cos(s * Math.PI * 6) * 46 * unit - s * 40 * unit] as [number, number];
					})}
					size={7 * unit}
					delay={60}
					duration={70}
					color={t.colors.text}
				/>
			</SvgLayer>
			<Morph
				paths={[starPath(0, 0, 5, 80, 34), circlePath(0, 0, 64), starPath(0, 0, 8, 80, 50)]}
				colors={[t.colors.accent2, t.colors.accent, t.colors.accent2]}
				width={180}
				delay={40}
				svgStyle={{position: 'absolute', left: width * 0.5 - 90 * unit, top: height * 0.62}}
			/>
			<Arrow from={[width * 0.62, height * 0.62]} to={[width * 0.86, height * 0.5]} head="filled" delay={100} />
			<Arrow from={[width * 0.62, height * 0.74]} to={[width * 0.86, height * 0.74]} head="open" tail="open" delay={110} color={t.colors.accent} />
			<Arrow from={[width * 0.62, height * 0.86]} to={[width * 0.86, height * 0.9]} bend={0.3} dash="2 14" head="filled" delay={120} color={t.colors.accent2} />
		</>
	);
};

const LineStepScene: React.FC = () => (
	<ChartFrame title="Two teams, one target" subtitle="Tickets closed per week" source="Example data" exit="fade">
		<LineChart
			series={[
				{name: 'Team North', points: [0, 1, 2, 3, 4, 5, 6, 7].map((w, i) => ({x: w, y: [38, 42, 41, 47, 52, 50, 58, 61][i]})), area: true},
				{name: 'Team South', points: [0, 1, 2, 3, 4, 5, 6, 7].map((w, i) => ({x: w, y: [30, 33, 39, 38, 44, 49, 47, 55][i]})), area: true},
				{name: 'Target', points: [{x: 0, y: 45}, {x: 7, y: 45}], dashed: true},
			]}
			curve="step"
			zero={false}
			dots="all"
			xFormat={(x) => `W${Number(x) + 1}`}
			endLabel="both"
		/>
	</ChartFrame>
);

const BarsInsideScene: React.FC = () => (
	<ChartFrame title="WHERE THE MONEY GOES" subtitle="Share of spend, percent" source="Example data" exit="fade">
		<BarChart
			orientation="horizontal"
			data={[
				{label: 'Rent', value: 34},
				{label: 'Salaries', value: 41},
				{label: 'Software', value: 11},
				{label: 'Travel', value: 6},
				{label: 'Other', value: 8},
			]}
			sort="desc"
			valuePosition="inside"
			format={{suffix: '%'}}
			axis
			ticks={4}
		/>
	</ChartFrame>
);

const FlowGridScene: React.FC = () => (
	<ChartFrame title="release.yml" subtitle="What runs on every merge" exit="fade">
		<FlowDiagram
			nodes={[
				{id: 'merge', label: 'merge', col: 0, row: 1, icon: 'code'},
				{id: 'test', label: 'test', col: 1, row: 0},
				{id: 'lint', label: 'lint', col: 1, row: 2},
				{id: 'build', label: 'build', col: 2, row: 1, icon: 'settings'},
				{id: 'deploy', label: 'deploy', col: 3, row: 1, icon: 'rocket', tone: 'accent'},
			]}
			edges={[
				{from: 'merge', to: 'test'},
				{from: 'merge', to: 'lint'},
				{from: 'test', to: 'build'},
				{from: 'lint', to: 'build'},
				{from: 'build', to: 'deploy', label: 'on green'},
				{from: 'deploy', to: 'merge', label: 'rollback', dashed: true},
			]}
			route="elbow"
			pulse
		/>
	</ChartFrame>
);

// ---------------------------------------------------------------- vertical (1080 x 1920)

const VerticalScene: React.FC = () => (
	<ChartFrame title="The apps people open every day" subtitle="Daily users, millions" source="Example data">
		<BarChart
			orientation="horizontal"
			sort="desc"
			data={[
				{label: 'Messages', value: 41.2},
				{label: 'Video', value: 33.8},
				{label: 'Maps', value: 18.1},
				{label: 'Music', value: 14.6},
				{label: 'Banking', value: 11.9},
				{label: 'News', value: 7.4},
			]}
			format={{decimals: 1}}
			highlight="Banking"
			highlightAt={90}
		/>
	</ChartFrame>
);

const VerticalTimelineScene: React.FC = () => (
	<ChartFrame title="The launch plan" subtitle="Six weeks, four steps">
		<Timeline
			events={[
				{label: 'Week 1', title: 'Research', text: 'Talk to 20 customers'},
				{label: 'Week 2', title: 'Design', text: 'Prototype the flow'},
				{label: 'Week 4', title: 'Build', text: 'Ship to the beta group'},
				{label: 'Week 6', title: 'Launch', text: 'Everyone gets it'},
			]}
			highlight={3}
		/>
	</ChartFrame>
);

// ---------------------------------------------------------------- icons

const IconsScene: React.FC = () => {
	const t = useTheme();
	const {unit, safe} = useStage();
	const cols = 9;
	return (
		<div
			style={{
				position: 'absolute',
				left: safe.x,
				top: safe.y,
				width: safe.w,
				height: safe.h,
				display: 'grid',
				gridTemplateColumns: `repeat(${cols}, 1fr)`,
				alignContent: 'space-evenly',
				rowGap: 18 * unit,
			}}
		>
			{ICON_NAMES.map((n, i) => (
				<div key={n} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 * unit}}>
					{i < 9 ? (
						<IconBadge name={n} size={96} delay={4 + i * 3} solid={i === 4} />
					) : (
						<Icon name={n} size={84} delay={4 + i * 2} color={i % 7 === 0 ? t.colors.accent : t.colors.text} />
					)}
					<div style={{fontFamily: t.type.mono, fontSize: 17 * unit, color: t.colors.muted}}>{n}</div>
				</div>
			))}
		</div>
	);
};

// ---------------------------------------------------------------- paths: draw, follow, morph

const PathsScene: React.FC = () => {
	const t = useTheme();
	const {width, height, unit} = useStage();
	const cx = [width * 0.2, width * 0.5, width * 0.8];
	const cy = height * 0.44;
	const s = 1.45 * unit;
	const hills = smoothPath(
		[
			[-170, 90],
			[-110, 10],
			[-40, 60],
			[35, -40],
			[110, 40],
			[170, -10],
		].map(([x, y]) => [x * s + cx[0], y * s + cy] as [number, number]),
		1,
	);
	const sun = circlePath(cx[0] - 70 * s, cy - 105 * s, 32 * s);
	const ground = `M${cx[0] - 180 * s} ${cy + 120 * s}H${cx[0] + 180 * s}`;
	const route = smoothPath(
		[
			[cx[1] - 170 * s, cy + 110 * s],
			[cx[1] - 80 * s, cy - 20 * s],
			[cx[1] + 30 * s, cy + 70 * s],
			[cx[1] + 165 * s, cy - 115 * s],
		],
		1,
	);
	const heart = (x: number, y: number, k: number) =>
		`M${x} ${y - 52 * k}C${x - 20 * k} ${y - 92 * k} ${x - 92 * k} ${y - 84 * k} ${x - 92 * k} ${y - 30 * k}C${x - 92 * k} ${y + 12 * k} ${x - 40 * k} ${y + 44 * k} ${x} ${y + 86 * k}C${x + 40 * k} ${y + 44 * k} ${x + 92 * k} ${y + 12 * k} ${x + 92 * k} ${y - 30 * k}C${x + 92 * k} ${y - 84 * k} ${x + 20 * k} ${y - 92 * k} ${x} ${y - 52 * k}Z`;
	const shapes = [circlePath(cx[2], cy, 96 * s), starPath(cx[2], cy + 6 * s, 5, 116 * s, 50 * s), heart(cx[2], cy - 6 * s, s)];
	return (
		<>
			<SvgLayer>
				<DrawnPath d={`${ground}${hills}${sun}`} stroke={t.colors.text} strokeWidth={6 * unit} delay={6} duration={70} mode="sequence" />
				<DrawnPath d={sun} stroke="none" fill={t.colors.accent2} fillFrom={0} delay={70} duration={16} />
				<path d={route} fill="none" stroke={t.colors.faint} strokeWidth={4 * unit} strokeDasharray={`${2 * unit} ${14 * unit}`} strokeLinecap="round" />
				<circle cx={cx[1] - 170 * s} cy={cy + 110 * s} r={10 * unit} fill={t.colors.text} />
				<circle cx={cx[1] + 165 * s} cy={cy - 115 * s} r={10 * unit} fill={t.colors.accent} />
				<PathFollow d={route} delay={20} duration={90} trail="solid" trailColor={t.colors.accent} trailWidth={5 * unit} scaleIn={0.06}>
					<g transform={`scale(${1.6 * unit})`}>
						<path d="M26 0L-14 -16L-8 0L-14 16Z" fill={t.colors.accent} stroke={t.colors.bg} strokeWidth={3} strokeLinejoin="round" />
					</g>
				</PathFollow>
				<MorphPath paths={shapes} colors={[t.colors.accent, t.colors.accent2, t.colors.negative]} delay={24} hold={24} move={28} />
			</SvgLayer>
			<Caption x={cx[0]} y={height * 0.8} delay={4}>
				Draw on
			</Caption>
			<Caption x={cx[1]} y={height * 0.8} delay={8}>
				Follow a path
			</Caption>
			<Caption x={cx[2]} y={height * 0.8} delay={12}>
				Morph
			</Caption>
		</>
	);
};

// ---------------------------------------------------------------- hand-drawn marks

const MARKS: {kind: HandKind; label: string; w: number; h: number}[] = [
	{kind: 'circle', label: 'circle', w: 220, h: 150},
	{kind: 'check', label: 'check', w: 150, h: 130},
	{kind: 'cross', label: 'cross', w: 130, h: 130},
	{kind: 'arrow', label: 'arrow', w: 220, h: 130},
	{kind: 'box', label: 'box', w: 220, h: 130},
	{kind: 'scribble', label: 'scribble', w: 200, h: 110},
];

const HandScene: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const text: React.CSSProperties = {
		fontFamily: t.type.display,
		fontWeight: t.weights.display,
		fontSize: 92 * unit,
		lineHeight: 1.15,
		letterSpacing: `${t.tracking.display}em`,
		color: t.colors.text,
	};
	return (
		<SafeArea style={{justifyContent: 'space-evenly'}}>
			<div style={{display: 'flex', flexDirection: 'column', gap: 34 * unit}}>
				<div style={text}>
					Sales grew <Marked kind="circle" delay={16}>42%</Marked> in <Marked kind="underline" delay={44}>one quarter</Marked>
				</div>
				<div style={{...text, fontFamily: t.type.bangla, fontSize: 70 * unit, wordSpacing: '0.12em'}}>
					বিক্রি বেড়েছে <Marked kind="highlight" delay={70}>এক প্রান্তিকে</Marked>, খরচ <Marked kind="strike" delay={96}>বাড়েনি</Marked>
				</div>
			</div>
			<div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', width: '100%'}}>
				{MARKS.map((m, i) => (
					<div key={m.kind} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18 * unit}}>
						<HandMark kind={m.kind} width={m.w} height={m.h} delay={30 + i * 10} seed={i + 2} color={i % 2 ? t.colors.accent : t.colors.accent2} />
						<div style={{fontFamily: t.type.mono, fontSize: 24 * unit, color: t.colors.muted}}>{m.label}</div>
					</div>
				))}
			</div>
		</SafeArea>
	);
};

// ---------------------------------------------------------------- callouts

const CalloutScene: React.FC = () => {
	const t = useTheme();
	const {width, height, unit} = useStage();
	const phone = {x: width * 0.5 - 200 * unit, y: height * 0.12, w: 400 * unit, h: height * 0.8};
	const pts = {
		balance: {x: phone.x + 30 * unit, y: phone.y + phone.h * 0.19},
		chart: {x: phone.x + phone.w - 26 * unit, y: phone.y + phone.h * 0.44},
		button: {x: phone.x + phone.w * 0.88, y: phone.y + phone.h * 0.855},
	};
	return (
		<>
			<Animate in="rise" style={{position: 'absolute', left: phone.x, top: phone.y}}>
				<div style={{width: phone.w, height: phone.h, borderRadius: 52 * unit, background: t.colors.surface, border: `${3 * unit}px solid ${t.colors.line}`, boxShadow: `0 ${24 * unit}px ${60 * unit}px rgba(15,23,42,0.12)`, position: 'relative', overflow: 'hidden'}}>
					<div style={{position: 'absolute', left: '12%', top: '11%', fontFamily: t.type.body, fontSize: 24 * unit, color: t.colors.muted}}>Balance</div>
					<div style={{position: 'absolute', left: '12%', top: '15%', fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 60 * unit, color: t.colors.text, fontVariantNumeric: 'tabular-nums'}}>$12,480</div>
					<DrawPath
						d="M0 136L64 112L120 120L184 72L248 88L312 40L400 16"
						viewBox="-6 0 412 150"
						width={320}
						stroke={t.colors.accent}
						strokeWidth={9}
						delay={14}
						duration={40}
						style={{position: 'absolute', left: '10%', top: '36%'}}
					/>
					<div style={{position: 'absolute', left: '12%', right: '12%', bottom: '10%', height: '9%', borderRadius: 999, background: t.colors.accent}} />
				</div>
			</Animate>
			<Sequence from={20} durationInFrames={130} layout="none">
				<Callout x={pts.balance.x} y={pts.balance.y} side="left" title="Live balance" text="Updates the second money moves" />
			</Sequence>
			<Sequence from={40} durationInFrames={110} layout="none">
				<Callout x={pts.chart.x} y={pts.chart.y} side="right" text="Spending trend, last 30 days" tone="accent" />
			</Sequence>
			<Sequence from={60} durationInFrames={90} layout="none">
				<Callout x={pts.button.x} y={pts.button.y} side="right" text="এক ট্যাপে টাকা পাঠান" />
			</Sequence>
			<Sequence from={78} durationInFrames={72} layout="none">
				<Arrow from={[width * 0.2, height * 0.8]} to={[phone.x + phone.w * 0.14, phone.y + phone.h * 0.87]} bend={-0.3} gap={16} color={t.colors.accent2} exit="fade" />
			</Sequence>
		</>
	);
};

export const demos: DemoDef[] = [
	{id: 'DemoGraphicsBars', component: themed(BarsScene, 'studio'), durationInFrames: 180},
	{id: 'DemoGraphicsBarsHorizontal', component: themed(BarsHorizontalScene, 'midnight'), durationInFrames: 180},
	{id: 'DemoGraphicsBarsNegative', component: themed(BarsNegativeScene, 'corporate'), durationInFrames: 150},
	{id: 'DemoGraphicsBangla', component: themed(BanglaBarsScene, 'dhaka'), durationInFrames: 150},
	{id: 'DemoGraphicsRace', component: themed(RaceScene, 'neon'), durationInFrames: barRaceFrames(RACE.length, 45, 10, 10) + 20},
	{id: 'DemoGraphicsLine', component: themed(LineScene, 'data'), durationInFrames: 210},
	{id: 'DemoGraphicsLineUneven', component: themed(LineUnevenScene, 'midnight'), durationInFrames: 180},
	{id: 'DemoGraphicsDonut', component: themed(DonutScene, 'studio'), durationInFrames: 180},
	{id: 'DemoGraphicsStats', component: themed(StatsScene, 'midnight'), durationInFrames: 120},
	{id: 'DemoGraphicsProgress', component: themed(ProgressScene, 'fresh'), durationInFrames: 120},
	{id: 'DemoGraphicsCompare', component: themed(CompareScene, 'studio'), durationInFrames: 150},
	{id: 'DemoGraphicsFlow', component: themed(FlowScene, 'studio'), durationInFrames: 210},
	{id: 'DemoGraphicsOrg', component: themed(OrgScene, 'midnight'), durationInFrames: 180},
	{id: 'DemoGraphicsTimeline', component: themed(TimelineScene, 'editorial'), durationInFrames: 180},
	{id: 'DemoGraphicsVertical', component: themed(VerticalScene, 'midnight'), durationInFrames: 180, width: 1080, height: 1920},
	{id: 'DemoGraphicsVerticalTimeline', component: themed(VerticalTimelineScene, 'studio'), durationInFrames: 150, width: 1080, height: 1920},
	{id: 'DemoGraphicsPaths', component: themed(PathsScene, 'midnight'), durationInFrames: 180},
	{id: 'DemoGraphicsHand', component: themed(HandScene, 'vox'), durationInFrames: 150},
	{id: 'DemoGraphicsIcons', component: themed(IconsScene, 'studio'), durationInFrames: 150},
	{id: 'DemoGraphicsCallout', component: themed(CalloutScene, 'studio'), durationInFrames: 150},
	{id: 'DemoGraphicsMarksVariants', component: themed(MarksVariantsScene, 'whiteboard'), durationInFrames: 180},
	{id: 'DemoGraphicsLineStep', component: themed(LineStepScene, 'corporate'), durationInFrames: 180},
	{id: 'DemoGraphicsBarsInside', component: themed(BarsInsideScene, 'brutalist'), durationInFrames: 150},
	{id: 'DemoGraphicsFlowGrid', component: themed(FlowGridScene, 'terminal'), durationInFrames: 210},
];
