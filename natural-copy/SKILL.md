---
name: natural-copy
description: "Writes, rewrites and checks any text an audience reads or hears (social posts, captions, ad copy, banner and poster lines, product descriptions, website and app text, emails, WhatsApp and SMS, reel and video scripts, comment replies) so it sounds like a real person from that audience wrote it: casual, easy everyday words, the way people talk to friends and the brands they like talk online. No AI tone, templates or cliches; no bookish, poetic, old, sadhu or stiff 'shuddho' style; no translation feel. Bangla and Banglish for Bangladesh first-class, plus English and 18 more languages. Use it whenever you write or fix copy for a brand, a client or the user's own posts, in any language, Banglish asks included ('caption likhe dao', 'post likho', 'ad copy banao', 'reply dao'). It learns the audience's own words first, picks the register, writes, then checks with copylint and a native-reader copyjudge. Pairs with codex-design for text on graphics."
allowed-tools: Bash(python3 ~/.claude/skills/codex-design/scripts/design.py:*), Read, Write, Edit
---

# Natural copy

Every word an audience reads or hears should sound like a person from that audience wrote it for them today: casual,
simple, specific, in their own words. Not a chatbot, a textbook, a poem, a government notice or a translation.

Why it decides whether a project works:
- Readers who *suspect* copy is AI trust it about half as much and are less willing to buy, whatever its real origin
  (Raptive 2025, 3,000 adults: trust down 48 %, purchase consideration down 14 %). Recognition, not quality, triggers
  the penalty.
- The penalty is largest on emotional and personal messages: thanks, apologies, greetings, replies (Kirk and Givi
  2025, seven experiments).
- Platforms show templated, generic copy less: LinkedIn names "it's not X, it's Y" as a pattern it demotes (May
  2026); Meta, YouTube, Google and Reddit demote unoriginal, mass-produced content.
- In Bangladesh, readers call AI Bangla "mechanical" (a Dhaka University Bangla professor, The Daily Star, Feb 2026),
  and staged AI "ordinary people" flooded the 2026 election: fake voices now cost trust fast.

The evidence and the numbers are in `~/.claude/skills/codex-design/references/research/voice-*.md`.

## 0. The five-second test (every line)

1. Would someone from this audience say it this way to a friend, or to a shopkeeper they like?
2. Could any other brand post it unchanged? Then it says nothing yet.
3. Is there one thing the reader could check, taste, count or find: a time, a place, a price, a name, the annoying
   part everyone knows?
4. Does it survive being read aloud in one breath per idea?
5. Is it free of every tell in §4 (the lint finds most of them)?

## 1. Before writing: learn how the audience talks (10 minutes)

1. **One reader.** Who exactly, where they meet it (platform, placement, moment), what they should do or feel after
   three seconds, what they already believe or complain about.
2. **Their own words.** Read 20 to 50 real comments, reviews, questions and replies from the client's page, a
   competitor's page, Facebook groups, Google Maps, Daraz or Amazon reviews, YouTube comments. Note:
   - the phrases they repeat, the slang they really use (and how often: usually rarely), the English words they mix
     in and in which script;
   - their complaints, jokes, worries and the words they use for the product;
   - how they address each other and the brand.
   Build the copy from those words. Never copy a person's post, and never invent a quote, a review or a customer.
3. **The brand.** `brand/brand.json` voice (its avoid and prefer lists), the posts that did well, what the brand must
   never say.
4. **The market.** Language and locale, script, address form, digits, currency, calendar. The market is the
   client's audience, never the requester's language or location (global by default).
5. **The facts.** Only the client's facts: prices, dates, places, results. Placeholders are visible and listed.

## 2. Pick the register (one per piece)

| Rung | Sounds like | Use for |
|---|---|---|
| Friend-chat | a regular chatting in the comments: fragments, slang the audience really uses, emoji | youth brands' posts; replies to someone who wrote that way first |
| Casual | a friendly shop owner: contractions (English), everyday words, one light joke, "you" | most social posts, ads, captions (the default) |
| Neutral-warm | a good nurse or bank adviser: plain words, facts first, no jokes or emoji, one sorry if at fault | money, health, service, bad news, luxury |
| Formal | a clear notice: full forms, "must", "do not", still plain words | legal terms, safety, dosage, official notices |

Rules: stakes set the rung, not the channel; bad news never climbs (no jokes, no "!"); an unfamiliar brand starts
one rung lower; match the person you reply to, one rung calmer; festivals one rung warmer; tragedy formal and quiet,
with the schedule paused. Bangladesh has its own ladder (তুই only in quoted dialogue, তুমি for youth, আপনি-warm
by default, আপনি-formal for alerts): `references/bangla.md` §2.

## 3. Write the way people talk

- **Talk to one person.** "You" for the reader, "we" or "I" only for real people who did the thing.
- **Everyday words.** use, not utilise; buy, not purchase; help, not assist; কিনুন, not ক্রয় করুন; এটা, not এটি.
  Swap lists: `references/voice.md` §3 and `references/bangla.md` §5.
- **Verbs, not nouns; active, not passive,** above all in bad news ("We sent it to the wrong depot", never "mistakes
  were made").
- **Spoken forms.** English contractions (we're, it's) except in safety and payment lines. Bangla চলিত as spoken:
  গেছে, কোনো, আর and ও more than এবং, the emphatic -ই (আজই, ঘরে বসেই) and -ও (আপনিও) rather than piles of
  particles.
- **Rhythm.** Mix a four-word line with a twenty-word one; start with And, But or So now and then. One fragment can
  land; a run of them is a formula.
- **Specific details a friend would mention.** The queue, the rain, the price, "window seats go first", load-shedding,
  traffic, exam week, salary day.
- **Real questions** people can answer ("Oat or whole milk?"), never rhetorical openers ("Ready to transform your
  mornings?").
- **Seasoning, one at a time, only where it does real work.** One reaction (Honestly? উফ,) before something true,
  one particle (তো, কিন্তু), one slang word the audience really uses, one joke, one emoji idea. Laugh with people,
  never at them; no jokes on bad news, grief or money trouble.
- **More human does not mean more slang.** Never add slang, particles, emoji, typos, feelings or a first-person
  experience to make a line sound human: experts still spot the AI shape underneath, and a rewrite that does this
  leaves its own fingerprint. Keep only the voice the brief or the brand gives.
- **Honest and a little self-aware.** Admit the limit ("We don't do refills yet"), name the friction ("It's heavier
  than it looks"). Copy with only praise reads fake.
- **Hook first, one idea, one call to action** that says the action and the thing ("Book a table", "অর্ডার করুন").
- **Write positively.** Say what to do ("Bring the receipt and we'll refund you"), not what fails.

## 4. Never

The lint catches most of these; the full lists, with sources, are in `codex-design/references/copy.md` §2 and §3 and
in `scripts/voice_rules.json` (932 tested rules in 24 languages).
- **AI structures:** "not X, it's Y" in all its forms ("It's not about X, it's about Y", "The problem isn't X. It's
  Y.", "X isn't the problem. Y is.", "No X, no Y, just Z", "doesn't just A, it Bs", ", not X" tails); "more than
  a X"; "Whether you're X or Y"; a question the copy answers itself ("The result?"); rule of three; "In today's
  fast-paced world"; inflated significance; trailing "-ing" clauses ("..., highlighting our commitment"); a roadmap
  line ("In this post, we'll..."); a closer that restates the point ("In short,"); stakes escalation; a stack of
  launch templates ("is here", "Meet our", "Discover our", an object that "noticed"); colon reveals piling up where
  the em dash used to be.
- **2026 social formulas:** "Meet X, your new favorite", "Think X meets Y", "Thank me later", a bare "Save this for
  later.", "*chef's kiss*", "(yes, really)", "Pro tip:" and "Real talk:" labels, a closing "What do you think?" that
  fits any post, "so this one hits" in a reply.
- **AI vocabulary:** delve, tapestry, testament, elevate, unlock, seamless, vibrant, curated, journey, camaraderie,
  palpable and the rest, in every form (delved, leveraging).
- **Purple and poetic lines:** "a symphony of flavours", "whispers of vanilla", "timeless elegance", "a sanctuary";
  in Bangla স্বপ্নের ডানায়, হৃদয়ের গভীর থেকে, and two or more praise words in a line (অপরূপ, মনোমুগ্ধকর,
  অনবদ্য...). Test: could a reader check, taste or count it?
- **Bookish, notice, sadhu or stiff "shuddho" register:** ক্রয় করুন, প্রদান, গ্রহণ করুন, পরিলক্ষিত হয়, করিয়াছি,
  উপসংহারে বলা যায়; English "please be advised", "prior to", "in order to".
- **Translation feel:** calques (অন্বেষণ করুন, নতুন উচ্চতায়, "Sumérgete"), English word order, আপনি in every slot,
  English punctuation in Bengali.
- **Fake casual:** a pile of slang, borrowed dialect, dated slang, memes you have not read, "hey bestie",
  over-familiar win-backs, confirmshaming, Dhaka phonetic spellings (করতেসি) in brand copy, rizz or bruh inside
  Bengali.
- **Punctuation tics:** the em dash (never, in any language), emoji bullets, arrows, more than one "!", 𝗯𝗼𝗹𝗱 Unicode
  letters, a colon reveal in a headline.
- **Anything fake:** see §8.

## 5. By format

| Format | What changes |
|---|---|
| Caption | the hook in the first line (before the platform's "more"), short lines, 0 to 3 hashtags, emoji within the platform's range, a real question or none |
| Ad | one benefit, the proof, the price or date as a fact, one CTA; urgency only with a real date or count |
| Banner, poster, thumbnail line | 2 to 8 words, the CTA 2 to 4 words (6 in Bengali): design it with codex-design |
| Product description | what it is, who it suits, the specs people ask about, the honest limit; no "elevate your" |
| Website and app text | plain labels, the verb on the button, errors that say what to do |
| Email | a subject a friend could send, the preheader as the second line, one ask |
| WhatsApp and SMS | like a message from a person: short, the fact, the link or code, no hashtags; Bengali SMS is 70 characters a part |
| Reel, ad read, explainer script | for the ear: one idea per breath (8 to 14 words), numbers as people say them, no brackets, symbols or links, the brand and the ask said twice; about 2.5 words a second (`references/voice.md` §7) |
| Replies and DMs | answer first in their words, their name, what happens next and by when, one owned apology, no emoji on complaints, never the same reply three times (`references/voice.md` §8) |
| Blog, newsletter, long post | start with the point, no roadmap line, real examples, end on the last new fact, not a restated conclusion |
| Festival and solemn days | follow `codex-design/references/occasions.md`: no selling on solemn days, no jokes on tragedy |

## 6. Languages

- **Bangla and Banglish for Bangladesh:** `references/bangla.md`, measured on 724 brand texts and 3,322 human and
  ChatGPT passage pairs; base lists in `codex-design/references/copy.md` §3.
- **English:** `references/voice.md`.
- **Hindi, Urdu, Nepali, Arabic, Turkish, Spanish, Portuguese, French, German, Indonesian, Malay, Filipino, Chinese,
  Japanese, Korean, Thai, Vietnamese, Tamil:** `references/languages.md`.
- Transcreate, never translate: start from the brief, write in the target market's social register, check its address
  form, digits and punctuation. A native reader signs off every language you cannot read yourself.

## 7. Check it (the loop)

```bash
python3 ~/.claude/skills/codex-design/scripts/design.py copylint --caption post.txt --platform facebook --locale BD
python3 ~/.claude/skills/codex-design/scripts/design.py copylint --text "অর্ডার করুন" --role cta --locale BD
python3 ~/.claude/skills/codex-design/scripts/design.py copylint --caption script.txt --role voiceover --lang en
python3 ~/.claude/skills/codex-design/scripts/design.py copylint --text "¿Listo para probarlo?" --lang es
python3 ~/.claude/skills/codex-design/scripts/design.py copyjudge --caption post.txt --brief brief.md --locale BD --goal order --runs 3
```

1. `copylint` (offline): fix every error and warning; read the notes and keep a noted word only when it is literally
   true. `--platform` also takes whatsapp, email, web, sms and voiceover; `--role` takes headline, cta, caption, body,
   reply, script, voiceover and alt; `--lang` picks the language's rules (the script, then a Latin line's small
   words, pick them when there is no tag), and its region (`zh-TW`, `pt-PT`) or `--locale` adds that market's rules.
   `--brand` leaves the brand's `keep` lines alone.
2. **Read it aloud** as the reader. If you would not say it across a counter, rewrite it.
3. `copyjudge` (a fresh native-reader session): PASS at least; PASS_NATIVE with `--runs 3` for client work. It scores
   fidelity to the brief first, so an invented detail costs the line. Its rewrites come back linted
   (`rewrite_lint`): use none that carries a finding. Take a rewrite only after checking disputed local words against
   a local source, and test it: delete each word it added (does anything go?), revert each word it replaced (was the
   old one already right?).
   Never pass copy through a third-party humanizer tool: they strip hyphens, break ranges and invent facts.
4. For a series, `design.py ledger` keeps hooks and templates from repeating (the same template in 3 of the last 12
   posts is a machine sign).

## 8. Natural is not fake (non-negotiable)

- **No invented people or proof:** no made-up customers, reviews, testimonials, quotes, ratings, follower counts, vox
  pops or "ordinary people", no default names (Emily, Sarah). Fake reviews and testimonials are illegal (US FTC rule,
  2024; UK DMCC Act, 2025).
- **No AI personas presented as real** staff, experts or customers; no astroturfing or planted "honest opinions".
- **Disclose where the law or the platform requires it:** realistic AI images, video and voice on Meta, TikTok and
  YouTube; AI-generated public-interest text in the EU without human editorial responsibility (AI Act Article 50,
  from 2 August 2026).
- **No fake imperfection:** never plant typos or staged "rawness" to seem human. Write for readers, not detectors.
- **A human owns the personal messages:** thanks, apologies, condolences and greetings are written or rewritten by the
  person who signs them.
- **Do not lead with "AI"** in consumer copy ("AI-powered"): it lowers trust and purchase intent, most in finance,
  health and costly products (WSU 2024). Say what it does.

## 9. References

- `references/voice.md`: the craft in English and across languages: the guides, the moves with before and after, the
  register ladder by brand type, what casual is not, purple prose and plain swaps, 2026 model templates, writing for
  the ear, replies and community posts, measurable signals.
- `references/bangla.md`: Bangla and Banglish for Bangladesh: how brands really write, the register ladder, particles
  and emphasis, the calibrated poetic list, stock AI Bangla phrases, measured AI habits, new formal to everyday swaps,
  sadhu forms, Dhaka speech and slang, Banglish, spelling slips, what readers say.
- `references/languages.md`: 18 more languages: register, address, code-mixing, swaps and AI tells for each.
- `~/.claude/skills/codex-design/references/copy.md`: the lint's lists, hooks, calls to action, captions and platform
  limits, the copy loop, brand voice in brand.json.
- `~/.claude/skills/codex-design/references/research/voice-*.md` and `copy-*.md`: the research, with every source
  (`voice-humanizer-skills.md` reads 89 humanizer and anti-slop projects and where they disagree).
