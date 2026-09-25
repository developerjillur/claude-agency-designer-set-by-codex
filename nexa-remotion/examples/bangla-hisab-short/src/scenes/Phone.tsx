import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {
	Animate,
	BarChart,
	Counter,
	DeviceRise,
	FormField,
	HandMark,
	PhoneFrame,
	PushIn,
	Stagger,
	TapIndicator,
	ThemeProvider,
	UiButton,
	curves,
	makeTheme,
	phoneScreen,
	ramp,
	useStage,
	useTheme,
} from '../kit';
import {CUE, CUT} from '../cues';
import {K, PHONE_LEFT, PHONE_W, STAGE_TOP} from '../layout';

// One phone for all three rules: the screen changes with each rule. Local frame 0 is global CUT.phone.
const S = phoneScreen(PHONE_W);
const L = (global: number) => global - CUT.phone;
const x = (px: number) => px * K; // UI sizes were drawn for a 380 px phone

// The app on the screen is light (the dhaka ground's cream text would vanish on it) and green, so the caption's red
// pill stays the one red thing to look at. Noto Sans Bengali: Hind Siliguri draws the digit ১ as a small hook.
const APP = makeTheme('studio', {
	name: 'app',
	colors: {bg: '#F6F5F0', bg2: '#FFFFFF', surface: '#FFFFFF', text: '#1D2B24', muted: '#5E6B64', faint: '#C9CFCB', line: '#E2E4E0', accent: '#127A4A', accentText: '#127A4A', onAccent: '#FFFFFF'},
	fonts: {display: 'AnekBangla', body: 'NotoSansBengali', bangla: 'AnekBangla'},
});
const GREEN = '#0E3B2E';
const CREAM = '#F5F1E8';
const MARIGOLD = '#F6C445';

const Header: React.FC<{title: string; sub?: string; tag?: string}> = ({title, sub, tag}) => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div style={{padding: `${(S.top + x(12)) * unit}px ${x(24) * unit}px ${x(10) * unit}px`}}>
			<div style={{fontFamily: t.type.display, fontWeight: 800, fontSize: x(32) * unit, color: t.colors.text, lineHeight: 1.2}}>{title}</div>
			{sub ? (
				<div style={{display: 'flex', alignItems: 'center', gap: x(8) * unit, marginTop: x(3) * unit}}>
					<div style={{fontFamily: t.type.body, fontSize: x(22) * unit, color: t.colors.muted}}>{sub}</div>
					{/* the figures are made up: said once, apart from the data */}
					{tag ? (
						<div style={{fontFamily: t.type.body, fontWeight: 600, fontSize: x(19) * unit, color: t.colors.muted, border: `${1.5 * unit}px solid ${t.colors.faint}`, borderRadius: 999, padding: `0 ${x(9) * unit}px`, lineHeight: 1.6}}>{tag}</div>
					) : null}
				</div>
			) : null}
		</div>
	);
};

const Row: React.FC<{left: string; right?: string; muted?: boolean}> = ({left, right, muted}) => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<div style={{display: 'flex', justifyContent: 'space-between', padding: `${x(7) * unit}px ${x(24) * unit}px`, borderBottom: `${unit}px solid ${t.colors.line}`, fontFamily: t.type.body, fontWeight: 500, fontSize: x(21) * unit, lineHeight: 1.45, color: muted ? t.colors.muted : t.colors.text}}>
			<span>{left}</span>
			{right ? <span style={{fontVariantNumeric: 'tabular-nums'}}>{right}</span> : null}
		</div>
	);
};

// the voice's own words, so the recap on the end card says what was heard
export const RULES = ['প্রতিটা বিক্রি লিখুন', 'রাতে মোট মিলিয়ে নিন', 'মাস শেষে দেখুন কোনটা বেশি চলে'];
export const NUM = ['১', '২', '৩'];

// App navigation: the next screen slides in from the right over the one before, which drifts left and dims.
const SLIDE = 12;
const Screen: React.FC<{enter?: boolean; leaveAt?: number; children: React.ReactNode}> = ({enter = true, leaveAt, children}) => {
	const frame = useCurrentFrame();
	const t = useTheme();
	const inP = enter ? ramp(frame, 0, SLIDE, curves.out) : 1;
	const outP = leaveAt === undefined ? 0 : ramp(frame, leaveAt, SLIDE, curves.out);
	return (
		<AbsoluteFill style={{translate: `${(1 - inP) * 100 - outP * 28}% 0`, background: t.colors.bg}}>
			{children}
			{outP > 0 ? <AbsoluteFill style={{background: `rgba(15, 25, 20, ${0.16 * outP})`}} /> : null}
		</AbsoluteFill>
	);
};

const Intro: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	return (
		<AbsoluteFill>
			<Header title="হিসাবের তিন নিয়ম" />
			<div style={{padding: `${x(10) * unit}px ${x(18) * unit}px`, display: 'flex', flexDirection: 'column', gap: x(12) * unit}}>
				<Stagger in="rise" each={5} delay={L(CUE.tinta) - 2} distance={18}>
					{RULES.map((r, i) => (
						<div key={r} style={{display: 'flex', alignItems: 'center', gap: x(14) * unit, background: t.colors.surface, borderRadius: x(18) * unit, padding: `${x(14) * unit}px ${x(16) * unit}px`, boxShadow: `0 ${x(4) * unit}px ${x(14) * unit}px rgba(0,0,0,0.07)`}}>
							<div style={{flexShrink: 0, width: x(44) * unit, height: x(44) * unit, borderRadius: x(22) * unit, background: t.colors.accent, color: t.colors.onAccent, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: t.type.display, fontWeight: 800, fontSize: x(25) * unit}}>{NUM[i]}</div>
							<div style={{fontFamily: t.type.body, fontWeight: 600, fontSize: x(23) * unit, lineHeight: 1.35, color: t.colors.text}}>{r}</div>
						</div>
					))}
				</Stagger>
			</div>
		</AbsoluteFill>
	);
};

const AddEntry: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const base = CUT.rule1;
	const left = x(24);
	const fieldW = S.w - 2 * left;
	const fieldTop = S.top + x(64);
	const buttonTop = fieldTop + x(189);
	const press = CUE.felun - base;
	return (
		<AbsoluteFill>
			<Header title="নতুন বিক্রি" />
			<div style={{position: 'absolute', left: left * unit, top: fieldTop * unit, display: 'flex', flexDirection: 'column', gap: x(16) * unit}}>
				<FormField label="জিনিস" value="চাল, ৫ কেজি" focusAt={CUE.prottekta - base - 4} typeAt={CUE.prottekta - base} cps={12} blurAt={CUE.prottekta - base + 29} width={fieldW} height={x(52)} mode="light" />
				<FormField label="দাম" value="৩৮০" kind="amount" prefix="৳" focusAt={CUE.prottekta - base + 29} typeAt={CUE.prottekta - base + 31} cps={8} width={fieldW} height={x(52)} mode="light" />
			</div>
			<div style={{position: 'absolute', left: left * unit, top: buttonTop * unit}}>
				<UiButton label="যোগ করুন" size="lg" width={fieldW} pressAt={press} doneLabel="যোগ হলো" doneIcon="check" />
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: (buttonTop + x(64)) * unit}}>
				<Animate in="rise" delay={press + 6} distance={16}>
					<div style={{fontFamily: t.type.body, fontSize: x(20) * unit, color: t.colors.muted, padding: `0 ${x(24) * unit}px ${x(4) * unit}px`}}>আজকের তালিকা</div>
					<Row left="চাল, ৫ কেজি" right="৳৩৮০" />
				</Animate>
			</div>
			<TapIndicator taps={[{x: left + fieldW / 2, y: buttonTop + 36, at: press}]} size={x(46)} />
		</AbsoluteFill>
	);
};

const DayTotal: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const base = CUT.rule2;
	const rows: [string, string][] = [
		['চাল, ৫ কেজি', '৳৩৮০'],
		['ডাল, ২ কেজি', '৳২৪০'],
	];
	// the habit, not just a tick: the day's total counts up, the cash in the box is counted, they match
	const counted = CUE.mot - base + 18;
	const cash = counted + 3;
	const matched = CUE.nin - base + 3;
	return (
		<AbsoluteFill>
			<Header title="আজকের হিসাব" sub="২৬ সেপ্টেম্বর" tag="উদাহরণ" />
			{rows.map(([a, b]) => (
				<Row key={a} left={a} right={b} />
			))}
			<Row left="আরও ২১টা বিক্রি" muted />
			<div style={{margin: `${x(12) * unit}px ${x(16) * unit}px 0`, background: GREEN, borderRadius: x(22) * unit, padding: `${x(10) * unit}px ${x(20) * unit}px ${x(10) * unit}px`}}>
				{/* the label row carries the check, so it never touches the total */}
				<div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: x(34) * unit}}>
					<div style={{fontFamily: t.type.body, fontSize: x(21) * unit, color: '#C9D3CC'}}>আজ মোট বিক্রি</div>
					<div style={{display: 'flex', alignItems: 'center', gap: x(8) * unit}}>
						<Animate in="fade" delay={matched + 6}>
							<div style={{fontFamily: t.type.body, fontWeight: 600, fontSize: x(21) * unit, color: MARIGOLD}}>মিলেছে</div>
						</Animate>
						<HandMark kind="check" width={x(34)} height={x(30)} size={x(4.5)} delay={matched} color={MARIGOLD} />
					</div>
				</div>
				<Counter to={12450} prefix="৳" digits="bangla" size={x(54)} color={CREAM} delay={CUE.mot - base} duration={counted - (CUE.mot - base)} align="left" enter="none" />
				<Animate in="rise" delay={cash} distance={10}>
					<div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', borderTop: `${1.5 * unit}px solid rgba(245, 241, 232, 0.22)`, marginTop: x(6) * unit, paddingTop: x(6) * unit, fontFamily: t.type.body, fontSize: x(21) * unit, color: '#C9D3CC'}}>
						<span>ক্যাশ গুনে পেলেন</span>
						<span style={{fontWeight: 600, color: CREAM, fontVariantNumeric: 'tabular-nums'}}>৳১২,৪৫০</span>
					</div>
				</Animate>
			</div>
		</AbsoluteFill>
	);
};

const MonthChart: React.FC = () => {
	const t = useTheme();
	const {unit} = useStage();
	const base = CUT.rule3;
	return (
		<AbsoluteFill>
			<Header title="এই মাসে বেশি চলে" sub="বিক্রি, হাজার টাকায়" tag="উদাহরণ" />
			<div style={{position: 'absolute', left: x(12) * unit, top: (S.top + x(108)) * unit}}>
				<BarChart
					orientation="horizontal"
					data={[
						{label: 'চাল', value: 42},
						{label: 'তেল', value: 31},
						{label: 'ডাল', value: 24},
						{label: 'ডিম', value: 19},
						{label: 'চিনি', value: 14},
					]}
					width={S.w - x(28)}
					height={x(284)}
					delay={SLIDE}
					highlight="চাল"
					highlightAt={CUE.beshi - base}
					format={{digits: 'bengali'}}
					labelSize={x(24)}
					valueSize={x(24)}
					color={t.colors.accent}
				/>
			</div>
		</AbsoluteFill>
	);
};

export const PhoneStage: React.FC = () => {
	const {unit} = useStage();
	return (
		// a slow push over the whole phone section, anchored mid-content so its words stay inside the safe area
		<PushIn amount={0.02} origin={`${540 * unit}px ${780 * unit}px`}>
			<div style={{position: 'absolute', left: PHONE_LEFT * unit, top: STAGE_TOP * unit}}>
				{/* the phone is gone before the closing title lands on 'আজই' */}
				<DeviceRise tilt={24} distance={260} exit={24} exitAt={L(CUT.phoneOut)}>
					<PhoneFrame width={PHONE_W} camera="dot" screen="#F6F5F0" statusBar="dark" time="৯:৪১">
						<ThemeProvider theme={APP}>
							<Sequence durationInFrames={L(CUT.rule1) + SLIDE}>
								<Screen enter={false} leaveAt={L(CUT.rule1)}>
									<Intro />
								</Screen>
							</Sequence>
							<Sequence from={L(CUT.rule1)} durationInFrames={CUT.rule2 - CUT.rule1 + SLIDE}>
								<Screen leaveAt={CUT.rule2 - CUT.rule1}>
									<AddEntry />
								</Screen>
							</Sequence>
							<Sequence from={L(CUT.rule2)} durationInFrames={CUT.rule3 - CUT.rule2 + SLIDE}>
								<Screen leaveAt={CUT.rule3 - CUT.rule2}>
									<DayTotal />
								</Screen>
							</Sequence>
							<Sequence from={L(CUT.rule3)}>
								<Screen>
									<MonthChart />
								</Screen>
							</Sequence>
						</ThemeProvider>
					</PhoneFrame>
				</DeviceRise>
			</div>
		</PushIn>
	);
};

// The rule number: a marigold badge pinned over the phone's left edge, from the rule's first word to the next rule.
export const StepBadge: React.FC<{n: string}> = ({n}) => {
	const t = useTheme();
	const {unit} = useStage();
	const d = 136;
	return (
		<div style={{position: 'absolute', left: (PHONE_LEFT - d + 34) * unit, top: (STAGE_TOP + 60) * unit}}>
			<Animate in="pop" out="fade" outDuration={8}>
				<div style={{width: d * unit, height: d * unit, borderRadius: (d / 2) * unit, background: MARIGOLD, color: '#1D2B24', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: t.type.display, fontWeight: 800, fontSize: 88 * unit, boxShadow: `0 ${12 * unit}px ${30 * unit}px rgba(0,0,0,0.32)`, lineHeight: 1}}>
					{n}
				</div>
			</Animate>
		</div>
	);
};
