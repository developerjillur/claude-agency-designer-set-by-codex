# Casual, conversational copy in English: the craft

Research note, 24 September 2026. Every source below was read on 24 September 2026.

Scope: how real people and the most human-sounding brands write casual copy in English, worldwide. It covers
- the voice guides of real teams;
- the techniques of casual writing and the ones you can measure;
- what casual does not mean, and when to stay neutral;
- a register ladder;
- purple prose and its plain replacements;
- writing for the ear;
- replies and community posts.

It adds only what `copy.md` and `copyrules.py` (including the new `lint_spoken`) do not already have. Every lint
candidate in `casual-craft-en.json` was checked against both files before it went in.

## 0. What is new here, in eight lines

1. **The current lint misses register.** On 40 stiff, purple or forced-casual lines, `copylint` flagged 3, and two of
   those only for exclamation marks. The 179 new candidates flag all 40 and none of 40 natural lines (§10).
2. **A 2026 model writes templates, not purple.** 72 captions from gpt-6-sol (via Codex) contained almost none of the
   classic purple or corporate words (6 of 72 hits). But 50 of 72 used a launch template: "is here", "has arrived",
   "Meet our", "Discover our", "X is calling", a personified object. The same templates appear in 38 of 1,658 real
   brand posts (2.3%). The tell is frequency, so the ledger should count templates (§7).
3. **Casual beats formal, and trust beats friendly.** In NN/g's test of tone of voice, casual, conversational and
   enthusiastic versions did best. Trust explained 52% of willingness to recommend; friendliness added 8%. A playful
   insurer read as friendlier and less trustworthy (§1).
4. **Slang mostly doesn't sell.** 74% of US adults say brands try too hard to act cool on social. About 60% say Gen Z
   slang has no effect on what they buy, and negative reactions (26%) outnumber positive ones (15%). Even Gen Z is
   only 29% positive (CivicScience, March 2026) (§4).
5. **In replies, laugh with people, never at them.** Observers reward affiliative humour over aggressive humour.
   Aggressive humour paid off only for "exciting" brand personalities (Béal and Grégoire 2021). Emoji in complaint
   replies lower perceived professionalism unless the voice is already human (Verheijen and Liebrecht 2025) (§9).
6. **A register ladder with four rungs** (friend-chat, casual, neutral-warm, formal) and defaults by brand type and
   moment. Monzo sets humour to zero in customer service and in any negative news, and to maximum on organic social
   (§5).
7. **Writing for the ear:** checks `lint_spoken` lacks. Currency signs and pence, ordinals, e.g./i.e., the x
   multiplier, "the former/latter", visual pointers, long opening clauses, lists of four or more, pace in words per
   second (§8).
8. **Measurable signals, with baselines from real brand posts:** contraction rate, sentence length, Flesch,
   syllables, passive share, nominalizations, adverbs, "brochure flatness". Most are register checks, not AI checks,
   so they are notes (§3).

## 1. What makes brand copy sound like a person: the guides

| Team or source | What they do (paraphrased) | Borrow this |
|---|---|---|
| Mailchimp Content Style Guide | Voice: plainspoken, genuine, translators of jargon, dry humour. Tone follows the reader's state of mind. Being clear matters more than being entertaining. Contractions are welcome. One "!" at most, never in failure messages or alerts. No "ninja", "rockstar" or "wizard". On social: no internet shorthand, no jumping on unrelated trends, pause scheduled posts in breaking news. | Tone moves with the reader's mood; the voice doesn't. Quote: "forced humor can be worse than none at all." |
| Nielsen Norman Group (Kate Moran, 2016) | Four tone dimensions: formal or casual, serious or funny, respectful or irreverent, matter-of-fact or enthusiastic. In the test, casual, conversational and enthusiastic tones did best. The playful insurer read as less trustworthy, and bank copy that was conversational but serious beat the formal version. Healthcare users preferred the warm version and called it "bedside manner". | Set the four dials per channel. Trust first: it explained 52% of willingness to recommend. What sounds witty to one reader sounds corny to another. |
| NN/g (Hoa Loranger, 2017) | Experts in science, IT and medicine also prefer plain, scannable, conversational text. | Plain is not dumbing down. |
| GOV.UK writing guidance | Plain English is mandatory. Tone: specific, brisk but not terse, human, "serious but not pompous". Write conversationally, one-to-one. Address the user as "you". Use the active voice. Split sentences over 25 words. Contract "you'll", but avoid negative contractions (can't, don't) and should've or could've, which some users misread. No need for "please note". Keeps a words-to-avoid list. | The words-to-avoid list (§2.3) and the contraction caution for safety text |
| digital.gov plain language guides (successor to plainlanguage.gov) | One idea per sentence. Avoid hidden verbs ("conduct an analysis") and noun strings. Simpler phrases ("now", not "at this point in time"). Avoid e.g. and i.e. Write positively. | Hidden verbs and phrase swaps |
| Microsoft Writing Style Guide | Use everyday words and common contractions. Don't mix "can't" and "cannot" in one UI. Never contract a noun and a verb. Avoid there'd, it'll and they'd. | Contraction rules |
| Monzo writing principles | Three principles: straightforward kindness everywhere; "everyday magic" in brand writing; "warm wit" mostly on social. Latin-root "business" words like require and provide sound cold. Say sorry once, sincerely: "It's never 'We'd like to apologise', it's 'We're sorry'." Serious isn't formal: 800 judges preferred plain English 66% to 34% (Flammer 2010). No passive in bad news. No cheap seasonal puns (eggcellent at Easter is its example). No literal magic. Never punch down. Use references most people get. Stay out of politics, celebrity health and court cases. | The channel dials (§5): wit is none in operational messages and customer service, medium in marketing, maximum on organic social |
| Duolingo brand guidelines | Voice: expressive, playful, embracing, worldly. Brief, active, contracted. Supportive when learners fail: a gentle "try again" rather than a flat "incorrect". No slang or references not everyone knows; calling a user a boss is its example. Tone drops the exuberance and the exclamation marks for serious stories: "Treat this content not like content, but like someone's life." | Celebrate wins, soften failures, and read the room |
| Intercom (PREACH, 2020; "Embracing a human tone", 2017) | Proud, Responsible, Empathetic, Articulate, Concise, Human. Answer "how are you?" like a person. Own mistakes with the real context. Emoji only in lighter moments. Don't force casualness. | Reply rules (§9) |
| 37signals, Getting Real | Copywriting is interface design: speak the customer's language, no internal lingo: "Don't sound like an engineer talking to another engineer." Give the product a personality and keep it. | A count reads better as a sentence (there are five new messages) than as a label with a colon |
| Paul Graham, "Write Like You Talk" (2015) | Ask of every sentence whether you'd say it to a friend. Read drafts aloud. If a draft is stiff, explain it out loud and write down what you said. | The friend test |
| Amazon Alexa Design Guide ("Be relatable") | Write it the way you'd say it. Act the script out. Use contractions. Pause where speech pauses. Apply the one-breath test. Vary repeated prompts. | Ear rules (§8) |
| Innocent (Dan Germain, 26.org.uk, 2009) | The voice grew from how the team talked to each other. The test was "Does it make my friends laugh?" Skip your first idea (most people have it) and your second. | The third-idea rule |
| Oatly (John Schoolcraft, eatbigfish, 2016) | People are easily bored, so write the unexpected. Honesty makes the voice work: they believe what they sell. | Surprise plus honesty |
| Wendy's (Rival IQ case study, 2022) | Sassy and fast. Roasts rivals and people who ask to be roasted. The Twitter team dropped layers of approval in 2017. In January 2017 a community manager posted a Pepe meme, a hate symbol by then, and Wendy's deleted it. | Speed needs a meme check |
| Liquid Death (PR Daily, 2023) | Behaves like a character, not a brand. Turns hate comments into content: three "Greatest Hates" albums, 800,000+ Spotify streams. | Self-aware answers to critics |
| Ryanair (CMO Dara Brady to Skift, October 2025) | The voice has been the same for 35 years: direct, honest, cheeky and "not afraid to be self-deprecating". | Self-deprecation works when the low price is the promise |
| Netflix | A fan's voice on social. In December 2017 it tweeted at the 53 people who had watched one film every day for 18 days, asking "Who hurt you?". The BBC reported the backlash: people called it creepy. | Don't joke with the reader's data (§4) |
| Zomato (Moneycontrol, 2024; afaqs, January 2026; Business Today, June 2026) | Its cheeky push notifications came from the founder's brief to "make a relationship with the customer". In 2026 it dropped dish-specific nudges (order biryani once, get asked about biryani again), which the founder called borderline manipulative, for generic ones. In June 2026 a fake Zomato notification joking about a viral row over a ₹370 biryani date and consent spread widely; Zomato said it wasn't theirs. | A known cheeky voice makes fakes believable; nudges can turn into pressure |
| Swiggy (Social Samosa, March 2023) | A Holi billboard for Instamart told people to eat eggs rather than throw them. It drew #HinduPhobicSwiggy and came down. | Festival jokes must not tell a community how to celebrate |
| Social teams 2025 to 2026 (Modern Retail, April 2026; Sprout Social 2025 to 2026) | Brands now spend time in other people's comment threads (Dude Wipes, Vita Coco). The work is "less about volume and more about timing and tone". When it's forced, people reply telling the brand to be quiet. 51% of people who complain publicly expect a public acknowledgement before a move to DM. | Comment etiquette (§9) |

**The common thread.** These voices sound like a person because they:
1. Have one speaker ("we" means real people) talking to one reader ("you").
2. Use the words that speaker would say out loud, contracted.
3. Notice specifics: a time, a place, a price, the thing that went wrong.
4. Keep the rhythm of speech: short and long sentences, the odd fragment, a sentence that starts with And or But.
5. Answer the question the reader would ask next.
6. Share a joke with the reader, never at the reader's cost, and only one at a time.
7. Admit limits ("We don't do refills yet").
8. Read the room: the same voice, a different tone, when the news is bad.

## 2. The playbook: rules with before and after

The examples are mine unless marked. Each rule says why.

### 2.1 Talk to one person

Use "you" for the reader and "we" for real people at the brand. In a meta-analysis of instructional text, the
conversational style (second person, direct address, a visible author) raised perceived friendliness (d = 0.46),
retention (d = 0.30) and transfer (d = 0.54) (Ginns, Martin and Marsh 2013). GOV.UK: address the user as "you".

- Before: Customers can collect orders from the counter after 5 pm.
- After: You can pick it up from the counter after 5.

### 2.2 Contract, except where a misread costs something

Contractions give an informal, friendly tone (Mailchimp, Microsoft, Duolingo, Alexa). GOV.UK's exception: some
readers misread negative contractions, so write "do not" and "cannot" in safety, legal, dosage and payment
instructions. Never mix "can't" and "cannot" in one piece (Microsoft).

- Before: We are open late on Fridays and it is worth the trip.
- After: We're open late on Fridays. Worth the trip.
- Safety line, keep it full: Do not give this to children under 12.

### 2.3 Everyday words beat Latinate and corporate ones

GOV.UK names the words: its list swaps utilise for use, and keeps deliver for things like post, not abstract ideas.
Monzo explains why Latin-root words like require and provide sound cold. Swaps not in `copy.md`:

| Stiff | Everyday | Stiff | Everyday |
|---|---|---|---|
| utilise / utilize | use | in order to | to |
| purchase | buy | prior to | before |
| assist, assistance | help | subsequently | later, then |
| approximately | about | in the event that | if |
| commence | start | at this point in time | now |
| facilitate | run, host, set up (say how) | due to the fact that | because |
| obtain | get | a number of | some, several, the number |
| require | need | on a daily basis | daily |
| additional | more, extra | is able to | can |
| numerous | many | with regard to, regarding | about |
| endeavour | try | we wish to inform you | (say the news) |
| initiate | start | going forward | from now on |
| terminate | end, cancel | one-stop shop | everything in one place |
| demonstrate | show | deliver value / results | (name the result) |
| liaise | work with | our solutions | (name the product) |
| individuals | people | state-of-the-art, industry-leading | (the spec or proof) |
| whilst | while | we pride ourselves on, we strive to | (say what you do) |

### 2.4 Verbs, not nouns

Hidden verbs ("conduct an analysis", "make the decision to", "the implementation of") make copy long and cold
(digital.gov). They are also a model habit: GPT-4o uses nominalizations at 2.1 times the human rate (Reinhart et al.
2025).

- Before: Our team conducted a thorough review and made the decision to implement changes.
- After: We checked every order from last week and changed how we pack glass.

### 2.5 Active voice, above all in bad news

Monzo warns that writers slip into the passive when the news is bad, and that it isn't fair to the reader.

- Before: Mistakes were made and your order was delayed.
- After: We sent your order to the wrong depot. It's with you tomorrow by noon.

### 2.6 Rhythm: mix short and long, and let a sentence start with And or But

Aim for 15 to 20 words on average, with variety (Plain English Campaign). One fragment can land; a run of them reads
as a formula (`copy.md`, staccato). Monzo: starting with And, But, So or Because is fine, because we do it when we
talk. Reinhart et al. found GPT-4o avoids joining clauses with "and" more than humans do.

- Before: Our bread is baked fresh daily using traditional methods and high-quality ingredients.
- After: We bake at 5. And yes, it's still warm at 8.

### 2.7 Specifics a person would notice

`copy.md` already asks for a number, name or date. The casual version is the detail a friend would mention: the
queue, the rain, the smell at 7 am, the thing that went wrong.

- Before: Enjoy our cosy atmosphere and friendly service.
- After: Window seats go first. Ask for Dan, he knows the playlist.

### 2.8 Ask questions people can answer

Real questions pull replies (`copy.md` §7). Rhetorical openers delay the point: "Did you know?", "Ever wondered?",
"Picture this:", "Ready to...?". Duolingo's tone page uses exactly this kind of opener as its example of what not to
write.

- Before: Ready to transform your mornings?
- After: Oat or whole milk? We've got both now.

### 2.9 Reactions and interjections, one at a time

"Honestly?", "Okay,", "Fair point.", "Yes, really." sound human when they react to something real (a question, a
complaint, a surprise). One per piece. Never "OMG" or "lol" in a post; in replies, only if the other person wrote
that way first. Patagonia's Bluesky team once replied "Beat us to it lol post incoming!".

### 2.10 Humour: one joke, shared, never on bad news

- Monzo: a pinch, not a dollop; pick the best joke, not five; smart asides, not the pun everyone makes that day.
- Mailchimp: if you're unsure, keep a straight face.
- Self-deprecation should be about small things (queues, spelling), never competence. Monzo won't play the victim.
  Ryanair can joke about legroom because low fares are its promise; a bank can't joke about losing money.
- No wit in outages, price rises, fraud, grief or complaints about loss (Monzo's dials; Duolingo's tone page).

### 2.11 Self-aware and honest

Say the true, slightly awkward thing: "It's heavier than it looks." "We don't do refills yet." Liquid Death and
Oatly turn criticism into copy. Ryanair owns its reputation. It works when the admission is true and small, and the
brand still does its job.

### 2.12 Read it aloud

Graham's friend test, and the Alexa guide's advice to act the script out with a second person. If you wouldn't say
it across a counter, rewrite it.

### 2.13 Plain is not dull

In NN/g's test, bank copy that was conversational but serious read as friendlier (+0.7), more trustworthy (+0.3)
and more recommendable (+0.4) than formal copy. Monzo cites 800 judges who preferred plain English and rated its
author as better educated.

### 2.14 Write positively

- Before: You can't get a refund if you don't have a receipt.
- After: Bring your receipt and we'll refund you on the spot. (Mailchimp and digital.gov both ask for the positive
  form.)

## 3. Measurable signals

Baselines come from 1,658 public Bluesky posts by nine brand accounts, fetched 24 September 2026: netflix.com,
patagonia.com, xbox.com, playstation.com, crunchyroll.com, substack.com, bsky.app, tumblr.com and kickstarter.com.
"Consumer brands" means all except Substack, whose posts are literary blurbs. Most metrics mark register rather than
machine authorship: the stiff calibration lines scored much like real brand posts. So they are notes, and they apply
to the casual and friend-chat rungs.

Baselines are shares of the 377 consumer-brand posts of 30 or more words, with the figure including Substack (548
posts) in brackets where it differs.

| Metric | Casual target | Flag at | Brand baseline | Source |
|---|---|---|---|---|
| Contraction rate | contract most pairs | 2+ uncontracted with none contracted, or 3+ with 70% or more uncontracted | 2% (13 of all 1,658 posts: Patagonia advocacy, a Bluesky incident notice) | Microsoft, Mailchimp, GOV.UK |
| Sentence length | mean 15 to 20 | mean over 25, or any sentence over 35 | 8% (21%) | Plain English Campaign; GOV.UK (25) |
| Flesch Reading Ease | 60 or more | note under 50, warning under 30 | 19% under 50 (31%), 2% under 30; median 61, Substack 46 | Flesch formula; Hemingway default grade 9 |
| Syllables per word | about 1.5 (Flesch's target for consumer copy) | over 1.75, or over 22% of words with 3+ syllables | 10% (12%) | Flesch; Reinhart et al. (word length separates LLM text) |
| Passive share | under 1 in 4 sentences | over 25% (4+ sentences) | 0% | GOV.UK, digital.gov, Monzo |
| Nominalizations | few | 6+ per 100 words (40+ words) | 2% | Reinhart et al. (2.1x); GOV.UK |
| -ly adverbs | few | over 5 per 100 words | 1% | Reinhart et al.; Hemingway |
| Brochure flatness | a "you", a contraction or a number | 40+ words with none of the three | 7% (9%) | Ginns et al. 2013 |
| Spoken pace | 2.5 words a second or less | note over 2.5, warning over 2.7 | n/a | audiobooks: 150 to 160 wpm |

Passive voice is a corporate tell, not an AI tell: GPT-4o uses agentless passives at about half the human rate
(Reinhart et al.).

## 4. What casual does not mean

### 4.1 The failure modes

| Failure | What it looks like | Why it fails | Case |
|---|---|---|---|
| Forced slang ("how do you do, fellow kids") | "No cap, this deal slaps." | Most readers don't respond, and negatives outnumber positives | CivicScience 2026 (figures above). The meme comes from Steve Buscemi's line in *30 Rock*. |
| Borrowed dialect | Brand copy in AAVE-derived slang | Taking a community's voice for sales: "digital blackface" | Wikipedia "Digital blackface": Vice called the food blog Thug Kitchen, run by two white Californians, its latest form |
| Dated slang | "on fleek", "bae", "totes", "amazeballs", "treat yo self" | Shows the brand arrived late | inference; Monzo (references everyone gets) |
| Misread meme | A meme whose meaning has changed | You inherit what it now means | Wendy's deleted a Pepe meme in January 2017; it said its community manager was "unaware of the recent evolution of the Pepe meme's meaning" |
| Hashtag hijack | Joining a trend you haven't read | The trend may be about pain | DiGiorno, September 2014: "#WhyIStayed You had pizza." The hashtag was about domestic violence (TIME) |
| Shock hook | A sexist or cruel first line "explained" in the thread | Nobody reads the thread | Burger King UK, International Women's Day 2021: "Women belong in the kitchen", then a scholarship; deleted after 12 hours (Adweek) |
| Solemn day, jolly post | A mascot, a flag, a smile on a day of loss | Grief used as content | SpaghettiOs, Pearl Harbor Day 2013 (USA Today) |
| Creepy data joke | "We see you ordered pizza four times this week" | Reads as surveillance | Netflix 2017 (BBC). Monzo: the same joke is fine in a year-end recap, not unprovoked at 3 am |
| Nudging as friendship | "You had biryani. Biryani again?" | Personal nudges turn into pressure | Zomato dropped dish-specific prompts in 2026 (afaqs) |
| Over-familiarity | "Hey bestie", "we love you", "our amazing community" | Strangers don't want a brand as a friend | Gretry et al. 2017, "Don't pretend to be my friend!": an informal brand style can backfire on social media (title-level; I couldn't open the paper) |
| Sarcasm at customers | "Skill issue." "Try being shorter." | Observers side with the customer | Béal and Grégoire 2021: aggressive humour loses to affiliative, except for "exciting" brands |
| Jokes over a real grievance | Cute trend videos while people are angry about something real | Reads as dodging | Duolingo, May 2025: comments on every video were about its AI-first memo; it deleted its TikTok and Instagram posts (Fast Company) |
| Jokes about a trial or tragedy in the comments | A quip about a domestic-abuse case | The comment section is public | Duolingo removed a TikTok comment about Amber Heard in May 2022 and its social lead apologised (PRWeek) |
| Festival policing | A joke telling people how to celebrate their festival | Reads as disrespect | Swiggy's Holi egg billboard, 2023 |
| Cheap seasonal puns | "Eggcellent", "sleigh", "spooktacular" | Everyone posts the same pun that day | Monzo bans the type (its example: eggcellent at Easter) |
| Confirmshaming | "No thanks, I don't like saving money." | Manipulation by guilt; a deceptive pattern the FTC has pursued | deceptive.design |
| Clingy win-back | "We miss you! Don't leave us hanging." | Guilt instead of news | Zomato 2026; deceptive.design |

### 4.2 When to stay neutral

Drop to neutral-warm or formal (§5) for:
- money trouble, debt, fraud, security and data breaches;
- health, symptoms, dosage and insurance claims;
- grief, bereavement and condolences;
- disasters, attacks, war and anniversaries of tragedies;
- outages, recalls, price rises and layoffs;
- legal terms, and complaints about loss or harm.

Monzo sets wit to none for operational messages and customer service, because there a misfire costs more than a
good joke earns. NN/g's playful insurer lost trust. Mailchimp pauses scheduled posts during major breaking
news. Monzo stays out of politics, celebrity health and court cases.

## 5. The register ladder

| Rung | Sounds like | Markers | Same message: the 6 pm class moves rooms tonight |
|---|---|---|---|
| 1. Friend-chat | a regular chatting in the comments | slang the audience actually uses, jokes, fragments, emoji, lower case in replies | "6 pm spin's in studio 2 tonight 🚲 same Maya, way more bikes" |
| 2. Casual | a friendly shop owner | contractions, "you", everyday words, one light joke, a fragment, no borrowed slang | "Tonight's 6 pm class is in studio 2. Same instructor, more bikes." |
| 3. Neutral-warm | a good nurse or bank adviser | contractions (not negative ones in instructions), "you", plain words, no jokes, no emoji, one "sorry" if at fault, facts first | "Tonight's 6 pm class will be in studio 2. The time and the instructor stay the same." |
| 4. Formal | a clear notice | full forms, defined terms, "must", "do not", no humour, still plain words | "On 24 September the 6 pm class will take place in Studio 2. The timetable is otherwise unchanged." |

Bad news uses rung 3 or 4 whatever the brand's usual rung (rule 2 below).

Defaults by brand type (posts / replies / bad news):

| Brand type | Posts | Replies | Bad news |
|---|---|---|---|
| Snacks, soft drinks, streetwear, gaming, youth apps | friend-chat or casual | friend-chat if the person invites it, else casual | neutral-warm |
| Restaurants, cafés, food delivery, fashion retail | casual | casual | neutral-warm |
| Beauty and wellness | casual, no purple | casual | neutral-warm; health claims formal |
| Luxury and hospitality | neutral-warm: short, concrete, no slang, no purple | neutral-warm, first name | neutral-warm or formal |
| Banks and fintech | marketing casual; product and operations neutral-warm | neutral-warm | neutral-warm (no wit, Monzo); legal formal |
| Health, pharma, insurance | neutral-warm | neutral-warm | formal for dosage and safety |
| B2B software | casual on social; neutral-warm in docs, support and status pages | neutral-warm | neutral-warm; security notices formal |
| Government, NGOs, charities | neutral-warm ("serious but not pompous") | neutral-warm | formal and quiet |

Rules for moving on the ladder:
1. **Stakes set the rung, not the channel.** Drop one rung as the reader's risk rises (money, health, safety, loss).
2. **Never climb during bad news.** Outages, price rises, breaches and recalls get neutral-warm or formal, with no
   jokes and no "!".
3. **An unfamiliar brand starts one rung lower.** A human voice raised purchase intent when readers browsed for
   pleasure. It did nothing when negative comments sat beside the post. When readers were highly involved, it
   lowered intent through perceived risk (Barcelos et al. 2018). The title of Gretry et al. 2017, "Don't pretend to
   be my friend!", makes the same point.
4. **Match the person, one rung calmer.** If they joke, you can smile back; if they're angry, you don't joke.
5. **Sincere brands keep humour affiliative.** Only an "exciting" brand personality can afford a roast, and only when
   the person asked for it (Béal and Grégoire; Wendy's roasts people who ask).
6. **Moments override the default.** A festival greeting goes one rung warmer, with no offer on solemn days
   (`occasions.md`). A tragedy goes formal and quiet, and you stop the schedule. For a celebrity death, a court case
   or a political fight, say nothing.

## 6. Purple prose: the list and the plain replacements

Purple prose is ornate writing that draws attention to its own style: stacked adjectives, adverbs and metaphors
(Wikipedia, "Purple prose"). The model habit is measured. GPT-4o uses "camaraderie" at 162 times the human rate,
"tapestry" 155x, "intricate" 119x, "underscore" 107x, "unspoken" 102x, "amidst" 100x, "palpable" and "solace" 95x,
"fleeting" 84x and "unravel" 83x. GPT-4o Mini uses "grapple" 131x and "ignite" 122x (Reinhart et al. 2025, Table 1).
The antislop-sampler slop list ranks "whisper" 7th and "symphony" 117th, and down-weights "a dance of" and
"orchestra of". Mailchimp's rule covers it: no fluffy metaphors, no cheap plays to emotion.

Test for a purple line: could a reader check it, taste it, count it or find it? If not, replace it with something
they could.

| Purple | Plain | Purple | Plain |
|---|---|---|---|
| a symphony (or dance, burst, explosion) of flavours | name the flavours in order | dances across your palate | sweet first, then a chilli kick |
| tantalise your taste buds, awaken your senses | say what it tastes or smells like | delectable, heavenly, divine | good, tasty, or the dish |
| culinary journey, gastronomic adventure | meal, menu, seven courses | whispers of vanilla | a hint of vanilla |
| the warmth of sandalwood | warm, woody | amber warmth meets fig (X meets Y) | amber and fig: warm, a bit sweet |
| timeless elegance | the same cut since 2009 | captivating, mesmerising, enchanting | name what holds the eye |
| exquisite | hand-rolled edges, 18k gold | ethereal | light, sheer, pale |
| allure, alluring | tempting, or why people want it | radiant, luminous (skin) | brighter, with the test result |
| thoughtfully designed, expertly crafted, lovingly made | hand-stitched in Porto | effortlessly chic | goes with jeans |
| embrace the season | wear it, try it, or cut | a sanctuary, a haven, an oasis of calm | a quiet room, no phones past the desk |
| tranquil, serene, idyllic, picturesque | quiet, or describe the view | kissed by golden sunlight | sun until 4 pm |
| awaits you, beckons | opens at 6, is ready | let it transport you | 40 minutes by ferry |
| immerse yourself in, step into a world of | spend an afternoon in | your next escape | trip, stay, holiday |
| the essence (soul, spirit) of summer | one smell, one street, one dish | feed your soul | hot, filling, ready in ten minutes |
| unforgettable | what they'll remember | cherished memories, moments that matter | the actual moment |
| a quieter moment, a softer finish | the actual thing | pure bliss | calm, happy |
| a celebration of, an ode to, a love letter to | our take on | a new chapter | what changed |
| camaraderie | friends, team spirit | palpable | cut it, or say what you saw |
| solace | comfort | fleeting | short, one week only |
| unravel | find out, explain | grapple with | deal with |
| ignite | start, set off | cacophony | noise |
| amidst | among, during | unspoken | cut, or say it |
| kaleidoscope | mix, or the colours | labyrinth | maze |
| odyssey | trip | beacon of hope | cut |
| unwavering | steady | boundless | lots of |
| unparalleled, unrivalled, unmatched, like no other | the proof | iconic | on the menu since 1978 |
| quaint | small, old | opulent, sumptuous, lavish | the material, the price |
| magical, the magic of | what happens (Monzo: no literal magic) | morning ritual | routine, coffee |

The words already in `copy.md` (tapestry, testament, nestled, breathtaking, indulge in, elevate, a feast for the
senses, a world of, journey, curated, vibrant, bustling) are not repeated here.

Before and after:
- "Indulge in a symphony of flavours that dance across your palate." becomes "Sour cherry first, then dark chocolate.
  A 70% bar with sea salt."
- "Step into a sanctuary where time slows down." becomes "No phones past the front desk. Twelve rooms, one garden."
- "Our captivating new fragrance embraces you in an ethereal glow." becomes "Amber and fig. Warm, a bit sweet, soft by
  lunchtime."
- "Discover the timeless elegance of our handcrafted collection." becomes "Hand-stitched in Porto. The same five shapes
  since 2009."
- "Kissed by golden sunlight, our terrace is a haven of tranquility." becomes "The terrace gets sun until 4. It's the
  quiet side of the street."
- "Immerse yourself in an unforgettable culinary journey." becomes "Seven courses, two and a half hours. Book the 7 pm
  sitting."

## 7. What a 2026 model writes by default: templates, not purple

**Method, 24 September 2026.** The model was gpt-6-sol with xhigh reasoning, through the Codex CLI 0.156.1 in a
read-only sandbox. Prompt: "two short social media captions for each of 12 briefs".
- **Set A:** everyday briefs with no style instruction.
- **Set B:** the same briefs, "casual, conversational and fun".
- **Set C:** twelve luxury and food briefs with no style instruction.

That is 72 captions in all, compared with the 1,658 brand posts from §3. The captions are in
`casual-src/gen/out_*.txt`.

Result: almost no purple or corporate words. A few captions used "purchases", "awaits", "ritual" or "Ready to...?".
Instead, the same launch templates came back again and again:

| Template | Model captions | Brand posts |
|---|---|---|
| "is here / has arrived / just landed / just dropped" | 16 of 72 | 20 of 1,658 (1.2%) |
| "Meet our / Say hello to / Introducing" | 11 of 72 | 9 (0.5%) |
| "Discover our / Explore our" | 8 of 72 | 8 (0.5%, mostly Patagonia linking to its book) |
| "a quieter moment", "a softer finish" (a comparative with nothing compared) | 4 of 24 luxury | 0 |
| a personified object ("Your coffee mug has been waiting for this", "Your sneaker rotation noticed") | 4 of 24 casual | 0 |
| meme casual: "Autumn called", "entered the skincare chat", "Cue the...", "Finally, a way to...", "just got easier" | 5 of 72 | 0 |
| "X plans:" opener; "New season, new menu"; "X is calling" | 2 or 3 of 72 each | 0 or 1 |
| "the warmth of", "X meets Y." | 2 to 3 of 24 luxury | 0 |
| two or more of these in one caption | 12 of 72 | 0 |

Each template is fine once; brands use them too (Netflix: "The trailer ... is HERE"). The machine signal is that
every caption reaches for one. So the JSON keeps them as notes, adds a warning when two appear in one piece, and
suggests the copy ledger count them across a client's last 12 posts. Caveat: the model ran inside the Codex agent,
not a bare API call, so this is one model on one day.

## 8. Writing for the ear

`copy.md` §5 already treats the spoken hook as its own hook, and `lint_spoken` checks symbols, links, emoji,
capitals, the taka sign and sentences over 16 words. These rules add the rest.

1. **Write it the way you'd say it, then act it out** (Alexa Design Guide). Use contractions.
2. **One breath, one idea.** The one-breath test: "If you need to take a breath, consider reducing the length"
   (Alexa). A list of steps may take several breaths, but breathe between ideas, not inside one.
3. **Main point first.** Don't make the listener hold "Although..., because..., if..." before the verb (digital.gov:
   dependent clauses confuse).
4. **Say numbers the way people say them.** Round what you can ("about half"). One number per sentence.

| Written | Say it |
|---|---|
| $19.99 | nineteen ninety-nine |
| £12.50 | twelve fifty, or twelve pounds fifty |
| $1,000,000 | one million dollars, or a million |
| 2nd | second |
| 9:30 pm | half past nine tonight |
| 3x faster | three times faster |
| 10-12 | ten to twelve |
| 50% off | half price, or fifty percent off |
| 555-201-3344 | in groups, twice, or a short word to text instead |
| shop.com/deals/autumn | shop dot com (the rest goes in the caption) |
| e.g., i.e., etc., vs. | for example, that is, and so on, versus |
| Part II | part two |

5. **No brackets, no asides, no "the former/the latter".** An aside becomes its own sentence. Repeat the noun.
6. **No visual pointers in audio-only copy** ("see below", "as shown", "link below"). Say where: "the link's in the
   show notes".
7. **Lists of three at most** in one sentence.
8. **Say the brand and the one action twice:** early, and again at the end. Listeners can't scroll back.
9. **Pace.** Audiobooks run at 150 to 160 words a minute, 2.5 to 2.7 a second. So 15 seconds holds about 35 to 40
   words, 30 seconds 70 to 80, and 60 seconds 140 to 160. Plan about 10% fewer for music and pauses. That is my
   arithmetic from the Wikipedia figure; cut words, not pauses.
10. **For text-to-speech, render and listen.** Homographs (read, live, lead, record, wind) can come out wrong. Put a
    pronunciation note for brand names in the brief, not in the caption. A pause is a full stop or a new line, never a
    dash (house rule).
11. **Podcast host reads are talking points, not scripts.** 68% of US podcast listeners say they're likely to trust
    host recommendations and 67% find host-read ads effective. 36% prefer them, citing the conversational, personal
    tone (The Harris Poll, QuestDIY, 1,000+ listeners). Give the host facts and one claim; let them use their own words
    and their own experience, only if it's real. Disclose the paid partnership as the law requires (in the US, the
    FTC's Endorsement Guides).

Before and after (a 15-second voiceover):
- Written: "Introducing our new autumn menu (available 12 to 3 pm, Mon to Fri), featuring 12 dishes, e.g. pumpkin
  risotto, from $14.99. Visit www.ourplace.com/autumn."
- For the ear: "New autumn menu. Twelve dishes, lunchtime on weekdays. Try the pumpkin risotto, it's fourteen
  ninety-nine. That's Our Place. Lunch, weekdays, twelve till three."

## 9. Replies and community posts

What the evidence says:
- **A human voice builds trust.** In interactive posts, a conversational human voice correlated with trust,
  satisfaction and commitment (Kelleher 2009).
- **Observers read your replies to other people.** They reward affiliative humour, and an affiliative joke did as
  well as a formal apology with compensation (Béal and Grégoire 2021).
- **Emoji cost competence.** In complaint replies (webcare), emoji made the company seem more human but less
  professional. A conversational human voice turned that around (Verheijen and Liebrecht 2025, N = 1,202). Emoticons
  raise warmth and lower perceived competence, which hurts with exchange-minded customers (Li, Chan and Kim 2019).
- **Acknowledge in public first.** 51% of people who complain publicly expect that before a move to DM (Sprout Social
  pulse survey, Q4 2025).
- **A bare full stop reads curt in chat.** Texts ending in a full stop read as less sincere (Gunraj et al. 2016). A
  one-word reply ("Noted.") reads cold; add a few words.

Rules:
1. **Answer first, in their words.** No opener script ("Thank you for reaching out", "We understand your
   frustration"). Thanks go at the end, if at all.
2. **Use their first name. Sign with a first name or initials** where the platform allows. A person answered, so show
   it.
3. **Say what happens next, who does it and by when.** "We'll look into it" isn't a plan.
4. **One apology, owned, then the fix.** Don't apologise for their feelings. Don't say sorry when you haven't done
   anything wrong; explain instead (Monzo).
5. **Acknowledge in public, then move private details to DM.** Never ask for passwords or full card numbers.
6. **Match their energy, one rung calmer.** Praise can get a joke back; a complaint gets facts. Laugh with people,
   never at them.
7. **No emoji in complaint replies.** They're fine in replies to praise.
8. **Don't copy and paste.** Three identical replies in a thread read as a bot.
9. **Roasts are opt-in.** Wendy's roasts people who ask for it. Ryanair's self-mockery rests on its low-fare promise.
   A roast without an invitation is aggressive humour.
10. **In other people's threads, add something or stay out.** Timing and tone matter more than volume, and forced
    brand comments draw replies telling the brand to be quiet (Modern Retail 2026). No sales pitch in a creator's
    comments.
11. **Community posts sound like a host, not a press office.** Ask questions people can answer. Name members, with
    permission. Say what you changed because of their feedback. No bait (`copy.md` §6).
12. **Some threads get no joke at all:** trials, deaths, disasters, and angry threads about a real decision. Answer
    plainly or not at all (Duolingo 2022 and 2025).

Reply pairs (robotic, then human):

| Situation | Robotic | Human |
|---|---|---|
| Late delivery | "We apologize for any inconvenience caused. Your concern has been escalated." | "Sorry, Priya, 50 minutes is too long for a burger. I've refunded the delivery fee, and it'll show in 3 to 5 days. Sam" |
| Price rise question | "Please be advised that prices are subject to change." | "Yes, the monthly plan goes up to £9 on 1 November. Your price stays at £7 until your renewal on 3 December." |
| Praise | "Thank you for your valuable feedback!" | "This made our morning. Telling the kitchen right now." |
| A customer's joke ("your croissants ruined my diet") | "We are pleased that you enjoyed our products." | "We accept no responsibility. Also, the almond one's back Saturday." |
| Outage | "Oops, our bad! Perfect excuse to touch grass." | "The app's down for payments right now. Cards still work in store. Next update here at 3:30." |
| Bereavement | "Dear valued customer, kindly submit the required documentation." | "I'm very sorry about your father. You can close his account by post or at any branch. I've sent you the one form you need." |

## 10. The lint candidates and how they were tested

`casual-craft-en.json` holds 179 candidates:
- 26 words, 2 phrases, 133 regexes, 7 structures and 11 metrics;
- 1 error (confirmshaming), 89 warnings, 89 notes;
- false-positive risk: 99 low, 76 medium, 4 high.

Groups:
- purple structures and 37 purple words;
- Latinate and corporate words;
- customer-service boilerplate and apology forms;
- casual gone wrong: over-familiar greetings and address terms, slang, text-speak, cheap puns, confirmshaming,
  clingy win-backs, creepy data jokes, solemn-plus-sell, jokes on bad news, aggressive humour, rhetorical openers;
- the measured 2026 templates;
- metrics;
- ear checks (scope: spoken).

Conventions:
- Regexes are Python and run with re.IGNORECASE.
- Purple words match in lower case, or capitalised only at the start of a sentence, so names and titles pass
  (Enigma, Radiant Black, The Odyssey, Allure).
- The "At [Brand], we believe" regex is case-sensitive.
- 22 candidates apply only to replies, safety text, spoken copy, text-to-speech or a whole thread; their `why` ends
  with the scope.

Tests, all on 24 September 2026. The harness is `casual-src/build_casual.py`: run as is, it prints the report; with
its write flag it also rebuilds the JSON.

| Set | Current `copylint` | New candidates |
|---|---|---|
| 40 natural casual lines (§11) | 0 flagged | 0 flagged |
| 40 robotic, purple or forced-casual lines (§11) | 3 flagged (one hype verb, two only for "!") | 40 flagged |
| 72 captions from a 2026 model (§7) | 0 flagged | 54 flagged: 50 by template notes, 6 by other candidates (2 by both) |
| 1,658 brand posts (Bluesky) | 179 with an error or warning, mostly em dashes (58) and spaced hyphens (52) | 51 posts (3.1%) by word, phrase and structure candidates; 38 (2.3%) by template notes; 89 (5.4%) by either; 298 (18%) once the readability metrics are counted |

The brand-post hits that are false positives shaped the final patterns:
- "U.S." was being read as text-speak "u";
- "Prom Queen" and "big sis" were read as address terms, so that check is now vocative only;
- "Endeavor" (a name) and game titles ("Ignite") matched purple words, so those now match only in lower case;
- "make decisions" matched as a hidden verb; bare "make decisions" is everyday English and now passes;
- "No problem! Glad we could help" tripped the failure-plus-"!" check.

Brand-post hits that remain are real usage worth a second look: PlayStation's iconic, Netflix's is-HERE trailer
posts, Patagonia's magical and its explore-the-book links. Those candidates are notes with medium or high
false-positive risk.

## 11. Calibration lines

Written for this study in the target styles. None quotes a brand.

Natural (40):
1. We open at 7. The first batch of croissants is usually gone by 8.
2. Your parcel's at the depot. It'll be with you tomorrow before noon.
3. Honestly? The small one's enough for two.
4. We got the date wrong in yesterday's email. The sale ends Sunday, not Saturday. Sorry about that.
5. It rained all week, so we made more soup. Tomato and lentil today.
6. New sizes are in, 8 to 22, same price as before.
7. Card declined? Check the expiry date first. It's usually that.
8. Yes, you can bring your dog. The water bowl's by the door.
9. The app's down for about 20 minutes. Payments still work in the shop.
10. And yes, the blue one's back.
11. We tried making it healthier. Nobody liked it, so the original stays.
12. Parking's free after 6 on weekdays.
13. Booked out Friday and Saturday. Thursday's wide open.
14. Two coats, four hours apart. That's the whole trick.
15. If it doesn't fit, send it back. Returns are free for 30 days.
16. You asked for a smaller bag. This one's 30 cm wide and still fits a laptop.
17. Our phones go quiet after 9 pm, but the chat stays open.
18. Fair point. We'll fix the label on the next batch.
19. Sold out in two hours. We're baking more for Saturday.
20. Leave it in the fridge overnight. It tastes better the next day, promise.
21. The price goes up on 1 October. Anything you order before then stays at £12.
22. We're closed Monday for a staff day out. Back Tuesday at 8.
23. Nothing fancy. Good bread and a window seat if you're early.
24. Grandma's recipe, minus the three hours of stirring.
25. Okay, the new menu's longer than we planned. Start with the dumplings.
26. Pay monthly, cancel whenever. There's no fee for leaving.
27. It's heavier than it looks. You'll want two people to carry it.
28. We messed up your order. A new one's on the way, and this one's on us.
29. Size up if you're between sizes. The cotton's a bit stiff for the first week.
30. Still deciding? The sample pack has all six.
31. Rain tomorrow, so the market moves indoors. Same stalls, hall B.
32. We don't do refills yet. Maybe next year.
33. You'll get a text when the rider's 5 minutes away.
34. Night owls, the kitchen now closes at 1 am.
35. Your refund of $48.20 went out today. Most banks show it within 3 working days.
36. Lost your card? Freeze it in the app first. It takes two taps.
37. We moved the 6 pm spin class to studio 2. Same instructor, more bikes.
38. The new export button is top right. It does CSV and PDF.
39. We're a small team, so replies can take a day. We read every one.
40. Cheaper than a taxi, and you get to pick the music.

Robotic, AI-sounding or purple (40):
1. Indulge in a symphony of flavours that dance across your palate.
2. Discover the timeless elegance of our handcrafted collection.
3. Let the essence of summer whisper through every sip.
4. Step into a sanctuary where time slows down and the soul finds solace.
5. Our captivating new fragrance embraces you in an ethereal glow.
6. Experience the enchanting allure of true Italian craftsmanship.
7. Each bite is a celebration of heritage, passion and artistry.
8. Awaken your senses with our exquisite, velvety house roast.
9. A kaleidoscope of colours awaits you this festive season.
10. Immerse yourself in an unforgettable culinary journey.
11. Where every thread tells a tale of timeless craftsmanship.
12. Kissed by golden sunlight, our terrace is a haven of tranquility.
13. We are pleased to inform you that your request has been received and will be processed shortly.
14. Kindly be advised that the store will remain closed until further notice.
15. Customers are required to present a valid receipt in order to obtain a refund.
16. Please do not hesitate to contact us should you require any further assistance.
17. Utilize our app to facilitate a more efficient ordering process.
18. Prior to commencing your subscription, please review the terms and conditions.
19. At this point in time, we are unable to fulfil your order due to the fact that the item is unavailable.
20. Our team conducted a thorough review and made the decision to implement changes going forward.
21. We apologize for any inconvenience this may have caused.
22. Your satisfaction is our top priority.
23. Mistakes were made, and we are committed to ensuring it does not happen again.
24. Thank you for reaching out. We understand your frustration and will look into it.
25. Please note that delivery times may vary on a daily basis.
26. We take the security of your data very seriously.
27. Hey bestie, this deal is lowkey giving main character energy.
28. No cap, our new burger slaps fr fr.
29. Hello lovelies! Treat yo self, queen, you've earned it!
30. We see you ordered pizza four times this week. Who hurt you?
31. We miss you! It's been 12 days since your last order. Don't leave us hanging.
32. No thanks, I don't like saving money.
33. Happy Monday, fam! Hope you're having an amazing week!
34. This deal is eggcellent, no yolk. Pun intended.
35. Ready to transform the way you shop? Your perfect wardrobe awaits.
36. Did you know? Our beans are thoughtfully sourced from the finest farms.
37. Picture this: a cosy evening, a warm drink and pure bliss.
38. It's time to reimagine your morning ritual.
39. Our thoughts are with everyone affected by the floods. Use code STAYSTRONG for 15% off.
40. Oops, our bad! The app is down again, but hey, perfect excuse to touch grass.

## Sources (all read 24 September 2026)

Guides:
- Mailchimp Content Style Guide: Voice and Tone; Grammar and Mechanics; Writing for Social Media
  (styleguide.mailchimp.com).
- Nielsen Norman Group: Kate Moran, "The Four Dimensions of Tone of Voice" (2016) and "The Impact of Tone of Voice on
  Users' Brand Perception" (2016); Hoa Loranger, "Plain Language Is for Everyone, Even Experts" (2017).
- GOV.UK: A to Z style guide (words to avoid, contractions, numbers); "Use clear language"; "Use the right tone"
  (guidance.publishing.service.gov.uk).
- digital.gov plain language guides: Writing for understanding; Clear and short; Style.
- Plain English Campaign, "How to write in plain English" (PDF); its "AI v human" page.
- Microsoft Writing Style Guide, "Use contractions" (learn.microsoft.com).
- Monzo writing principles (monzo.com/tone-of-voice).
- Duolingo brand guidelines: Writing, Voice and Tone (design.duolingo.com, Internet Archive capture, 2025).
- Intercom: Jack Jenkins, "The PREACH framework for customer support tone" (2020); Orla Tuite, "Embracing a human
  tone in customer support" (2017).
- 37signals, Getting Real: "Copywriting is interface design", "Personify your product".
- Paul Graham, "Write Like You Talk" (2015).
- Amazon Alexa Design Guide, "Be relatable" (Internet Archive capture).
- ElevenLabs documentation, text normalisation.
- Hemingway Editor help, readability.
- Wikipedia: "Flesch-Kincaid readability tests", "Words per minute", "Purple prose", "Digital blackface", "Full stop"
  (text messages), "Steve Buscemi".
- deceptive.design, "Confirmshaming".

Brands and cases:
- 26.org.uk interview with Dan Germain (Innocent, 2009); eatbigfish interview with John Schoolcraft (Oatly, 2016).
- Rival IQ, "Wendy's social media strategy" (2022).
- PR Daily, Liquid Death (4 October 2023).
- Skift, "From Tanks to TikTok: Inside Ryanair's cheeky marketing strategy" (18 October 2025).
- BBC, Netflix's A Christmas Prince tweet (13 December 2017).
- Moneycontrol, Zomato's cheeky notifications (13 November 2024); afaqs, Zomato revises its notification strategy
  (7 January 2026); Business Today, Zomato on the '₹370 biryani' notification (11 June 2026).
- Social Samosa, Swiggy Holi ad (9 March 2023).
- Fast Company, Duolingo deletes its TikTok videos (20 May 2025); PRWeek, Duolingo deletes an Amber Heard joke (May
  2022).
- USA Today and Adweek, Burger King UK (8 March 2021).
- TIME and Adweek, DiGiorno #WhyIStayed (September 2014).
- The Daily Beast, Inverse and WYFF4, Wendy's Pepe meme (January 2017).
- USA Today, SpaghettiOs Pearl Harbor tweet (7 December 2013).
- Modern Retail, "Why brands can't stop acting like reply guys" (14 April 2026).
- Sprout Social, social media customer service statistics (2026).
- CivicScience, "Does Gen Z-coded marketing actually work?" (31 March 2026).
- The Harris Poll, "Podcast advertising: what makes it work" (QuestDIY survey).

Research:
- Reinhart et al., "Do LLMs write like humans? Variation in grammatical and rhetorical styles", PNAS 2025 (arXiv
  2410.16107).
- Barcelos, Dantas and Sénécal, "Watch your tone", Journal of Interactive Marketing 2018.
- Gretry, Horváth, Belei and van Riel, "Don't pretend to be my friend!", Journal of Business Research 2017 (title
  only; the publisher blocked access).
- Béal and Grégoire, "How do observers react to companies' humorous responses to online public complaints?", Journal
  of Service Research 2021.
- Verheijen and Liebrecht, emoji in company responses to online complaints, International Journal of Business
  Communication 2025.
- Li, Chan and Kim, "Service with emoticons", Journal of Consumer Research 2019.
- Kelleher, "Conversational voice, communicated commitment, and public relations outcomes", Journal of Communication
  2009.
- Ginns, Martin and Marsh, "Designing instructional text in a conversational style: a meta-analysis", Educational
  Psychology Review 2013.
- Gunraj et al., "Texting insincerely", Computers in Human Behavior 2016 (via Wikipedia).

Data:
- antislop-sampler slop lists (sam-paech, 2025-04-07 copies in `../research/`).
- Public Bluesky posts from netflix.com, patagonia.com, xbox.com, playstation.com, crunchyroll.com, substack.com,
  bsky.app, tumblr.com and kickstarter.com (`casual-src/bsky_brand_corpus.json`).
- 72 model captions (`casual-src/gen/`).
