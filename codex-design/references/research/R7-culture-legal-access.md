# R7 - Culture, legal safety, accessibility and AI labelling for the design skill

Research date: 2026-09-23. Researcher: R7 subagent. Scope: what a Claude Code design skill needs to know to produce
culturally accurate, legally safe, accessible and correctly labelled graphics (social posts, occasion/day posts, ads,
posters, flyers, brochures, infographics, logos, brand kits) for agency clients worldwide, using GPT Image visuals plus
typeset HTML/CSS.

THIS IS NOT LEGAL ADVICE. It records sources and practical rules. Anything that decides money, liability or a
regulator's view (EU AI Act labelling, contests, health/finance claims, logos/trademarks) needs a qualified reviewer in
the client's jurisdiction.

## 0. How to read these notes

Evidence tags used on every claim that matters:

- **[V]** Verified this session from the official or primary source (fetched on 2026-09-23). Paragraph/section numbers given where possible.
- **[S]** Secondary source fetched this session (law-firm note, reputable news, Wikipedia). Good enough to act on, but re-check the primary before a legal decision.
- **[C]** Computed this session (calendar algorithm). Deterministic, but confirm local observance.
- **[U]** Unverified: general knowledge, memory or a search-result snippet only. Treat as a lead, verify before relying on it.

Source IDs in square brackets (e.g. `[EU-GL]`) resolve in section 7.

Two house rules drive everything below:

1. **Global by default.** Place, language, culture, calendar, religion mix and legal regime come from the *client's market and audience*,
   never from the requester's language, location or timezone. A Bangladesh-based operator making a post for a client in Canada gets a
   Canadian calendar; Bangladesh days only appear when the client or audience is Bangladeshi (including diaspora).
2. **Honest provenance.** Keep the C2PA manifest and the IPTC digital-source-type tag on generated images, carry them through
   compositing, and never fabricate camera EXIF.

### 0.1 What changed in 2025-2026 (read this first)

| Date | Change | Why it matters for the skill | Tag |
|---|---|---|---|
| 2025-09-01 | China's Measures for Labeling AI-Generated Synthetic Content and mandatory standard GB 45438-2025 take effect: visible ("explicit") labels plus machine-readable ("implicit") labels | Any AI imagery distributed in mainland China needs both | [S] [CN-AI] |
| 2025-11-19 | TikTok adds invisible watermarking; C2PA auto-labelling; "see less AI" control; 1.3 bn videos labelled | TikTok will label our C2PA-tagged images automatically | [V] [TT-NEWS-25] |
| 2025-12-11 | New York signs S.8420-A: ads with AI "synthetic performers" must carry a conspicuous disclosure (in force 2026-06-09) | Any ad reaching NY audiences with a synthetic human needs a disclosure | [V] [NY-SP] |
| 2026-01-01 | C2PA Interim Trust List frozen; conformant certificates now come via the C2PA Trust List / conformance programme | Self-made signing certificates will not validate as trusted | [V] [C2PA-TRUST] |
| 2026-01-22 | South Korea AI Basic Act in force (labelling of generative outputs; fines deferred during a grace period of at least a year) | Korean market labelling expectations | [S] [KR-AI] |
| 2026-02-20 | India IT (Intermediary) Amendment Rules 2026 in force: synthetically generated audio/visual content must be prominently labelled by platforms, with metadata | Indian platforms will require/declare labels | [S] [IN-AI] |
| 2026-04 | TikTok ads policy (misleading content) updated: AIGC ads must carry the AIGC label or your own clear disclaimer; undisclosed AIGC ads rejected | Every TikTok ad with fully AI images needs a disclosure, even stylised | [V] [TT-ADS] |
| 2026-05-19 | OpenAI: images from ChatGPT, Codex and the API carry C2PA **and** a SynthID invisible watermark | Our GPT Image outputs are watermarked at source; do not try to remove it | [S] [OAI-C2PA-SYNTHID] |
| 2026-06-01 | Meta labels ads made/edited with third-party gen-AI tools (detected via C2PA and similar signals) with "AI info" in "About this ad"; label sits next to "Sponsored" when an AI photorealistic human appears | Clients will see "AI info" on our AI-made ads; tell them in advance | [V] [META-ADS-25] [META-HELP-ADS] |
| 2026-06-10 | EU Code of Practice on Transparency of AI-generated Content published, with three official EU "AI" icons | Ready-made, free label icons for EU deep-fake disclosure | [V] [EU-CoP] [EU-ICONS] |
| 2026-07-20 | Commission adopts final Article 50 Guidelines C(2026) 5054 | Defines "deep fake", narrow creative exemption, advertising examples | [V] [EU-GL] |
| 2026-07-27 | Digital Omnibus on AI (Regulation (EU) 2026/1744) in force; Art. 50(2) marking grace period to 2026-12-02 for gen-AI systems already on the market | Provider-side only; deployer labelling duties still apply from 2026-08-02 | [V] [EU-GL] para 153; [S] [UC-OMNI] |
| 2026-08-02 | EU AI Act Article 50 applies (penalties up to EUR 15 m or 3% of worldwide turnover) | Deep-fake labelling by deployers (the agency) is now law for EU-directed content | [V] [EU-GL] paras 152-153 |

---

## 1. Special-day and occasion posts, worldwide

### 1.1 What brands post (categories)

1. **UN international days and weeks** (fixed Gregorian dates, set by UN General Assembly). Around 200 exist. Brands post the ones that
   match their category (e.g. World Environment Day 5 Jun for sustainability brands, International Women's Day 8 Mar). [V] [UN-DAYS]
2. **Solemn UN days** that must never get a festive or sales treatment [V] [UN-DAYS]:
   27 Jan Holocaust victims commemoration; 25 Mar Remembrance of Victims of Slavery and the Transatlantic Slave Trade; 7 Apr Reflection
   on the 1994 Genocide against the Tutsi in Rwanda; 26 Apr Chernobyl Disaster Remembrance; 8-9 May Remembrance and Reconciliation (WWII);
   19 Jun Elimination of Sexual Violence in Conflict; 26 Jun Victims of Torture; 11 Jul Srebrenica genocide; 21 Aug Victims of Terrorism;
   22 Aug Victims of Violence Based on Religion or Belief; 23 Aug Slave Trade and its Abolition; 30 Aug Victims of Enforced Disappearances;
   16 Nov Road Traffic Victims (third Sunday of Nov in practice [U]); 25 Nov Elimination of Violence against Women; 30 Nov Victims of
   Chemical Warfare; 9 Dec Victims of the Crime of Genocide.
3. **Awareness / heritage months** (country-specific, mostly US/UK/Canada) [U]: Black History Month (Feb in US/Canada, Oct in UK),
   Women's History Month (Mar), Autism Acceptance Month (Apr), AAPI Heritage Month (May, US), Mental Health Awareness Month (May, US;
   UK has a Mental Health Awareness *Week*), Pride Month (Jun), Hispanic Heritage Month (15 Sep - 15 Oct, US), Breast Cancer Awareness
   Month (Oct), Movember (Nov), Native American Heritage Month (Nov, US). Rule: only post if the brand has a real connection or action;
   "rainbow-washing" and empty heritage posts are a documented backlash pattern [U].
4. **Religious and cultural festivals** (often lunar/lunisolar; dates move) - see 1.2 and the region notes in 1.9.
5. **National days** (independence, victory, founding, unity) - celebratory, but many sit next to a solemn day (e.g. Bangladesh 25 Mar
   night vs 26 Mar).
6. **Commercial days** (Black Friday, Singles' Day 11.11, 520 in China, Valentine's, Mother's/Father's Day - dates differ by country).
   Mother's Day example: US 9 May 2027 (2nd Sunday of May) vs UK Mothering Sunday 7 Mar 2027 [C].

### 1.2 Date variability - why every date must be verified per year AND per country

| Calendar | Festivals | Why dates differ | Real 2026-2027 divergence found this session |
|---|---|---|---|
| Islamic lunar (moon sighting) | Ramadan, Eid al-Fitr, Eid al-Adha, Islamic New Year, Ashura, Mawlid, Shab-e-Barat, Shab-e-Qadr | Month starts on local crescent sighting (or on a calculated calendar). Countries can differ by a day; the date is often only confirmed the evening before. "Ramadan dates vary in different countries, but usually by only a day." [S] [WIKI-RAMADAN] | Eid al-Fitr 2026: Umm al-Qura calendar 20 Mar [S] [WIKI-EID]; Singapore 21 Mar [V] [SG-MOM]; Bangladesh (official list, expected) 21 Mar [S] [BD-HOL-2026]. Eid al-Adha 2026: Singapore 27 May [V] vs Bangladesh 28 May [S]. |
| Hindu lunisolar (panchang, regional) | Diwali/Deepavali, Holi, Navratri, Durga Puja, Janmashtami, Raksha Bandhan, Karva Chauth, Chhath | Tithi-based; regional traditions (North vs South India, Bengal) and time-zone of observance; 2026 had an extra (adhik) month so autumn festivals ran late [U] | Deepavali 2026: 8 Nov; 2027: 28 Oct (Singapore) [V] [SG-MOM]. Durga Puja Bijoya Dashami 2026 in Bangladesh: 21 Oct [S] [BD-HOL-2026]. |
| Chinese lunisolar | Lunar New Year (Spring Festival/Seollal/Tet), Lantern Festival, Qingming (solar term), Dragon Boat, Mid-Autumn/Chuseok | New moon between 21 Jan and 20 Feb; zodiac animal changes with it [U] | Lunar New Year: 17-18 Feb 2026, 6-7 Feb 2027 (Singapore holidays) [V] [SG-MOM]. 2026 = Horse, 2027 = Goat/Sheep [U]. |
| Buddhist lunar | Vesak / Buddha Purnima / Buddha's Birthday | Theravada countries use the Vesakha full moon, some use a different month; East Asia celebrates Buddha's Birthday on 8th day of 4th lunar month; Japan uses 8 Apr [U] | Vesak 2026: UN Day of Vesak and Bangladesh Buddha Purnima 1 May [V] [UN-DAYS], [S] [BD-HOL-2026]; Singapore Vesak Day 31 May [V] [SG-MOM]. A full month apart. 2027: Singapore 20 May [V]. |
| Christian: Gregorian vs Julian computus | Easter, Good Friday, Lent, Carnival; Christmas for some Orthodox churches on 7 Jan | Western and Orthodox Easter use different calendars; Orthodox Christmas 7 Jan in Russia, Serbia, Ethiopia, Egypt (Coptic) etc. [U] | Easter 2026: Western 5 Apr, Orthodox 12 Apr; 2027: Western 28 Mar, Orthodox 2 May; 2028: both 16 Apr [C]. Good Friday 2027 = 26 Mar [C], confirmed by Singapore list [V]. |
| Hebrew lunisolar | Rosh Hashanah, Yom Kippur, Sukkot, Hanukkah, Purim, Passover, Shavuot, Tisha B'Av; Israeli civil/memorial days | "Holidays begin at sundown on the evening before" [V] [HEBCAL]. Diaspora vs Israel observe some festivals for different lengths [U] | 5787: Rosh Hashanah 11-13 Sep 2026; Yom Kippur 20-21 Sep 2026; Sukkot 25 Sep - 2 Oct 2026; Hanukkah 4-12 Dec 2026; Purim 22-23 Mar 2027; Pesach 21-29 Apr 2027; Shavuot 10-12 Jun 2027; Tisha B'Av 11-12 Aug 2027 [V] [HEBCAL]. |
| Bengali solar (Bangladesh revised calendar vs West Bengal panjika) | Pohela Boishakh | Bangladesh fixes 14 April; West Bengal follows the traditional almanac (14 or 15 April) [U] | Bangladesh 14 Apr 2026 [S] [BD-HOL-2026]. Bangla year 1433 starts 14 Apr 2026, 1434 on 14 Apr 2027 [C: Gregorian year - 593]. |
| Rule-based Gregorian | US Memorial Day, Thanksgiving, UK Remembrance Sunday, German Volkstrauertag | Weekday rules | US Thanksgiving 26 Nov 2026 / 25 Nov 2027; US Memorial Day 31 May 2027; UK Remembrance Sunday 8 Nov 2026 / 14 Nov 2027; Volkstrauertag 15 Nov 2026; Totensonntag 22 Nov 2026; Carnival Tuesday 9 Feb 2027 [C]. |

**Same-day collisions to watch** [C][V]:
- 8 Nov 2026: Deepavali (Singapore list) **and** UK Remembrance Sunday. A UK brand with South Asian audiences must not blend them;
  schedule separately and keep the Remembrance post solemn.
- 11 Nov: Singles' Day sales (China) vs Armistice/Remembrance/Veterans Day (UK, Commonwealth, US).
- 26 Mar 2027: Good Friday (solemn for Christians) = Bangladesh Independence Day.
- Ramadan 2027 (Umm al-Qura estimate 8 Feb - 8 Mar [S]) contains Bangladesh's 21 February and starts right after Lunar New Year (6-7 Feb).

**Verification protocol (for the skill):** for any variable day, the skill must record `{market, year, date, source URL, retrieved-on}`
from an official national list (government holiday gazette, ministry of manpower/labour, religious authority) before rendering a dated
creative. If only an estimate exists (Islamic dates before sighting), produce the creative **without a date** or produce two variants
(day X and X+1) and publish after the official announcement.

### 1.3 Key dates, Oct 2026 - Dec 2027 (seed list; re-verify each year)

| Date | Occasion | Markets | Tone | Source |
|---|---|---|---|---|
| 1 Oct (fixed) | China National Day; Nigeria Independence Day | CN, NG | Celebratory | [U] |
| 2 Oct | Gandhi Jayanti; UN International Day of Non-Violence | IN, global | Respectful | [V] UN-DAYS; IN [U] |
| 20-21 Oct 2026 | Durga Puja (Mahanabami, Bijoya Dashami) | BD, IN (West Bengal) | Festive; Bijoya is a bittersweet farewell | [S] BD-HOL-2026 |
| 12 Oct 2026 | Columbus Day / Indigenous Peoples' Day (naming contested) | US | Contested - avoid unless client stance | [C] date; naming [U] |
| 1-2 Nov | Dia de Muertos | MX, LatAm, US Hispanic | Joyful but reverent remembrance; not Halloween | [U]; see 1.8 Disney case [S] |
| 8 Nov 2026 | Deepavali / Diwali | IN, SG, MY, UK, global diaspora | Celebratory | [V] SG-MOM |
| 8 Nov 2026 | Remembrance Sunday | UK | Solemn | [C] |
| 11 Nov | Armistice Day / Remembrance Day / Veterans Day | UK, CA, AU, US, FR, BE | Solemn (UK/CA/AU); gratitude to living veterans (US Veterans Day) | [U] |
| 15 Nov 2026 | Volkstrauertag | DE | Solemn | [C] |
| 26 Nov 2026 | Thanksgiving (US); Black Friday 27 Nov | US | Celebratory / commercial | [C] |
| 4-12 Dec 2026 | Hanukkah (starts at sundown 4 Dec) | Jewish communities | Celebratory | [V] HEBCAL |
| 14 Dec | Martyred Intellectuals Day (Shaheed Buddhijibi Dibosh) | BD | Solemn | [U] |
| 16 Dec | Victory Day (Bijoy Dibosh) | BD | Celebratory + tribute | [S] BD-HOL-2026 |
| 18 Dec | Qatar National Day; UN Arabic Language Day | QA, Arab world | Celebratory | UN [V]; QA [U] |
| 25 Dec | Christmas; Quaid-e-Azam Day (PK) | global; PK | Celebratory | [S] BD-HOL-2026 lists Christmas; PK [U] |
| 7 Jan 2027 | Orthodox / Coptic Christmas | RU, RS, EG (Coptic), ET (Genna) | Celebratory | [U] |
| 26 Jan | India Republic Day; Australia Day (contested - also marked as "Invasion Day" by many) | IN; AU | IN celebratory; AU contested | [U] |
| 27 Jan | International Holocaust Remembrance Day | global | Solemn | [V] UN-DAYS |
| 6-7 Feb 2027 | Lunar New Year (Spring Festival / Seollal / Tet) | CN, SG, MY, KR, VN, diaspora | Celebratory | [V] SG-MOM |
| ~8 Feb 2027 | Ramadan begins (estimate; sighting-dependent) | Muslim-majority markets, diaspora | Spiritual, restrained | [S] WIKI-RAMADAN |
| 9 Feb 2027 | Carnival Tuesday | BR, Caribbean, parts of EU | Festive | [C] |
| 21 Feb | Shaheed Dibosh / International Mother Language Day | BD (solemn); global (IMLD) | Solemn in BD | [V] UN-DAYS; [S] BD-HOL-2026 |
| 8 Mar | International Women's Day | global | Celebratory/advocacy | [V] UN-DAYS |
| ~9-10 Mar 2027 | Eid al-Fitr (Umm al-Qura 9 Mar; Singapore 10 Mar) | Muslim markets | Celebratory | [S] WIKI-EID; [V] SG-MOM |
| 25 Mar | BD Genocide Day (night of 25 Mar 1971) [U]; UN slavery remembrance [V] | BD; global | Solemn | [U]/[V] |
| 26 Mar | Bangladesh Independence and National Day; Good Friday 2027 | BD; Christian | BD celebratory + tribute; Good Friday solemn | [S]/[C] |
| 28 Mar 2027 | Easter (Western) | global | Celebratory | [C] |
| 14 Apr | Pohela Boishakh (Bangla year 1434 in 2027) | BD | Festive | [S]/[C] |
| 21-29 Apr 2027 | Passover | Jewish communities | Celebratory | [V] HEBCAL |
| 2 May 2027 | Orthodox Easter; 3 May Sham el-Nessim (EG) | Orthodox; EG | Celebratory | [C] |
| ~16-17 May 2027 | Eid al-Adha (Singapore 17 May) | Muslim markets | Celebratory; no slaughter/blood imagery | [V] SG-MOM |
| 20 May 2027 | Vesak Day (Singapore); other countries differ | SG, Buddhist markets | Serene, respectful | [V] SG-MOM |
| 31 May 2027 | US Memorial Day | US | Solemn | [C]; statute [V] USC-116 |
| 28 Oct 2027 | Deepavali | SG, IN, MY | Celebratory | [V] SG-MOM |

The Bangladesh 2027 official list is normally announced late in the preceding year (the 2026 list was reported on 10 Nov 2025) [S].

### 1.4 Tone taxonomy and the "no Happy" rule

| Tone class | Examples | Greeting allowed? | Commercial content | Visual register |
|---|---|---|---|---|
| **Celebratory** | Eid, Diwali, Lunar New Year, Christmas, Pohela Boishakh, national/independence days, Hanukkah | Yes ("Eid Mubarak", "Happy Diwali", "Shubho Noboborsho") | Soft brand presence OK; festive offers OK if the client wants (except where culturally inappropriate, e.g. during Ramadan fasting-hour imagery) | Festival palette, correct symbols |
| **Commemorative-celebratory** | Bangladesh 16 Dec and 26 Mar, US Independence Day, Juneteenth, International Women's Day | Greeting OK but pair with tribute | Low-key; no gimmicky sales framing on Juneteenth [U] | Dignified festive |
| **Solemn / memorial** | BD 21 Feb, 14 Dec, 25 Mar; Holocaust Remembrance (27 Jan, Yom HaShoah); UK Remembrance; US Memorial Day, 9/11 (Patriot Day), Pearl Harbor Day; Ashura (Shia mourning); Good Friday; Qingming (ancestor day); Nanjing Massacre Memorial Day (13 Dec); Hiroshima/Nagasaki (6/9 Aug); Kwibuka (from 7 Apr, Rwanda) | **Never "Happy", "Congratulations", "Celebrate", "Mubarak", "শুভ" (shubho)** | **None**: no products, prices, discounts, promo codes, CTAs, contests, emojis, trending-audio tricks | Muted/monochrome, customary symbols (flowers, candle, wreath, memorial silhouette), logo small or omitted |
| **Fast / penitential** | Yom Kippur, Tisha B'Av, Ramadan daytime, Lent/Ash Wednesday | Use the customary wish ("G'mar chatima tova", "Have an easy fast", "Ramadan Kareem/Mubarak") | Minimal; no food/drink imagery aimed at fasting hours | Calm |
| **Contested / political** | Australia Day, Columbus/Indigenous Peoples' Day, Kashmir Solidarity Day, partisan national days (see Bangladesh 2024 changes), anything touching Israel/Palestine, Taiwan, Crimea | Only with explicit client decision | None | Neutral |
| **Unscheduled mourning** | National mourning after a head of state's death, disasters, terror attacks | No | Pause all scheduled promotion; review queue | - |

Statutory anchors for US solemn days: 36 U.S.C. §144 designates 11 September as Patriot Day and asks for flags at half-staff and a
moment of silence "in honor of the individuals who lost their lives" [V] [USC-144]. 36 U.S.C. §116 makes the last Monday in May
Memorial Day, a day to "pray ... for permanent peace" [V] [USC-116]; the National Moment of Remembrance Act ties it to those who
"made the ultimate sacrifice" [V as summarised]. Memorial Day honours the dead; Veterans Day (11 Nov) thanks living veterans - do not
swap them [U].

**Bangladesh 21 February.** Officially "Shaheed Day and International Mother Language Day" (holiday list) [S] [BD-HOL-2026]. The
Bangladeshi observance is a mourning commemoration: barefoot processions to the Shaheed Minar, black badges, floral wreaths, mourning
songs [S] [BANGLAPEDIA-EKUSHEY] (search-snippet level). The national flag flies at half-mast on 21 February under the Flag Rules
[S] [BD-FLAG]. UNESCO/UN frame the same date internationally as a celebration of linguistic diversity [V] [UN-DAYS], so a global
(non-Bengali) brand saying "Happy International Mother Language Day" is common - but for any Bangladeshi/Bengali audience treat the day
as solemn: no "Happy", no "শুভ", no offers. Typical tribute wording (native-speaker review required) [U]:
`অমর একুশে` (Amar Ekushe), `মহান শহীদ দিবস ও আন্তর্জাতিক মাতৃভাষা দিবস`, `ভাষা শহীদদের প্রতি বিনম্র শ্রদ্ধা` (humble tribute to the
Language Martyrs).

**Bangladesh 14 December** (Martyred Intellectuals Day, `শহীদ বুদ্ধিজীবী দিবস`) and **25 March** (Genocide Day, night of 25 March 1971)
are solemn; **26 March** and **16 December** are celebratory-with-tribute (`স্বাধীনতা দিবসের শুভেচ্ছা`, `বিজয় দিবসের শুভেচ্ছা` are
normal) [U].

### 1.5 How a brand day post is usually structured

**Celebratory template**
1. Greeting headline in the audience's language and script, typeset (never AI-rendered), optionally with a secondary language line.
2. One culturally correct hero motif from *one* tradition (see 1.7). The festival palette leads; brand colours support.
3. One short line of warmth (roughly 8-20 words): gratitude, togetherness, the festival's meaning. No feature lists.
4. Brand logo small (bottom corner or centred footer). No product packshot unless the client asks for a festive collection post.
5. Caption repeats the greeting + one line + 1-3 correctly spelled hashtags (CamelCase). Alt text written (section 4.3).
6. Offers are optional and separate: if the client wants an Eid/Diwali sale, make it a *second* creative so the greeting stays clean.

**Solemn template**
1. Official name of the day (e.g. "Shaheed Dibosh and International Mother Language Day", "Remembrance Sunday").
2. Tribute phrase ("We remember", "In humble tribute", `শ্রদ্ধাঞ্জলি`). No exclamation marks, no emojis.
3. Restrained palette (black, white, grey; a single customary accent such as the poppy red in the UK when licensed, see 2.1).
4. Accurate symbol: memorial silhouette traced from a reference (Shaheed Minar, National Memorial, Cenotaph), flowers, candle.
   AI must not invent monuments.
5. Logo small, optionally monochrome, or omitted; no URL, no CTA, no price, no product.
6. Check the news before publishing (unscheduled tragedies change what is appropriate that day).

### 1.6 Common brand mistakes and documented backlash

| Case | What happened | Lesson | Tag |
|---|---|---|---|
| SpaghettiOs, 7 Dec 2013 | Light-hearted Pearl Harbor anniversary tweet; criticised as disrespectful; deleted and apologised | Mascots and brand play do not belong on memorial days | [S] [WIKI-SPAGHETTIOS] |
| Pepsi "Live for Now", Apr 2017 | Ad borrowed protest imagery; pulled within a day; "Clearly we missed the mark, and we apologize." | Do not use social-justice movements or protest imagery as props | [S] [WIKI-PEPSI] |
| Dolce & Gabbana "DG Loves China", Nov 2018 | Stereotyped chopsticks videos; Shanghai show cancelled; products delisted by Alibaba/JD and Net-a-Porter | Cultural stereotypes in market-entry content are commercially fatal | [S] [WIKI-DG] |
| Tanishq, Oct and Nov 2020 | Interfaith baby-shower ad and a no-firecrackers Diwali ad both withdrawn after boycott campaigns | In polarised markets, religion/interfaith themes need an explicit client risk decision | [S] [WIKI-TANISHQ] |
| Disney, 2013 | Tried to trademark "Dia de los Muertos"; petition of 21,000+; withdrawn within a week | Never claim or brand a community's festival name | [S] [WIKI-COCO] |
| Lunar New Year naming | Korean and Vietnamese advocates object to "Chinese New Year"; "Chinese New Year" remains official usage in Singapore, Malaysia, Brunei | Name the festival by market: 春节/Chinese New Year (CN, SG, MY), Seollal (KR), Tet (VN), "Lunar New Year" for mixed Western audiences | [S] [WIKI-LNY] |
| Saudi flag on footballs (FIFA 2002) | Saudi objected to the Shahada on a ball meant to be kicked | Never put the Saudi flag (or sacred text) on things that are kicked, worn, discarded | [S] [SA-FLAG] |
| Rising Sun Flag | Seen in Korea and China as a symbol of Japanese imperial aggression; FIFA banned it at events; Capcom removed it from Street Fighter II in 2021 | Never use the rays motif for KR/CN audiences | [S] [RISING-SUN] |
| AT&T 9/11 tweet (2013); Miracle Mattress "Twin Towers" sale video (2016); Walmart Juneteenth ice cream (2022); H&M "monkey" hoodie (2018); Burger King UK "Women belong in the kitchen" IWD tweet (2021); Nike Air Max 270 sole logo read as "Allah" (2019); Gap China-map T-shirt without Taiwan (2018); Fabindia "Jashn-e-Riwaaz" Diwali naming (2021); Dabur Karva Chauth ad withdrawn (2021); brand posts during UK national mourning (Sep 2022) | Widely reported | Same patterns: selling on tragedy, identity-day merchandising, stereotypes, sacred text, maps, naming | [U] |

### 1.7 Correct symbols: flags, maps, religious signs, not mixing traditions

**Hard rule for the skill: flags, national emblems, maps and sacred text are never generated by the image model.** Use vector artwork
built from the official specification, placed in the HTML layer. AI image models routinely get proportions, star counts, spoke counts,
disc offsets and script wrong.

#### Flag specifications (for the vector library)

| Flag | Proportion | Key geometry | Colours | Frequent AI/design errors | Tag |
|---|---|---|---|---|---|
| Bangladesh | 10:6 (length:width) | Red disc radius = 1/5 of length; disc centre on the vertical line at 9/20 of the length from the hoist, on the horizontal centre line (offset toward the pole so it looks centred in flight) | Bottle green and red; the Rules specify dyes ("Procion Brilliant Green H-2RS 50 parts per 1000", "Procion Brilliant Orange H-2RS 60 parts per 1000"); hex values in use differ by source (#006A4E/#F42A41 or Pantone 342 C/485 C ~ #006747/#DA291C) - pick one approximation per brand kit and record it | Disc centred (reads as Palau/Japan geometry); disc too big; lime/teal green; the 1971 yellow map revived; disc on the wrong side when the pole is on the right | [S] [BD-FLAG] (official PDFs at cabinet.portal.gov.bd were unreachable from this network) |
| India | 3:2 | Three equal bands, saffron on top; navy-blue Ashoka Chakra with 24 equally spaced spokes | Saffron, white, India green, navy blue (IS 1 manufacturing standard) | Wrong spoke count, blue/black chakra, saffron shown orange-red, upside down (green on top), text on the flag | [S] [IN-FLAG] |
| United States | 10:19 official [U] | 50 stars (rows of 6 and 5), 13 stripes, red at top and bottom [U] | - | Wrong star/stripe counts, canton size | [U] |
| Saudi Arabia | [U] | Shahada text above a sword; made two-sided so the text reads correctly from both sides; never lowered to half-mast | Green, white | Garbled Arabic, mirrored text, use on merchandise | [S] [SA-FLAG] |
| Japan | 2:3 [U] | Red disc centred; Rising Sun rays are a different (military) flag | - | Adding rays | [U]; rays [S] |
| EU | 2:3 [U] | Always 12 gold stars in a circle, one point up | - | Star count "per member state" | [U] |

Flag-use law and codes that affect ads:
- **US Flag Code, 4 U.S.C. §8**: "The flag should never be used for advertising purposes in any manner whatsoever"; never used as
  apparel/drapery; nothing placed on it (no mark, letter, word, picture); not printed on paper napkins or boxes "designed for temporary
  use and discard" [V] [USC-4-8]. The Code carries no penalties and is treated as advisory [U], but US audiences notice violations.
- **India**: the Flag Code of India 2002 says the flag shall not be used for commercial purposes in violation of the Emblems and Names
  (Prevention of Improper Use) Act 1950; not on cushions, handkerchiefs, napkins, undergarments or costume; no lettering; penalties under
  the Prevention of Insults to National Honour Act 1971 [S] [IN-FLAG]. The State Emblem (Lion Capital) is separately protected by the
  State Emblem of India (Prohibition of Improper Use) Act 2005 [U].
- **Bangladesh**: Flag Rules 1972 (revised to 2023) set specification and half-mast days (21 February and days notified by government)
  [S] [BD-FLAG]. Whether the Rules restrict commercial/decorative use was not verified this session [U].
- **Saudi Arabia**: the flag's Shahada makes it sacred; not for clothing or commercial products [S] [SA-FLAG].
- **China**: the PRC Advertising Law is widely reported to prohibit use of the national flag, anthem and emblem in ads and to ban
  superlatives such as "best/No. 1/national-level" [U] - verify before any China ad.
- **Mexico/Brazil**: national-symbol statutes restrict commercial use [U].

**Maps.** Disputed borders (Kashmir, Arunachal Pradesh, Taiwan, South China Sea, Crimea, Western Sahara, Falklands/Malvinas, Israel/
Palestine) trigger backlash or legal exposure in the markets concerned [U]. Rule: no maps in marketing art unless the client supplies an
approved market-specific map; never let the image model draw a map.

**National monuments.** Shaheed Minar (21 Feb), Jatiyo Smriti Soudho (26 Mar/16 Dec), Rayer Bazar memorial (14 Dec), India Gate, the
Cenotaph, etc. must come from licensed photographs or vector silhouettes traced from reference - never AI "impressions" [U].

#### Religious symbols - correct forms and no mixing

| Tradition / festival | Correct | Common errors to block | Tag |
|---|---|---|---|
| Hanukkah | Hanukkiah has **9** branches (8 + shamash); one more candle each night | Seven-branched Temple menorah; Christmas trees/Santa mixed in | [S] [WIKI-HANUKIAH] |
| Jewish High Holy Days | Rosh Hashanah "Shana Tova"; Yom Kippur is a fast: "G'mar chatima tova" / "Have an easy fast" | "Happy Yom Kippur"; food imagery on Yom Kippur | [U] |
| Ramadan / Eid | Crescent, lanterns (fanous), dates, mosque silhouettes that are real mosques; Arabic typeset by a native-quality font | Taj Mahal used as a mosque (it is a mausoleum); church spires; Christmas lights/trees; alcohol; people eating in daylight during Ramadan; AI-garbled Arabic; slaughter/blood for Eid al-Adha; Allah's name or Quranic verses as decoration | [U] |
| Diwali / Deepavali | Diyas, rangoli, lanterns, marigolds; Lakshmi/Ganesha respectfully placed | Chinese lanterns as the hero motif; Holi colour-throwing mixed in; deities on floors, feet, footwear, underwear, bins; Hindu swastika in Western-facing creatives (read as Nazi) | [U] |
| Christmas / Easter | Nativity, star, tree; Easter eggs/lilies; Good Friday solemn | "Happy Good Friday"; crosses on products that are sat on or discarded | [U] |
| Buddhist (Vesak) | Lotus, lanterns, Bodhi leaf; Buddha image placed high and respectfully | Buddha heads as decor, near alcohol, on feet/floors; Buddha tattoos (legal trouble in Sri Lanka) | [U] |
| Sikh (Vaisakhi, Gurpurab) | Khanda, Nishan Sahib; correct turban styles | Generic "Indian" turbans; mixing with Hindu deity imagery | [U] |
| Lunar New Year | Year animal of the correct year (2027 Goat/Sheep); red and gold; for Vietnam, Tet uses Cat in place of Rabbit | Wrong zodiac animal; Japanese/Korean/Chinese costume mash-ups; the number 4 | [U]; 4 [S] |
| Dia de Muertos | Ofrendas, cempasuchil marigolds, papel picado, calaveras as honouring the dead | Halloween horror mash-ups; sexualised "sugar skull" costumes | [U] |

### 1.8 Bangladesh-specific notes (only when the client/audience is Bangladeshi)

- **2026 official list** (reported 10 Nov 2025, updated 12 Jan 2026): general holidays - 21 Feb Shaheed Day and International Mother
  Language Day; 20 Mar Jumatul Bida; 21 Mar Eid ul Fitr; 26 Mar Independence and National Day; 1 May May Day and Buddha Purnima; 28 May
  Eid ul Azha; 5 Aug Mass Uprising Day; 26 Aug Eid-e-Miladunnabi; 4 Sep Janmashtami; 21 Oct Durga Puja (Bijoya Dashami); 16 Dec Victory
  Day; 25 Dec Christmas. Executive-order holidays include 4 Feb Shab-e-Barat, 17 Mar Shab-e-Qadr, 14 Apr Bangla New Year, 26 Jun Ashura,
  20 Oct Durga Puja (Mahanabami). [S] [BD-HOL-2026]
- **The list of observed national days is political and has changed recently.** In October 2024 the interim government cancelled eight
  national days, including 7 March, 17 March (as Bangabandhu's birthday / National Children's Day), 15 August National Mourning Day,
  4 November Constitution Day and 12 December Smart Bangladesh Day [S] [BD-8DAYS]. 5 August "Mass Uprising Day" appears as a 2026
  general holiday [S]. Further changes after the February 2026 transition of government were not verified [U]. Rule: never post a
  partisan commemoration unless the client explicitly asks; always check the current Cabinet Division list.
- **Greetings** (native-speaker review required) [U]: Pohela Boishakh `শুভ নববর্ষ ১৪৩৪` (2027); Eid `ঈদ মোবারক`,
  `ঈদুল ফিতরের শুভেচ্ছা`, `ঈদুল আযহার শুভেচ্ছা`; Durga Puja `শুভ শারদীয়া`, Bijoya Dashami `শুভ বিজয়া`; Buddha Purnima
  `শুভ বুদ্ধ পূর্ণিমা`; Christmas `শুভ বড়দিন`. Official English spelling on the government list is "Eid ul Azha"/"Eid-ul-Azha" [S].
- **Colour trap:** Bangladesh red on Bangladesh green has a contrast ratio of about 1.66:1 [C] - never set red text on green (a
  frequent Victory Day design) and never encode meaning by red vs green (red-green colour blindness). White on the green is about
  6.6:1 (fine); white on the red #F42A41 is about 4.0:1 (large text only) [C].
- **Script:** use Unicode Bengali fonts (e.g. Noto Sans/Serif Bengali, Hind Siliguri, Anek Bangla, Tiro Bangla, Baloo Da 2). Legacy
  Bijoy-encoded fonts such as SutonnyMJ, still common in local print shops, produce non-Unicode text that is not searchable, not
  screen-reader friendly and breaks in browsers [U].

### 1.9 Region notes (other markets)

**India** [U unless tagged]
- National: 26 Jan Republic Day, 15 Aug Independence Day, 2 Oct Gandhi Jayanti; 30 Jan Martyrs' Day is solemn.
- Festivals vary by state; name them the local way (Diwali/Deepavali; Pongal/Makar Sankranti/Lohri/Bihu in mid-January; Onam; Durga Puja
  vs Navratri vs Dussehra).
- Flag and emblem law: see 1.7 [S]. Map depictions of Jammu and Kashmir, Ladakh and Arunachal must follow India's official map.
- Interfaith and "progressive" festival themes carry boycott risk (Tanishq 2020 [S]).
- 22 scheduled languages; choose script by state (Devanagari, Bengali, Tamil, Telugu, Gujarati, Gurmukhi, Kannada, Malayalam, Odia...).

**Pakistan** [U]
- 23 Mar Pakistan Day, 14 Aug Independence Day (not 15 Aug), 6 Sep Defence Day, 9 Nov Iqbal Day, 25 Dec Quaid-e-Azam Day, 5 Feb Kashmir
  Solidarity Day (political).
- Ashura (9-10 Muharram) is a mourning period, especially for Shia audiences - no festive content, black/green palettes, no "Happy".
- Urdu typography: readers expect Nastaliq (e.g. Noto Nastaliq Urdu); Naskh reads as Arabic.
- Blasphemy law exposure makes religious imagery and text a zero-error zone.

**Middle East / GCC** [U unless tagged]
- Ramadan and Eid dates by national moon-sighting announcements; publish after the announcement.
- National days: Saudi 23 Sep (National Day) and 22 Feb (Founding Day); UAE 2 Dec (National Day) and 30 Nov (Commemoration Day, solemn);
  Qatar 18 Dec; Kuwait 25-26 Feb; Bahrain 16 Dec; Oman November (date changed recently - verify).
- Saudi flag: sacred text; no commercial/merchandise use; never half-mast [S].
- Imagery: modest dress norms, no alcohol, no pork, careful with dogs in homes/food, no same-sex romantic depiction (legal risk), avoid
  music-heavy Ramadan content; right-hand for eating/giving.
- For Shia audiences (Bahrain, Iraq, Iran, Lebanon, parts of KSA/Kuwait), Muharram is mourning; "Happy Hijri New Year" can be wrong.
- Mawlid is a public holiday in some countries (e.g. Egypt, Pakistan, Bangladesh [S list]) but not observed officially in Saudi Arabia.
- Digits: Eastern Arabic countries often use Arabic-Indic digits (٠-٩); Iran/Afghanistan use Eastern Arabic-Indic (۰-۹); Maghreb uses
  European digits [V] [W3C-ALREQ].

**United States**
- Solemn: Memorial Day (last Mon May) [V statute], Patriot Day 11 Sep [V statute], Pearl Harbor Remembrance Day 7 Dec [U].
- Identity days: Juneteenth (19 Jun, federal holiday since 2021 [U]); MLK Day; heritage months (1.1). Avoid merchandising identity days.
- Contested naming: Columbus Day vs Indigenous Peoples' Day [U].
- Flag Code [V]; right-of-publicity and sweepstakes law are state-level (section 2).

**United Kingdom** [U unless tagged]
- Remembrance: 11 Nov Armistice Day and Remembrance Sunday (8 Nov 2026 [C]); two-minute silence at 11:00. "RBL, Poppy, Poppy Appeal,
  Poppy Shop, are all registered trade marks of the Royal British Legion" [V] [RBL] - commercial poppy use needs RBL permission.
- Holocaust Memorial Day 27 Jan [V intl day]. Black History Month is October.
- Advertising rules: CAP Code/ASA (section 2). Periods of national mourning: pause and review scheduled posts.

**European Union** [U unless tagged]
- National days differ per country (FR 14 Jul, DE 3 Oct, ES 12 Oct, IT 2 Jun, NL 27 Apr King's Day, IE 17 Mar, PL 3 May and 11 Nov);
  Europe Day 9 May. All Saints' Day (1 Nov) is a cemetery-visit day in Catholic countries; Germany has Volkstrauertag and Totensonntag
  (15 and 22 Nov 2026 [C]).
- Germany criminalises use of symbols of unconstitutional organisations (StGB §86a), which covers Nazi symbols and look-alikes [U] -
  another reason to keep swastika forms out of EU-facing art.
- EU AI Act Article 50, UCPD and the European Accessibility Act apply (sections 2-4).

**China and East Asia** [U unless tagged]
- China: Spring Festival (6 Feb 2027 [V SG list]), Lantern Festival, Qingming (ancestor/tomb-sweeping day - solemn; avoid "快乐"),
  Dragon Boat, Qixi, Mid-Autumn, National Day Golden Week, Singles' Day 11.11, 520 (romance, from "I love you") [S] [WIKI-CN-NUM].
  Solemn: 13 Dec Nanjing Massacre National Memorial Day; 18 Sep.
- Numbers: avoid 4 (sounds like "death" in Chinese, Japanese, Korean, Vietnamese) [S] [WIKI-TETRA]; 8 lucky, 6 smooth, 9 longevity,
  250 an insult, 1314 "a lifetime" [S] [WIKI-CN-NUM].
- Colour: red/gold festive; white is the traditional mourning colour in Chinese culture [S] [WIKI-MOURNING]; a "green hat" on a man
  implies a cheated husband [U].
- Scripts: Simplified (mainland, Singapore) vs Traditional (Taiwan, Hong Kong); set `lang` so the right glyph forms are used (section 4.7).
- AI labelling: explicit + implicit labels in China [S].
- Korea: Seollal, Chuseok, Hangul Day (9 Oct); Memorial Day 6 Jun solemn; Liberation Day 15 Aug; Rising Sun motif offensive [S]; do not
  write a living person's name in red [U]. AI Basic Act labelling [S].
- Japan: New Year greetings (akemashite omedeto) only from 1 Jan - before that "yoi otoshi wo"; Obon; 6 Aug, 9 Aug and 11 Mar memorials
  are solemn; avoid 4 and 9 [U].
- Vietnam: Tet (Cat year where China has Rabbit); peach blossom (north) vs yellow apricot blossom (south) [U].

**Africa** [U unless tagged]
- 7 Apr: UN Day of Reflection on the 1994 Genocide against the Tutsi [V]; Rwanda's Kwibuka commemoration starts that day - no festive
  brand content in Rwanda during commemoration week [U].
- South Africa: 21 Mar Human Rights Day (Sharpeville), 27 Apr Freedom Day, 16 Jun Youth Day (Soweto 1976), 9 Aug Women's Day, 24 Sep
  Heritage Day, 16 Dec Day of Reconciliation; multiple official languages.
- Nigeria: 1 Oct Independence, 12 Jun Democracy Day; Muslim and Christian festivals both major - balance.
- Kenya: 1 Jun Madaraka, 20 Oct Mashujaa, 12 Dec Jamhuri. Ethiopia: own calendar (Enkutatash ~11 Sep, Genna 7 Jan, Timket ~19 Jan,
  Meskel ~27 Sep). Egypt: Coptic Christmas 7 Jan; Sham el-Nessim 3 May 2027 [C]. Maghreb: Yennayer (Amazigh New Year) mid-January.

**Latin America** [U unless tagged]
- Dia de Muertos 1-2 Nov (Disney 2013 case [S]). Independence: MX 16 Sep (Grito on the night of 15 Sep), BR 7 Sep, AR 9 Jul (and 25 May),
  CL 18-19 Sep, CO 20 Jul, PE 28-29 Jul.
- Holy Week 2027 21-28 Mar, Good Friday solemn; Carnival 9 Feb 2027 [C].
- Argentina 2 Apr (Malvinas veterans and fallen) is solemn; "Malvinas" vs "Falklands" naming is political.
- Spanish vs Brazilian Portuguese: never mix; Spanish varies by country (vosotros vs ustedes, vocabulary).

---

## 2. Legal and policy

### 2.1 Third-party trademarks and logos

- **Default: no third-party logos.** A logo in an ad implies endorsement or partnership. Use them only (a) with written permission
  (client logos on a "trusted by" strip, partner co-branding), or (b) as an official badge used exactly per the owner's badge guidelines
  (App Store / Google Play badges, "Available on Amazon").
- **Referential ("nominative") use** of a name in text to identify a product ("works with iPhone") is narrower than people assume:
  US nominative fair use and EU "honest practices" referential use both require no more than necessary and no implied sponsorship [U].
- **Platform brands in ads:** LinkedIn's ad policy: "Do not use 'LinkedIn' or refer to LinkedIn ... in your ad. Do not imply affiliation
  with or an endorsement by LinkedIn," and "Do not imply you or your product are affiliated with or endorsed by others without their
  permission" (policy revised 18 Nov 2025) [V] [LI-ADS]. Google Ads restricts trademark use in ad text by direct competitors or in a
  confusing way, with reseller/informational exceptions; the policy text covers ad text, not images [V] [G-TM].
- **Event marks (ambush marketing).** In the US the USOPC has exclusive rights to "Olympic", "Olympiad", "Citius Altius Fortius",
  "Paralympic", the five rings etc., with a civil action against use "for the purpose of trade" that falsely suggests a connection [V]
  [USC-220506]. FIFA (World Cup), UEFA, the NFL ("Super Bowl"), ICC etc. run similar brand-protection programmes [U]. Rule for non-sponsor
  clients: no event names, logos, mascots, trophies, official photos or athlete likenesses; generic sport themes only.
- **Remembrance poppy (UK):** registered trade mark of the Royal British Legion [V] [RBL].
- **Emoji:** platform emoji artwork (e.g. Apple's) is copyrighted; for artwork use an openly licensed set (Noto Emoji, Twemoji with its
  attribution licence) [U].

### 2.2 Copyrighted characters, style imitation, and who owns AI output

- No copyrighted characters (Disney/Marvel/anime/game characters, cartoon mascots of other brands), no "in the style of <living
  artist or studio>" prompts, no recreations of famous photographs or ad campaigns [U]. Look-alike AI output can still infringe.
- **US Copyright Office, Part 2 report (29 Jan 2025)** [V] [USCO-P2]:
  - "Copyright does not extend to purely AI-generated material, or material where there is insufficient human control over the
    expressive elements."
  - "Based on the functioning of current generally available technology, prompts do not alone provide sufficient control."
  - Human authors are entitled to copyright in their expression "perceptible in AI-generated outputs, as well as the creative selection,
    coordination, or arrangement of material in the outputs, or creative modifications of the outputs."
  - "The use of AI tools to assist rather than stand in for human creativity does not affect the availability of copyright protection."
- **Consequences for the skill:**
  - Logos: a raw AI-generated mark may have no copyright in the US. Trademark rights come from use/registration, not authorship, but a
    logo nobody can own the copyright in is weaker commercially. Use AI for exploration only; the final logo should be a human-drawn
    vector with documented human decisions, and it must pass a trademark clearance search (USPTO, EUIPO, WIPO Global Brand Database, the
    local registry) before delivery [U for the procedure].
  - Typeset layout, copy, selection and arrangement done by the designer remain protectable; keep a record of human contributions.
  - Tell clients plainly which parts of a deliverable are AI-generated.

### 2.3 Real people, celebrities and synthetic humans

- Never depict a real, identifiable person (celebrity, politician, influencer, employee, customer) without a written release covering the
  use. Right of publicity is state law in the US (e.g. California Civil Code §3344, New York Civil Rights Law §§50-51; Tennessee's ELVIS
  Act 2024 covers voice) and image rights/passing off elsewhere (UK Irvine v Talksport, Fenty v Arcadia; France droit a l'image; GDPR
  treats a likeness as personal data) [U]. Look-alikes and sound-alikes are also actionable in the US [U].
- **EU AI Act:** an AI-generated depiction of a celebrity influencer in an ad is listed by the Commission as a deep fake; an "AI-generated
  image of celebrities implying their involvement in activities that never happened" is not creative work [V] [EU-GL] examples on pp. 36
  and 39. A company outside the EU that generates a celebrity deep fake for an ad shown in the EU is a deployer in scope [V] para 14 box.
- **TikTok ads:** no misuse of a public figure's likeness without permission [V] [TT-ADS].
- **New York (from 9 Jun 2026):** ads made commercially must "conspicuously disclose in such advertisement that a synthetic performer is
  in such advertisement" where the producer has actual knowledge; a synthetic performer is a digital asset "intended to create the
  impression that the asset is engaging in an audiovisual and/or visual performance of a human performer who is not recognizable as any
  identifiable natural performer"; audio ads and certain expressive-work promos are exempt; penalty USD 1,000 first violation, USD 5,000
  thereafter [V] [NY-SP]. It reaches any ad distributed to a New York audience, wherever the advertiser is based [S].

### 2.4 Fonts

- **SIL Open Font License (OFL)** [V] [OFL-FAQ]: OFL fonts may be used for "logos, posters, business cards, stationery, video titling,
  signage, t-shirts..." and the artwork is yours; embedding in PDFs (full or subset) is allowed; fonts may be bundled with software/web
  but not sold on their own; subsetting a webfont counts as modification (Reserved Font Name rules apply unless functionally equivalent);
  "Referencing or embedding an OFL font in any document does not change the license of the document itself." Most Google Fonts are OFL
  (some Apache 2.0 / Ubuntu Font Licence) [U].
- **Commercial fonts:** EULAs split rights by use: desktop (static images and print usually OK), webfont (page views), app/embedding,
  ePub, broadcast, and **server** (automated generation of images/PDFs on a server for others). An automated HTML-to-PNG/PDF renderer
  running for many clients is the "server/automated" case and often needs its own licence - check each EULA [U].
- **Embedding bits (OS/2 fsType)** [V] [MS-OS2]: 0 = Installable; 2 = Restricted License ("must not be modified, embedded or exchanged in
  any manner without first obtaining explicit permission"); 4 = Preview & Print (documents opened read-only); 8 = Editable; bit 0x0100 =
  no subsetting; 0x0200 = bitmap embedding only. Applications "must not embed fonts which are not licensed to permit embedding." The
  PDF step of the skill should read fsType and refuse restricted fonts.
- **Adobe Fonts:** commonly understood to allow commercial design work including logos and PDF embedding, but not sharing font files
  with clients; the licence page (helpx.adobe.com/fonts/using/font-licensing.html) was blocked from this network [U].
- Keep a font registry per project: family, source URL, licence, allowed uses, fsType, date checked.

### 2.5 Stock images

- **Unsplash licence** [V] [UNSPLASH]: irrevocable, worldwide, free, commercial use, no attribution; restrictions: "Images cannot be sold
  without significant modification" and no "compiling images from Unsplash to replicate a similar or competing service." The licence page
  says nothing about model or property releases - assume none [U].
- **Pexels licence** [V] [PEXELS]: "Identifiable people may not appear in a bad light or in a way that is offensive"; "Don't imply
  endorsement of your product by people or brands on the imagery"; don't sell unaltered copies; no redistribution on stock/wallpaper
  platforms; don't use as part of a trade mark or business name.
- Paid stock: check commercial vs **editorial-only**, model/property releases, and "sensitive use" restrictions (health conditions,
  sexuality, poverty, crime) that may need a "posed by model" note or be prohibited [U].
- Logos, artworks, trademarked products and some buildings inside a stock photo can need their own clearance [U].

### 2.6 Testimonials, reviews and endorsements

- **US FTC Rule on consumer reviews and testimonials** (announced 14 Aug 2024; effective 60 days after Federal Register publication, i.e.
  late Oct 2024 [U exact date]): bans fake reviews/testimonials, including "AI-generated fake reviews" and those by people "who did not
  have actual experience with the business"; compensated sentiment-conditional reviews; undisclosed insider reviews; company-controlled
  "independent" review sites; review suppression; fake social-media indicators; with civil penalties against knowing violators [V]
  [FTC-REV].
- **FTC Endorsement Guides** [V] [FTC-EG]: disclosures of material connections must be "clear and conspicuous" and hard to miss - not
  only in a description, comment or behind a link; overlaying the disclosure on the visual itself is the robust approach; if an endorser's
  results are not typical, the ad must clearly say what consumers "will generally achieve." (The 2023 revision of 16 CFR Part 255 also
  covers virtual influencers [U].)
- **EU:** the Omnibus Directive (EU) 2019/2161 added to the Unfair Commercial Practices Directive blacklist (Annex I, points 23b and 23c)
  (i) claiming reviews come from real users without reasonable steps to check, and (ii) submitting or commissioning fake reviews or
  endorsements, or misrepresenting reviews [U - EUR-Lex was not readable from this network].
- **UK:** the Digital Markets, Competition and Consumers Act 2024 makes fake reviews and concealed incentivised reviews banned practices
  (in force April 2025) with CMA direct fining powers [U]; CAP Code rules on testimonials apply [U].
- **Rules for the skill:** testimonial creatives only from real, documented customers with written permission and the exact wording;
  never AI-generated faces, names or quotes for testimonials; no stock model presented as a reviewer; star ratings only with a
  verifiable source and date; "Results not typical" is not a cure for atypical results.

### 2.7 Health, finance, before/after, body image

- **Meta (Health and wellness, version dated 22 Jul 2026)** [V] [META-HW]: weight-loss/gain, dietary and cosmetic products/procedures
  must target 18+; no "statements of inferiority about physical appearance"; no "close up on specific body area by pinching fat"; no
  claims to "cure, heal, or eliminate" incurable conditions; "general cosmetic products, procedures, surgeries depicting before and after
  transformation" are listed as allowed when targeted 18+. Meta's before/after rules have changed several times; recheck before each
  campaign.
- **TikTok (Misleading and false content, updated Apr 2026)** [V] [TT-ADS]: no "product effect comparisons, such as before-and-after
  results, which may cause viewers to have a false or distorted impression"; no absolute-effect claims ("Get slim legs right away", "Get
  money in 10 seconds"); cure claims for incurable diseases banned; comparative claims need evidence; mismatched ad/landing-page offers
  banned.
- **Google Ads Misrepresentation** [V] [G-MISREP]: no clickbait or "sensationalist text or imagery"; no use of "negative life events such
  as death, accidents, illness, arrests or bankruptcy to induce fear, guilt"; no claims that entice "with an improbable result"; no
  impersonation of other brands.
- **Meta personal attributes** [V] [META-PA]: ads must not assert or imply "race, ethnicity, religion, beliefs, age, sexual orientation or
  practices, gender identity, disability, physical or mental health (including medical conditions), vulnerable financial status, voting
  status, membership in a trade union, criminal record, or name." Examples: "Depression getting you down?" disallowed vs "Depression
  counseling" allowed; "Are you Christian?" disallowed vs "Date Christian singles!" allowed.
- **Regulatory background** [U]: US FTC Health Products Compliance Guidance (Dec 2022, "competent and reliable scientific evidence");
  EU Regulation (EC) 1924/2006 (only authorised nutrition/health claims); UK FCA financial promotions (fair, clear, not misleading; crypto
  risk warnings); no "guaranteed returns"; representative APR examples in consumer credit.
- **Retouched/virtual bodies** [U]: France (2017 decree) requires "photographie retouchee" on commercial photos with altered body
  silhouettes, and the 2023 influencer law (Loi 2023-451) requires "image virtuelle" on influencer content whose face or silhouette was
  AI-generated; Norway (2022) requires a label on retouched body images in ads. Verify before using AI models in FR/NO campaigns.

### 2.8 Platform ad policies that shape the creative

| Platform | Rules that change the design | Tag |
|---|---|---|
| **Meta** | Advertising Standards sections include Personal attributes, Adult nudity and sexual activity, Violent and graphic, Profanity, Prohibited commercial practices (deceptive pricing, unauthorised endorsements, guaranteed returns), Restricted goods (alcohol, finance, crypto, gambling, health). AI: "AI info" labels (2.x/3.3). Political/social-issue ads must disclose AI-created or altered photorealistic content. Text in images: the old 20% rule was dropped in 2020 but less text is still recommended [U]. | [V] [META-ADSTD] [META-PA] [META-MID26]; 20% [U] |
| **Google Ads / PMax / Display** | Editorial: no gimmicky capitalisation/punctuation, no sideways/upside-down/blurry images, no "strobing, flashing" images, no phone numbers in ad text. Misleading design: no fake buttons, fake input fields, fake system notifications. **Responsive Display / PMax image assets:** do not overlay logos, avoid overlaid text, never overlay buttons, avoid collages and digital composite backgrounds - i.e. supply clean photographic assets, not finished graphics. | [V] [G-EDIT] [G-MISREP] [G-RDA] |
| **TikTok** | AIGC disclosure (AIGC label or own "clear disclaimer, caption, watermark, or sticker"); "significantly modified" includes "completely AI-generated" images; insignificant edits = lighting/colour, "removing or modifying backgrounds", denoising; undisclosed AIGC "will be rejected or restricted"; fake CTA buttons/pop-ups banned; before/after banned; identity misuse banned. | [V] [TT-ADS] |
| **LinkedIn** | No LinkedIn brand/implied endorsement; "Any claims in your ad must have factual support"; ads "must not be ... hateful, vulgar, sexually suggestive or violent"; **political ads prohibited**; no discrimination on personal attributes. | [V] [LI-ADS] |
| **X** | Synthetic and manipulated media policy: may label or remove media that is significantly and deceptively altered/fabricated and likely to cause harm. The page returned 403 here; ad-specific AI rules not verified. | [U] [X-MM] |

### 2.9 Contests and giveaways

- **Facebook Pages (Meta Pages, Groups and Events Policies, section on promotions)** [V] [META-PGE]: you are responsible for lawful
  operation, including "providing entrants a copy of the promotion's official rules" and eligibility; each entrant must "(a) fully release
  and hold Meta harmless from liability, and (b) acknowledge that the promotion is in no way sponsored, endorsed, administered by or
  associated with Meta"; and **"Your promotion must not require or incentivise participants to share, repost, tag others or in any other
  way publicise your promotion."** So "Share + tag 3 friends to win" creatives are out on Facebook.
- **Instagram** promotion guidelines (official rules, eligibility, release, no inaccurate tagging / no encouraging people to tag themselves
  in content they are not in) - page not reachable here [U] [IG-PROMO].
- **US:** a promotion with prize + chance + consideration is an illegal lottery - keep a free method of entry ("No purchase necessary")
  [U]. New York: promotions with total announced prizes over USD 5,000 must be filed with the Secretary of State at least 30 days before
  start and bonded or trust-funded; rules and prize information must appear in advertising [V] [NY-GBL-369e]. Florida has a similar
  USD 5,000 registration rule [U].
- **UK CAP Code Section 8** [V] [CAP-8]: ads must state significant conditions - how to enter, closing date, number/nature of prizes,
  restrictions (age, location), promoter's full name and address; space-limited ads must "direct consumers clearly to an easily
  accessible alternative source"; free-entry routes explained "clearly and prominently"; prize draws judged by or under supervision of an
  independent person.
- **Elsewhere:** Canada requires a skill-testing question; the Gulf states and several Asian markets require permits for promotions [U].
  Rule: every contest creative carries (or links to) T&Cs, the promoter's name, and a closing date; legal review before launch.

---

## 3. AI disclosure in 2026

### 3.1 EU AI Act Article 50 (applies from 2 Aug 2026)

**The four obligations** (Commission Guidelines, table in para 6) [V] [EU-GL]:
- 50(1) Providers of interactive AI: tell people they are talking to AI.
- **50(2) Providers** of AI generating synthetic image/video/audio/text: outputs "marked in a machine-readable format and detectable as
  artificially generated or manipulated" (technical solutions "effective, interoperable, robust and reliable"). Exceptions: "assistive
  function for standard editing", or no substantial alteration of the input.
- 50(3) Deployers of emotion recognition/biometric categorisation: inform people.
- **50(4) Deployers**: disclose that **deep fake** image/audio/video content "has been artificially generated or manipulated"; and disclose
  AI-generated/manipulated **text published to inform the public on matters of public interest**, unless it underwent human review or
  editorial control with editorial responsibility. Attenuated regime for evidently artistic/creative/satirical/fictional works.
- 50(5): information "in a clear and distinguishable manner at the latest at the time of the first interaction or exposure" and
  conforming to accessibility requirements.

**Dates and penalties** [V] [EU-GL] paras 2, 152-154:
- Article 50 applies from **2 Aug 2026**. Penalties up to **EUR 15,000,000 or 3%** of worldwide annual turnover (lower of the two for
  SMEs).
- The **AI Omnibus** (Regulation (EU) 2026/1744 of 8 Jul 2026, in force 27 Jul 2026 [S] [UC-OMNI]) gives providers of generative systems
  already on the market before 2 Aug 2026 until **2 Dec 2026** for the 50(2) marking duty only; deployer labelling is unaffected [V] para 153.
- No retroactive labelling of deep fakes generated before 2 Aug 2026; but text generated earlier and published on/after 2 Aug 2026 must
  be labelled [V] para 154.

**Who is the deployer - it is usually the agency** [V] [EU-GL] paras 12-14:
- Deployer = whoever uses the AI system "under their authority" (decides purpose and how outputs are used). "Where the deployer ... is a
  legal person ... (e.g. an advertising company), the individual employees ... should not be considered as separate deployers."
- "A company that merely commissions an advertising agency to produce an advertisement, without taking decisions and exercising control
  over whether and how the advertising agency uses AI in the production process, is not a deployer." So the agency carries 50(4) for
  EU-directed work unless the client controls the AI use.
- Deployers outside the EU are in scope when they foresee use in the Union, "including by posting deep fakes on the globally accessible
  internet" (para 13). A Bangladesh-based agency making EU-facing ads is covered.
- In complex distribution chains, deployers "should take proportionate measures to ensure that the labelling ... is displayed ... at the
  point of first exposure ... (e.g., via contractual conditions with distributing partners ...)" (para 12).
- Personal, non-professional use is excluded (para 19), but any business, trade or freelance activity is professional.

**What counts as a deep fake** (Art. 3(60); Guidelines 6.1.1) [V] [EU-GL] paras 113-116:
- Four cumulative criteria: appreciable **resemblance** to **existing** (or plausibly existing) **persons, objects, places, entities or
  events** that would **falsely appear authentic or truthful**.
- "It is sufficient for simulated persons, objects, places, entities or events to resemble someone or something that exists, can
  plausibly exist or could have plausibly existed" - so realistic **synthetic people count**, as do "realistic AI-generated human avatars
  or personas".
- Out of scope: content that defies nature/biology "(such as e.g. humans flying without mechanical aids, dragons, or elephants driving
  cars)".
- No intent to deceive is needed; the assessment considers the whole foreseeable audience, including children, the elderly and less
  AI-literate people (paras 114-115).
- "A high degree of photorealism renders it more likely" to be a deep fake, but is not alone decisive (para 114).
- Minor AI edits usually do not create a deep fake: removing passers-by, lighting, colour correction, noise reduction, "background
  extensions", "adjustments or replacements of backgrounds for clearly aesthetic purposes, compositions and arrangements of existing
  products, or re-scaling of images applied in product advertisements or packaging" (para 116).
- Commission examples **of deep fakes**: AI image of two real footballers at a stadium; AI video of a celebrity influencer in an ad; a
  realistic synthetic CEO avatar; "an AI-generated image of a product in advertisement or packaging that can ... mislead as to the actual
  product appearance, characteristics or use" (p. 36).
- Commission examples **not** deep fakes: a sphinx flying over the Eiffel Tower; mice arguing about cheese in a cheese ad; an AI cartoon of
  a historical event photo; AI fictitious game environments; "a real product (e.g., a car) shown in an advertisement against an
  AI-generated background ... as long as the ad is not likely to mislead" (p. 36).

**The creative/artistic exemption is narrow for advertising** [V] [EU-GL] paras 119-124:
- Only "evidently" artistic, creative, satirical, fictional or analogous works get the lighter duty (disclose "in an appropriate manner
  that does not hamper the display or enjoyment").
- Excluded where the content's nature "is exclusively informative or commercial and recognisable as such"; "some kinds of content (e.g.
  advertisements ...) might be regarded as evidently creative or fictional in certain, specific situations, but not in others"; if content
  mixes informative and creative characters, "the informative character should always prevail".
- Listed as **not** creative: a teleshopping-style deep fake of humans advertising a product; a "realistic synthetic influencer testing
  out a sponsored real product"; "AI-generated video depicting realistic, holocaust scenes being shared on publicly available social
  media platforms" (p. 39).

**How to disclose** [V] [EU-GL] paras 117, 126, 142-144; [V] [EU-ICONS]; [S] [DLA]:
- Deployers **cannot rely on metadata or watermarks**: disclosure must be perceivable "without them needing to rely on any specific
  technical tools" (para 117).
- Clear = noticeable, understandable, accessible (including for people with disabilities); not hidden in menus, manuals or terms (para 142).
- At first exposure, for each person exposed, including "when encountering AI-manipulated deep fakes when scrolling on social media"
  (para 143).
- Deployers on very large platforms "can rely on" platform labelling tools that give a clear disclosure (para 126) - e.g. the platform's
  "AI-generated" toggle.
- **EU icons** (published 10 Jun 2026, free to use "without the need for attribution"): a Basic "AI" icon, a "Fully AI-generated" icon
  (no human-created elements apart from prompting) and a "Partially AI-modified" icon; each in black, white, and 50%-transparent
  variants; SVG/PNG downloads. Placement: clearly perceivable at first exposure, no overlay on top of it, "directly embedded into the deepfake
  ... (except for creative works)", visible when reshared or downloaded; user testing found the icon worked better with a text label
  (e.g. "modified") [V] [EU-ICONS].
- The Code says labels belong where they are noticed without hunting, "such as the top corner of an image or video"; accessible
  (high-contrast icons, screen-reader compatibility) [S] [DLA].
- **Code of Practice**: final text 10 Jun 2026; about 190 signatories by end of July 2026 [V] [EU-CoP]; Commission confirmed its adequacy
  in early July 2026 [S] [FD]; Meta signed on 28 Jul 2026 [V] [META-EUCOP]. Non-signatories must show equivalent compliance and may face
  more information requests (paras 147-148). Providers under the Code apply at least two machine-readable layers (signed metadata plus an
  imperceptible watermark) for images [S] [DLA].

**AI text** (captions, articles) [V] [EU-GL] section 6.2 (paras 130-138) and table pp. 28-29:
- Standard editing (grammar, spelling, minor stylistic polishing, **AI translations**) is exempt from 50(2) marking.
- The 50(4) text duty covers text *published* to *inform the public* on *matters of public interest* (politics, public administration,
  justice, fundamental rights, public health, environment, consumer protection/safety, economic, financial, scientific or cultural
  developments) (para 131).
- **Ordinary ad copy is outside it:** the Commission lists "AI-manipulated text that is part of a company's advertisement or product
  descriptions (not including any claims related to e.g. health, consumer safety or sustainability)" as out of scope (p. 42). So
  AI-drafted captions and headlines for normal ads need no AI-text label; health, safety and sustainability claims, corporate
  reports/investor information and public-information posts (e.g. weather or safety warnings) do, unless the exception applies.
- Exception = two cumulative conditions (para 133): (i) human review or editorial control - "deliberate examination of the substance ...
  by one or more natural persons possessing relevant knowledge", with fact-checking as a minimum (para 134); spell-checking, an editorial
  policy on paper, automated review or "cursory editorial approval" do not count (para 135); and (ii) a legal or natural person holds
  editorial responsibility, ideally with identity/contact publicly findable (para 138). Substantive AI changes after sign-off void the
  exception (para 136).

**Scope note (50(2) exceptions and closed workflows):** outputs used "only in closed loop environments in industrial and product development
workflows (for example for film, animation, games or advertising production)" need not be marked unless they are the final output
(para 68). Content mixed with human-created material still counts as synthetic (para 59). Examples needing marking include "creation of
composite images ... that modifies the representation of persons, objects, events or facts" (p. 29).

### 3.2 Other jurisdictions

| Market | Rule | Status | Tag |
|---|---|---|---|
| China | CAC Measures for Labeling AI-Generated Synthetic Content + GB 45438-2025: explicit (visible, e.g. "AI生成") and implicit (metadata/watermark) labels on AI text, images, audio, video, virtual scenes; obligations on service providers and distribution platforms | In force 1 Sep 2025 | [S] [CN-AI] |
| India | IT (Intermediary Guidelines) Amendment Rules 2026 (G.S.R. 120(E)): "synthetically generated information" (audio/visual that appears real) must be "clearly and prominently labelled", with permanent metadata/identifiers; labels may not be removed; exclusions for routine good-faith editing, document creation, accessibility; AI text excluded; the draft 10%-of-area label rule was dropped | Notified 10 Feb 2026, in force 20 Feb 2026 | [S] [IN-AI] |
| South Korea | AI Basic Act: advance notice of generative AI use, labelling of outputs (incl. machine-readable), clear labelling of realistic deepfakes; fines up to KRW 30 m; enforcement grace of at least one year | In force 22 Jan 2026 | [S] [KR-AI] |
| USA - New York | Synthetic performer disclosure in ads (GBL §396-b) | In force 9 Jun 2026 | [V] [NY-SP] |
| USA - federal | FTC Act s.5 deception; Reviews Rule bans AI fake reviews | In force | [V] [FTC-REV] |
| USA - California | AI Transparency Act (SB 942, as amended) - provider-side latent/manifest disclosures and detection tools | Operative date reported as 2 Aug 2026 | [U] |
| France | Influencer law 2023: "image virtuelle" label for AI faces/silhouettes in influencer commercial content | In force | [U] |
| UK | No AI-specific labelling statute found; CAP Code misleading-advertising rules apply | - | [U] |

### 3.3 Platform labels and how they read provenance

| Platform | What triggers a label | What the user sees | Our action | Tag |
|---|---|---|---|---|
| **Meta (organic)** | "Industry standard AI image indicators" (C2PA, IPTC) or self-disclosure; people must use the disclosure tool for photorealistic video / realistic audio | "AI info"; since 12 Sep 2024 minimally edited content has the label in the post menu, fully generated content stays visible; a more prominent label for high risk of deceiving the public | Expect labels on AI images we deliver; use the disclosure tool for realistic video/audio | [V] [META-APR24] |
| **Meta (ads)** | Meta gen-AI tools (background/image generation, animation) with significant edits; third-party gen-AI tools detected via "industry-standard detection methods, such as C2PA"; minor edits (resizing, colour correction) not labelled | "AI info" in "About this ad" (three-dot menu); placed "Next to the Sponsored label" when an AI photorealistic human appears | Tell clients up front; for EU deep fakes add our own visible label too | [V] [META-HELP-ADS] [META-ADS-25]; [S] [SMT] |
| **Meta political/social-issue ads** | Must disclose AI-created or altered photorealistic images/video/audio | Disclosure in ad | Escalate political work; never auto-produce | [V] [META-MID26] |
| **TikTok (organic)** | Creators must label realistic AIGC; auto-labels via C2PA Content Credentials, TikTok AI effects and detection; invisible watermark added | "AI-generated" label with context on how it was labelled | Label realistic content; expect auto-labels | [V] [TT-NEWS-25]; [S] |
| **TikTok (ads)** | Completely AI-generated images/video/audio, or substantial AI alteration | AIGC label via Ads Manager toggle or own clear disclaimer | Always disclose fully-AI ad visuals on TikTok, even stylised | [V] [TT-ADS] |
| **YouTube** | Creators must disclose realistic altered/synthetic content (real people saying/doing things they did not, altered real events/places, realistic scenes that never happened); not required for clearly unrealistic/animated content, colour/lighting, beauty filters, blur, AI-written scripts, thumbnails or captions | Label on the player for photorealistic content, in the description for others; YouTube may add labels itself (its own tools, C2PA, detection); "Captured with a camera" for C2PA-verified camera footage | Tick the disclosure for realistic video; thumbnails are exempt | [V] [YT-GENAI]; [S] [YT-CAM] |
| **LinkedIn** | Reads C2PA Content Credentials | "CR" icon; click shows tool, signer, time, AI involvement | Expect the CR icon on our images; brief clients | [S] [LI-FORT] |
| **Pinterest** | IPTC metadata + classifiers + self-report | "AI modified" label at the bottom left in close-up; for ads, disclosure behind the ellipsis ("modified with AI" or "contains an AI-generated person") | Expect labels | [V] [PIN] |
| **Google** | Search "About this image" shows whether an image was created/edited with AI (C2PA); Ads uses C2PA signals "to inform how we enforce key policies"; SynthID watermark detection; **Merchant Center requires AI-generated product images to keep IPTC DigitalSourceType metadata** (TrainedAlgorithmicMedia etc.) and not strip it | Varies | Never strip metadata from product images | [V] [GOOG-C2PA] [SYNTHID]; [S] [GMC] |
| **X** | Labels or removes deceptive synthetic/manipulated media likely to cause harm; C2PA display not confirmed | Contextual label | Rely on our own visible label where needed | [U] [X-MM] |

Upstream: OpenAI says images from ChatGPT, Codex and the API carry C2PA metadata and (from May 2026) a SynthID watermark; OpenAI's
Content Provenance API checks both signals and reports `not_detected` when "metadata was stripped" or the watermark degraded
[S] [OAI-C2PA-SYNTHID]; [V] [OAI-PROV]. SynthID is designed to survive cropping, filters and lossy compression [V] [SYNTHID].

### 3.4 Provenance mechanics for our pipeline

**IPTC Digital Source Type** (vocabulary modified 2024-10-23) [V] [IPTC-DST]. XMP property: `Iptc4xmpExt:DigitalSourceType`, value is the
full URI `http://cv.iptc.org/newscodes/digitalsourcetype/<term>`.

| Our output | Correct term | Definition (IPTC) |
|---|---|---|
| Raw GPT Image output used as-is | `trainedAlgorithmicMedia` | "Digital media created algorithmically using an Artificial Intelligence model trained on captured content" |
| Finished graphic = AI image + typeset text/logo/vector composited in HTML | `compositeSynthetic` | "Mix or composite of several elements, at least one of which is Generative AI" |
| Real client photo edited with generative fill/inpainting/outpainting | `compositeWithTrainedAlgorithmicMedia` | "Augmentation, correction or enhancement using a Generative AI model, such as with inpainting or outpainting operations" |
| Real photo with non-generative sharpening/denoise only | `algorithmicallyEnhanced` | "Modification or correction by algorithm without changing the main content" |
| Human-made vector/typographic design with no gen-AI pixels | `digitalCreation` | "Media created by a human using non-generative tools" |
| Composite of real captures only | `compositeCapture` | "Mix or composite of several elements that are all captures of real life" |

So "keep trainedAlgorithmicMedia" is right for the raw asset; the composited deliverable is more honestly `compositeSynthetic`, with the raw
AI image kept as a C2PA ingredient that retains its own `trainedAlgorithmicMedia` claim. (Google Merchant Center accepts
TrainedAlgorithmicMedia, CompositeSynthetic and AlgorithmicMedia [S] [GMC].) Whether Meta/TikTok/Pinterest detectors treat
`compositeSynthetic` exactly like `trainedAlgorithmicMedia` was not verified [U] - test with a private upload.

**C2PA for composites** [V] [C2PA-SPEC] (spec 2.2):
- Every standard manifest must contain exactly one `c2pa.created` or `c2pa.opened` action, as the first action.
- `c2pa.opened` requires one ingredient with relationship `parentOf` (use when editing an existing AI image as the base).
- `c2pa.placed` requires ingredients with relationship `componentOf` (use when the HTML canvas is new and the AI image is placed into it).
- Recommended for the HTML renderer: new manifest with `c2pa.created` (digitalSourceType `compositeSynthetic`, softwareAgent = our
  renderer), then `c2pa.placed` referencing the GPT image as a `componentOf` ingredient (its original OpenAI manifest embedded), then
  `c2pa.edited` for text/logo layers; sign; embed in the PNG/JPEG; verify with a C2PA validator.
- Any tool that re-encodes without C2PA support breaks the chain: "Avoid screen-shotting or re-exporting the file through tools that remove
  metadata ... Always work with the original exported file"; edit with C2PA-aware tools "so that the edit history can be appended"
  [V] [C2PA-DEPLOY] section 5.3.
- **Signing and trust:** conforming validators check certificates against the C2PA Trust List; the Interim Trust List was frozen on
  1 Jan 2026; conforming generator products need a certificate traceable to the Trust List [V] [C2PA-TRUST]. A self-signed certificate
  keeps an internal audit trail but will not show as a trusted signer. Getting a trusted certificate means going through the conformance
  programme (launched 4 Jun 2025) [S] [C2PA-CONF].
- **Platforms strip metadata** on delivery (most social networks re-encode). Labels there come from upload-time detection and toggles,
  so the visible label (when needed) must be burned into the pixels, and the master files with manifests must be archived.

**Never fake EXIF.** Do not write camera Make/Model/Lens, exposure data, `DateTimeOriginal` or GPS into AI or composite images; do not set
`digitalCapture`; set `Software`/`CreatorTool` truthfully. Do not attempt to remove or weaken SynthID or C2PA - it contradicts the house rule,
TikTok/Meta policies and (for Indian platforms) the rule against removing labels/metadata [S] [IN-AI].

### 3.5 Practical agency guidance: AI-assisted design vs fully AI imagery

| Tier | What it is | EU Art. 50(4) visible label? | Platform expectations | Metadata |
|---|---|---|---|---|
| 0 | No generative pixels (typeset + licensed photos/vectors) | No | None | `digitalCreation` / none |
| 1 | AI-assisted standard edits: upscaling, denoise, colour, minor cleanup, background removal/extension or replacement for aesthetic purposes, product rescaling | Normally no - para 116 and 50(2) exception examples | TikTok counts background removal/modification as insignificant; Meta skips minor edits | `algorithmicallyEnhanced` or `compositeWithTrainedAlgorithmicMedia` if generative fill used |
| 2 | AI visuals that are clearly stylised, illustrative or fantastical, composited with typeset text (festive illustrations, abstract textures, surreal scenes) | No (not a deep fake: no false appearance of authenticity) - still machine-marked upstream | **TikTok ads: disclose** (fully AI images); Meta will show "AI info" in the menu; YouTube not required | `compositeSynthetic` + C2PA ingredients |
| 3 | Photorealistic AI people, places, products or events | **Yes, likely a deep fake** for EU audiences (synthetic people count; photoreal product renders that could mislead are deep fakes) | Meta shows "AI info" next to Sponsored for photoreal humans; NY synthetic performer disclosure for ads reaching NY; TikTok/YouTube disclosures; Indian platforms require labels; China explicit label | `compositeSynthetic`/`trainedAlgorithmicMedia` + C2PA + burned-in label |
| 4 | Real identifiable people, celebrities, manipulated real footage, historical tragedies, political/social-issue content | Yes, and usually **do not produce** without written consent and legal sign-off | Identity-misuse bans (TikTok), unauthorised endorsements (Meta), political AI disclosures | Full chain + legal file |

Defaults that keep agencies out of trouble:
1. Prefer real product photography; if AI renders a product, it must match the real product exactly (else it is misleading advertising and
   an EU deep fake).
2. Prefer illustration over photorealism for synthetic people when the client does not need realism.
3. Never photoreal-AI a real historical event, war, genocide, disaster or national tragedy (Bangladesh 1952/1971 scenes included).
4. Burned-in label wording (localise): "AI-generated image" / "Image generated with AI" / "AI-modified"; or the EU "AI" icon plus word.
5. Toggle the platform's AI disclosure as well (Meta, TikTok, YouTube) when a label is required.
6. Put "AI-generated" in the alt text/caption too, for screen-reader users (Art. 50(5) accessibility).
7. Delivery note to the client listing, per asset: AI tier, model, date, label applied or not and why, and who publishes where (the
   contract should oblige the client/distributor to keep labels intact - EU Guidelines para 12).
8. Keep records: prompts, model/version, generation timestamps, source images and licences, manifest files, reviewer names and review
   dates (evidence of editorial control for text).

---

## 4. Accessibility for social and print graphics

### 4.1 Contrast
- WCAG 2.2 SC 1.4.3 (AA): text and images of text at least **4.5:1**; large-scale text at least **3:1**. Large = at least 18 pt or 14 pt
  bold (about 24 px / 18.5 px in CSS; CJK equivalents). Logotypes and incidental text in photos are exempt. [V] [WCAG-143]
- 1.4.6 (AAA) 7:1 / 4.5:1; 1.4.11 non-text contrast 3:1 for meaningful graphics and UI [U - not fetched, standard values].
- For text over photos, measure against the worst-case background pixels behind the glyphs (add a scrim/gradient/solid panel when needed)
  [U - method].
- Computed palette facts [C]: Okabe-Ito blue #0072B2 vs white 5.19:1 (text-safe); vermillion #D55E00 3.87:1 and bluish green #009E73 3.42:1
  (large text only); orange #E69F00 2.25:1, sky blue #56B4E9 2.31:1, yellow #F0E442 1.32:1 vs white (never for white text; use black text:
  9.3, 9.1, 15.9:1).

### 4.2 Minimum text size at display size
WCAG has no minimum font size; the useful rule is **effective CSS px after the platform scales the image down** [derived]. Scale =
display width / canvas width. Minimum canvas text height for typical worst-case displays [C]:

| Canvas and display | Scale | 12 px floor | 14 px body | 16 px comfortable | 24 px "large" (3:1 allowed) |
|---|---|---|---|---|---|
| 1080-wide feed or Stories on a 375-px phone | 0.347 | 35 px | 41 px | 47 px | 70 px (bold 54 px) |
| 1200x628 link/landscape ad on phone | 0.312 | 39 px | 45 px | 52 px | 77 px |
| 1600x900 X image on phone | 0.234 | 52 px | 60 px | 69 px | 103 px |
| 1200x1200 LinkedIn on desktop (~555 px) | 0.463 | 26 px | 31 px | 35 px | 52 px |
| 1280x720 YouTube thumbnail in sidebar (~168 px) | 0.131 | 92 px | 107 px | 122 px | 183 px |

Practical skill defaults: on 1080-wide canvases, body/detail text >= 40 px, headline >= 72 px, legal fine print >= 30 px (and repeat it in
the caption); add 10-20% for Bengali, Devanagari, Arabic/Urdu, Thai and CJK body text (dense glyphs, stacked marks) [U - practice].

Print and signage:
- Large print for people with sight loss: "A minimum size of 16 point is recommended"; 50-65 characters per line (under 65 preferred,
  never over 80); type above 28 pt can be counter-productive [V] [GOVUK-FORMATS]. General clear-print body text: 12-14 pt minimum [U].
- Signage/posters (ADA 2010 Standards 703.5.5, visual characters): at 40-70 in mounting height, 5/8 in minimum under 6 ft viewing
  distance, plus 1/8 in per foot beyond 6 ft; above 70 in to 10 ft: 2 in minimum under 15 ft, plus 1/8 in per foot beyond; above 10 ft:
  3 in under 21 ft, plus 1/8 in per foot beyond; stroke width 10-30% of character height; spacing 10-35%; non-glare finish, light-on-dark
  or dark-on-light [V] [ADA-703].

### 4.3 Alt text for social images
- W3C decision tree [V] [WAI-ALT]: if an image contains text that appears nowhere else, "use the alt attribute to include the text of the
  image"; informative images get a brief description of the meaning; complex images need the information elsewhere; decorative images empty.
- Social rules (derived from W3C + practice) [U]:
  - Write alt text for every post; put all essential in-image text verbatim (greeting, offer, date, time, venue, price, URL).
  - Describe purpose, not pixels: "Eid ul-Fitr greeting from Acme: crescent moon and lanterns over a night skyline; text reads 'Eid Mubarak'".
  - Do not start with "Image of"; mention the logo only if it matters; keep it to 1-2 sentences (about 125-250 characters) and put long
    information in the caption.
  - Write alt text in the post's language; bilingual alt text may be mispronounced because platform alt fields carry no language tag.
  - Hashtags in CamelCase (#InternationalMotherLanguageDay); few emojis (screen readers read their names); no ALL CAPS.
  - If the image is AI-generated and labelled, say so in the alt text.
  - Platform limits differ (X allows up to 1,000 characters [U]); do not rely on automatic alt text.

### 4.4 Colour-blind-safe palettes
- About 1 in 12 men have colour vision deficiency; the most common type makes red and green hard to tell apart; others make blue and yellow
  look the same or remove colour entirely [V] [NEI].
- Okabe & Ito Colour Universal Design: "Use not only different colors but also a combination of different shapes, positions, line types
  and coloring patterns"; avoid red-green pairs, use magenta and green instead [V] [OKABE-ITO]. Commonly used hex set [U - as implemented
  in plotting libraries]: black #000000, orange #E69F00, sky blue #56B4E9, bluish green #009E73, yellow #F0E442, blue #0072B2, vermillion
  #D55E00, reddish purple #CC79A7. Paul Tol's "bright" scheme is an alternative [U].
- WCAG 1.4.1: colour must not be the only means of conveying information [U - standard].
- Run a deuteranopia/protanopia/tritanopia simulation on infographics and offer badges.

### 4.5 Do not put essential information only in images
- WCAG 1.4.5 Images of Text (AA): use real text rather than images of text unless customisable or "essential" (logotypes) [V] [WCAG-145];
  people cannot enlarge, recolour or respace text inside images.
- Social graphics are images of text by nature, so the caption and alt text must carry everything essential; web banners should use
  live HTML text where possible.
- EU AI Act disclosures must also meet accessibility requirements; Directive 2019/882 (European Accessibility Act) and Directive 2016/2102
  are the reference points [V] [EU-GL] para 144.
- Animated/video: no content flashing more than three times per second (WCAG 2.3.1 [U]); Google also rejects "strobing, flashing" images
  [V] [G-EDIT]; caption all video.
- Brochure PDFs: tagged PDF with document language, reading order, real text (not outlines), alt text on figures, bookmarks (PDF/UA,
  ISO 14289) [U].

### 4.6 RTL layout (Arabic, Hebrew, Persian, Urdu)
- Put `dir="rtl"` on the root element and set `lang` separately; "Do not use CSS to apply base direction"; use `dir="auto"`/`bdi` for inserted
  text of unknown direction; prefer CSS logical properties (start/end) [V] [W3C-DIR].
- Arabic-script pages are laid out right to left [V] [W3C-ALREQ]. Mirror the reading order: headline block and primary element start at the
  top right; arrows, "next" chevrons, progress bars, timelines, step numbers and before/after order flip.
- Do not mirror: logos and brand wordmarks, photographs of real objects, clocks, media play controls, checkmarks [S] [APPLE-RTL]; do not flip
  Latin text or numbers.
- Do not letter-space Arabic: moving joined letters "closer to or further from each other creates undesirable results"; justify with
  kashida/tatweel sparingly [V] [W3C-ALREQ]. No faux italics; no uppercase transforms.
- Digits: choose per market - European digits (Maghreb), Arabic-Indic (much of the Eastern Arab world), Eastern Arabic-Indic (Iran,
  Afghanistan) [V] [W3C-ALREQ]; keep phone numbers and prices in a bidi-isolated span.
- Fonts (OFL, verify each) [U]: Arabic - Noto Naskh Arabic, Noto Kufi Arabic, IBM Plex Sans Arabic, Tajawal, Cairo, Almarai; Persian -
  Vazirmatn; Urdu - Noto Nastaliq Urdu (Nastaliq expected); Hebrew - Noto Sans Hebrew, Heebo, Assistant, Rubik, Frank Ruhl Libre. Give
  Arabic/Urdu extra line height (about 1.5-1.8, Nastaliq more) [U].
- "Avoid embedding text in images ... If images must contain text, create separate assets for RTL" [S] [APPLE-RTL].

### 4.7 Readable fonts for non-Latin scripts
- Set `lang` correctly: Simplified Chinese, Traditional Chinese, Japanese and Korean "may share the same code point for an ideographic
  character, but speakers of these languages expect the glyphs used to vary"; `lang` also drives hyphenation, speech output and spell
  checking [V] [W3C-LANG]. Use Noto Sans SC / TC / HK / JP / KR (or Source Han) matched to the market.
- Line breaking: Thai, Lao, Khmer (and Myanmar) have no spaces between words and need dictionary-based breaking; CJK breaks between
  characters with kinsoku rules (no opening bracket at line end, etc.) [V] [W3C-LINEBREAK]. Insert zero-width spaces or manual breaks for
  headlines.
- Indic scripts (Bengali, Devanagari, Tamil, etc.): conjuncts, reph, matras and vowel signs need an OpenType-shaping-capable font and
  engine (Chrome/HarfBuzz is fine); allow extra line height for top and bottom marks. Recommended families [U]: Bengali - Noto Sans/Serif
  Bengali, Hind Siliguri, Anek Bangla, Tiro Bangla, Baloo Da 2; Devanagari - Noto Sans Devanagari, Mukta, Hind, Tiro Devanagari Hindi;
  Tamil - Noto Sans Tamil, Mukta Malar, Catamaran; others - the matching Noto family.
- Legacy non-Unicode encodings to reject: Bijoy/SutonnyMJ (Bengali), Zawgyi (Myanmar) [U].
- Vietnamese needs fonts with stacked diacritics (e.g. Be Vietnam Pro, Noto) [U].
- **Never let the image model render non-Latin text** (Bengali, Arabic, Devanagari, CJK, Thai, Hebrew): typeset it in HTML with the right
  font and `lang`, and have a native reader check it.

---

## 5. Cultural colour and symbol meanings

Treat this table as prompts for a local check, not as rules of nature. Meanings vary within countries and change over time.

### 5.1 Colours

| Colour | Positive associations | Risky associations | Tag |
|---|---|---|---|
| White | Purity, weddings (West); Eid clothing in South Asia | Traditional mourning in Chinese culture [S]; historical mourning in Thailand and medieval European royals [S]; Hindu widowhood and funerals in South Asia [U]; Korean/Japanese funerals [U] | [S]/[U] |
| Black | Elegance, premium (West) | Mourning in Western Europe/North America and in Japan's mofuku [S]; Bangladesh 21 Feb black badges [S]; inauspicious in some Hindu ceremonies [U] | [S]/[U] |
| Red | Luck, prosperity, weddings (China, India); festive LNY red envelopes | Danger/debt/warnings (West); taboo near a death in Philippine custom [S]; names written in red ink (Korea, China) associated with death [U]; South Africa mourning [U] | [S]/[U] |
| Green | Islam and paradise; flags of Saudi, Pakistan, Bangladesh; Ireland; eco | A green hat on a man (China) = cuckold [U]; party-political green in some markets [U] | [U] |
| Yellow/gold | Imperial in China; prosperity; marigolds in Diwali and Dia de Muertos | Yellow Star imagery (Holocaust) never; political yellow in Thailand/Malaysia protest history [U]; royal colour in Thailand/Malaysia [U] | [U] |
| Purple | Royalty (UK), Lent/Advent | Widows' mourning in Thailand [S]; mourning in Brazil [U]; Rwanda commemoration uses purple [U] | [S]/[U] |
| Saffron/orange | Sacred in Hinduism, Buddhism, Sikhism | Political connotations in India [U]; Orange Order (Protestant) vs green (Catholic) in Northern Ireland [U] | [U] |
| Blue | Trust (global); protective evil-eye blue (Turkey, Iran, Greece) [U]; Krishna | - | [U] |

### 5.2 Numbers
- 4: avoid in China, Japan, Korea, Taiwan, Hong Kong, Singapore, Malaysia, Vietnam (sounds like "death"); buildings skip floors, products skip
  model numbers [S] [WIKI-TETRA]. Watch prices (4.44), quantities, bundle counts, slide numbers.
- 8 (prosperity), 6 (smooth), 9 (longevity) positive in China; 250 insult; 520 "I love you"; 1314 "a lifetime" [S] [WIKI-CN-NUM].
- 9 unlucky in Japan (sounds like "suffering") [U]; 13 (West), 17 (Italy) unlucky [U].
- 88 = "Heil Hitler" code, often combined with 14 as 1488 or 14/88; the ADL notes innocent uses exist (ham radio, NASCAR) [V] [ADL-88].
  Avoid 88/1488/14 as decorative or promo numbers for Western markets (e.g. "88% off", "SAVE88").
- 786 is used by many South Asian Muslims as a numeric stand-in for "Bismillah" - do not use it flippantly [U].
- Russia/Eastern Europe: even numbers of flowers are for funerals; bouquets for celebrations use odd numbers [U].

### 5.3 Gestures (check every AI-generated hand)
- OK sign: vulgar or insulting in Turkey, Tunisia, Greece, parts of the Middle East, Brazil and parts of Latin America/Germany; "zero/
  worthless" in France; money in Japan [S] [WIKI-OK]. The ADL notes a 2017 4chan hoax tied it to white power, but "the overwhelming usage ...
  is still its traditional purpose" [V] [ADL-OK].
- Thumbs-up: an insult in Iran [S] [WIKI-THUMB]; also reported offensive in parts of West Africa and the Middle East [U].
- V-sign palm inward: insult in UK/Australia/NZ; horns (corna) insult in Italy/Spain; beckoning finger rude in the Philippines; soles of feet
  offensive in the Middle East and Thailand; left hand for eating/giving offensive in the Middle East, South Asia and much of Africa; touching
  heads (Thailand); open-palm moutza (Greece) [U].

### 5.4 Animals and objects
- Pigs/pork: avoid for Muslim and Jewish audiences [U]. Dogs: avoid in home/food scenes for conservative Muslim audiences [U]. Cows: sacred
  for Hindus - avoid beef imagery in Indian Hindu contexts; cattle are central to Eid al-Adha in Bangladesh (show calmly, no slaughter) [U].
- Owls: "fool" (ullu) in Hindi/Urdu slang, bad omen in some regions, but Lakshmi's vehicle [U]. Black cats: bad luck in the US and parts
  of Europe, good luck in Japan/UK [U]. Turtles/tortoises as insults in China [U]. Dragons: auspicious in China, evil in Western lore [U].
  Crows: death omen in some cultures [U].
- Clocks, umbrellas, pears and sharp objects as gifts are unlucky in China [U]; white chrysanthemums are funeral flowers in Japan, Korea
  and parts of Europe (All Saints' Day) [U].

### 5.5 Imagery sensitivities
- No depictions of the Prophet Muhammad; no sacred Arabic text (Allah, Quranic verses) generated by AI or placed on floors, footwear,
  packaging meant to be discarded, or near alcohol/pork [U].
- Hindu deities, Buddha images, crosses, the Khanda and the Star of David: never on footwear, underwear, toilets, floors or doormats;
  Buddha heads are not decor in Thailand/Sri Lanka [U].
- Swastika: auspicious for Hindus, Buddhists and Jains in Asia, but a Nazi symbol for Western audiences and legally restricted in Germany
  [U]; the Rising Sun Flag is offensive in Korea and China [S].
- Never blackface/brownface, "fairness" skin-whitening messaging, sacred headdresses as costume, or pan-Asian costume mash-ups [U].
- Same-sex couples, alcohol, gambling, dating and revealing clothing are legally restricted in some markets (e.g. parts of the Gulf,
  Russia's "LGBT propaganda" law, Indonesia) - escalate to the client; do not self-censor for markets where there is no such rule [U].
- Protest, war and disaster imagery: never as an aesthetic prop (Pepsi 2017 [S]).

---

## 6. Recommendations for our skill

### 6.1 Inputs the skill must collect before designing
1. **Market profile** per deliverable: country/region, audience languages and scripts, writing direction, digit style, religious/cultural
   communities (including diaspora), platform(s), paid vs organic, whether it reaches the EU, New York, China, India or Korea.
2. **Occasion record** (for day posts): official name per locale, tone class, verified date with source URL and retrieval date, allowed and
   banned phrases, approved symbols, commercial allowance (none/soft/full).
3. **Asset provenance plan**: which pixels are generative, AI tier (3.5), labelling decision.

Never infer any of these from the operator's language, location or clock (house rule 1).

### 6.2 Lint rules (machine-checkable where possible)

Severity: **BLOCK** = cannot export; **WARN** = export only with a recorded human override; **INFO** = note in QA report.

**Day posts**
- `DAY-001 BLOCK` Solemn-day greeting: if tone = solemn or fast, block "Happy", "Congratulations", "Celebrate", "Mubarak", "শুভ", "快乐",
  "Feliz", "Joyeux", exclamation marks, and party emojis (per-locale lexicon).
- `DAY-002 BLOCK` Commerce on solemn days: block price patterns, currency symbols, "%", "off", "sale", "offer", "buy", "shop now", promo codes,
  CTA buttons, product packshots, contest mechanics.
- `DAY-003 BLOCK` Unverified variable date: a dated creative for a lunar/lunisolar/moon-sighting day needs a source URL + market + year;
  otherwise render undated or produce two variants (X and X+1).
- `DAY-004 WARN` Collision check: flag same-day or adjacent solemn/celebratory pairs in the same market (e.g. Remembrance Sunday and Diwali on
  8 Nov 2026; Good Friday and Bangladesh Independence Day on 26 Mar 2027).
- `DAY-005 WARN` Naming by market: Lunar New Year / Chinese New Year / Seollal / Tet; Diwali / Deepavali; Eid ul-Azha spelling per locale;
  Bijoya Dashami vs Dussehra.
- `DAY-006 BLOCK` Tradition mixing: symbol co-occurrence lexicon (e.g. hanukkiah + Christmas tree/Santa; seven-branch menorah labelled
  Hanukkah; Taj Mahal in Eid art; Chinese lanterns as Diwali hero; church + crescent; alcohol near any religious symbol).
- `DAY-007 WARN` Partisan/contested days (Bangladesh national days removed or added since 2024, Kashmir Solidarity Day, Australia Day,
  Columbus Day, Israel/Palestine): require explicit client instruction.
- `DAY-008 INFO` News check reminder before publishing any scheduled post.

**Symbols, flags, maps**
- `SYM-001 BLOCK` No AI-generated flags, emblems, maps, monuments or sacred text; must come from the vector/asset library.
- `SYM-002 BLOCK` Flag geometry check against spec (Bangladesh 10:6, disc r = L/5 at 9/20 L; India 3:2 with 24-spoke chakra; EU 12 stars;
  US 50/13; Saudi two-sided Shahada).
- `SYM-003 BLOCK` Flag misuse: no text or logos on flags; no flags as apparel or on disposable items; no Saudi flag on merchandise; show
  half-mast (or no flag) on mourning days where custom requires (Bangladesh 21 Feb).
- `SYM-004 BLOCK` Maps with disputed territories unless client-approved market map.
- `SYM-005 BLOCK` Forbidden-in-market symbols: swastika forms for Western markets; Rising Sun rays for KR/CN; Nazi codes 88/1488/14 as promo
  numbers for Western markets; the number 4 in prices/quantities for East Asian markets (WARN).
- `SYM-006 WARN` Hand-gesture scan on generated people (OK sign, thumbs-up, V-sign, left-hand eating) against the market list.

**Legal**
- `LEG-001 BLOCK` Third-party logos/trademarks without a permission record or official badge rules; no platform names in LinkedIn ads.
- `LEG-002 BLOCK` Event marks for non-sponsors (Olympic words/rings, World Cup, Super Bowl, mascots, trophies).
- `LEG-003 BLOCK` Real or look-alike people without a release; celebrity names in prompts.
- `LEG-004 BLOCK` Copyrighted characters or "in the style of <living artist/studio/brand>" prompts.
- `LEG-005 BLOCK` Font licence registry: every font must have an entry; reject fsType = 2 for PDF embedding; reject non-Unicode legacy
  fonts; commercial fonts need server-rendering rights for automated output.
- `LEG-006 BLOCK` Testimonials: require a customer-permission record; block AI faces/names/quotes in testimonial layouts; star ratings need a
  source and date.
- `LEG-007 WARN` Health/finance/beauty: flag cure words, "guaranteed", "risk-free", "instant", "No. 1/best" (and China superlatives),
  before/after layouts (block on TikTok and when targeted to under-18s on Meta), body close-ups of fat, "Are you ...?" attribute
  questions (Meta).
- `LEG-008 BLOCK` Contest creatives must show or link T&Cs, promoter name, closing date; Facebook: no "share/tag to enter"; flag NY/FL
  prize totals over USD 5,000 for registration.
- `LEG-009 WARN` Stock licence check: editorial-only, sensitive-use, missing model release, unmodified resale.
- `LEG-010 BLOCK` Political/social-issue ads: stop and escalate (AI disclosure rules, LinkedIn ban).

**Ads formatting**
- `AD-001 WARN` Google RDA/PMax export mode: deliver clean image assets with no overlaid text, logos or buttons; no collages; no plain white
  composite backgrounds.
- `AD-002 BLOCK` Fake UI: play/download/close buttons, fake notifications, fake input fields.
- `AD-003 WARN` Sensational/negative-life-event fear appeals; excessive caps or punctuation.
- `AD-004 BLOCK` Flashing more than three times per second in animated output.

**AI provenance and labelling**
- `AI-001 BLOCK` Every export carries IPTC `DigitalSourceType` (term per 3.4) and, when AI pixels exist, a C2PA manifest listing the AI
  ingredient; verify the manifest after writing.
- `AI-002 BLOCK` Never write camera EXIF (Make, Model, Lens, exposure, DateTimeOriginal, GPS) on AI or composite images; never set
  `digitalCapture`.
- `AI-003 BLOCK` Never strip or degrade C2PA/SynthID; never screenshot-launder an AI image.
- `AI-004 BLOCK` Deep-fake classifier: if the image contains photoreal people, real-looking places, products or events and the audience
  includes the EU (or the ad reaches NY with a synthetic human, or distribution in China/India), require a burned-in label (EU icon + word)
  placed top corner, legible at display size, contrast at least 3:1 for the icon and 4.5:1 for text, plus alt-text mention and platform toggle.
- `AI-005 BLOCK` TikTok ads with fully AI-generated visuals: require AIGC toggle or own disclaimer.
- `AI-006 BLOCK` AI-rendered product must match the real product (reference-photo comparison); otherwise use real photography.
- `AI-007 BLOCK` No photoreal AI depictions of real historical tragedies, wars, genocides, disasters or real news events.
- `AI-008 INFO` Client briefing line: "Meta, TikTok, LinkedIn and Pinterest may show an AI label on this image because it carries honest
  provenance data."

**Accessibility**
- `A11Y-001 BLOCK` Contrast: 4.5:1 for text under the large threshold at display size; 3:1 for large text and meaningful graphics; measure
  against worst-case background pixels.
- `A11Y-002 BLOCK` Minimum text size at display size per the 4.2 table (default 1080-wide canvas: body >= 40 px, headline >= 72 px, fine print
  >= 30 px and repeated in caption; +10-20% for complex scripts).
- `A11Y-003 BLOCK` Alt text produced for every image; includes all essential in-image text; language matches the post.
- `A11Y-004 WARN` Essential info (date, time, place, price, URL, T&Cs) duplicated in caption.
- `A11Y-005 WARN` Colour-only encoding; red/green pairs; fail on CVD simulation.
- `A11Y-006 BLOCK` RTL: `dir` + `lang` set; mirrored layout; no letter-spacing on Arabic; logos and photos not mirrored; digits per market.
- `A11Y-007 BLOCK` Non-Latin text must be typeset (never generated), with a script-appropriate Unicode font and correct `lang`; native-reader
  check recorded.
- `A11Y-008 WARN` Print: body text >= 12 pt; large-print variants >= 16 pt; line length 50-65 characters; signage heights per ADA table.
- `A11Y-009 WARN` Brochure PDFs: tagged, language set, reading order, figure alt text, real text.

### 6.3 Checklists

**Brief intake**
- [ ] Market profile complete (6.1); audience languages and scripts named; RTL/digits decided.
- [ ] Occasion record with verified date, tone class, naming, allowed phrases/symbols.
- [ ] Third-party assets listed with permissions (logos, photos, fonts, people, music).
- [ ] Claims list (health, finance, "best", prices) with substantiation owner.
- [ ] AI tier chosen per asset; labelling decision recorded with reason.

**Pre-export QA**
- [ ] Lint rules pass (6.2) or overrides recorded with a name.
- [ ] Flags/maps/monuments/sacred text from library, not model.
- [ ] Native-language check of every non-English line (typeset, correct glyphs).
- [ ] Contrast and size at display size; CVD simulation; alt text written.
- [ ] Provenance written (IPTC + C2PA) and verified; no camera EXIF.
- [ ] Label burned in where required; platform toggle noted in the delivery sheet.

**Pre-publish (client or agency)**
- [ ] Date confirmed on the day (moon-sighting announcements, national mourning, breaking news).
- [ ] Platform-specific toggles set (Meta AI disclosure, TikTok AIGC, YouTube altered/synthetic).
- [ ] Contest T&Cs live and linked.
- [ ] Caption carries essential info, hashtags CamelCase, alt text pasted.

### 6.4 Day-post rules (summary for the generator)
1. Choose occasions from the client's market calendar, not the operator's.
2. Verify the date from an official list for that market and year; store the source.
3. Pick the tone class; apply the template (1.5); solemn = no commerce, no "Happy", muted palette, small or no logo.
4. One tradition per creative; symbols from the approved lexicon; no AI-drawn flags, monuments or scripts.
5. Name the festival the local way; greeting in local script, typeset, native-checked.
6. Offers go in a separate creative, never in the greeting.
7. For moon-sighting festivals, prepare undated or two-date variants; publish after the announcement.
8. Check collisions and the news before publishing.
9. Alt text and caption carry the greeting and essential details.

### 6.5 Labelling guidance (summary)
1. Always honest metadata: IPTC DigitalSourceType (raw AI = `trainedAlgorithmicMedia`; composite design = `compositeSynthetic`; AI-edited
   photo = `compositeWithTrainedAlgorithmicMedia`) + C2PA manifest with the AI image as an ingredient; archive masters.
2. Visible label only where the law or platform requires it - but then burned into the image (metadata alone never satisfies EU Art. 50(4)):
   - EU audience + deep fake (photoreal persons/places/objects/events that could pass as real) -> EU "AI" icon with a word ("AI-generated" /
     "AI-modified"), top corner, legible, contrasting, embedded so it survives resharing; plus alt text and platform toggle.
   - Ads reaching New York with an AI synthetic human -> conspicuous on-ad disclosure (e.g. "This ad features an AI-generated person").
   - TikTok ads with fully AI visuals -> AIGC toggle or own disclaimer.
   - China -> explicit label (e.g. "AI生成") + implicit metadata. India platforms -> prominent label for realistic synthetic visuals.
   - Political/social-issue ads -> escalate; platform AI disclosures mandatory.
3. Stylised/fantastical AI art composited with typography (tier 2) needs no EU visible label, but platforms may still auto-label it; clients
   can choose to label everything as a transparency policy.
4. AI-drafted copy: ordinary ad/product copy needs no EU AI-text label; copy with health, consumer-safety or sustainability claims, investor
   information or public-information content needs substantive human review (fact-checked) + named editorial responsibility, logged -
   otherwise label it as AI-generated text.
5. Tell the client in writing what is AI, what is labelled, why, and that labels must not be removed downstream.

### 6.6 Open items to verify before hard-coding
- Current Bangladesh national-day list after the February 2026 change of government (Cabinet Division).
- Exact Meta weight-loss before/after rule (Health and wellness page changes often).
- Instagram promotion guidelines and X ad rules on AI (pages blocked here).
- Adobe Fonts licence page; each commercial font EULA for server rendering.
- EU UCPD Annex I 23b/23c wording and UK DMCC fake-review provisions (EUR-Lex and legislation.gov.uk blocked here).
- Whether platform detectors treat `compositeSynthetic` the same as `trainedAlgorithmicMedia` (test upload).
- France "image virtuelle" and Norway retouch-label scope for AI models; California SB 942 operative status.
- 2027 dates for Rosh Hashanah 5788, Holi, Mid-Autumn/Chuseok, Vesak outside Singapore, and all Islamic dates per target country.

---

## 7. Sources (all accessed 2026-09-23 unless noted)

EU AI Act and labelling
- [EU-GL] European Commission, Guidelines on the implementation of the transparency obligations for certain AI systems under Article 50 of
  the AI Act, C(2026) 5054 final, Annex, Brussels 20.7.2026 -
  https://ai-act-service-desk.ec.europa.eu/sites/default/files/2026-07/guidelines_on_the_implementation_of_the_transparency_obligations_for_certain_ai_systems_under_article_50_of_the_ai_act_bzptwqhk0ikg1dtlddap41psfy_131215.pdf [V]
- [EU-GL-page] https://digital-strategy.ec.europa.eu/en/policies/guidelines-ai-transparency-obligations (last update 6 Aug 2026) [V]
- [EU-GL-news] https://digital-strategy.ec.europa.eu/en/news/commission-publishes-guidelines-transparency-obligations-providers-and-deployers-certain-ai-systems (20 Jul 2026) [V]
- [EU-CoP] https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content (final 10 Jun 2026; ~190 signatories by end Jul 2026) [V]
- [EU-CoP-news] https://digital-strategy.ec.europa.eu/en/news/commission-publishes-code-practice-marking-and-labelling-ai-generated-content (10 Jun 2026) [V]
- [EU-CoP-FAQ] https://digital-strategy.ec.europa.eu/en/faqs/code-practice-transparency-ai-generated-content [V]
- [EU-ICONS] https://digital-strategy.ec.europa.eu/en/policies/eu-icons-labelling-ai-generated-content (updated 10 Aug 2026) [V]
- [EU-OMNI] Regulation (EU) 2026/1744 (Digital Omnibus on AI) - https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng (page not readable here; details via [EU-GL] para 153 and [UC-OMNI]) [S]
- [AIA] Regulation (EU) 2024/1689, Article 50 - https://eur-lex.europa.eu/eli/reg/2024/1689/oj ; https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50 [V via EU-GL]
- [GD-OMNI] Gibson Dunn, "EU AI Act Omnibus Agreement" (political agreement 6 May 2026) - https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/ [S]
- [UC-OMNI] Usercentrics, "EU AI Act Deal: Digital Omnibus Now in Force" - https://usercentrics.com/knowledge-hub/eu-ai-act-high-risk-delay-article-50-transparency-consent/ [S]
- [FD] Faegre Drinker, Jul 2026 - https://www.faegredrinker.com/en/insights/publications/2026/7/eu-ai-act-commission-confirms-transparency-code-of-practice-as-adequate-and-publishes-final-version-of-its-guidelines-on-transparency-obligations [S]
- [DLA] DLA Piper, Jul 2026 - https://www.dlapiper.com/en-us/insights/publications/2026/07/what-the-eus-new-code-of-practice-means [S]
- [GT] Greenberg Traurig, Jun 2026 (draft guidelines of 8 May 2026) - https://www.gtlaw.com/en/insights/2026/6/deepfakes-chatbots-ai-generated-text-european-commission-details-transparency-obligations-under-the-ai-act [S]

Other AI laws
- [CN-AI] Measures for Labeling of AI-Generated Synthetic Content (translation) - https://www.chinalawtranslate.com/en/ai-labeling/ ; Covington summary https://www.insideprivacy.com/international/china/china-releases-new-labeling-requirements-for-ai-generated-content/ [S]
- [IN-AI] Freshfields - https://www.freshfields.com/en/our-thinking/blogs/technology-quotient/india-targets-deepfakes-and-ai-generated-content-key-changes-under-meitys-2026-102mjwn ; Khaitan https://www.khaitanco.com/thought-leadership/MeitY-notifies-the-IT-Amendment-Rules-2026 [S]
- [KR-AI] US ITA - https://www.trade.gov/market-intelligence/south-korea-ai-basic-act ; FPF https://fpf.org/blog/south-koreas-new-ai-framework-act-a-balancing-act-between-innovation-and-regulation/ [S]
- [NY-SP] NY Senate S8420-A - https://www.nysenate.gov/legislation/bills/2025/S8420/amendment/A (signed 11 Dec 2025, Chapter 617; effective 180 days later) [V]; Reed Smith https://www.reedsmith.com/our-insights/blogs/viewpoints/102n129/fake-performer-real-penalty-what-advertisers-need-to-know-before-june-9/ [S]

Platforms and provenance
- [META-APR24] Meta, "Our Approach to Labeling AI-Generated Content and Manipulated Media" (Apr 2024, updates Jul and Sep 2024) - https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/ [V]
- [META-24] Meta, "Labeling AI-Generated Images on Facebook, Instagram and Threads" (Feb 2024) - https://about.fb.com/news/2024/02/labeling-ai-generated-images-on-facebook-instagram-and-threads/ [S]
- [META-ADS-25] Meta, "Expanding GenAI Transparency for Meta's Ads Products" (3 Feb 2025, updated 1 Jun 2026) - https://about.fb.com/news/2025/02/gen-ai-transparency-metas-ads-products/ [V]
- [META-HELP-ADS] Meta Help, "How AI-generated images are labeled in Ads on Meta products" - https://www.meta.com/help/artificial-intelligence/355108217670024/ [V]
- [META-MID26] Meta, "How Meta Is Preparing for the 2026 US Midterm Elections" (19 Feb 2026) - https://about.fb.com/news/2026/02/meta-prepares-for-2026-us-midterms/ [V]
- [META-EUCOP] Meta, "Meta is Signing the EU AI Act Code of Practice on Transparency of AI-Generated Content" (28 Jul 2026) - https://about.fb.com/news/2026/07/meta-is-signing-the-eu-ai-act-code-of-practice-on-transparency-of-ai-generated-content/ [V]
- [SMT] Social Media Today, 7 Jul 2026 - https://www.socialmediatoday.com/news/meta-adds-updated-disclosure-tags-for-ai-generated-ads/824658/ [S]
- [TT-ADS] TikTok Advertising Policies, "Misleading and false content" (last updated Apr 2026) - https://ads.tiktok.com/help/article/tiktok-ads-policy-misleading-and-false-content [V]
- [TT-NEWS-25] TikTok Newsroom, "More ways to spot, shape and understand AI-generated content" (19 Nov 2025) - https://newsroom.tiktok.com/more-ways-to-spot-shape-and-understand-ai-content?lang=en [V]
- [YT-GENAI] YouTube Help, "Disclosing use of altered or synthetic content" - https://support.google.com/youtube/answer/14328491?hl=en [V]
- [YT-CAM] YouTube Help, "Captured with a camera" - https://support.google.com/youtube/answer/15446725?hl=en [S]
- [LI-FORT] Fortune, 26 Nov 2024 - https://fortune.com/2024/11/26/linkedin-content-credentials-labeling-challenges-c2pa [S]
- [PIN] Pinterest Help, "Gen AI labels" - https://help.pinterest.com/en/article/gen-ai-labels [V]
- [GOOG-C2PA] Google, "How we're increasing transparency for gen AI content with the C2PA" (17 Sep 2024) - https://blog.google/technology/ai/google-gen-ai-content-transparency-c2pa/ [V]
- [SYNTHID] Google DeepMind SynthID - https://deepmind.google/technologies/synthid/ [V]
- [GMC] Google Merchant Center Help, "AI-generated content" - https://support.google.com/merchants/answer/14743464 ; IPTC news https://iptc.org/news/google-reminds-publishers-and-merchants-not-to-strip-metadata-from-images/ [S]
- [X-MM] X Help, synthetic and manipulated media policy - https://help.x.com/en/rules-and-policies/manipulated-media (HTTP 403 here) [U]
- [OAI-PROV] OpenAI API docs, Content provenance - https://developers.openai.com/api/docs/guides/content-provenance [V]
- [OAI-C2PA-SYNTHID] OpenAI, "Advancing content provenance ..." (19 May 2026) - https://openai.com/index/advancing-content-provenance/ (403 here); PetaPixel 20 May 2026 https://petapixel.com/2026/05/20/openai-gets-serious-about-detecting-fake-images/ ; OpenAI Help https://help.openai.com/en/articles/8912793-c2pa-and-synthid-in-openai-generated-images (403 here) [S]
- [IPTC-DST] IPTC Digital Source Type NewsCodes (modified 2024-10-23) - https://cv.iptc.org/newscodes/digitalsourcetype/ [V]
- [C2PA-SPEC] C2PA Technical Specification 2.2 - https://c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html [V]
- [C2PA-TRUST] CAI open-source docs, Trust lists - https://opensource.contentauthenticity.org/docs/conformance/trust-lists/ [V]
- [C2PA-CONF] C2PA conformance - https://c2pa.org/conformance/ ; https://opensource.contentauthenticity.org/docs/conformance/ [S]
- [C2PA-DEPLOY] C2PA, Content Credentials Deployment Guidance 1.0 (2026-07-08) - https://c2pa.org/wp-content/uploads/sites/33/2026/07/Content-Credentials-Deployment-Guidance.pdf [V partial]

Advertising, IP, consumer law
- [META-ADSTD] Meta Advertising Standards - https://transparency.meta.com/policies/ad-standards/ [V]
- [META-PA] Meta, Privacy violations and personal attributes (27 Jun 2024) - https://transparency.meta.com/policies/ad-standards/objectionable-content/privacy-violations-personal-attributes/ [V]
- [META-HW] Meta, Health and wellness (22 Jul 2026) - https://transparency.meta.com/policies/ad-standards/restricted-goods-services/health-wellness/ [V]
- [META-PCP] Meta, Prohibited commercial practices - https://transparency.meta.com/policies/ad-standards/deceptive-content/prohibited-commercial-practices/ [V partial]
- [META-PGE] Facebook Pages, Groups and Events Policies (promotions) - https://www.facebook.com/policies_center/pages_groups_events [V]
- [IG-PROMO] Instagram promotion guidelines - https://help.instagram.com/179379842258600 (not reachable) [U]
- [G-EDIT] Google Ads Editorial policy - https://support.google.com/adspolicy/answer/6021546 [V]
- [G-MISREP] Google Ads Misrepresentation - https://support.google.com/adspolicy/answer/6020955 [V]
- [G-TM] Google Ads Trademarks - https://support.google.com/adspolicy/answer/6118 [V]
- [G-RDA] Google Ads, Best practices guide for responsive display ads - https://support.google.com/google-ads/answer/9823397 [V]
- [LI-ADS] LinkedIn Advertising Policies (revised 18 Nov 2025) - https://www.linkedin.com/legal/ads-policy [V]
- [FTC-REV] FTC press release, 14 Aug 2024 - https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials [V]
- [FTC-EG] FTC, "FTC's Endorsement Guides: What People Are Asking" - https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking [V]
- [USCO-P2] US Copyright Office, Copyright and AI Part 2: Copyrightability (29 Jan 2025) - https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf [V]
- [USCO-AI] https://www.copyright.gov/ai/ [V]
- [OFL-FAQ] SIL OFL FAQ - https://openfontlicense.org/ofl-faq/ [V]
- [MS-OS2] Microsoft OpenType spec, OS/2 fsType - https://learn.microsoft.com/en-us/typography/opentype/spec/os2 [V]
- [UNSPLASH] https://unsplash.com/license [V]; [PEXELS] https://www.pexels.com/license/ [V]
- [USC-220506] 36 U.S.C. §220506 - https://www.law.cornell.edu/uscode/text/36/220506 [V]
- [USC-4-8] 4 U.S.C. §8 - https://www.law.cornell.edu/uscode/text/4/8 [V]
- [USC-116] 36 U.S.C. §116 - https://www.law.cornell.edu/uscode/text/36/116 [V]
- [USC-144] 36 U.S.C. §144 - https://www.law.cornell.edu/uscode/text/36/144 [V]
- [RBL] Royal British Legion, The Poppy - https://www.britishlegion.org.uk/get-involved/remembrance/about-remembrance/the-poppy [V]
- [NY-GBL-369e] NY General Business Law §369-E - https://www.nysenate.gov/legislation/laws/GBS/369-E [V]
- [CAP-8] CAP Code Section 8 - https://www.asa.org.uk/type/non_broadcast/code_section/08.html [V]
- EU Omnibus Directive (EU) 2019/2161 - https://eur-lex.europa.eu/eli/dir/2019/2161/oj [U - not readable here]

Days, symbols, culture
- [UN-DAYS] UN, List of International Days and Weeks - https://www.un.org/en/observances/list-days-weeks [V]
- [BD-HOL-2026] The Daily Star, "Govt announces official list of public holidays 2026" (10 Nov 2025, updated 12 Jan 2026) - https://www.thedailystar.net/news/bangladesh/news/govt-announces-official-list-public-holidays-2026-4031596 [S]
- [BD-8DAYS] Dhaka Tribune - https://www.dhakatribune.com/bangladesh/government-affairs/362070/eight-national-days-including-august-15-to-be ; ThePrint https://theprint.in/world/bangladesh-interim-govt-cancels-8-national-holidays-linked-to-mujibur-rahman-nations-liberation-war/2319527/ [S - snippet level]
- [BD-FLAG] Bangladesh Flag Rules 1972 (revised to Aug 2023), Cabinet Division - https://cabinet.portal.gov.bd/sites/default/files/files/cabinet.portal.gov.bd/legislative_information/9906ed4e_a1ac_4d85_8265_4a2f24a0cb17/2839.pdf (unreachable from this network); Wikipedia https://en.wikipedia.org/wiki/Flag_of_Bangladesh [S]
- [BANGLAPEDIA-EKUSHEY] https://en.banglapedia.org/index.php/Ekushey_February ; https://en.banglapedia.org/index.php/National_Days [S - search snippet; site blocked fetch]
- [IN-FLAG] https://en.wikipedia.org/wiki/Flag_Code_of_India ; https://en.wikipedia.org/wiki/Flag_of_India [S]; MHA Flag Code PDF https://www.mha.gov.in/sites/default/files/flagcodeofindia_070214.pdf (scanned images, not text-readable) [U]
- [SA-FLAG] https://en.wikipedia.org/wiki/Flag_of_Saudi_Arabia [S]
- [RISING-SUN] https://en.wikipedia.org/wiki/Rising_Sun_Flag [S]
- [SG-MOM] Singapore Ministry of Manpower, Public holidays 2026 and 2027 - https://www.mom.gov.sg/employment-practices/public-holidays [V]
- [HEBCAL] Hebcal, Jewish holidays 5787 - https://www.hebcal.com/holidays/2026-2027 [V]
- [WIKI-EID] https://en.wikipedia.org/wiki/Eid_al-Fitr [S]; [WIKI-RAMADAN] https://en.wikipedia.org/wiki/Ramadan [S]
- [WIKI-LNY] https://en.wikipedia.org/wiki/Lunar_New_Year [S]
- [WIKI-PEPSI] https://en.wikipedia.org/wiki/Live_for_Now_Moments_Anthem [S]; [WIKI-SPAGHETTIOS] https://en.wikipedia.org/wiki/SpaghettiOs [S]
- [WIKI-DG] https://en.wikipedia.org/wiki/Dolce_%26_Gabbana [S]; [WIKI-TANISHQ] https://en.wikipedia.org/wiki/Tanishq [S]; [WIKI-COCO] https://en.wikipedia.org/wiki/Coco_(2017_film) [S]
- [WIKI-HANUKIAH] https://en.wikipedia.org/wiki/Hanukkah_menorah [S]
- [ADL-88] https://www.adl.org/resources/hate-symbol/88 [V]; [ADL-OK] https://www.adl.org/resources/hate-symbol/okay-hand-gesture [V]
- [WIKI-TETRA] https://en.wikipedia.org/wiki/Tetraphobia [S]; [WIKI-CN-NUM] https://en.wikipedia.org/wiki/Chinese_numerology [S]
- [WIKI-MOURNING] https://en.wikipedia.org/wiki/Mourning [S]; [WIKI-OK] https://en.wikipedia.org/wiki/OK_gesture [S]; [WIKI-THUMB] https://en.wikipedia.org/wiki/Thumb_signal [S]
- German StGB §86a - https://www.gesetze-im-internet.de/stgb/__86a.html [U - not fetched]

Accessibility and typography
- [WCAG-143] https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html [V]
- [WCAG-145] https://www.w3.org/WAI/WCAG22/Understanding/images-of-text.html [V]
- [WAI-ALT] https://www.w3.org/WAI/tutorials/images/decision-tree/ [V]
- [NEI] https://www.nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/color-blindness [V]
- [OKABE-ITO] https://jfly.uni-koeln.de/color/ [V partial]
- [W3C-DIR] https://www.w3.org/International/questions/qa-html-dir [V]
- [W3C-ALREQ] https://www.w3.org/TR/alreq/ [V]
- [W3C-LANG] https://www.w3.org/International/questions/qa-lang-why [V]
- [W3C-LINEBREAK] https://www.w3.org/International/articles/typography/linebreak [V]
- [APPLE-RTL] https://developer.apple.com/design/human-interface-guidelines/right-to-left [S - paraphrased by fetch tool]
- [GOVUK-FORMATS] https://www.gov.uk/government/publications/inclusive-communication/accessible-communication-formats [V]
- [ADA-703] US Access Board, Guide to the ADA Standards, Chapter 7: Signs - https://www.access-board.gov/ada/guides/chapter-7-signs/ [V]

Research limits this session: the WebSearch budget for the session ran out part-way, so the later items were fetched directly from known
official URLs. Several official pages were blocked or unreadable from this network (EUR-Lex, legislation.gov.uk, cabinet.portal.gov.bd,
banglapedia.org, help.x.com, help.instagram.com, helpx.adobe.com, timeanddate.com, openai.com). Items relying on them are tagged [U] or [S].
