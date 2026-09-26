# Outbound: cold email, follow-ups, Upwork proposals, LinkedIn

Outbound that works is short, about the reader's problem, starts from a true reason for writing now, and asks for
interest, not a meeting. Evidence: `research/R6-email-and-outbound.md` §6 to §11 (vendor data marked; all templates
are ours; brackets are inputs from the brief, never invented).

## 1. What the data says (R6 §6.1)

| Finding | Source |
|---|---|
| 3 to 4 sentences and 100 words or fewer get the highest reply rates; pitching cuts replies up to 57 %; the average rep needs 344 cold emails per meeting (28 million emails) | Gong, 2025 |
| At the cold stage an interest question performs best; a specific day-and-time ask booked meetings 15 % of the time cold against 37 % inside active deals | Gong Labs, 2020 |
| First touches of 25 to 50 words; a 3rd to 5th grade reading level got 67 % more replies; 70 % of cold emails are written at 10th grade or above | Lavender (vendor), 2023 |
| Three messages in total is best: two follow-ups nearly double replies, three or more lower them; 21 to 50 recipients replied 6.2 % against 2.4 % for 500+; manually edited emails 5.2 % against 4.4 % fully automated | Hunter, 2026 (31 million emails) |
| Custom domains replied 5.2 % against 2.5 % for free webmail; campaigns without open tracking 7.4 % against 4.4 % | Hunter, 2026 |
| Problem-first framing +20 % replies, social proof +41 %, a compelling offer +28 %; short enough to read on a phone without scrolling | Jason Bay (Gong data), 2025 |
| 65 % of buyers say cold emails fail for being too sales-focused, 61 % cite irrelevance, 69 % are bothered by AI use unless the result feels human | Hunter survey, 2026 |

Where the data disagrees (step 1 brings 41 to 58 % of replies; the best length varies), the working rule is a short
first touch, more context in follow-ups, relevance above length.

## 2. The practitioners (R6 §6.2)

- **Josh Braun:** sell the outcome; solve an expensive problem; the prospect's words; "poke the bear" with a neutral
  question that exposes a risk they may not see; a yes-or-no interest question ("Open to learning more?"); detach.
- **Becc Holland, premise-first:** the premise is the researched reason you are writing to this person now. Best
  premises, in order: content they wrote, content they engaged with, traits they state about themselves; company news
  and persona pain are fallbacks. Rapport means adding value, not flattery.
- **Will Allred:** an observation, the problem it suggests, then a question about that problem that implies you can
  solve it.
- **Jason Bay:** a trigger-based first line, the problem that trigger usually creates, social proof, a closed interest
  question with a soft out; under 100 words; 1 to 3 word subjects.
- **Samantha McKenna, "Show Me You Know Me":** research visible in the subject and first line, objections handled up
  front, no calendar link on a first touch.
- **Alex Berman:** under 80 words, problem first, yes-or-no asks, no apologies, no links in the body, case studies
  matched to the prospect's industry.

## 3. Our structure (R6 §6.3)

**Premise** (one true, specific sentence), **problem** in their words (one sentence), **proof** (one sentence, a real
result for a similar client), a **soft interest question**, an optional **detached out**. 50 to 90 words, grade 3 to
6, plain text, no link, a signature with the name, company, city and postal address.

```text
Subject: [Company] mobile checkout

Hi [first name],
On my phone, the [collection] product page shows two promo banners above the add-to-cart button, so buyers scroll before they can buy.
We moved the button up for [similar store] and their mobile conversion went from [x]% to [y]% in [n] weeks.
Worth a 2-minute screen recording of what I'd change on yours?
[Name], [Agency], [City, postal address]
Not relevant? Reply "no" and I won't follow up.
```

The weak pattern it replaces: "Quick question" as the subject; "I hope this email finds you well"; "I came across
your company and was really impressed"; "[Agency] is a leading full-service agency offering cutting-edge solutions
tailored to your unique needs"; "Would you be available for a 30-minute call next Tuesday?". Not one line that only
this reader could receive.

**Follow-ups** (same thread, each adds something new; 3 to 4 emails in total, 3 to 4 days apart):
```text
Day 3 (25 to 50 words): One more thing: PageSpeed shows the product page taking [n] seconds on mobile. I can cover that in the recording too. Want it?
Day 7 (referral ask): Is [role] the right person for site conversion at [Company], or should I talk to someone else?
Day 12 to 14 (breakup, 20 to 40 words): I'll close the loop here. If mobile checkout isn't a priority this quarter, no problem. Should I check back in [month]?
```

**Premises come from the brief or research only.** When none is given, ask, or fall back to role-level relevance;
never invent a detail about the reader. The judges' first question: could this be sent to 1,000 people unchanged?

## 4. Legal basics (general information, not legal advice; R6 §7)

- **United States, CAN-SPAM:** all commercial email, B2B included: honest headers, a subject that matches the
  content, identified as an ad, a valid physical postal address, a working opt-out honoured within 10 business days.
  Up to $53,088 per violating email. A fake "Re:" breaks the deceptive-subject rule and Gmail's guidelines.
- **EU and UK GDPR:** B2B direct marketing can rest on legitimate interests; document the balancing test, target only
  roles the offer suits, give privacy information in the first message (who you are, purpose, legal basis, data
  source, rights) and flag the absolute right to object. In practice: a privacy link, "reply stop and I'll delete your
  details", and a suppression list. Set `meta.region` to EU or UK and the lint checks for it.
- **UK PECR:** companies may receive unsolicited B2B email without consent; sole traders and some partnerships need
  consent or the soft opt-in; every message names the sender and gives a valid opt-out.
- **Elsewhere:** Germany is commonly said to expect consent even for B2B, and Canada's CASL generally requires consent
  (not verified in our research); check the recipient's country first.
- **Bangladesh:** no specific e-marketing or spam rules were found (DLA Piper, 2024); an agency writing abroad follows
  the recipient's law plus the platforms' rules (Gmail, Outlook, Upwork, LinkedIn).

## 5. Upwork and freelance proposals (R6 §8)

- **Upwork's own guidance** (2026): only the first couple of sentences show in the client's list, so open by restating
  the core problem or commenting on something specific in the post; two or three short paragraphs; lead with a
  relevant sample or result; ask questions only when they show understanding; end with a clear next step. No email,
  phone, WhatsApp or calendar links before a contract (the lint errors on them). Upwork's AI assistant drafts proposals
  too, so generic AI-shaped letters are common and easy to spot.
- **GigRadar data** (vendor; 133,872 agency proposals, 2025 to 2026): replies peaked at 11.86 % for bids 3 to 4
  minutes after posting and fell to 5.34 % at 30 to 60 minutes; a long question mirroring the client's goal got 16.0 %;
  "I came across your job posting" got 5.4 % against a 7.45 % baseline; "Hey [name]" beat "Dear [name]" (8.50 % against
  5.79 %); "Can I send a 1-minute Loom?" got 11.7 %, "Can we discuss the details?" 2.6 %. Replies were U-shaped by
  length, but hires peaked at 300 to 499 words and no 500+ word letter won a hire. Only 112 hires were tracked: read
  direction only. The proposal text explained about 16 % of reply variance; the profile, category, rate and client
  explain the rest.
- **What clients dislike:** "I'm passionate about...", credential dumps, skipped screening questions, walls of text,
  portfolio dumps, price talk before a plan, copy-paste or AI-sounding letters, "Dear Sir/Madam".

**Message 1, the reply-winner (50 to 110 words; type `proposal`):**
```text
Hi [name],
Reading your post, the goal is [their outcome, in their words] by [date], and [constraint] looks like the tricky part. Is that the priority, or is [second item] just as important?
I just finished something close: [one-line result with a number] ([one sample link]).
For yours I'd start with [first concrete step], so you'd see [visible result] within [n] days.
Can I send a 2-minute Loom showing how I'd handle [specific part]?
[First name]
```

**Message 2, after the client replies (300 to 450 words; type `proposal-plan`):** restate the goal; a first milestone
with "done means..." acceptance criteria; the timeline; 2 or 3 price options (small paid discovery, a fixed first
slice, capped hourly); a guarantee or first-milestone commitment; one proof artifact; a choice-based next step.

## 6. LinkedIn (R6 §9)

A note slightly lowered acceptance (25.3 % against 27.6 %) but raised replies after acceptance (8.2 % against 5.3 %)
in one 2025 vendor dataset. The note gives a reason to connect, never a pitch; the first DM asks about their world; an
asset only after a reply; no links in the note; stop after two unanswered DMs.

```text
Connection note (under 200 characters):
Hi [name], your post on [topic] made a point I keep seeing with [type of client]: [detail]. I work on [adjacent area]. Would be good to connect.

First DM (under 60 words):
Thanks for connecting, [name]. The [detail] you mentioned matches what we saw in [n] [type] audits this year: [one observation]. How are you handling [problem] at [company] right now?

Follow-up DM, 5 to 7 days later (under 40 words):
I put the [n] fixes we see most often for [problem] into a one-page checklist. Want me to send it here?
```

## 7. Budgets (R6 §11)

| Type | Subject | Body | Skeleton |
|---|---|---|---|
| `email-cold` | 2 to 6 words | 50 to 90 words, 3 to 5 sentences | premise, problem, proof, interest ask |
| `email-followup` | same thread | 25 to 60 words | one new fact, asset or referral ask |
| `email-breakup` | same thread | 20 to 40 words | close the loop, detach, a future date |
| `proposal` | n/a | 50 to 110 words | goal question, proof, first step, easy ask |
| `proposal-plan` | n/a | 300 to 450 words | milestone, criteria, options, guarantee |
| `linkedin-note` | n/a | under 200 characters | reason to connect |
| `linkedin-dm` | n/a | 30 to 60 words | observation, question |

Hard fails: an invented fact, client or result; a deceptive subject; a missing opt-out on marketing mail; contact
details in an Upwork proposal; a merge-tag leftover. Report outbound in positive replies and meetings per 100
contacts, never opens.
