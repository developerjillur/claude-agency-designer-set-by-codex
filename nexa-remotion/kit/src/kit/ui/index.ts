// The ui module: product and interface animation. Pointer and touches, controls that react, device and window
// frames, code and terminals, chat, notifications, lower thirds, title, chapter and end cards, logo reveals.
export {uiPalette, uiTypeSchedule, useUiTyping} from './shared';
export type {TypedText, TypingOptions, TypingPlan, UiMode, UiPalette} from './shared';
export {UI_ICONS, UiIcon} from './Icon';
export type {UiIconName, UiIconProps} from './Icon';
export {ClickSounds, Cursor, cursorMoveFrames, cursorPose, cursorTimeline, TapIndicator} from './Cursor';
export type {ClickSoundsProps, CursorKey, CursorPose, CursorProps, CursorShape, CursorTimeline, SwipeKey, TapIndicatorProps, TapKey} from './Cursor';
export {FormField, KeyCombo, Pressable, pressStateAt, SearchBar, Toggle, UiButton} from './Controls';
export type {FormFieldProps, KeyComboProps, PressableProps, PressState, SearchBarProps, ToggleProps, UiButtonProps, UiButtonVariant} from './Controls';
export {
	BrowserWindow,
	browserChromeHeight,
	DeviceRise,
	LaptopFrame,
	laptopScreen,
	MAC_TITLE_HEIGHT,
	MacWindow,
	PhoneFrame,
	phoneScreen,
	ScrollView,
	StatusBar,
	UiBackdrop,
	useInsidePhone,
	usePhoneScreen,
} from './Frames';
export type {
	BrowserTab,
	BrowserWindowProps,
	DeviceRiseProps,
	LaptopFrameProps,
	MacWindowProps,
	PhoneFrameProps,
	PhoneScreen,
	ScrollKey,
	ScrollViewProps,
	StatusBarProps,
	UiBackdropProps,
} from './Frames';
export {CodeBlock, codePalette, Terminal, terminalTimeline, tokenizeCode, tokenLines} from './Code';
export type {CodeBlockProps, CodeFocus, CodeLang, CodePalette, CodeToken, TermLine, TermSlot, TermTone, TerminalProps, TokenKind} from './Code';
export {ChatThread, chatTimeline, TypingDots} from './Chat';
export type {ChatMessage, ChatSlot, ChatThreadProps} from './Chat';
export {Notification, NotificationStack} from './Notify';
export type {NotificationPlace, NotificationProps, NotificationStackItem, NotificationStackProps} from './Notify';
export {ChapterBar, Countdown, FocusRing, LowerThird, Subscribe, subscribeClicks, UiTooltip} from './Overlays';
export type {ChapterBarProps, CountdownProps, FocusKey, FocusRingProps, LowerThirdProps, LowerThirdVariant, SubscribeProps, UiChapter, UiTooltipProps} from './Overlays';
export {EndCard, SectionTitle, TitleCard} from './Cards';
export type {EndCardProps, SectionTitleProps, TitleCardProps} from './Cards';
export {LogoMarkView, LogoReveal, UI_MARKS} from './Logo';
export type {LogoMark, LogoPart, LogoRevealProps, LogoRevealVariant} from './Logo';
