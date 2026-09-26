# R6: Email and outbound copywriting, 2024 to 2026

Research pass: 2026-09-26. Covers newsletters, promotional and lifecycle email, cold B2B outbound, freelance proposals and LinkedIn. Tags like [S12] point to the source list at the end (publisher, title, URL, date). "Vendor" marks data a tool company reports about its own users: read it as direction, not law. "Unverified" marks claims not confirmed in this pass. All templates are ours.

## 0. The short version

1. Opens are unreliable since Apple's Mail Privacy Protection (Apple is 62% of tracked opens): judge copy by clicks, replies, orders and revenue per recipient [S8][S9].
2. Deliverability is rule-based: authentication for bulk senders at Gmail, Yahoo and Microsoft, Gmail rejections since November 2025, complaints under 0.3% (target 0.1%) [S1][S2][S4][S5].
3. Automated lifecycle email earns far more per send than campaigns [S14][S16].
4. Cold email that works is short, about the reader's problem, ends with an interest question and runs about three emails in total [S27][S33][S34].
5. Buyers punish sales-heavy and AI-sounding copy [S27]. On Upwork the first two lines, speed and job choice matter most, and the message that wins a reply is not the one that wins the hire [S59][S61][S62].

## 1. Reading the numbers correctly

**Apple Mail Privacy Protection (MPP).** Apple announced MPP on June 7, 2021 for iOS 15 and macOS Monterey. It stops senders from learning whether and when an email was opened and hides the reader's IP address [S8]. Apple clients now make up 62.26% of opens in Litmus data, Gmail 27.03%, Outlook 5.83% (July 2026, 1 billion+ opens) [S9]. Campaign Monitor reported a 21.5% average open rate for 2021 and saw the jump right after iOS 15 shipped on September 20, 2021 [S10]; MailerLite's 2025 median is 43.46% [S12]. Most of that rise is measurement, not better subject lines.

**Different denominators.** Cold email reply rates are counted per contact by some vendors and per email sent by others. Belkins reports 0.45% replies per email sent across 7.5 million emails in 2025 [S30]; Instantly reports a 3.43% campaign average [S29]; Hunter reports 4.5% [S27]. Never compare across vendors without checking the denominator.

| Source (data period) | Open | Click | Notes |
|---|---|---|---|
| Mailchimp (updated Dec 2023) [S11] | 35.63% | 2.62% | unsubscribe 0.22% |
| MailerLite (Dec 2024 to Nov 2025, 3.6M campaigns, medians) [S12] | 43.46% | 2.09% | click-to-open 6.81%, unsubscribe 0.22% (0.08% a year earlier) |
| Klaviyo campaigns (2026 report, 205k+ B2C brands) [S14] | 31% | 1.69% | placed order 0.16% |
| Klaviyo flows (same report) [S14] | 32.2% | 5.58% | placed order 2.11% |
| Omnisend (2025, 150k brands, 27B emails) [S16] | 30.7% | n/a | fifth straight year of rising opens |
| HubSpot compilation (Nov 2025) [S13] | 42.35% | 2.3% | compiled from other vendors, not HubSpot data |

MailerLite links its more than doubled unsubscribe rate to Gmail letting people unsubscribe without opening [S12]. For cold email, Hunter puts average opens at 30%, unsubscribes at 1.6% and bounces at 3.6% [S27].

What to measure instead: clicks and click-to-open for newsletters, placed order rate and revenue per recipient for ecommerce, positive replies and meetings per 100 contacts for outbound, and "human opens" where the platform filters machine opens, as Attentive recommends [S18].

## 2. Subject lines, preview text, sender, timing

**Length.** Attentive analysed 91 billion+ subject lines (July 2026): under 25 characters won opens and clicks for campaigns, while 25 to 35 won for triggered emails and for conversions [S18]. MailerLite compared its 10,000 best and 10,000 worst campaigns: top ones were 45% more likely to use 20 to 40 characters, bottom ones 27% more likely to run past 40 [S19]. Cold email differs: Hunter found 5 to 6 words gave the best reply rates [S27], Belkins found 2 to 4 words gave the best opens [S32], Boomerang (2016) found 3 to 4 words got the most responses [S38], and Jason Bay teaches 1 to 3 [S45].

**Personalization.** Attentive: personalization in campaign subject lines showed no meaningful lift, while in triggered emails it helped, especially with past buyers (13%+) [S18]. Hunter (cold): one custom attribute in the subject gave a 35.4% open rate, two gave 40.2%; two attributes in the body gave 5.6% replies against 3.6% with none [S27]. Personalization that proves relevance works; a name token alone does little.

**Emoji.** Attentive found emojis hurt triggered emails and did not win on revenue in campaigns [S18]. Hunter found no meaningful effect on cold reply rates [S27]. MailerLite's top campaigns were 21% more likely to include one, which is correlation only [S19]. The often repeated "emoji lifts opens by 56%" claims trace to old, unverified studies.

**Words.** Gong says buzzwords and numbers in cold subject lines cut opens by up to 17.9% [S33]. Hunter found "Quick question" subjects underperform: 2.5% replies and 28.7% opens vs 2.9% and 32.9% for others [S27]. Belkins (vendor) rates question subjects among the best openers [S32]: questions are fine, stale formulas are not.

**Preview text.** Clients show between 0 and about 278 characters. Litmus advises under 90 and warns that without preview text the client pulls the first text it finds, often "View in browser" [S21]. Attentive's best Cyber Week 2025 pairing was a subject under 25 characters with a 35 to 50 character preheader [S18]. Top MailerLite campaigns were 22.58% more likely to set a custom preheader [S19].

**Sender name.** A MailerLite A/B test found "person @ brand" beat the brand name alone by 3.81% in opens [S19].

**Send time.** MailerLite's 2.1 million campaigns (Dec 2024 to Nov 2025): opens peak 9 to 11 AM, clicks 8 to 9 PM, and only Friday 6 PM aligns both [S20]. For cold email, Hunter found no meaningful day-of-week effect [S27], Belkins saw small differences (Wednesday and Thursday 0.48% per email, 8 AM to noon 0.54%) [S30], and Instantly moves Friday follow-ups to Monday because of auto-replies [S29]. The myth to drop: there is no universal best time. Send cold email in the recipient's local morning, test marketing sends, and put the effort into relevance.

## 3. Deliverability rules

| Mailbox | Who | Requirements | Since |
|---|---|---|---|
| Gmail [S1][S2] | All senders | SPF or DKIM, valid forward and reverse DNS, TLS, RFC 5322 format, spam rate under 0.3%, no "Re:" or "Fwd:" unless it really is one | Feb 2024 |
| Gmail [S1][S2][S3] | Bulk: close to 5,000+ a day to personal Gmail accounts; the label is permanent | SPF and DKIM, DMARC (p=none is enough) aligned with the From domain, one-click unsubscribe (RFC 8058) plus a visible link on marketing mail, removal within 48 hours, spam rate ideally under 0.1% and never 0.3% | Feb 2024; no mitigation above 0.3% from June 2024; temporary and permanent rejections from Nov 2025 |
| Yahoo [S4] | Bulk | SPF and DKIM, DMARC p=none that passes, one-click unsubscribe, honor within 2 days, complaints under 0.3% measured on inbox mail | Feb 2024 |
| Outlook.com, Hotmail, Live [S5] | Over 5,000 a day | SPF pass, DKIM pass, DMARC at least p=none aligned with SPF or DKIM; failures rejected with "550 5.7.515" | May 5, 2025 |

Microsoft first said failing mail would go to Junk, then switched to outright rejection just before enforcement. It also recommends working From or Reply-To addresses, visible unsubscribe links and list hygiene [S5].

**Spam words: myth vs reality.** Gmail's list of reasons mail lands in spam (spoofing, phishing, unverified senders, mail after an unsubscribe, empty messages, similarity to reported spam) names no trigger words [S6]. Mailchimp's filter guide stresses reputation and clean code and tells you to avoid link shorteners; it offers no word list [S7]. Our reading: filters score who you are (authentication, reputation), how people react (complaints, replies, deletes) and patterns (deceptive subjects, shortened or mismatched links, broken HTML). One "free" does not sink a good sender; a pushy tone raises complaints, and complaints do. Long "spam word" lists are folklore.

**Plain text vs HTML.** HubSpot's 2014 A/B tests across more than half a billion marketing emails found plain text won every test and even one image lowered clicks, although nearly two thirds of surveyed professionals said they preferred HTML [S22]. Old data, but it matches current cold email practice; newsletters and promos can use light HTML, image-only layouts are a risk.

**Links, tracking, domains.** MailerLite: emails with 2 to 5 links had the best open rate (34.17%), 20+ links the worst (29.9%) [S19]. Hunter: cold campaigns without open tracking replied at 7.4% vs 4.4% with it, and custom domains replied at 5.2% vs 2.5% for free webmail [S27]. Alex Berman keeps links out of the cold email body entirely [S48]. Rule for cold: no link in the first touch, at most one later, no images, no attachments, tracking off.

**Accessibility.** The Email Markup Consortium tested 443,585 emails (May 2024 to May 2025): 99.89% had serious or critical issues; 96.67% lacked a language declaration, 72.04% had links without readable text, 59.37% had low contrast and 51.42% missed alt text [S23]. Buttons should be at least 24 by 24 CSS pixels (WCAG 2.2 AA), ideally 44 by 44 (AAA) [S24][S25].

**AI in the inbox.** On January 8, 2026 Google announced Gemini features for Gmail: AI Overviews that summarise threads (free for all users) and an AI Inbox, in testing, that picks VIPs from people you email often, your contacts and relationships inferred from message content [S26]. Our inference: the first two sentences must carry the point because a summary may be all the reader sees, "just bumping this" follow-ups look empty in a summarised thread, and strangers start outside the VIP set.

## 4. Lifecycle emails: data and templates

Automation earns more per send. Klaviyo: flows produced about 41% of email revenue from 5.3% of sends [S14]. Omnisend: automations were 2% of sends but 30% of email revenue, $2.87 per send vs $0.18, and cart plus welcome flows drove 76% of automation orders [S16].

**Abandoned cart.** Klaviyo's review of 143,000+ cart flows (2023 data): 50.5% open, 6.25% click, 3.33% placed order and $3.65 revenue per recipient, the highest of any flow (welcome $2.65, browse abandonment $1.07). It suggests a first email 2 to 4 hours after abandonment, a second at 24 hours and a third at 48 hours, and warns that routine discounts train shoppers to wait [S15]. Baymard puts average cart abandonment at 70.22% across 50 studies; top reasons are extra costs (40%), slow delivery (20%) and not trusting the site with card details (19%) [S66]. Good cart copy answers those three.

**Welcome.** GetResponse measured 83.63% opens and 16.6% clicks for welcome emails (2023 data) [S17]. Opens are inflated, but welcome is still the most read email a brand sends.

Templates. Brackets are inputs from the brief; never invent them.

**Welcome (60 to 120 words)**
```text
Subject: Your [brand] code is inside
Preview: Plus the product most people start with

Hi [first name],
Thanks for joining. Your code is [CODE]: [x]% off anything until [date].
Not sure where to start? Most first orders include [bestseller], because [reason in customers' own words, from reviews].
[Button: Shop [bestseller]]
Got a question? Just reply. [Name] on our team reads every reply.
```

**Onboarding (one action per email, 50 to 100 words each).** Day 0, "Step 1: connect [tool]": why it matters, one button, what happens next. Day 2, only if step 1 is still open, "Stuck on [step]?" with the two most common fixes. Day 5: a similar customer's first result and the next step. Stop once the user acts.

**Abandoned cart (3 emails)**
1. After 2 to 4 hours. Subject: Your [product] is still in your cart. Body, 40 to 70 words: item photo, price and total with shipping, one line on delivery time or returns, a "Back to my cart" button.
2. After 24 hours. Subject: Before you decide on the [product]. Body: the question buyers ask most, answered, and one short review from a real customer.
3. After 48 hours. Subject: Last reminder about your cart. Body: one line; an offer only for high-value carts if policy allows, or two alternatives.

**Win-back (2 or 3 emails, then sunset).** Trigger at about twice the normal buying or engagement cycle.
1. "Here's what changed since your last order": three concrete new things, one button.
2. "Want fewer emails?": a preference link (monthly only, chosen topics) next to unsubscribe. Lower frequency beats a spam complaint.
3. Sunset: "We'll stop emailing you on [date] unless you click here." Then suppress everyone who stayed silent. This protects the complaint rate Gmail and Yahoo police [S1][S4].

**Launch (3 emails).** Tease, 3 to 5 days before (optional): the problem and the date, no hype. Launch day: what it is, who it is for, one proof point, one CTA. Last call: the deadline in the subject, one objection answered, the CTA again.

## 5. Newsletters and promotional email

What the best newsletters do (our analysis, facts cited where available):
- One promise, kept every issue. Lenny's Newsletter calls itself a deeply researched advice column on product, growth and careers, with 1,000,000+ subscribers [S64]; each post goes deep on one question.
- A recognisable voice and a fixed skeleton. Morning Brew and The Hustle grew on a conversational, joke-friendly tone and skimmable repeated sections (observed; audience and referral-program figures unverified here).
- Reply loops: asking readers to hit reply builds engagement signals.
- Swipe files: Really Good Emails curates real brand emails by type, from welcome to re-engagement [S65]. Study layout there, never wording.

**Story-led newsletter (250 to 600 words)**
1. Hook: one specific scene, number or line of dialogue.
2. Story: 3 to 6 short paragraphs, one tension.
3. The idea: one sentence the reader could repeat to a colleague.
4. Use it: 1 to 3 bullets.
5. One CTA: "reply with X" or one link.
6. Optional P.S. for a secondary item.

If the draft carries two ideas, it is two issues.

**Promo email (80 to 200 words).** Subject: offer plus reason or deadline. Preview: who it is for. Then a headline, at most 3 bullets, one button with a verb and an outcome ("Get the bundle", never "Click here"), the deadline repeated in the last line and plain-language terms. Keep 2 to 5 links in total [S19], with descriptive link text and alt text [S23].

## 6. Cold outbound B2B

### 6.1 What the data says

| Finding | Source |
|---|---|
| 3 to 4 sentences and 100 words or fewer get the highest reply rates; pitching cuts replies by up to 57%; the average rep needs 344 cold emails per meeting (28M+ emails) | Gong, Jul 2025 [S33] |
| At the cold stage the interest CTA performs best (Gong's example: "Are you interested in learning more about X?"); a specific day-and-time ask booked meetings 15% of the time cold vs 37% inside active deals (304,174 emails) | Gong Labs, May 2020 [S34] |
| First touches of 25 to 50 words; a 3rd to 5th grade reading level gets 67% more replies; 70% of cold emails are written at 10th grade or above | Lavender, Jan and Mar 2023, vendor [S35][S36] |
| 50 to 125 words is the sweet spot; 3rd grade reading level beats college level by 36%; 1 to 3 questions make a reply 50% more likely (40M emails of all kinds) | Boomerang, Feb 2016 [S38] |
| Average reply 3.43%, top quarter 5.5%+, top tenth 10.7%+; 58% of replies come from step 1; 4 to 7 touches, 3 to 4 days apart; under 80 words; one CTA | Instantly, Jan 2026, vendor [S29] |
| Average reply 4.5% (sales outreach 3%); three messages in total is best: two follow-ups nearly double replies, three or more lower them; 21 to 50 recipients 6.2% vs 500+ 2.4%; manually edited emails 5.2% vs 4.4% fully automated | Hunter, 2026 report, 31M emails sent in 2025 [S27] |
| Referral-request follow-ups did best; unsubscribes rise after the third follow-up | Hunter, 2025 report, 11M emails sent in 2024 [S28] |
| 0.45% replies per email sent; founders 0.57%, VPs 0.32%; companies of 0 to 10 staff 0.72% vs 10,000+ 0.22%; step 3 produced 35.6% of email-sourced meetings; 3 to 5 steps is the practical range | Belkins, Jun 2026, vendor [S30][S31] |
| Problem-first framing +20% replies, social proof +41%, a compelling offer +28%; short enough to read on a phone without scrolling (85M+ emails, Gong data) | Jason Bay, 30MPC, Jul 2025 [S39] |

Where the data disagrees: Instantly says step 1 brings 58% of replies [S29], Belkins says 41.4% [S31]. Hunter found no single best length (both 61 to 80 and 181 to 200 words did well) [S27], while Lavender says 25 to 50 but cites Gong data that longer follow-ups book more meetings [S36]. Working rule: short first touch, more context in follow-ups, relevance above length. Apollo and Smartlead reports were not reviewed in this pass.

### 6.2 Practitioners and frameworks

- **Josh Braun** [S40][S41]: sell the outcome ("superpowers, not swords"), solve an expensive problem, use the prospect's words, write for one person, cut fluff and jargon, "poke the bear" with a neutral question that exposes a risk they may not see, ask a yes/no interest question instead of 30 minutes (his example: "Open to learning more?"), and detach from the outcome.
- **Becc Holland**, Flip the Script [S42][S43]: premise-first personalization. The premise is the researched reason you are writing to this person now ("why you, why now"); a transition line hooks it to relevance, the problem you solve. Best premises, in order: content they wrote, content they engaged with, traits they state about themselves; company news and persona pain are fallbacks. Rapport means adding value, not flattery. Her sequences run 16 steps over 21 business days across email, phone and LinkedIn (secondary summary).
- **Will Allred**, Lavender [S44][S37][S35]: an observation, the problem it suggests, then a question about that problem that implies you can solve it (the "Mouse Trap"). The longer form adds credibility and a "call to conversation" instead of a meeting ask.
- **Jason Bay**, Outbound Squad [S45][S39]: a trigger-based first line, the problem that trigger usually creates, social proof, and a closed interest question ("Worth a quick chat?") with a soft out; under 100 words; 1 to 3 word subjects.
- **Sam Nelson** [S46]: known mainly for cold calling; his Agoge sequence with 30MPC runs 15 touches over 27 days across email, phone, LinkedIn and video, ending with one of three breakup emails. "Show Me You Know Me" (research visible in the subject and first line, objections handled up front, no calendar link on a first touch) is Samantha McKenna's #samsales method [S47]; the brief may have meant her.
- **Alex Berman** [S48]: agency-focused; under 80 words, problem first, yes/no asks ("Would you be open to...?"), no apologies, no body links, case studies matched to the prospect's industry, 4 to 7 touches, niches few competitors email.

### 6.3 Our structure

Premise (one true, specific sentence), then the problem in their words (one sentence), then proof (one sentence, a real result for a similar client), then a soft interest question, then an optional detached out. 50 to 90 words, grade 3 to 6, plain text, no link, signature with name, company, city and postal address.

**Weak (a common pattern)**
```text
Subject: Quick question

Hi John, I hope this email finds you well. I came across your company and was really impressed by your amazing growth. [Agency] is a leading full-service agency offering cutting-edge web design, SEO and marketing solutions tailored to your unique needs. Would you be available for a 30-minute call next Tuesday or Wednesday? Looking forward to hearing from you!
```
Why it fails: stale subject [S27], filler opener, fake familiarity, pitch before problem [S33], jargon, a time ask on a cold touch [S34], and not one line that only John could receive.

**Strong (about 65 words)**
```text
Subject: [Company] mobile checkout

Hi [first name],
On my phone, the [collection] product page shows two promo banners above the add-to-cart button, so buyers scroll before they can buy.
We moved the button up for [similar store] and their mobile conversion went from [x]% to [y]% in [n] weeks.
Worth a 2-minute screen recording of what I'd change on yours?
[Name], [Agency], [City, postal address]
Not relevant? Reply "no" and I won't follow up.
```

**Follow-ups (same thread, each adds something new)**
```text
Day 3 (25 to 50 words): One more thing: PageSpeed shows the product page taking [n] seconds on mobile. I can cover that in the recording too. Want it?
Day 7 (referral ask): Is [role] the right person for site conversion at [Company], or should I talk to someone else?
Day 12 to 14 (breakup): I'll close the loop here. If mobile checkout isn't a priority this quarter, no problem. Should I check back in [month]?
```
Default: 3 to 4 emails, 3 to 4 days apart, small segments [S27][S28][S29].

## 7. Legal basics for outreach (general information, not legal advice)

**United States, CAN-SPAM** [S49]. Covers all commercial email, with no exception for B2B: honest headers, subject lines that match the content, the message identified as an ad, a valid physical postal address (street, registered PO box or registered private mailbox), a clear opt-out that works for at least 30 days after sending (a reply or a single web page, no fee, no extra data), and opt-outs honored within 10 business days. Each violating email can cost up to $53,088. A fake "Re:" breaks the deceptive-subject rule and Gmail's guidelines [S1].

**EU and UK GDPR** [S50][S51][S52]. Emailing named people processes personal data. Direct marketing can rest on legitimate interests (Recital 47) when it fits the person's reasonable expectations, so document a balancing test and target only roles the offer suits. When the address came from elsewhere, privacy information (who you are, purpose, legal basis, interest pursued, data source, rights) is due at the latest in the first message (Art. 14(3)). The right to object to direct marketing is absolute, must be flagged clearly and separately at first contact, and ends marketing use at once (Art. 21(2) to (4)). Practical form: a privacy-page link, "reply stop and I'll delete your details", and a suppression list.

**UK PECR** [S53][S54][S55][S56]. Companies, LLPs, Scottish partnerships and public bodies ("corporate subscribers") may receive unsolicited marketing email without consent; sole traders and some partnerships count as individuals and need consent or the soft opt-in. Every message must name the sender and give a valid opt-out address. The ICO updated this guidance on April 28, 2026. The Data (Use and Access) Act 2025 adds a charity soft opt-in, phased in from June 2025 to June 2026 [S56]; reports that it raised PECR fines to UK GDPR levels are unverified.

**Elsewhere (unverified).** Some EU states, Germany being the usual example, expect consent even for B2B email; Canada's CASL generally requires consent. Check the recipient's country first.

**Bangladesh.** DLA Piper (last updated January 2024) found no specific rules on electronic marketing or spam [S57]. The Cyber Security Act 2023 was replaced by the Cyber Security Ordinance 2025 in May 2025 [S58]; a standalone personal data protection ordinance was reported in progress in 2025 (unverified). In practice, a Bangladeshi agency writing abroad follows the recipient's law (CAN-SPAM, GDPR, PECR, CASL) plus platform rules: Gmail and Outlook sender requirements, Upwork's ban on sharing contact details before a contract [S59], and LinkedIn's terms.

## 8. Freelance proposals (Upwork and similar)

**Upwork's own guidance** (June 24, 2026) [S59]: only the first couple of sentences show in the client's list, so open by restating the core problem or commenting on something specific in the post. Keep to two or three short paragraphs, lead with a relevant sample or result, ask questions only when they show understanding without creating work, and end with a clear next step. The first four slots in a client's list go to Boosted Proposals; freelancers with a published portfolio are hired 9x more often, Upwork says. No email, phone or LinkedIn details before a contract. Upwork's AI assistant, Uma, also drafts proposals, so generic AI-shaped letters are common and easy to spot.

**GigRadar data** (vendor; 133,872 proposals sent by agencies through its auto-bidder, Dec 2025 to Feb 2026) [S61][S62]:
- Speed: replies peaked at 11.86% for bids 3 to 4 minutes after posting and fell to 5.34% at 30 to 60 minutes.
- Competition: 9.44% replies when only one GigRadar agency bid, 2.11% with 11 or more. Boosting 16 to 20 Connects was the best value band.
- Openers: a long question mirroring the client's goal got 16.0%; "I came across your job posting" got 5.4% against a 7.45% baseline. "Hey [name]" beat "Dear [name]" (8.50% vs 5.79%). "Can I send a 1-minute Loom?" got 11.7%; "Can we discuss the details?" 2.6%.
- Replies vs hires: reply rate was U-shaped by length (under 50 words 9.4%, 100 to 149 words 6.7%, 700+ words 18.5%), but hires peaked at 300 to 499 words and 500+ word letters won no hires in 334 sends. Discount and guarantee offers were hire signals; question openers were not. Only 112 hires were tracked, so read direction only.
- The proposal text explained only about 16% of reply variance; profile, category, rate and client explain the rest.

**What clients dislike** (Upwork [S59], GigRadar [S63], our analysis): generic openers such as "I'm passionate about...", credential dumps, skipped screening questions, walls of text, portfolio dumps, price talk before a plan, copy-paste or AI-sounding letters, and "Dear Sir/Madam".

**Proposal message 1, the reply-winner (50 to 110 words)**
```text
Hi [name],
Reading your post, the goal is [their outcome, in their words] by [date], and [constraint] looks like the tricky part. Is that the priority, or is [second item] just as important?
I just finished something close: [one-line result with a number] ([one sample link]).
For yours I'd start with [first concrete step], so you'd see [visible result] within [n] days.
Can I send a 2-minute Loom showing how I'd handle [specific part]?
[First name]
```

**Message 2, after the client replies (300 to 450 words).** Restate the goal; a first milestone with "done means..." acceptance criteria; timeline; 2 or 3 price options (small paid discovery, fixed first slice, capped hourly); a guarantee or first-milestone commitment; one proof artifact; a choice-based next step (call or async plan) [S62][S63].

## 9. LinkedIn connection notes and DMs

Belkins, using Expandi data on 112,005 invite sequences run in 2025, found a note slightly lowered acceptance (25.31% vs 27.56% without) but raised replies after acceptance (8.18% vs 5.28%); messages to existing connections got 12.22% replies (vendor) [S31]. Hunter's 2026 survey: 50.5% of decision makers prefer LinkedIn for outreach, 25% email [S27]. Notes are capped at roughly 300 characters, less on free accounts, which also get only a few personalized invites a month (unverified; limits change, check in the app).

Rules: the note gives a reason to connect, never a pitch; the first DM after acceptance asks about their world; offer an asset only after a reply; no links in the note; stop after two unanswered DMs.

```text
Connection note (under 200 characters):
Hi [name], your post on [topic] made a point I keep seeing with [type of client]: [detail]. I work on [adjacent area]. Would be good to connect.

First DM (under 60 words):
Thanks for connecting, [name]. The [detail] you mentioned matches what we saw in [n] [type] audits this year: [one observation]. How are you handling [problem] at [company] right now?

Follow-up DM, 5 to 7 days later (under 40 words):
I put the [n] fixes we see most often for [problem] into a one-page checklist. Want me to send it here?
```

## 10. Failures and AI tells

Buyer data: 65% say cold emails fail because they feel too sales-focused, 61% cite irrelevance, and 69% are bothered by AI use unless the result feels genuinely human [S27].

| Tell | Why it fails | Fix |
|---|---|---|
| "I hope this email finds you well", "Hope you're doing well" | Filler that signals a template | Open with the premise |
| "I came across your profile / job posting" | Could be sent to anyone; 5.4% vs a 7.45% baseline on Upwork [S62] | Name the specific detail |
| "Quick question" subject; fake "Re:" or "Fwd:" | Overused [S27]; deceptive [S1][S49] | 2 to 6 specific words |
| "Loved your recent post!" with no detail; school, hometown or weather as the hook; compliment, then pitch | Scraped flattery, irrelevant premise [S43] | Their own words or company events, tied to a problem |
| "I wanted to reach out", "Just following up", "Bumping this" | No new value; empty in AI thread summaries [S26] | Each follow-up adds a fact, asset or referral ask |
| Leverage, streamline, cutting-edge, seamless, robust, tailored solutions, next level | Fluff [S40]; buzzword penalty [S33] | The customer's words |
| AI rhythm: triple lists, "not just X, it's Y", even sentence lengths, em dashes, "delve", "in today's fast-paced world" | Pattern-matched as machine text | Vary length, cut lists, plain punctuation |
| Walls of text, 9+ sentences | Unreadable on a phone [S33][S39] | 3 to 5 short sentences |
| 30-minute ask or calendar link on the first touch; "Sorry to bother you" | High friction [S34][S47]; apologetic [S40][S48] | One interest question |
| "Hi {first_name}", wrong company, invented results | Instant credibility loss | Pre-send lint; facts only from the brief |

## 11. Implications for our skill

### Rules
1. Classify the job first (newsletter, promo, welcome, onboarding, cart, win-back, launch, cold first touch, follow-up, breakup, proposal reply-winner, proposal plan, LinkedIn note, DM); each has its own budget and skeleton (table below).
2. Premise before prose. Every cold email, proposal and LinkedIn message starts from a real "why you, why now" from the brief or research. If none is given, ask, or fall back to role-level relevance; never invent a detail.
3. One reader, one idea, one ask. Cold first touches end with an interest question; specific times only after interest.
4. The reader's problem first, in their words; proof second; no pitch on a first touch.
5. Plain text for cold email, proposals and DMs: no images or attachments, no link in the first cold touch, tracking off.
6. Subject lines: promos 20 to 40 characters (under 25 for campaigns), triggered 25 to 35, cold 2 to 6 specific words. Marketing and lifecycle emails always get 35 to 90 characters of preview text that adds to the subject.
7. Reading level: grade 3 to 6 for cold email, proposals and DMs; 6 to 8 for newsletters.
8. Follow-ups: 3 emails in total by default, up to 5 only when each adds something new, 3 to 4 days apart, same thread; the last one detaches.
9. Compliance by context: marketing needs unsubscribe and postal address; cold B2B needs sender identity, postal address and an opt-out line; EU and UK prospects also get a privacy link and the right-to-object line; Upwork proposals never carry email, phone, WhatsApp or calendar links.
10. Truth: every number, client name and result comes from the brief; otherwise leave a visible placeholder and flag it.
11. Report success in clicks, replies, orders and meetings, never opens. House voice applies: no em or en dashes, none of the section 10 tells, varied sentence length.

### Word budgets

| Type | Subject | Body | Skeleton |
|---|---|---|---|
| Cold first touch | 2 to 6 words | 50 to 90 words, 3 to 5 sentences | premise, problem, proof, interest ask |
| Follow-up | same thread | 25 to 60 words | one new fact, asset or referral ask |
| Breakup | same thread | 20 to 40 words | close the loop, detach, future date |
| Proposal message 1 | n/a | 50 to 110 words | goal question, proof, first step, easy ask |
| Proposal message 2 | n/a | 300 to 450 words | milestone, criteria, options, guarantee |
| LinkedIn note | n/a | under 200 characters | reason to connect |
| LinkedIn DM | n/a | 30 to 60 words | observation, question |
| Welcome | 20 to 40 characters | 60 to 120 words | deliver the promise, one next step |
| Abandoned cart | 25 to 35 characters | 40 to 90 words | item, objection answered, button |
| Promo | under 25 to 40 characters | 80 to 200 words | offer, who, 3 bullets, one CTA, deadline |
| Newsletter | 20 to 40 characters | 250 to 600 words | hook, story, one idea, use it, one CTA |

### Automatic checks
- Word, sentence and character counts against the budget; reading grade by type.
- Subject length by type; no "Quick question"; no "Re:" or "Fwd:" unless it is a real reply; no all-caps words, "!!" or emoji in B2B cold email.
- Preview text present on marketing and lifecycle emails.
- Links: none in the first cold touch, at most one after; 2 to 5 in newsletters and promos; no shorteners; descriptive link text.
- One primary CTA; cold email ends in a question; 1 or 2 questions in total.
- Banned phrases from section 10; "you/your" at least as often as "I/we" in cold copy; first sentence not starting with "I" or "My name is".
- Leftover merge tags, placeholders or mismatched names; every number and proper noun traceable to the brief.
- Compliance lines by context (unsubscribe, address, opt-out, EU notice, no contact details on Upwork).
- No U+2014 or U+2013 characters.

### Judge criteria (score 1 to 5; ship only at 4 or more on every line)
1. Premise: specific, true, clearly about this reader now.
2. Relevance: a problem the reader would recognise in their own words.
3. Clarity: the point and the ask can be restated within five seconds from the first two lines on a phone.
4. Ask: friction fits the stage (interest when cold, a specific time after interest).
5. Proof: concrete, relevant and checkable, no hype.
6. Voice: reads like a busy, competent person wrote it, with no AI tells.
7. Fit: right type, budget, subject and preview.
8. Compliance: legal and platform lines present, nothing deceptive.

Hard fails whatever the score: an invented fact, a deceptive subject, a missing opt-out on marketing mail, contact details in an Upwork proposal, a merge-tag leftover, an em or en dash.

Questions the judge should ask: could this be sent to 1,000 people unchanged (if yes, the premise fails)? What does the reader lose by ignoring it? Can they answer with one word?

### Still to verify before quoting as fact
Apollo and Smartlead benchmark reports; LinkedIn note and invite limits; Morning Brew and The Hustle audience figures; Data (Use and Access) Act fine levels; German and Canadian (CASL) specifics; the status of Bangladesh's data protection ordinance.

## Sources (all accessed 2026-09-26)

- S1 Google, Email sender guidelines, https://support.google.com/mail/answer/81126 (rules effective Feb 1, 2024)
- S2 Google, Email sender guidelines FAQ, https://support.google.com/a/answer/14229414 (includes the Nov 2025 enforcement note)
- S3 Spam Resource (Al Iverson), Google warns: sender requirements enforcement ramping up, https://www.spamresource.com/2025/11/google-warns-sender-requirements.html (Nov 6, 2025)
- S4 Yahoo Sender Hub, Sender Best Practices, https://senders.yahooinc.com/best-practices/ (requirements from Feb 2024)
- S5 dmarcian, Microsoft enforces SPF, DKIM, DMARC for high-volume senders, https://dmarcian.com/microsoft-enforces-spf-dkim-dmarc/ (Apr 4, 2025, updated May 20, 2026), summarising Microsoft's April 2025 Tech Community announcement
- S6 Google, Gmail Help page on why messages go to spam, https://support.google.com/mail/answer/1366858 (undated)
- S7 Mailchimp, About Spam Filters, https://mailchimp.com/help/about-spam-filters/ (undated)
- S8 Apple Newsroom, Apple advances its privacy leadership with iOS 15, iPadOS 15, macOS Monterey, and watchOS 8, https://www.apple.com/newsroom/2021/06/apple-advances-its-privacy-leadership-with-ios-15-ipados-15-macos-monterey-and-watchos-8/ (Jun 7, 2021)
- S9 Litmus, Email Client Market Share, https://www.litmus.com/email-client-market-share (July 2026 data)
- S10 Campaign Monitor, Email Marketing Benchmarks, https://www.campaignmonitor.com/resources/guides/email-marketing-benchmarks/ (Jan 2022, 2021 data)
- S11 Mailchimp, Email Marketing Benchmarks and Industry Statistics, https://mailchimp.com/resources/email-marketing-benchmarks/ (updated Dec 2023)
- S12 MailerLite, Email marketing benchmarks 2025, https://www.mailerlite.com/blog/compare-your-email-performance-metrics-industry-benchmarks (Dec 3, 2025, updated Apr 7, 2026)
- S13 HubSpot, Email marketing benchmarks by industry, https://blog.hubspot.com/sales/average-email-open-rate-benchmark (updated Nov 4, 2025)
- S14 Klaviyo, Email marketing benchmarks 2026, https://www.klaviyo.com/uk/blog/email-marketing-benchmarks-open-click-and-conversion-rates (Feb 24, 2026)
- S15 Klaviyo, Abandoned cart benchmark report, https://www.klaviyo.com/blog/abandoned-cart-benchmarks (May 15, 2024)
- S16 Omnisend, 2026 ecommerce marketing report, https://www.omnisend.com/resources/reports/2026-ecommerce-marketing-report/ (2026, 2025 data)
- S17 GetResponse, Key insights from the 2024 Email Marketing Benchmarks Report, https://www.getresponse.com/blog/email-marketing-benchmarks-report-key-insights (updated Nov 1, 2025, 2023 data)
- S18 Attentive, What we learned analyzing billions of email subject lines, https://www.attentive.com/blog/email-subject-line-best-practices (Jul 21, 2026)
- S19 MailerLite, How to increase your email open rate (20,000 campaigns studied), https://www.mailerlite.com/blog/improve-email-open-rate (Apr 15, 2026)
- S20 MailerLite, The best time to send email in 2026, https://www.mailerlite.com/blog/best-time-to-send-email (2026, data Dec 2024 to Nov 2025)
- S21 Litmus, The ultimate guide to email preview text, https://www.litmus.com/blog/the-ultimate-guide-to-preview-text-support (Nov 8, 2024)
- S22 HubSpot, Plain text vs. HTML emails, https://blog.hubspot.com/marketing/plain-text-vs-html-emails-data (2014 study, updated Jun 13, 2025)
- S23 Email Markup Consortium, Email Accessibility Report 2025, https://emailmarkup.org/en/reports/accessibility/2025/ (2025)
- S24 W3C, Understanding SC 2.5.8 Target Size (Minimum), https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- S25 W3C, Understanding SC 2.5.5 Target Size (Enhanced), https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html
- S26 Google, Gmail is entering the Gemini era, https://blog.google/products-and-platforms/products/gmail/gmail-is-entering-the-gemini-era/ (Jan 8, 2026)
- S27 Hunter, State of Email Outreach 2026, https://hunter.io/the-state-of-cold-email (2026, 2025 data)
- S28 Hunter, The State of Cold Email 2025, https://hunter.io/the-state-of-cold-email-2025 (2025, 2024 data)
- S29 Instantly, Cold Email Benchmark Report 2026, https://instantly.ai/cold-email-benchmark-report-2026 (updated Jan 12, 2026, data Jan 1 to Dec 18, 2025)
- S30 Belkins, What are B2B cold email response rates? (2026 study), https://belkins.io/blog/cold-email-response-rates (Jun 26, 2026)
- S31 Belkins, Sales follow-up statistics in B2B (2026 study), https://belkins.io/blog/sales-follow-up-statistics (updated Jun 26, 2026)
- S32 Belkins, B2B cold email subject lines and engagement (2025 study), https://belkins.io/blog/b2b-cold-email-subject-line-statistics (Aug 6, 2025)
- S33 Gong, Does cold email even work any more? Here's what the data says, https://www.gong.io/blog/does-cold-email-even-work-any-more-heres-what-the-data-says (Jul 24, 2025)
- S34 Gong Labs, This surprising cold email CTA will help you book a lot more meetings, https://www.gong.io/blog/this-surprising-cold-email-cta-will-help-you-book-a-lot-more-meetings (May 27, 2020)
- S35 Lavender, Cold Email 101, https://www.lavender.ai/blog/cold-email-101 (Mar 23, 2023)
- S36 Lavender, Data says: the shorter, the better for your cold email, https://lavender.ai/blog/best-length-cold-email (Jan 8, 2023)
- S37 Lavender, The ultimate compilation of Lavender sales email frameworks, https://lavender.ai/blog/sales-email-frameworks (updated Jan 8, 2024)
- S38 Boomerang, 7 tips for getting more responses to your emails (with data!), https://blog.boomerangapp.com/2016/02/7-tips-for-getting-more-responses-to-your-emails-with-data/ (Feb 12, 2016)
- S39 30 Minutes to President's Club (Jason Bay), The data-backed cold email formula, https://www.30mpc.com/newsletter/the-data-backed-cold-email-formula-the-exact-words-length (Jul 10, 2025)
- S40 Josh Braun, 15 Cold Email Copywriting Principles (PDF), https://joshbraun.com/wp-content/uploads/2021/08/15coldemail-copywriting.pdf (Aug 2021)
- S41 Josh Braun, Ditch the pitch. Poke the bear, https://joshbraun.com/ditch-the-pitch-poke-the-bear/ (undated)
- S42 Flip the Script (Becc Holland), How to hook personalization to relevance, https://www.flipthescript.com/personalization-to-relevance-webinar (about 2021)
- S43 Antoine Buteau, Lessons from Becc Holland (secondary summary), https://www.antoinebuteau.com/lessons-from-becc-holland/ (undated)
- S44 Will Allred, LinkedIn post on his cold email framework, https://www.linkedin.com/posts/williamallred_i-posted-this-cold-email-framework-a-while-activity-7050083802047533056-rI8o (about Apr 2023)
- S45 Magical, Jason Bay's Outbound Squad cold email starter pack, https://www.getmagical.com/templates/jbays-cold-email-starter-pack (undated)
- S46 30MPC x Sam Nelson, Agoge sequence (Scribd), https://www.scribd.com/document/696420315/30MPC-x-Sam-Nelson-s-Agoge-Sequence (undated)
- S47 #samsales Consulting (Samantha McKenna), Cold email template, https://www.samsalesconsulting.com/resource/cold-email-outreach-template/ (undated)
- S48 Alex Berman, Cold email strategy: what actually works, https://alexberman.com/cold-email-strategy-what-actually-works (Feb 16, 2026)
- S49 US Federal Trade Commission, CAN-SPAM Act: A Compliance Guide for Business, https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business (current version)
- S50 GDPR Recital 47, https://gdpr-info.eu/recitals/no-47/
- S51 GDPR Article 14, https://gdpr-info.eu/art-14-gdpr/
- S52 GDPR Article 21, https://gdpr-info.eu/art-21-gdpr/
- S53 ICO, Guidance on direct marketing using electronic mail, https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-direct-marketing-using-electronic-mail/ (updated Apr 28, 2026)
- S54 ICO, How do we comply with the PECR electronic mail marketing rules?, https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-direct-marketing-using-electronic-mail/how-do-we-comply-with-the-pecr-electronic-mail-marketing-rules/ (undated)
- S55 ICO, Electronic mail marketing (Guide to PECR), https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/electronic-and-telephone-marketing/electronic-mail-marketing/ (undated)
- S56 ICO, The Data (Use and Access) Act 2025: what does it mean for organisations?, https://ico.org.uk/about-the-ico/what-we-do/legislation-we-cover/data-use-and-access-act-2025/the-data-use-and-access-act-2025-what-does-it-mean-for-organisations/ (2025 to 2026)
- S57 DLA Piper, Data Protection Laws of the World: Bangladesh, https://www.dlapiperdataprotection.com/index.html?t=law&c=BD (last modified Jan 3, 2024)
- S58 Wikipedia, Cyber Security Act, 2023, https://en.wikipedia.org/wiki/Cyber_Security_Act,_2023
- S59 Upwork (Cassie Moorhead), How to create a proposal that wins jobs (with examples), https://www.upwork.com/resources/how-to-create-a-proposal-that-wins-jobs (Jun 24, 2026)
- S61 GigRadar, The job you bid on matters more than the proposal you write, https://gigradar.io/blog/upwork-bidding-strategy (Apr 5, 2026)
- S62 GigRadar (Vadym Ovcharenko), Sales script template: the one that wins replies is losing you hires, https://gigradar.io/blog/sales-script-template (Aug 15, 2026)
- S63 GigRadar, The Upwork cover letter: modern best practices for 2026, https://gigradar.io/blog/the-upwork-cover-letter-modern-best-practices (Jan 28, 2026)
- S64 Lenny's Newsletter, About, https://www.lennysnewsletter.com/about (undated)
- S65 Really Good Emails, homepage, https://reallygoodemails.com/ (2026)
- S66 Baymard Institute, Cart abandonment rate statistics, https://baymard.com/lists/cart-abandonment-rate (Sep 22, 2025)
