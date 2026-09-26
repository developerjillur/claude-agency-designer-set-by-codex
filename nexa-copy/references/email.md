# Email: newsletters, promotions and lifecycle

Evidence: `research/R6-email-and-outbound.md` §1 to §5 and §11 (vendor datasets are read as direction; every template
is ours, with brackets for inputs from the brief that are never invented). Cold email, proposals and LinkedIn are in
`outbound.md`.

## 1. Read the numbers correctly

- Apple's Mail Privacy Protection (2021) hides opens; Apple clients are 62 % of tracked opens. Open rates rose mostly
  from measurement, so judge copy by clicks, click-to-open, orders, revenue per recipient, replies and meetings, never
  opens.
- Benchmarks disagree by denominator (per contact or per email sent): never compare vendors without checking.

## 2. Subject, preview, sender, time (R6 §2)

- **Subject length:** campaigns under 25 characters won opens and clicks; triggered emails 25 to 35 (Attentive, 91
  billion subject lines, 2026). Top MailerLite campaigns sat at 20 to 40 characters. Cold email differs: 2 to 6
  specific words.
- **Personalisation** that proves relevance works (past buyers in triggered emails +13 %); a name token alone does
  little in campaigns.
- **Emoji:** no reliable lift; they hurt triggered emails. **Buzzwords and numbers** in cold subjects cut opens up to
  17.9 % (Gong); "Quick question" underperforms.
- **Preview text:** always set it (35 to 90 characters that add to the subject); without it the client shows the first
  text it finds, often "View in browser". The best Cyber Week 2025 pairing was a subject under 25 characters with a 35
  to 50 character preheader.
- **Sender:** "person @ brand" beat the brand alone by 3.81 % in opens (one MailerLite test).
- **Send time:** no universal best time; test marketing sends; send cold email in the recipient's local morning.

## 3. Deliverability (R6 §3)

| Mailbox | Who | Requirements |
|---|---|---|
| Gmail | all senders (since Feb 2024) | SPF or DKIM, valid DNS, TLS, spam rate under 0.3 %, no fake "Re:" or "Fwd:" |
| Gmail, Yahoo | bulk (about 5,000 a day) | SPF and DKIM, aligned DMARC (p=none is enough), one-click unsubscribe plus a visible link, removal within 2 days, complaints ideally under 0.1 %; Gmail rejects non-compliant bulk mail since Nov 2025 |
| Outlook.com | over 5,000 a day (since May 2025) | SPF, DKIM and DMARC; failures are rejected |

- Spam-word lists are folklore: filters score who you are (authentication, reputation), how people react (complaints,
  replies, deletes) and patterns (deceptive subjects, shortened or mismatched links, broken HTML).
- Plain text won every HubSpot A/B test in 2014; one image lowered clicks. Newsletters and promos can use light HTML;
  image-only layouts are a risk.
- 2 to 5 links did best; 20 or more did worst. No link shorteners. Descriptive link text; alt text on images; a
  language declaration; buttons at least 24 by 24 pixels (99.89 % of 443,585 tested emails had serious accessibility
  issues).
- Gmail now summarises threads with AI: the first two sentences must carry the point, because a summary may be all the
  reader sees.

## 4. Lifecycle email (R6 §4)

Automation earns more per send: Klaviyo flows produced about 41 % of email revenue from 5.3 % of sends; Omnisend
automations were 2 % of sends and 30 % of revenue ($2.87 a send against $0.18).

**Welcome (60 to 120 words):**
```text
Subject: Your [brand] code is inside
Preview: Plus the product most people start with

Hi [first name],
Thanks for joining. Your code is [CODE]: [x]% off anything until [date].
Not sure where to start? Most first orders include [bestseller], because [reason in customers' own words, from reviews].
[Button: Shop [bestseller]]
Got a question? Just reply. [Name] on our team reads every reply.
```

**Onboarding** (one action per email, 50 to 100 words): day 0 "Step 1: connect [tool]" with why it matters, one
button and what happens next; day 2, only if step 1 is still open, "Stuck on [step]?" with the two most common fixes;
day 5 a similar customer's first result and the next step. Stop once the user acts.

**Abandoned cart (3 emails):** Klaviyo's 143,000 cart flows averaged 3.33 % placed orders and $3.65 revenue per
recipient, the highest of any flow; the top abandonment reasons are extra costs (40 %), slow delivery (20 %) and not
trusting the site with card details (19 %): good cart copy answers those three. (1) After 2 to 4 hours: "Your
[product] is still in your cart"; the item photo, price and total with shipping, one line on delivery or returns, a
"Back to my cart" button (40 to 70 words). (2) After 24 hours: "Before you decide on the [product]"; the question
buyers ask most, answered, and one short real review. (3) After 48 hours: "Last reminder about your cart"; one line; an
offer only for high-value carts if policy allows. Routine discounts train shoppers to wait.

**Win-back (2 or 3, then sunset)** at about twice the normal cycle: what changed since the last order; a preference
link (fewer emails) next to unsubscribe; then "We'll stop emailing you on [date] unless you click here" and suppress
the silent. This protects the complaint rate.

**Launch (3):** a tease 3 to 5 days before (the problem and the date, no hype); launch day (what it is, who it is for,
one proof point, one CTA); last call (the deadline in the subject, one objection answered, the CTA again).

## 5. Newsletters and promotions (R6 §5)

- One promise, kept every issue; a recognisable voice and a fixed skeleton; reply loops; swipe files for layout, never
  wording.
- **Story-led newsletter (250 to 600 words):** a hook (one scene, number or line of dialogue); the story (3 to 6 short
  paragraphs, one tension); the idea in one sentence a reader could repeat; "use it" (1 to 3 bullets); one CTA ("reply
  with X" or one link); an optional P.S. Two ideas make two issues.
- **Promo (80 to 200 words):** the subject is the offer plus a reason or deadline; the preview says who it is for; a
  headline, at most 3 bullets, one button with a verb and an outcome ("Get the bundle", never "Click here"), the
  deadline repeated in the last line, plain-language terms; 2 to 5 links.

## 6. Budgets and checks (R6 §11)

| Type (`copywriter.py` type) | Subject | Body | Skeleton |
|---|---|---|---|
| Welcome (`email-welcome`) | 20 to 40 characters | 60 to 120 words | deliver the promise, one next step |
| Cart (`email-cart`) | 25 to 35 | 40 to 90 words | the item, the objection answered, a button |
| Promo (`email-promo`) | under 25 to 40 | 80 to 200 words | offer, who, 3 bullets, one CTA, deadline |
| Newsletter (`email-newsletter`) | 20 to 40 | 250 to 600 words | hook, story, one idea, use it, one CTA |

The lint checks the budgets, the preview, the links, one primary CTA, the unsubscribe and the postal address (set
`meta.footer_by_tool` when the email tool adds the footer), fake "Re:" subjects, merge-tag leftovers, template
phrases and the reading grade (6 to 8 for newsletters, 5 to 8 for lifecycle). Report results in clicks, replies,
orders and revenue, never opens.
