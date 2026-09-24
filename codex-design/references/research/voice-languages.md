# Casual versus bookish copy in 18 languages

Research note for the codex-design copy guide (`references/copy.md` §4) and the lint (`scripts/copyrules.py`).
Researched on 2026-09-24 (Asia/Dhaka). Every source was read on 2026-09-24: "read" means the page was opened,
"snippet" means only the search result was seen. The lint candidates and calibration lines are in
`languages-casual.json` next to this file.

**What this adds.** `copy.md` §4 gives one register row per language and names the generic translation and AI tells;
`copyrules.py` checks punctuation for Spanish, French, German and CJK and has word lists only for English and Bengali.
This note brings, for each language, the everyday words and particles that people and brands use on social media in
2024 to 2026, the bookish words that read stiff, the local AI and machine-translation tells with fixes, and lint
candidates tuned against natural and robotic lines. It covers the twelve languages of §4 plus Filipino (Taglish),
Vietnamese, Thai, Korean and Nepali, which §4 does not have yet.

**Confidence marks** (on every finding):
- **native source**: a native writer, editor, linguist or language body says it;
- **several sources**: two or more independent sources agree;
- **single source**: one source;
- **inference**: the researcher's own knowledge of the language, not found in a source. Treat these as hypotheses
  for a native reviewer.

**Limits.** The session's shared web-search budget ran out partway through, so most late evidence comes from pages
fetched directly: Microsoft's localization style guides, Wikipedia (including the German, French, Portuguese and
Chinese community pages on AI writing), GitHub humanizer lists written by native speakers, newspapers and
localisation blogs. Instagram, X, Facebook, Reddit, Quora and several newspapers blocked fetching, so no language
section quotes real 2024 to 2026 brand posts at scale, and brand-voice claims are marked accordingly. Every example
line was written for this note; the few quoted lines are short and attributed. A native reader signs off real copy,
as `copy.md` §4 already requires.

## 1. The lint file in numbers

`languages-casual.json` has two keys, as asked:
- `lint_candidates`: 347 candidates across 18 languages (17 to 20 each). By level: 228 warnings, 104 notes and 15
  errors (the errors are chatbot leftovers such as "¡Claro! Aquí tienes…"). By kind: 301 regex, 38 structure,
  5 phrase and 3 word. False-positive risk as rated: 161 low, 173 medium, 13 high (all 13 high-risk ones are notes).
- `calibration`: for each language, 8 robotic lines and 8 natural lines written by the language researcher, plus
  2 to 4 hard negatives per language written during the merge (197 natural and 144 robotic lines in all).

Calibration result (run on the merged file, 2026-09-24):
- Every robotic line is caught by at least one candidate of its language, and no natural line triggers any candidate
  of its language, not even a note.
- Hard-negative test before the merge: 68 natural lines built around words that look like tells but are native
  (Turkish Keşfet, Chinese 沉浸式护肤 and 解锁新吃法, Japanese 没入感, Korean 차원이 다른, Vietnamese Trải nghiệm ngay,
  German "nicht nur … sondern auch", Spanish "Te estaremos esperando", the twelve sample lines in `copy.md` §4, and
  more). Result: 0 warnings and 3 notes, all on candidates already rated high risk (Malay terokai in travel copy,
  Turkish keşfedin, Thai สัมผัสประสบการณ์). Those three lines and the `copy.md` samples were left out of the
  calibration set; the other 53 were added as natural lines.
- No string in the file contains an em dash, a double hyphen or a spaced en dash.

How the harness matches (use the same semantics when the candidates go into `copyrules.py`):
- `regex` and `structure`: a Python `re` pattern, compiled with IGNORECASE, searched in NFC-normalised text.
- `word` and `phrase`: the literal, case-insensitive, with a boundary that depends on the script. Latin needs no
  letter on either side; Devanagari, Arabic script and Tamil need no letter or sign of the same script on either
  side (dandas, Arabic-script punctuation and digits count as boundaries); Hangul needs no syllable before it and
  stays open on the right, because particles attach; Thai and CJK match as plain substrings.
- Several candidates use scoped flags such as `(?-i:…)` for Title Case, which needs Python 3.6 or later.

## 2. Across languages

### 2.1 Why a word list catches only part of it

- LLM output in other languages carries an "English accent". Guo et al. (ACL 2025) measured lexical and syntactic
  distance from human text in English, French and Chinese: every model was further from human text in French and
  Chinese than in English, the syntax gap was larger than the vocabulary gap, and Chinese was furthest. (several
  sources: the paper and a paper note)
- Valentini et al. (arXiv, August 2026) trained classifiers on LLM text in German, Spanish, Greek and Pashto. Gemini's
  German was classified as translated 60.2% of the time. LLM German uses "auch" far less than native text, and
  Llama's Spanish drops articles. Native annotators spotted translationese in only 28 to 37% of outputs, against 45
  to 60% for the classifiers, so a human skim misses most of it. (single source, read)
- LLM translation is literal by training: over 40% of GPT-4 translations in one study had translationese errors, and a
  second "polish for native fluency" pass cut that from 43% to 25% (Slator on arXiv 2503.04369, which
  `copy-transcreation.md` already cites for the "overly literal" finding; the numbers are new here). (single source)
- What this means for the copy loop: the lint catches the stock phrases; the judge still has to read for structure.
  Two checks travel across languages: does the line have the market's particles or spoken forms (§2.4), and does
  every sentence have a doer and a verb instead of a noun chain or a passive (§2.3)?

### 2.2 The same English moves, calqued

The same handful of English marketing moves turn up, translated word for word, in every language. The cells give the
local form named in each language section, most of them lint candidates; "native" marks a word the researchers
found in normal human copy, so it is left alone or only noted. Evidence strength differs by cell: see each language
section.

| Language | Dive in, discover | Experience, journey | Next level, unlock, empower | Not just X, it's Y | Era opener |
|:-|:-|:-|:-|:-|:-|
| Hindi | खोजें, अन्वेषण करें | अनुभव करें, का आनंद लें; स्वाद की यात्रा | नई ऊँचाइयों पर | सिर्फ़ X नहीं, बल्कि Y | आज की भागदौड़ भरी ज़िंदगी में |
| Arabic | انغمس في (اكتشف native in Gulf ads) | تجربة فريدة من نوعها; رحلة من النكهات | ارتقِ بـ، أطلق العنان لـ | ليس مجرد X بل Y | في عالم اليوم المتسارع |
| Spanish | sumérgete, adéntrate, embárcate; descubre la magia de | vive una experiencia única; un viaje de sabores | al siguiente nivel, eleva tu, potencia tu | No es solo X, es Y | en el vertiginoso mundo de |
| Portuguese | mergulhe no universo de, embarque nessa jornada | experiência inesquecível; jornada | ao próximo nível, eleve, potencialize | não é apenas X, é Y | no mundo atual, no cenário atual |
| French | plongez dans l'univers de (Découvrez alone native) | vivez une expérience unique; voyage culinaire | élevez votre, libérez votre potentiel | plus qu'un X, un Y | dans un monde où, à l'ère du numérique |
| German | tauche ein, entdecke die Welt der (Entdecke alone native) | erlebe unvergessliche…, erlebe pure… (plain Erlebe left alone) | auf das nächste Level, entfessle dein Potenzial | Das ist nicht nur X. Das ist Y. | in der heutigen schnelllebigen Welt |
| Indonesian | selami dunia, temukan keajaiban (temukan alone native) | rasakan pengalaman; perjalanan rasa | wujudkan impianmu | bukan sekadar X, melainkan Y | di era digital saat ini |
| Malay | terokai (native in travel, a note) | rasai pengalaman | merealisasikan impian | bukan sekadar X, tetapi Y | dalam dunia yang pantas berubah |
| Urdu | دریافت کریں | تجربہ کریں، لطف اندوز ہوں; ذائقے کا سفر | نئی بلندیوں تک | صرف X نہیں بلکہ Y | آج کی تیز رفتار زندگی میں |
| Tamil | கண்டறியுங்கள் | அனுபவியுங்கள்; பயணம் | புதிய உயரங்களுக்கு | வெறும் X அல்ல | none found |
| Chinese | 探索 (native) | 开启…之旅 | 赋能 | 不仅仅是X，更是Y | 在当今快节奏的时代 |
| Japanese | 〜の世界へようこそ (没入 native) | 体験 native, not linted; 物語を紡ぐ in purple copy | 可能性を解き放つ, 新たな高みへ | 単なるXではなく | 今日の急速に変化する世界において |
| Turkish | dalın, dünyasına dalın (Keşfet native) | deneyimleyin; lezzet yolculuğu | bir üst seviyeye taşıyın | sadece X değil; bir X'ten fazlası | günümüzün hızla değişen dünyasında |
| Filipino | tuklasin, galugarin | maranasan; paglalakbay tungo sa | none found | hindi lamang X kundi pati na rin Y | sa mabilis na mundo ngayon |
| Vietnamese | đắm chìm, khám phá thế giới (khám phá ngay native) | hành trình vị giác (trải nghiệm native) | nâng tầm is native, left alone | không chỉ là X mà còn là Y (narrow; the shape is native) | trong bối cảnh ngành X đang phát triển không ngừng |
| Thai | ดื่มด่ำ, ค้นพบประสบการณ์ | สัมผัสประสบการณ์ (native cliché, a note); การเดินทางแห่ง… | ยกระดับประสบการณ์, ปลดล็อกศักยภาพ | ไม่ใช่แค่ X แต่ยัง Y | ในยุคปัจจุบัน |
| Korean | 발견하세요, 탐험하세요 | 경험하세요; 여정 | 새로운 차원 (차원이 다른 native) | 단순한 X가 아니라 Y | 오늘날 빠르게 변화하는 세상에서 |
| Nepali | पत्ता लगाउनुहोस्, अन्वेषण | अनुभव गर्नुहोस्; स्वादको यात्रा | नयाँ उचाइमा | केवल X होइन, यो Y हो (X मात्र होइन, Y पनि is native) | आजको व्यस्त जीवनशैलीमा |

Where native writers name the move themselves: Spanish, Portuguese, French, German, Chinese, Japanese and Vietnamese
(articles and Wikipedia community pages); Korean for the "not just" shape (a corpus study measured it 9.2 times more
often in AI text); Hindi for "not just" (India TV Hindi, 2026); Arabic for "not just" (a native writer on X) and the
era opener; Turkish for the era opener and stock report phrases. The remaining cells are inference.

### 2.3 Translated structure, shared across languages

These are the syntax habits behind the "English accent". Most cannot be caught by a word list alone; the candidates
catch the commonest surface forms.

- **Agent passives ("made by our experts").** ar من قبل and بواسطة, tr "tarafından", hi
  द्वारा + passive, ur کی جانب سے, ko 에 의해 and the double passive 되어지다, th ถูกออกแบบมาเพื่อ (neutral ถูก began as
  an Anglicism), vi "được … bởi", ta -ப்படு, id and ms formal passives. Fix everywhere: the doer as the subject
  ("our chefs make it every morning").
- **Light-verb and noun chains.** es "realizar su pedido", pt "efetuar o pagamento", fr "effectuer un achat", de "Die
  Lieferung erfolgt", ar تم + masdar and قام بـ, tr "gerçekleştirilecektir", hi प्रदान करते हैं, ur فراہم کرتے ہیں,
  ne प्रदान गर्दछौं, zh 进行购买, ko 이벤트가 진행됩니다, th ดำเนินการสั่งซื้อ and มีความสามารถในการ, vi "thực hiện",
  id "pelaksanaan pengiriman dilakukan". Fix: the verb itself (pide, pagar, acheter, wir liefern, 买, กันน้ำได้).
- **The "have" calque.** tr "…'e sahip", ko ~를 가지고 있다, pt "possui" and "conta com" (the Portuguese Wikipedia essay
  links avoiding plain "tem" to AI text), es "contamos con", "disponer de". Fix: "is" or "has" in the local plain form
  (tem, var, 좋아요).
- **Essay connectors.** es "cabe destacar", pt "vale ressaltar", fr "il est important de noter", de "es ist wichtig zu
  beachten", ar علاوة على ذلك, tr "bununla birlikte", id "tak dapat dipungkiri", ms "walau bagaimanapun", zh 值得注意的是
  and 总而言之, ja と言えるでしょう, ko 또한 and 결론적으로 at the start of a sentence, th นอกจากนี้, vi "Hơn nữa". Fix: cut
  them; ads need no summary.
- **English punctuation and case.** Title Case in es, pt, fr and de headlines (now linted as a structure); the English
  list comma with a final "and" in Arabic (برجر، بيتزا، وحلا); full stops at the end of Thai sentences; a comma after
  Korean connective endings (가볍지만,); English thousand separators in Vietnamese (99,000đ), Indonesian (Rp 49,000)
  and Malay (RM1.299).
- **Wrong variant.** European Portuguese in a Brazilian post (LLMs default to it, per the Portuguese Wikipedia essay),
  Indonesian words in Malaysian copy (gratis, ongkir, bisa) and the reverse, Hindi words in Nepali (और, हैं, नहीं),
  mainland words in Taiwan posts (視頻 for 影片), Arabic letters in Urdu text (ك and ي for ک and ی).

### 2.4 What natural copy has that machine copy lacks

The spoken layer. Machine copy is grammatical but uses the written register; natural social copy uses the particles
and contractions of speech. Two sources back this: the Indonesian anti-slop list says LLM text almost never uses the
particles (nih, dong, deh, sih) and that their total absence is itself a tell, and Valentini et al. measured that LLM
German underuses "auch". The markers each language section documents:

| Language | Spoken markers a natural caption carries |
|:-|:-|
| Hindi | तो / toh, ना / na, बस / bas, ही / hi, भी / bhi; अरे, चलो; एकदम, पक्का |
| Urdu | toh, na, bas, abhi, chalo; تو، بس، ابھی، چلو |
| Nepali | ल, नि, त, है as a tag, अनि; the spoken imperative गर्नुस् |
| Arabic | one dialect's words: Gulf الحين، وش، زين، واجد، علينا; Egyptian دلوقتي، عايز، أوي، بجد؛ Levantine هلق، شو، كتير، منيح؛ Moroccan دابا، بزاف، واخا |
| Turkish | ya, yani, işte, bak, hadi, gel, bi'; valla, cidden, resmen; verbless lines (Kargo bedava.) |
| Spanish | finde, pásate, vale (ES); se te antoja (MX); voseo pedí, probá (AR); jajaja |
| Portuguese | tá, pra, a gente, bora, vem, corre, sextou (BR); fixe, bué (PT); kkkk |
| French | on for nous, dropped ne (c'est pas), questions by intonation, clipped words (dispo, promo, resto, appli) |
| German | mal, doch, halt, eben, ja, auch; gibt's, geht's; gönn dir, hol dir, schau mal vorbei |
| Indonesian | nih, dong, deh, sih, kok, lho, kan, ya, yuk; udah, aja, banget, gimana, buat, cuma, nggak |
| Malay | lah, je, tak, nak, dah, kat, ni, tu; korang, kitorang; jom |
| Filipino | na, pa, lang, naman, talaga, ba, din or rin, nga, kasi, eh; po and opo in replies |
| Tamil | spoken endings: இருக்கு, வந்தாச்சு, பண்ணுங்க, வாங்க, -ன்னு |
| Chinese | 啊, 呀, 吧, 啦, 哦, 嘛, 呢; 超, 巨, 真的 (CN); 喔, 耶, 欸 (TW); 嘅, 咗, 啲, 喺, 嚟 (HK) |
| Japanese | ね and よ, 体言止め, short plain asides (正直, やっぱり) mixed into です・ます |
| Korean | 해요체 endings ~요, ~죠, ~네요, ~거든요; ㅎㅎ; a tilde tail (놀러 오세요~) |
| Thai | นะ, จ้า, น้า, เลย, สิ, มั้ย; one polite particle set per persona (ค่ะ or ครับ) |
| Vietnamese | nha, nhé, nè, đó, thôi, á; ạ in replies to customers |

A possible check (inference, not yet a candidate): a caption of 20 or more words in id, ms, tl, vi, th, ko or hi-Latn
with none of its language's particles gets a note asking for a read-aloud pass. Particle sets are closed lists, so the
check is cheap; it should never fire on headlines, notices or legal lines.

### 2.5 Template lines in every language

`copyrules.py` knows greeting openers, engagement bait and generic CTAs only in English and Bengali. The candidates add
them for every language; the forms below are what they catch.

| Language | Greeting or letter opener | Engagement bait | Generic CTA (note) | Chatbot leftover (error) |
|:-|:-|:-|:-|:-|
| Hindi | प्रिय ग्राहकों, नमस्ते दोस्तों | दोस्तों को टैग करें, लाइक और शेयर | और जानें, अधिक जानकारी के लिए | यहाँ आपके लिए कुछ कैप्शन दिए गए हैं |
| Arabic | عملاءنا الكرام، يسعدنا أن نعلن | منشن لصديقك، اكتب تم في التعليقات | اعرف المزيد، لا تفوت الفرصة | none found |
| Spanish | Estimado cliente, Hola a todos | etiqueta a un amigo, dale like si | Más información, Haz clic aquí | ¡Claro! Aquí tienes… |
| Portuguese | Prezado cliente, Olá pessoal | marque aquele amigo, curta e compartilhe | Saiba mais, Clique aqui | Claro! Aqui está uma legenda… |
| French | Chers clients, Bonjour à tous | Identifie un ami | En savoir plus, Cliquez ici | Bien sûr ! Voici… |
| German | Liebe Kundinnen und Kunden | Markiere einen Freund | Mehr erfahren, Hier klicken | Gerne! Hier sind drei Vorschläge |
| Indonesian | Halo Sobat, Pelanggan yang terhormat | tag temanmu, like dan share | Ketahui lebih lanjut, Klik di sini | Berikut adalah beberapa caption |
| Malay | Pelanggan yang dihormati, Hai semua | tag kawan korang | Ketahui lebih lanjut, Klik di sini | Berikut ialah beberapa kapsyen |
| Urdu | محترم صارفین، السلام علیکم | اپنے دوستوں کو ٹیگ کریں | مزید جانیں (Roman mazeed janein) | یقیناً! یہ رہا آپ کا کیپشن |
| Tamil | அன்புள்ள வாடிக்கையாளர்களே | நண்பர்களை டேக் பண்ணுங்க | மேலும் அறிய | none found |
| Chinese | 尊敬的客户, 亲爱的用户, 大家好 | @你的好友, 评论区扣1 | 了解更多 | 以下是为你生成的文案 |
| Japanese | 皆様こんにちは, お客様各位 | 友達をタグ付け | 詳しくはこちら (high risk) | 以下は投稿文の案です |
| Turkish | Değerli müşterilerimiz | arkadaşını etiketle | Daha fazla bilgi için | none found |
| Filipino | Mahal naming mga customer, Magandang araw | i-tag ang barkada | Alamin pa | Narito ang ilang caption |
| Vietnamese | Kính gửi Quý khách | tag bạn bè, like và share | Tìm hiểu thêm | Dưới đây là một số gợi ý caption |
| Thai | เรียนลูกค้าผู้มีอุปการคุณ, สวัสดี | แท็กเพื่อน, กดไลก์ กดแชร์ | ดูเพิ่มเติม, คลิกที่นี่ | นี่คือแคปชัน… |
| Korean | 존경하는 고객님, 안녕하세요 | 친구 태그, 좋아요와 팔로우 | 자세히 보기 (high risk) | 다음은 캡션입니다, 물론입니다 |
| Nepali | प्रिय ग्राहक, आदरणीय ग्राहक महानुभावहरू | साथीहरूलाई ट्याग गर्नुहोस् | none found | पक्कै पनि! यहाँ केही क्याप्सनहरू छन् |

Levels differ by language in the file: letter salutations are warnings in hi, ur, ne, ar, tr, fr, de, ko and th,
while plain hellos are notes in es, pt, id, ms, tl, ta, zh, ja, vi, ko (안녕하세요) and th (สวัสดี), because some
local brands do open that way. The English and Bengali rule in `copyrules.py` is a warning; when implementing, warn on
letter salutations and note plain hellos.

### 2.6 Address and code-mixing, one line per language

Address rows for the five new languages are new; for the other twelve, only what goes beyond §4.

| Language | Address default | Code-mixing rule |
|:-|:-|:-|
| Hindi | आप with कीजिए or करें (§4) | one script per line; Roman lines stay Roman (order karo); Devanagari lines transliterate (ऑर्डर, ऑफ़र) and keep only brand names in Latin |
| Urdu | آپ with کریں (§4); کیجئے reads classic | loanwords in Urdu script (ری چارج، آرڈر); brand names in Latin; Roman Urdu with English is the app voice (scan karo) |
| Nepali | तपाईं with the polite imperative; हजुर in service replies; तिमी for youth; never तँ | loanwords in Devanagari (अफर, डेलिभरी) with गर्नु (अर्डर गर्नुस्); Roman Nepali is common on Facebook and TikTok |
| Arabic | plural or no verb (§4); dialect plurals: اطلبوا، حيّاكم، الحقوا | English nouns in Arabic script take Arabic grammar (أوردرك، الديليفري); Latin only for names; French loans in the Maghreb; Arabizi only if the brand already posts that way, never mixed with Arabic script in a line |
| Turkish | siz by default, -(y)In imperatives; -(y)InIz (tıklayınız) is letter style | English nouns take suffixes, with an apostrophe after names and numbers (23.59'a); English verb + etmek (confirm etmek) is mocked office talk |
| Spanish | per market (§4) | keep the loans the market uses (link en bio, look, outfit); never spell out a shortened loan (enlace en la biografía) |
| Portuguese | per market (§4) | BR delivery, cashback, link na bio; European Portuguese forms in a BR post read as a wrong variant |
| French | on for the brand voice; nous for notices | franglais nouns yes (live, story, drop, collab); English hype verbs no; Québec prefers French words (courriel, magasiner, infolettre) |
| German | du or Sie (§4) | loans joined or hyphenated (Sommer-Sale, Onlineshop); never split compounds (Kunden Service) |
| Indonesian | kamu (§4); kak in marketplace captions and replies; never mix Anda with kamu | English commerce words are normal; English verbs take local affixes (di-cancel, nge-cancel) |
| Malay | anda in lowercase inside a sentence; korang or no pronoun when casual; awak one-to-one | bahasa rojak is normal for youth, food and commerce; never Indonesian words |
| Filipino | ka and mo; po and opo in service replies and for older readers; never kayo or inyo to one reader | English verbs and nouns take Tagalog affixes with a hyphen (mag-order, i-download, na-deliver) |
| Tamil | நீங்க with -ங்க (§4) | English nouns take Tamil case endings (ஆர்டருக்கு, store-la); English verbs take பண்ணு (ஆர்டர் பண்ணுங்க); one script per line |
| Chinese | no vocative by default; 姐妹们 and 宝子们 only on female-skewed 小红书 accounts; 家人们 reads as livestream selling | a few lowercase Latin words are native (city, citywalk, vlog, OOTD, emo, MBTI); no English sentences; HK mixes more (book位, check下) |
| Japanese | 〜の方 or 皆さん; お客様 in service notices | everyday katakana loans are fine (セール, コスパ, タイパ); business katakana (ソリューション, シナジー) reads like a slide deck |
| Korean | drop "you"; 여러분, 고객님, ~님 or a community nickname; never 당신 in ads; 해요체 by default, 합쇼체 for formal notices | loanwords in Hangul (세일, 쿠폰, 굿즈, 팝업); Latin only for names, short sticker words (NEW, SALE, D-3) and codes |
| Thai | omit คุณ and address groups (ลูกค้าทุกคน, ใครที่…); one admin persona with one particle set; ท่าน only in formal notices | loanwords in Thai script (โปร, รีวิว, ไลฟ์); Latin for names, sizes, codes and 11.11; one form per word |
| Vietnamese | bạn, mọi người, cả nhà; the brand as mình or nhà mình; quý khách for banks and airlines | English words slot in unchanged (order, ship, freeship, sale, deal, combo, size, ib) |

### 2.7 Numbers, money and dates for the new languages

| Language | Money | Dates and time | Other |
|:-|:-|:-|:-|
| Korean | 9,900원 (numeral attached), 1만 원; avoid ₩ and KRW in consumer copy | 9월 24일(목) or 9.24(목); ranges with ~ (9/24~9/30); 오후 2시 or 14:00 | Western punctuation; no comma after connective endings |
| Thai | 1,290 บาท, ฿99 with no space, or the tag form 99.- | Buddhist Era: 2026 is พ.ศ. 2569; 24 ก.ย. 69; 10:00 น. | no spaces between words; a space ends a phrase or sentence; no full stop |
| Vietnamese | 99.000đ (a full stop for thousands, a comma for decimals); 99k on social; never 99,000đ | day first (30/9/2026); 20h or 20:00; no AM or PM | k also means thousand, so never write k for không near a price |
| Filipino | ₱499; "₱99 lang" is the everyday price line | 10AM and 8PM appear in everyday posts | inference |
| Nepali | रु. with Devanagari digits in Nepali script (रु. ९९९); Rs with Western digits in Roman posts; lakh grouping (रु. १,००,०००) | । ends a statement | inference |
| Indonesian, Malay | Rp49.000, 49rb, 99K (id); RM12.90, RM1,299 (ms) | ms months Mac, Ogos, Disember | an English separator in either is a wrong-format tell |

## 3. Notes for the lint

These come from reading `copyrules.py` against the new candidates and from running its current checks over the
calibration lines. They are proposals, not measured rules, except where a number is given.

1. **Route by the `lang` tag, not by script.** Hindi and Nepali share Devanagari and words like उपलब्ध; Arabic and Urdu
   share the Arabic script; Roman Hindi, Roman Urdu, Roman Nepali, Indonesian, Malay, Filipino, Turkish and
   Vietnamese are all Latin, where the English lists already run. The candidates are written per language, and a few
   would misfire in the sister language (Nepali uses है as a tag, which the Hindi-leak check deliberately skips).
2. **`script_of()` needs a majority test for every script.** Today only Bengali gets one, so a Chinese, Japanese, Korean,
   Thai or Tamil line with one Latin brand name becomes "latin", and the English CTA-verb note and question-headline
   note then run on it.
3. **Word counts fail for Chinese, Japanese and Thai.** `_words()` splits on spaces and punctuation, so a 28-character
   Chinese line counts as three words and a 40-character Japanese line as five, and the long-headline and long-CTA
   checks never fire. Count characters
   for these scripts; the caps belong with the format research.
4. **The one-"!" exemption should not be Bengali-only.** Run as headlines, the 144 original natural calibration lines
   drew 36 exclamation warnings in 13 languages (hi, ur, ne, ar, pt, fr, de, id, ms, tl, ko, ta, vi), all on hooks
   that end in a single "!" the way those markets write them (Jom tapau!, Order na!, 신메뉴 출시!, புது மெனு ரெடி!).
   The rule also flags the `copy.md` §4 sample lines for French, German, Turkish, Indonesian and Tamil, which end their
   hook the same way, while a full-width ！ in Chinese or Japanese is not counted at all. Proposal: allow one "!" or
   "！" at the end of a hook for every language except English, and keep one per line. (measured on lines written for
   this study, so a native check of real posts should confirm it)
5. **The English AI list misfires on mixed Latin-script lines.** Natural inside Hinglish, Roman Urdu, Taglish,
   Indonesian and Malaysian copy: unlock (rewards unlock karo, i-unlock), hidden gem, must-visit, must-try,
   world-class, game-changer, next-gen, experience (Sulit na experience), journey (fitness journey ko), curated,
   effortless, empower, innovative, comprehensive. Roman Hindi tokens also collide with English words (hi for ही,
   the for थे, pure for पूरे, bus for बस, man for मन, par for पर). Proposal: on lines tagged hi-Latn, ur-Latn, ne-Latn,
   id, ms or tl, treat unlock, hidden gem, must-visit and world-class as tier 2 and skip experience and journey unless
   the line is otherwise English. A cheap Roman Hindi or Urdu detector: two or more of hai, hain, karo, karein, mein,
   ke, ki, ka, aur, toh, bhi. (inference from usage, both researchers)
6. **The English CTA-verb note needs local verbs.** It expects an English first word, so Pesan sekarang, Jom tempah and
   Tara na get a note. Add id beli, pesan, cek, daftar, klaim, ambil, coba, yuk; ms beli, tempah, daftar, jom, rebut,
   cuba; tl order, bili, tara, subukan, i-download, mag-order; and the equivalents in other languages, or skip the
   note when `lang` is not English.
7. **Normalise before matching.** Vietnamese needs NFC (the lint already normalises). Turkish needs Turkish lowercasing
   (İ to i, I to ı) before an IGNORECASE match, because Python does not fold them. For Arabic, stripping tatweel and
   short vowels before matching makes the word lists robust (inference). For Urdu, warn on Arabic ك, ي and ى in Urdu
   text, but skip Arabic quotations such as a dua or a verse.
8. **Greeting levels.** Align as in §2.5: letter salutations warn, plain hellos note.
9. **Particles as a positive signal.** See §2.4; a note, never a warning.
10. **Keep the calibration with the rules.** When a candidate moves into `copyrules.py`, run its language's natural
    and robotic lines from the JSON, as the Bengali study did: every robotic line caught, no natural line flagged.

## 4. The languages

Each section has the same parts: register guide, formal to everyday swaps, AI and translation tells, purple phrasing,
natural and robotic lines, what could not be verified, and sources. Sections come in the order of `copy.md` §4, then
the five new languages.

### 4.1 Hindi (hi)

#### Register guide
- **Everyday over formal (native source).** Microsoft's Hindi localization guide tells translators to write the way people talk in everyday
  conversation instead of the formal language of technical and commercial text, and to drop
  literal translation when it stops serving the reader. Its list of words to avoid is in the swaps table.
- **Script (several sources).** Casual Hindi online is mostly Roman: Wikipedia's Hinglish article cites a YouTube
  comment sample with 52% Romanised Hindi against 1% Devanagari, and Winata et al. (2026) report that people write mixed
  Hindi and English in Latin script while models drop Devanagari into it. Rule: one script per line. A Roman line stays
  Roman (order karo, 20% off). A Devanagari line transliterates English words (ऑर्डर, ऑफ़र, सेल) and keeps only brand
  and product names in Latin (Paytm, iPhone 16).
- **English words, Hindi grammar (single source and inference).** English words take a Hindi light verb (order karo or
  ऑर्डर कीजिए, book karo, try karo, download karo) and Hindi postpositions (offers pe, ऐप पर). Google Pay's Hinglish
  interface works the same way; Wikipedia cites "Transaction History Dekhein". Normal loanwords: order, offer, sale,
  off, cashback, delivery, free, combo, deal, EMI, app, booking, size, stock.
- **Casual markers (inference).** Particles तो/toh (आज तो बनता है), ना/na (try karo na), बस/bas (bas ₹99), भी/bhi,
  ही/hi (आज ही); interjections अरे/arre, चलो/chalo, वाह/wah; intensifiers एकदम/ekdum, पक्का/pakka, मस्त/mast,
  बढ़िया/badhiya; sale words धमाका, बंपर, फटाफट. Peer address यार/yaar, भाई/bhai and boss only in youth, food and
  street voices. Emoji follow the global rule; 🙏 reads as thanks or namaste, so it suits thank-you posts, not sale lines.
- **Sentence shapes (single source and inference).** A question hook plus a hard fact (Bhook lagi? ₹99 mein thali),
  number-first fragments, one imperative at the end. Hindi copywriters told Social Samosa (2025) that Hinglish leads on
  digital because it matches how people actually type and talk online.
- **Official Hindi moved the same way (single source, snippet).** A 2011 Department of Official Language circular asked
  for saral Hindi and swapped coinages for English words in Devanagari (misil for file, pratyabhuti for guarantee,
  kunjipatal for keyboard, sanganak for computer). The stiffest coinages come from official glossaries (Microsoft's
  guide lists the CSTT glossary among its references), so pick the word people say, not the glossary word.
- **Where Devanagari still wins (single source).** A 2026 ad-tool guide (Lapis) pairs Devanagari with Tier 2 and 3
  audiences and Hinglish with metros. Its own Hinglish sample puts Latin words into a Devanagari sentence, the model habit
  above, so treat it as a warning, not a template.
- **Politeness (native source and inference).** Keep the covered address rule (आप + कीजिए/करें). कृपया is standard, not
  a tell: Microsoft's own Hindi samples use it once per message. In Roman Hinglish the आप forms are kijiye/karein and
  the तुम form is karo; one form per post.
- **Words that are fine (inference, checked against the lint).** उपलब्ध (अब सभी स्टोर पर उपलब्ध), उत्पाद, प्राप्त
  करें and कृपया are ordinary in Indian Hindi ads and UI, so the lint leaves them alone. तत्काल is also the Tatkal
  railway ticket, so it is not flagged.

#### Formal to everyday swaps
| formal | everyday | note | confidence |
|:-|:-|:-|:-|
| चयन करें | चुनें | Microsoft's avoid list | native source |
| इसके अतिरिक्त | साथ ही | same list | native source |
| अतः | इसलिए | same list | native source |
| संदर्भ लें | देखें | same list | native source |
| परिवर्तित करें | बदलें | same list | native source |
| पुनः प्रयास करें | दोबारा कोशिश करें | same list (the guide spells it दुबारा) | native source |
| सीखें कि सेटिंग्स कैसे परिवर्तित करें | सेटिंग्स बदलने का तरीका जानें | Microsoft's example of a short rewrite | native source |
| संगणक, कुंजीपटल, प्रत्याभूति, मिसिल | कंप्यूटर, कीबोर्ड, गारंटी, फ़ाइल | 2011 official-language circular | single source (snippet) |
| प्रदान करते हैं | देते हैं | corporate "we provide" | inference |
| सुनिश्चित करें | पक्का कर लें, ध्यान रखें | right in government notices | inference |
| क्रय करें | ख़रीदें | | inference |
| निःशुल्क | फ़्री, मुफ़्त | right for government schemes and health camps | inference |
| अत्यंत | बहुत, एकदम | | inference |
| शीघ्र | जल्दी, जल्द (जल्द आ रहा है) | | inference |
| हेतु | के लिए | fine on forms | inference |

#### AI and translation tells
| tell | robotic example | natural fix | evidence | confidence |
|:-|:-|:-|:-|:-|
| "not X, but Y" | यह सिर्फ़ चाय नहीं, बल्कि एक एहसास है। | कड़क इलायची चाय, ₹30 में। | India TV Hindi 2026 | native source |
| rule of three | स्वाद, सेहत और सुकून, सब एक साथ। | एक कप में 8 ग्राम प्रोटीन। | India TV Hindi 2026 | native source |
| over-polished length for a small message | a five-sentence apology for a late order | देर हुई, माफ़ कीजिए। अगला ऑर्डर फ़्री डिलीवरी पर। | India TV Hindi 2026 | native source |
| Devanagari inside Hinglish | Monsoon sale में 30% off, आज ही shop करें! | Monsoon sale: 30% off, aaj hi shop karo! | Winata et al. 2026 | single source |
| refined textbook register | आपकी सुविधा हेतु हम निःशुल्क होम डिलीवरी प्रदान करते हैं। | घर तक डिलीवरी फ़्री है। | Winata et al. 2026; Microsoft Hindi guide | several sources |
| "experience" or "enjoy" CTA | इस गर्मी ठंडी लस्सी का आनंद लें। | गर्मी है? ठंडी लस्सी पी लीजिए, ₹60। | none found | inference |
| "discover" or "explore" | हमारा नया कलेक्शन खोजें। | नया कलेक्शन देखिए, ₹799 से। | none found | inference |
| "to new heights" | अपने बिज़नेस को नई ऊँचाइयों पर ले जाएँ। | GST बिल अब 2 मिनट में, ऐप पर। | none found | inference |
| journey metaphor | स्वाद की यात्रा पर चलिए। | 12 राज्यों की 40 डिश, एक मेन्यू में। | none found | inference |
| passive with an agent | हमारे शेफ़ द्वारा हर डिश ताज़ा तैयार की जाती है। | हमारे शेफ़ हर डिश ऑर्डर के बाद बनाते हैं। | Microsoft voice rules | inference |
| busy-world opener | आज की भागदौड़ भरी ज़िंदगी में सेहत ज़रूरी है। | लंच छूट जाता है? 15 मिनट में सलाद। | none found | inference |
| letter opener | प्रिय ग्राहकों, दिवाली ऑफ़र शुरू हो गया है। | दिवाली ऑफ़र शुरू: हर ऑर्डर पर ₹100 कैशबैक। | none found | inference |
| engagement bait | दोस्तों को टैग करें और शेयर ज़रूर करें! | आपकी फ़ेवरेट कौन सी है, मसाला या इलायची? | none found | inference |
| chatbot framing | यहाँ आपके लिए कुछ कैप्शन दिए गए हैं: | delete it | none found | inference |
| Roman textbook calques | Naye swaad khojein aur anubhav karein. | Naya menu try karo, ₹249 se. | none found | inference |

#### Purple or poetic phrasing
- स्वाद का जादू, हर बाइट में जादू: name what is in it (हर बर्गर में 150 ग्राम पनीर).
- हर पल को ख़ास बनाएँ: name the moment (शाम की चाय के साथ).
- सपनों को दें नई उड़ान: give the concrete result (EMI ₹999 महीने से).
- परंपरा और आधुनिकता का अनूठा संगम: say what is old and what is new (दादी की रेसिपी, एयर फ़्रायर में).
- दिल को छू लेने वाला अनुभव: give one detail a customer would repeat.
Confidence: inference; India TV's "over-polished" pattern is the closest source.

#### Natural vs robotic lines
Natural:
- बारिश में पकौड़े का मन? आज शाम 7 बजे तक सारे कॉम्बो पर 20% की छूट।
- Chai ke saath samosa? Sirf ₹49 mein, aaj raat 10 baje tak.
- Weekend ka plan pakka? Movie ticket pe ₹150 off, code FILMY150 lagao.
- दिवाली सेल शुरू! ₹999 से ऊपर की शॉपिंग पर ₹200 कैशबैक, सिर्फ़ ऐप पर।

Robotic, each with a fix:
- यह सिर्फ़ एक चाय नहीं, बल्कि सुकून का एहसास है।
  Fix: कड़क इलायची चाय, ₹30 में। शाम 5 से 7 बजे तक समोसा फ़्री।
- हमारे नए मेन्यू के साथ स्वाद की यात्रा का अनुभव करें।
  Fix: नया मेन्यू आ गया: 12 नई डिश, ₹149 से शुरू। आज ही चखिए।
- प्रिय ग्राहकों, हम आपको सर्वोत्तम सेवा प्रदान करते हैं।
  Fix: ऑर्डर में दिक़्क़त? चैट पर लिखिए, 10 मिनट में जवाब मिलेगा।
- Apne pasandeeda khane ka anubhav karein aur naye swaad khojein.
  Fix: Naya menu aa gaya! Butter chicken combo sirf ₹249, aaj try karo.

#### Hypothesis check
- Confirmed (native source): सिर्फ़/केवल X नहीं, बल्कि Y. India TV lists "यह X नहीं, बल्कि Y है" among six AI patterns,
  with the rule of three, the em dash and over-polish.
- Kept as inference (no Hindi source found): अनुभव करें, खोजें and अन्वेषण, आनंद लें, यात्रा as a metaphor, नई
  ऊँचाइयों, आज की तेज़ रफ़्तार दुनिया में, सुनिश्चित करें, प्रदान करता है, द्वारा with a passive, हेतु, क्रय,
  निःशुल्क, अत्यंत, शीघ्र, आपका in every phrase.
- Refined: "Google Translate shuddh Hindi". Zulip's Hindi guide says informal Hindi avoids text that looks
  machine-written and notes that Google uses it; the heaviest coinages trace to official glossaries.
- Rejected as tells: उपलब्ध, उत्पाद, प्राप्त करें, कृपया (all standard), तत्काल (Tatkal ticket).
- Not verified: the voices of Zomato, Swiggy, Blinkit, Zepto and Amul topicals. The pages found describe Zomato's tone
  as a friend talking, but quote no Hinglish lines; Amul's site was in maintenance. The Hinglish casual words above are
  inference.

#### Sources
- कैसे पहचानें कि कोई लेख AI ने लिखा है? खास पैटर्न से पकड़ सकते हैं मशीन की भाषा (Vineet Kumar Singh, 2026-08-25), India TV Hindi, https://www.indiatv.in/explainers/how-to-detect-ai-written-text-6-language-patterns-that-reveal-machine-writing-2026-08-25-1239356 (read 2026-09-24, read)
- Can Large Language Models Understand, Reason About, and Generate Code-Switched Text? (Winata et al., 2026-01-12), arXiv, https://arxiv.org/html/2601.07153v1 (read 2026-09-24, read)
- Hindi Style Guide, Microsoft Localization Style Guides, https://aka.ms/hindi-styleguide (read 2026-09-24, read)
- Microsoft Localization Style Guides (index), Microsoft Learn, https://learn.microsoft.com/en-us/globalization/reference/microsoft-style-guides (read 2026-09-24, read)
- Hinglish, Wikipedia, https://en.wikipedia.org/wiki/Hinglish (read 2026-09-24, read)
- Is Indian advertising underappreciating its Hindi storytellers? (2025-09-12), Social Samosa, https://www.socialsamosa.com/experts-speak/is-indian-advertising-underappreciating-hindi-copywriters-10441457 (read 2026-09-24, read)
- How to Create Ads in Hindi with AI (2026-08-01), Lapis, https://www.trylapis.com/resources/create-ads-hindi-ai (read 2026-09-24, read)
- Hindi translation style guide, Zulip documentation, https://github.com/zulip/zulip/blob/5.0/docs/translating/hindi.md (read 2026-09-24, read)
- Zomato's Push Notification Strategy: A Copywriting Breakdown (2026-04-30), Juno School, https://www.junoschool.org/article/zomato-push-notification-strategy/ (read 2026-09-24, read)
- Zomato and Swiggy Push Notifications: Why They Convert So Well (2026-05-26), PushPilot, https://pushpilot.ai/blog/zomato-swiggy-push-notification-teardown (read 2026-09-24, read; English-only examples)
- Prefer Hinglish words over pure, Deccan Herald, https://www.deccanherald.com/amp/story/india%2Fprefer-hinglish-words-over-pure-2459817 (read 2026-09-24, snippet; the page refused fetching)
- सरल हिन्दी परिपत्र (upload by Pramod Joshi), Scribd, https://www.scribd.com/doc/68883631/%E0%A4%B8%E0%A4%B0%E0%A4%B2-%E0%A4%B9%E0%A4%BF%E0%A4%A8-%E0%A4%A6%E0%A5%80-%E0%A4%AA%E0%A4%B0%E0%A4%BF%E0%A4%AA%E0%A4%A4-%E0%A4%B0 (read 2026-09-24, read; only the opening was visible)

### 4.2 Arabic (ar)

#### Register guide

- Social copy should sound like the market's own dialect. Standard Arabic reads formal, and the new evidence says so plainly. Nemer Al-Qarout, a product director who worked on Careem and talabat localisation, says standard Arabic microcopy can be correct and still feel cold and distant (Product-Led Alliance, June 2026). He also says talabat kept separate copy decks and CTAs for each market cluster. In Al Majalla (2020), Saudi creative director Hisham Abdo calls fusha in ads stiff and distant. Writer Noof Al-Harbi suggests the "white dialect" for reach across Saudi Arabia: simple fusha with familiar colloquial words everyone understands. Confidence: native source.
- An Arab copywriter's post on Medium compares ChatGPT's Arabic ad copy to an old-fashioned radio news bulletin (snippet only). Confidence: single source.
- Casual markers by dialect. Use one dialect per post.
  - Gulf: الحين، وش or إيش، زين، واجد or وايد، لين (until)، علينا (on us)، حيّاكم، لا يفوتكم.
  - Egyptian: دلوقتي، عايز or عايزة، إيه، أوي، جامد، بجد، كده، بقى، خلاص، لحد، بس.
  - Levantine: هلق or هلّأ، شو، كتير، منيح، هيك، فيك (you can)، بدّك، يلا.
  - Moroccan: دابا، بزاف، واخا، مزيان، غير (only)، فابور (free).
  - Confidence: Wikipedia confirms وش and إيش (Gulf), إيه, بقى and خلاص (Egyptian), منيح and كتير (Levantine) and daba (Moroccan). The rest is inference.
- Sentence shape: open with a question in dialect (وش تنتظر؟ / عايز ...؟ / شو رأيك ...؟). Then give the price, time and place in one short clause. Phrases with no verb are fine (القهوة الثانية علينا). Leave out essay connectors, حيث chains and the تم or قام helper verbs. Confidence: inference, consistent with the tell sources below.
- Address: the skill already requires plural verbs or no verb. Here are the plural forms used in each dialect:
  - Gulf: اطلبوا، حيّاكم، لا يفوتكم
  - Egyptian and Levantine: الحقوا (hurry), جرّبوا
  - Gulf copy often says علينا (it's on us) instead of مجاناً.
  - Confidence: inference.
- Mixing in English: English nouns written in Arabic script are normal and take Arabic grammar (أوردر، أوردرك، الديليفري، أونلاين، الأوفرات، كومبو، ويكند). Keep Latin script for brand or event names only. Maghreb copy mixes in French loans (كوموند، ليفريزون، بروموسيون). Wikipedia notes that Moroccan Arabic is strong in advertising and that speakers switch to French. Confidence: single source (Maghreb), inference (loanword grammar).
- Arabizi (a7la, ya3ni, 3shan) is Arabic written in Latin letters and digits. Wikipedia says Levantine speakers use it on social media and Moroccans prefer it for chat and SMS, and that it has appeared in advertising. The rule for brands: use Arabic script by default. Use Arabizi only if the brand already talks to a youth audience that way, and never mix it with Arabic script in the same line. Confidence: single source (usage), inference (brand rule). I found no 2024 to 2026 data on brands using it.
- Trust cues differ by market. According to Al-Qarout (2026), an official tone builds trust in Saudi Arabia, social proof and community language work in Egypt, and warmth works in Jordan. Bayan Tech (2026) notes that Egyptian Arabic is understood widely enough for pan-Arab campaigns, while Gulf ads should use Gulf dialect. Confidence: several sources.
- Emoji: put an emoji after a complete clause. Never put one between a number and its currency word, because right-to-left text layout can reorder the neutral characters and split "29 ريال". Confidence: inference.

#### Formal to everyday swaps

| Formal (MSA) | Everyday | Note (dialect) | Confidence |
|:-|:-|:-|:-|
| الآن | الحين / دلوقتي / هلق / دابا | Gulf / Egyptian / Levantine / Moroccan | single source (دابا), rest inference |
| ماذا تريد؟ | وش تبي؟ / عايز إيه؟ / شو بدك؟ | Gulf / Egyptian / Levantine | several sources (وش، إيه), rest inference |
| جيد جداً | زين / كويس أوي / منيح كتير | Gulf / Egyptian / Levantine | single source (منيح، كتير), rest inference |
| كثيراً | واجد / أوي / كتير / بزاف | Gulf / Egyptian / Levantine / Moroccan | single source (كتير), rest inference |
| تم افتتاح فرعنا الجديد | فتحنا فرعنا الجديد; in MSA افتُتح | all dialects; removes the تم calque | native source |
| نقوم بتوصيل طلبك | نوصّلك طلبك / بنوصّلك الأوردر / منوصّلك طلبك | Gulf / Egyptian / Levantine; removes the قام بـ calque | native source (calque), inference (dialect) |
| مُعدّ من قبل طهاتنا | طهاتنا يحضّرونه كل صبح | Gulf or light MSA; doer as subject | native source |
| برجر، بيتزا، وحلا | برجر وبيتزا وحلا | all; list joined with و | native source |
| التوصيل مجاني | التوصيل علينا / الديليفري ببلاش / التوصيل ببلاش / فابور | Gulf / Egyptian / Levantine / Moroccan | inference |
| احصل على خصم 20% | خذ / خد / خود خصم 20% | Gulf / Egyptian / Levantine; احصل على copies "get" | inference |
| سارع بالطلب، لا تفوت الفرصة | لا يفوتكم / الحقوا | Gulf / Egyptian and Levantine; add the deadline | inference |
| لفترة محدودة | لين الخميس / لحد الخميس بس | Gulf / Egyptian; name the day | inference |
| يسعدنا أن نعلن عن افتتاح ... | الفرع الجديد فتح اليوم | all; state the news | inference |

#### AI and translation tells

| Tell | Robotic example | Natural fix | Evidence | Confidence |
|:-|:-|:-|:-|:-|
| ليس مجرد X بل Y, ليس فقط, لا يقتصر على | هذه ليست مجرد قهوة، بل أسلوب حياة | قهوتنا تنطحن كل صبح (Gulf) | Khaled Al-Yahya on X calls the hedge "ليس كذا.. بل كذا" a recurring AI habit | single source (native writer) |
| Scene-setting opener | في عالم اليوم المتسارع، صار التوصيل ضرورة | التوصيل خلال 30 دقيقة داخل الرياض | amwaly.com guide lists في عالم اليوم | single source |
| Essay connectors | علاوة على ذلك، يوفر التطبيق ... | cut it and start a new line | Al-Rai (March 2026) names علاوة على ذلك and بالإضافة إلى ذلك; amwaly names من ناحية أخرى and في الختام | several sources |
| تم + verbal noun | تم إطلاق النكهة الجديدة | النكهة الجديدة نزلت (Gulf) | قطار الترجمة, error 3; Ahmed Jameel | several sources (native) |
| قام بـ + verbal noun | نقوم بتجهيز طلبك خلال دقائق | نجهّز طلبك في 10 دقايق | Ahmed Jameel (LinkedIn, 2015) | native source |
| من قبل / من طرف / بواسطة for "by" | مصنوع بواسطة حرفيين محليين | حرفيين من جدة يصنعونه | EnglishTips&Tools; قطار الترجمة, error 1 | several sources (native) |
| English list commas X، Y، وZ | برجر، بيتزا، وحلا | برجر وبيتزا وحلا | قطار الترجمة, error 2 | native source |
| Phrase moved to the front, then a comma | في رمضان، نقدم لكم خصم 30% | رمضان هذا عندنا خصم 30% (Gulf) | قطار الترجمة, error 9 | native source |
| Empty claims about the "experience" | تجربة فريدة من نوعها، كل ما تحتاجه في مكان واحد | the concrete fact: الطلب يوصلك حار خلال 20 دقيقة | amwaly names empty descriptors; rest inference | single source |
| AI verbs | انغمس في عالم الأناقة، أطلق العنان لإبداعك، ارتقِ بإطلالتك | جرّبوا المجموعة الجديدة | none found | inference |
| حيث chains | حيث يمكنك الاستمتاع بأجمل الأوقات | start a new clause | none found | inference |
| Report words | بشكل كبير، يعتبر، العديد من | واجد / كتير / أوي | none found | inference |
| Fusha mixed with clauses that sound translated | a standard Arabic caption that reads like English turned into Arabic | pick one register, one dialect | amwaly; annajah.net (Feb 2026) says AI uses literally translated expressions and leaves out local persuasive phrasing | several sources |
| Flat emotion, repeated words, stiffness | the same adjective three times in a post | vary words; add a real detail | Youm7 (19 Sep 2026): novelist Afnan Joulani on stiffness, repetition and broken flow in machine prose | single source (native) |

#### Purple or poetic phrasing

1. حيث تلتقي الأصالة بالحداثة. Fix: name the old thing and the new thing, for example قهوة سعودية بالهيل في مكان تصميمه حديث.
2. رحلة من النكهات / تأخذك في رحلة. Fix: give the dish and the price, for example مندي لحم بـ 65 ريال.
3. سيمفونية من النكهات / نكهات تأسر الحواس. Fix: describe the taste, for example حار ومقرمش.
4. لمسة من الفخامة / عنوان الأناقة. Fix: name the material, for example جلد طبيعي وخياطة يدوية.
5. بكل حب وشغف. Fix: describe the process, for example نخبزه كل يوم الساعة 6 الصبح.

#### Natural vs robotic lines

Natural:

1. (Gulf, Saudi) وش تنتظر؟ القهوة الثانية علينا كل يوم من 7 لين 10 الصبح
2. (Egyptian) عايز تتغدى من غير ما تستنى؟ اطلب دلوقتي والأوردر يوصلك في 30 دقيقة جوه مدينة نصر
3. (Levantine, Jordan) شو رأيك بفطور الجمعة؟ منقوشة زعتر مع كاسة شاي بـ 2 دينار بفرعنا بعبدون من 8 للساعة 12
4. (Moroccan) دابا التوصيل فابور فكازا على كل كوموند فوق 150 درهم، غير هاد السيمانة

Robotic, each with a fix:

1. عملاءنا الكرام، يسعدنا أن نعلن عن افتتاح فرعنا الجديد في الرياض
   Fix (Gulf): فرعنا الجديد في حي الملقا فتح اليوم، والقهوة الأولى علينا لين 10 الصبح
2. تم تصميم هذا المنتج بشكل احترافي من قبل نخبة من الخبراء
   Fix (Egyptian): الشنطة دي جلد طبيعي ومتخيطة باليد، وعليها ضمان سنتين
3. انغمس في رحلة من النكهات حيث تلتقي الأصالة بالحداثة
   Fix (Levantine): منسف على أصوله وكنافة سخنة، كل جمعة بفرعنا بعبدون
4. منشن لصديقك اللي يحب القهوة واكتب تم في التعليقات
   Fix (Gulf): قهوتكم الصبح حارة ولا باردة؟

#### Sources

- 10 أخطاء شائعة في الترجمة إلى اللغة العربية (Bushra L.), قطار الترجمة, https://translatrain.com/%D8%A3%D8%AE%D8%B7%D8%A7%D8%A1-%D8%B4%D8%A7%D8%A6%D8%B9%D8%A9-%D9%81%D9%8A-%D8%A7%D9%84%D8%AA%D8%B1%D8%AC%D9%85%D8%A9/ (read 2026-09-24, read)
- 7 «بصمات كاشفة» تفضح النص المكتوب بالذكاء الاصطناعي (Abdulaleem Al-Hajjar, 22 Mar 2026), الراي, https://www.alraimedia.com/article/1760414/%D8%A3%D8%AE%D9%8A%D8%B1%D8%A9/%D8%A3%D8%AE%D8%A8%D8%A7%D8%B1-%D9%85%D9%86%D9%88%D8%B9%D8%A9/7-%D8%A8%D8%B5%D9%85%D8%A7%D8%AA-%D9%83%D8%A7%D8%B4%D9%81%D8%A9-%D8%AA%D9%81%D8%B6%D8%AD-%D8%A7%D9%84%D9%86%D8%B5-%D8%A7%D9%84%D9%85%D9%83%D8%AA%D9%88%D8%A8-%D8%A8%D8%A7%D9%84%D8%B0%D9%83%D8%A7%D8%A1-%D8%A7%D9%84%D8%A7%D8%B5%D8%B7%D9%86%D8%A7%D8%B9%D9%8A (read 2026-09-24, read)
- كيف تجعل نص الذكاء الاصطناعي يبدو طبيعياً بالعربية, أموالي, https://tech.amwaly.com/blog/207411/%D9%83%D9%8A%D9%81-%D8%AA%D8%AC%D8%B9%D9%84-%D9%86%D8%B5-%D8%A7%D9%84%D8%B0%D9%83%D8%A7%D8%A1-%D8%A7%D9%84%D8%A7%D8%B5%D8%B7%D9%86%D8%A7%D8%B9%D9%8A-%D9%8A%D8%A8%D8%AF%D9%88-%D8%B7%D8%A8%D9%8A%D8%B9%D9%8A%D8%A7-%D8%A8%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9 (read 2026-09-24, read)
- Khaled Al-Yahya post on the AI hedge pattern, X, https://x.com/Kh_alyahya/status/2004869958791033302?lang=ar (read 2026-09-24, snippet)
- Stop Using ChatGPT for Arabic Content, Medium, https://medium.com/@abdelmseehhenri/stop-using-chatgpt-for-arabic-content-4332ff9c8f18 (read 2026-09-24, snippet)
- 3 ways product teams get Arabic localization wrong (Nemer Al-Qarout, 16 Jun 2026), Product-Led Alliance, https://www.productledalliance.com/3-ways-product-teams-get-arabic-localization-wrong/ (read 2026-09-24, read)
- لماذا يتأرجح المحتوى الإعلاني السعودي بين الفصحى و«البيضاء» والعامية؟ (31 Aug 2020), المجلة, https://www.majalla.com/node/101306/%D9%84%D9%85%D8%A7%D8%B0%D8%A7-%D9%8A%D8%AA%D8%A3%D8%B1%D8%AC%D8%AD-%D8%A7%D9%84%D9%85%D8%AD%D8%AA%D9%88%D9%89-%D8%A7%D9%84%D8%A5%D8%B9%D9%84%D8%A7%D9%86%D9%8A-%D8%A7%D9%84%D8%B3%D8%B9%D9%88%D8%AF%D9%8A-%D8%A8%D9%8A%D9%86-%D8%A7%D9%84%D9%81%D8%B5%D8%AD%D9%89-%D9%88%C2%AB%D8%A7%D9%84%D8%A8%D9%8A%D8%B6%D8%A7%D8%A1%C2%BB-%D9%88%D8%A7%D9%84%D8%B9%D8%A7%D9%85%D9%8A%D8%A9%D8%9F (read 2026-09-24, read)
- Common Errors in Arabic Language Translations (Ahmed Jameel, 2015), LinkedIn, https://ae.linkedin.com/pulse/common-errors-arabic-language-ahmed-jameel (read 2026-09-24, read)
- بعض الأخطاء الشائعة في ترجمة المبني للمجهول, EnglishTips&Tools, http://englishtipsandtools.blogspot.com/2013/10/blog-post_1890.html (read 2026-09-24, read)
- الكاتب الشبح.. هل بدأ الذكاء الاصطناعي يكتب الرواية العربية؟ (19 Sep 2026), اليوم السابع, https://www.youm7.com/story/2026/9/19/%D8%A7%D9%84%D9%83%D8%A7%D8%AA%D8%A8-%D8%A7%D9%84%D8%B4%D8%A8%D8%AD-%D9%87%D9%84-%D8%A8%D8%AF%D8%A3-%D8%A7%D9%84%D8%B0%D9%83%D8%A7%D8%A1-%D8%A7%D9%84%D8%A7%D8%B5%D8%B7%D9%86%D8%A7%D8%B9%D9%8A-%D9%8A%D9%83%D8%AA%D8%A8-%D8%A7%D9%84%D8%B1%D9%88%D8%A7%D9%8A%D8%A9-%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-%D9%85%D9%86/7551006 (read 2026-09-24, read)
- كيف تستخدم الذكاء الاصطناعي لكتابة محتوى عربي احترافي؟ (9 Feb 2026), النجاح نت, https://www.annajah.net/%D9%83%D9%8A%D9%81-%D8%AA%D8%B3%D8%AA%D8%AE%D8%AF%D9%85-%D8%A7%D9%84%D8%B0%D9%83%D8%A7%D8%A1-%D8%A7%D9%84%D8%A7%D8%B5%D8%B7%D9%86%D8%A7%D8%B9%D9%8A-%D9%84%D9%83%D8%AA%D8%A7%D8%A8%D8%A9-%D9%85%D8%AD%D8%AA%D9%88%D9%89-%D8%B9%D8%B1%D8%A8%D9%8A-%D8%A7%D8%AD%D8%AA%D8%B1%D8%A7%D9%81%D9%8A-article-47347 (read 2026-09-24, read)
- Arabic Dialects for Business (Heba El Tarabishy, 6 Aug 2026), Bayan Tech, https://bayan-tech.com/blog/arabic-dialects/ (read 2026-09-24, read)
- Arabic chat alphabet, Wikipedia, https://en.wikipedia.org/wiki/Arabic_chat_alphabet (read 2026-09-24, read)
- Gulf Arabic, Wikipedia, https://en.wikipedia.org/wiki/Gulf_Arabic (read 2026-09-24, read)
- Egyptian Arabic, Wikipedia, https://en.wikipedia.org/wiki/Egyptian_Arabic (read 2026-09-24, read)
- Levantine Arabic, Wikipedia, https://en.wikipedia.org/wiki/Levantine_Arabic (read 2026-09-24, read)
- Moroccan Arabic, Wikipedia, https://en.wikipedia.org/wiki/Moroccan_Arabic (read 2026-09-24, read)

#### Could not verify

- X and Medium returned 403, so the Al-Yahya and Medium points are search snippets only.
- No real brand posts could be fetched (Instagram and X need a login; brand sites returned empty pages), so brand wording such as the Gulf علينا is inference.
- No 2024 to 2026 data on brands using Arabizi.
- No native source for بشكل, يعتبر, العديد من, حيث, انغمس or أطلق العنان; they are inference.

### 4.3 Spanish (es)

#### Register guide

- Fact first, one idea per line. Everyday brand posts lead with the offer and a hard fact (price, hour, place). Maldita.es's experts describe machine Spanish as ceremonious, relentlessly positive, generic and closed with very rounded endings, and say it lacks colloquial and regional texture. (native source)
- Market words, not checked this session: ES finde, planazo, pásate, mola, vale, plus the os and queréis forms; MX se te antoja, quincena, Buen Fin, meses sin intereses, with padre and chido only for youth brands; AR voseo imperatives (pedí, probá, aprovechá), re as an intensifier (re fácil), cuotas sin interés, Hot Sale; CO usted even in a casual tone, chévere, de una; CL and PE bacán. (inference)
- Questions work as hooks when they are concrete (¿Plan para el sábado?). The bare one-word question followed by its answer (¿La trampa?, ¿El resultado?) is a named AI transition. (native source: León Carpio)
- Code-mixing: keep the loanwords the market already uses in social copy (link en bio, look, outfit, tips, stock, Black Friday, Hot Sale in MX and AR, 30 % off in AR) and translate the rest. Never spell out a loan the market shortens: enlace en la biografía reads as machine translation. (inference)
- Emoji and laughter: jajaja is the default laugh in every market (jsjs among younger users). Emoji close a line to set its tone; they do not open list items. (inference)
- Voice benchmark: ironic, meme-literate accounts (Ryanair, Burger King, Netflix and local Argentine brands) set the tone for social in Spain and Argentina. LA NACION's warning is that forced humour reads rigid or false. (single source)
- Headlines take sentence case. A Spanish editor names English Title Case on LinkedIn titles as a ChatGPT sign. This is now linted by the Title Case structure candidate. (native source: Iturbide)
- Most Spanish "ChatGPT words" lists (Genbeta, ADSLZone, Xataka) are translations of English studies (Margaret Efron's Medium list, AI Phrase Finder, the delve research). Treat single words from them (vibrante, innovador, transformador, cautivar, tapiz, crucial) as weak signals and lint phrases instead. (several sources)
- Native marketers single out a small set of stock copy phrases: descubre, sumérgete, transforma tu vida, potencia tu negocio, experiencia única, en un mundo..., ¿Sabías que...? They also name corporate filler (sinergia, potenciar, optimizar) and copy that is correct but has no soul. (several sources: Julita en Remoto, OliSapiens, Borja Girón)

#### Formal to everyday swaps

| formal | everyday | note (variant) | confidence |
|-|-|-|-|
| adquirir, adquiera | comprar; llévate (ES, MX), llevate (AR), llévese (CO) | imperative follows the market's address form | inference |
| realizar su pedido | pide (ES, MX), pedí (AR), pida (CO) | all | inference |
| efectuar el pago | pagar | all | inference |
| contamos con | tenemos | all | inference |
| disponer de | tener | all | inference |
| con el objetivo de, a fin de | para | all | inference |
| en la actualidad | hoy, ya, ahora | all | inference |
| le informamos que | drop it and give the news; te contamos | all | inference |
| no dude en contactarnos | escríbenos (ES, MX), escribinos (AR), escríbanos (CO) | all | inference |
| le invitamos a visitarnos | pásate (ES), date una vuelta (MX), vení (AR), lo esperamos (CO) | market-specific | inference |
| obsequio | regalo | all | inference |
| establecimiento | tienda, local | all | inference |
| fin de semana | finde | ES, AR, younger MX audiences | inference |
| en base a | según, a partir de, con | all | native source (Wikilengua) |
| aplicar a un empleo o una beca | postularse, solicitar | ES and formal copy; LATAM uses aplicar widely | several sources (RAE DPD and El español sin misterios, snippets) |

#### AI and translation tells

| tell | robotic example | natural fix | evidence | confidence |
|-|-|-|-|-|
| Scene-setting opener | En un mundo donde todo va rápido, te ofrecemos calma. | Yoga a las 7:00 en Chamberí, 12 € la clase. | León Carpio; Julita en Remoto; ADSLZone (en el dinámico mundo de) | several sources |
| Immersion verbs (sumérgete, adéntrate, embárcate) | Sumérgete en el sabor de Oaxaca. | Mole negro de Oaxaca, $180 el plato. | Julita en Remoto; Borja Girón; PostPro App Store listing | several sources |
| Growth calques (al siguiente nivel, eleva tu, potencia tu, desbloquea tu potencial, transforma tu vida) | Lleva tu negocio al siguiente nivel. | Vende más en diciembre con envíos en 24 h. | Julita en Remoto; Borja Girón; PostPro listing | several sources |
| Antithesis No es solo X, es Y | No es solo café, es un ritual. | Café de especialidad tostado cada lunes. | León Carpio | native source |
| One-word question hook | ¿El secreto? Amor. | Masa madre de 48 horas. | León Carpio | native source |
| Essay connectors, closers and the inflated role phrase | Cabe destacar que tu rutina juega un papel crucial. En resumen, te esperamos. | Abrimos el domingo de 10 a 14. | Genbeta; Borja Girón; Maldita.es; CVC (jugar un papel is an accepted gallicism, so the inflation is the tell) | several sources |
| Title Case headline | Descubre Nuestra Nueva Colección | Nueva colección de otoño | Iturbide | native source |
| Future progressive calque | Estaremos enviando los premios el lunes. | Enviamos los premios el lunes. | none found | inference |
| Trailing gerund clause (gerundio de posterioridad) | Nuevo sérum, haciendo que tu piel brille. | Nuevo sérum. Tu piel, luminosa en 7 días. | Fundéu Guzmán Ariza and Academia Argentina de Letras for the rule (snippets) | several sources for the rule; the AI link is inference |
| Calqued announcement and CTA lines | Estamos emocionados de anunciar... Siéntete libre de escribirnos. | Tenemos novedades: abrimos en Gràcia el 3 de octubre. Escríbenos cuando quieras. | none found for Spanish; the email opener is flagged in Portuguese | inference |
| Possessive with body parts | Lava tus manos antes de cocinar. | Lávate las manos antes de cocinar. | none found | inference |
| en base a, a nivel de, aplicar | Precios en base a tu zona. | Precios según tu zona. | Wikilengua (two entries); RAE DPD (snippet) | several sources |
| Chatbot leftovers | ¡Claro! Aquí tienes una propuesta: ... | Delete the wrapper. | La Tercera (via Semana) on Como un modelo de lenguaje IA | single source |
| Single words from translated lists | Un espacio vibrante e innovador. | Un bar con terraza y DJ los viernes. | Genbeta; ADSLZone; elEconomista headline (snippet) | several sources, all derived from English lists |
| Generic promise | Vive una experiencia única. | Cena en la terraza con vistas, 45 € por persona. | Julita en Remoto | single source |

#### Purple or poetic phrasing

1. un viaje de sabores, un tapiz de sabores, una sinfonía de aromas. Fix: name the dish and one fact, for example "Tacos al pastor con piña asada, 3 por $75."
2. donde la tradición se encuentra con la modernidad (a calque of "where X meets Y"). Fix: say what is old and what is new, for example "Receta de 1962, horno nuevo."
3. cada bocado cuenta una historia. Fix: tell the story in one fact, for example "Masa madre de 48 horas."
4. despierta tus sentidos, déjate llevar. Fix: give the sensory fact, for example "Pan recién hecho desde las 7:00."
5. haz que cada momento cuente. Fix: name the occasion, for example "Para la cena del viernes."
6. descubre la magia de... Fix: drop it and name the thing.

#### Natural vs robotic lines

Natural:
- es-ES: Este finde, 2x1 en todas las pizzas medianas. Pídelas en la app hasta el domingo a las 23:59.
- es-MX: Ya llegó la quincena: 15 % de descuento en tenis seleccionados, solo en tiendas de CDMX y Monterrey.
- es-AR: Pedí hasta las 22 y te llega mañana. Envío gratis en CABA desde $25.000.
- es-CO: ¿Ya conoce la nueva sede en Chapinero? Abrimos de lunes a sábado de 8 a. m. a 7 p. m.

Robotic, each with its fix:
- es-ES robotic: En el vertiginoso mundo de la moda, sumérgete en nuestra colección y lleva tu estilo al siguiente nivel.
  Fix: Nueva colección de otoño: chaquetas desde 39,99 € en tienda y online hasta el domingo.
- es-MX robotic: Descubre la magia de nuestro café de olla: un viaje de sabores donde la tradición se encuentra con la modernidad.
  Fix: Café de olla con piloncillo y canela, como el de la abuela. Vaso grande a $45 todo octubre.
- es-CO robotic: Estimado cliente: estamos emocionados de anunciar nuestra nueva tienda. Siéntete libre de visitarnos.
  Fix: Abrimos tienda en el Centro Andino este sábado a las 10 a. m. Los primeros 50 clientes se llevan un termo.
- es-AR robotic: ¡Apresúrate! Oferta por tiempo limitado. Más información en el enlace de nuestra biografía.
  Fix: Hasta el domingo, 30 % off en toda la tienda y 6 cuotas sin interés. Link en bio.

#### Could not verify (es)

- The individual market slang (chido, padre, neta, guay, mola, bacán, chévere, re, posta, che, finde) and the brand voices of Mercado Libre, Rappi, Glovo, Telepizza, Oxxo and Netflix LATAM. No source was opened before the search budget ran out.
- No Spanish source was found for estaremos + gerund, the body-part possessive, siéntete libre de or mantente sintonizado. They are linted on inference.

#### Sources

- 11 señales de que ChatGPT escribió tu texto, Substack (Luis Orlando León Carpio, Spain, 2025-10-30), https://luisorlandolencarpio.substack.com/p/11-senales-de-que-chatgpt-escribio (read 2026-09-24, read)
- Copywriting con IA: Textos que Sí Venden (2026), Julita en Remoto (Argentina), https://julitaenremoto.com/copywriting-con-ia/ (read 2026-09-24, read)
- Las Palabras y Frases que repite ChatGPT, Borja Girón, https://borjagiron.com/palabras-frases-repite-chatgpt/ (read 2026-09-24, read)
- ¿Se puede saber si un texto está escrito con inteligencia artificial?, Maldita.es, https://maldita.es/malditatecnologia/20250917/detectar-textos-generados-inteligencia-artificial/ (read 2026-09-24, read)
- Copywriting con IA: cómo escribir sin sonar a robot, OliSapiens, https://olisapiens.com/blog/copywriting-con-ia/ (read 2026-09-24, read)
- ChatGPT: ¿El nuevo Cervantes o un loro con Wi-Fi?, Substack (Oihan Iturbide), https://loseditoresdenextdoor.substack.com/p/chatgpt-el-nuevo-cervantes-o-un-loro (read 2026-09-24, read)
- Estas palabras y frases de tus textos lo dejan claro: has usado ChatGPT, Genbeta, https://www.genbeta.com/inteligencia-artificial/estas-palabras-frases-tus-textos-dejan-claro-has-usado-chatgpt (read 2026-09-24, read)
- ¿Quieres saber si algo se ha escrito con ChatGPT? Presta atención a estas palabras, ADSLZone, https://www.adslzone.net/noticias/ia/palabras-mas-usadas-chatgpt/ (read 2026-09-24, read)
- ChatGPT está escribiendo estudios médicos y económicos, Xataka, https://www.xataka.com/robotica-e-ia/chatgpt-esta-escribiendo-estudios-medicos-economicos-sabemos-porque-usa-palabras-rarunas (read 2026-09-24, read)
- ChatGPT: las palabras que delatan a los estudiantes, La Tercera, https://www.latercera.com/tendencias/noticia/chatgpt-las-palabras-que-delatan-a-los-estudiantes-que-presentan-textos-hechos-con-inteligencia-artificial/XU4I6AWNFJE2BIBSIYHXW2SDCM/ (read 2026-09-24, read)
- De "crucial" a "esencial": las palabras que revelan que un texto está escrito con IA, elEconomista, https://www.eleconomista.es/tecnologia/noticias/12925132/07/24/de-crucial-a-esencial-estas-son-las-palabras-que-revelan-que-un-texto-esta-escrito-con-ia.html (read 2026-09-24, snippet)
- PostPro: AI for Posts Creation, App Store listing in Spanish, https://apps.apple.com/hn/app/postpro-ai-for-posts-creation/id6462699110 (read 2026-09-24, read)
- a nivel de, Wikilengua, https://www.wikilengua.org/index.php/a_nivel_de (read 2026-09-24, read)
- en base a, Wikilengua, https://www.wikilengua.org/index.php/en_base_a (read 2026-09-24, read)
- Jugar un papel importante, CVC Instituto Cervantes, https://cvc.cervantes.es/lengua/alhabla/museo_horrores/museo_052.htm (read 2026-09-24, read)
- jugar un papel, Fundéu (Facebook post), https://www.facebook.com/fundeu/posts/se-puede-jugar-un-papel-pero-tambi%C3%A9n-representarlo-o-desempe%C3%B1arlo/859337167424048/ (read 2026-09-24, snippet)
- aplicar, aplicarse, Diccionario panhispánico de dudas, RAE, https://www.rae.es/dpd/aplicar (read 2026-09-24, snippet)
- Aplicar a una universidad o a un trabajo: anglicismo superfluo, El español sin misterios, http://espanolsinmisterios.blogspot.com/2011/07/aplicar-una-universidad-o-un-trabajo.html (read 2026-09-24, snippet)
- gerundio de posterioridad, restricciones de uso, Fundéu Guzmán Ariza, https://fundeu.do/gerundio-de-posterioridad-restricciones-de-uso/ (read 2026-09-24, snippet)
- Fundéu BBVA en la Argentina recomienda evitar el gerundio de posterioridad, Academia Argentina de Letras, https://www.aal.edu.ar/?q=node%2F49 (read 2026-09-24, snippet)
- El boom de la sátira digital: el contenido raro se impone entre las marcas, LA NACION, https://www.lanacion.com.ar/economia/negocios/el-boom-de-la-satira-digital-el-contenido-raro-se-impone-entre-las-marcas-nid11112023/ (read 2026-09-24, read)
- Ryanair: Utilizamos mucho social media, MarketingNews, https://www.marketingnews.es/marcas/noticia/1168769054305/ryanair-utilizamos-mucho-social-media-mas-fuerza-instagram-y-tiktok.1.html (read 2026-09-24, read)

### 4.4 Portuguese (pt)

#### Register guide

- BR casual copy is written the way people talk: tá, pra, a gente, bora, vem, corre (native urgency), chegou to open a launch, sextou on Fridays, promo, off (R$ 10 off). (inference; the dictionary pages for these words could not be opened)
- Chat abbreviations and laughter (vc, tb, blz, vlw; kkkk, rs, haha) belong in replies and playful captions, not on banners. kkkk reads younger and louder than rs. (single source, pt.wikipedia Internetês, for the forms; the register advice is inference)
- PT-PT casual has its own words. Priberam marks fixe (cool, good) and bué (a lot) as informal and Portugal-only; malta, giro and telemóvel are further PT-PT markers. (single source for fixe and bué; inference for the rest)
- For an action in progress, PT-PT uses estar a + infinitive (estamos a preparar), while BR uses the gerund (estamos preparando). A BR gerund in PT-PT copy, or telemóvel and estás a in BR copy, is a wrong-variant tell. The Portuguese Wikipedia essay notes that several LLMs default to European Portuguese even where the context calls for another variant. (native source)
- Plain verbs win: é and tem, not constitui, possui, conta com or ostenta; usar, not utilizar. The Portuguese Wikipedia essay lists these swaps as AI habits and says human text prefers simple é and tem sentences. (native source)
- Code-mixing: in BR, delivery, cashback, Black Friday, live, look, link na bio and promo are native in social copy, and dicas beats tips. In PT-PT, take away, Black Friday and look are native. (inference)
- Headings and banners take sentence case (Dia das Mães, not Dia Das Mães), which is the Lusophone convention the Portuguese Wikipedia essay contrasts with AI output. (native source)
- Brazilian readers now call out specific AI words in posts and comments: crucial, jornada, mergulhar, incrível, oportunidade única, transformação, ansioso. A few of them in one caption mark it as AI. (several sources)
- TargetHD's Portuguese list is a translation of the same English list the Spanish sites used (Margaret Efron). The native evidence comes from the Portuguese Wikipedia essay, Marcelo Sabbatini and Exame. (several sources)

#### Formal to everyday swaps

| formal | everyday | note (variant) | confidence |
|-|-|-|-|
| adquirir | comprar; garanta o seu (BR promo) | BR, PT | inference |
| efetuar o pagamento | pagar | BR, PT | inference |
| possui, conta com, ostenta | tem, temos | BR, PT | native source (pt.wikipedia essay) |
| utilizar | usar | BR, PT | native source (pt.wikipedia essay) |
| com o objetivo de, a fim de | pra (BR casual), para | BR, PT | native source (pt.wikipedia essay flags com o objetivo de as wordy) |
| em decorrência de | por causa de | BR, PT | native source (pt.wikipedia essay) |
| gratuito | grátis | frete grátis (BR), portes grátis (PT) | inference |
| solicitar | pedir | BR, PT | inference |
| no momento | agora | BR, PT | inference |
| informamos que | drop it and give the news; olha só (BR) | BR, PT | inference |
| aguardamos a sua visita | passa aqui (BR), aparece (PT) | market-specific | inference |
| estabelecimento | loja | BR, PT | inference |
| vamos estar enviando | vamos enviar, a gente envia | mainly BR | single source (pt.wikipedia Gerundismo) |
| estamos preparando (in PT-PT copy) | estamos a preparar | PT | single source (pt.wikipedia Português europeu) |
| apresse-se | corre | BR, PT | inference |

#### AI and translation tells

| tell | robotic example | natural fix | evidence | confidence |
|-|-|-|-|-|
| Scene-setting opener | No cenário atual, sua marca precisa aparecer. | Posts prontos pra sua loja em 48h, a partir de R$ 290. | pt.wikipedia essay (cenário as an abstract noun) | single source |
| Immersion and journey words | Mergulhe no universo do café e embarque nessa jornada. | Café coado do Sul de Minas, torra desta semana. | Sabbatini (mergulhar); Stork post comments (jornada) | several sources |
| Growth calques (ao próximo nível, eleve, potencialize, desbloqueie seu potencial) | Leve seu treino ao próximo nível. | Treino de 30 minutos, 3 vezes por semana, no app. | Stork post comments (transformação); the rest is inference | inference |
| Negative parallelism and a punchline closer | Não é apenas um café, é um ritual. E isso muda tudo. | Café torrado toda segunda, R$ 12 o coado. | Exame; pt.wikipedia essay | several sources |
| Essay fillers | Vale ressaltar que o frete é grátis. Em suma, aproveite. | Frete grátis até domingo. | pt.wikipedia essay; Sabbatini; TargetHD | several sources |
| Inflated role phrase | Nosso atendimento desempenha um papel fundamental. | Respondemos no WhatsApp em até 10 minutos. | pt.wikipedia essay | native source |
| High-density AI vocabulary | Uma tapeçaria de sabores, um testemunho da nossa paixão. | 14 sabores de sorvete feitos aqui. | pt.wikipedia essay; Sabbatini | several sources |
| Avoiding é and tem | A loja conta com estacionamento e possui Wi-Fi. | Tem estacionamento e Wi-Fi grátis. | pt.wikipedia essay | native source |
| Title Case headline | Promoção Dia Das Mães | Promoção de Dia das Mães | pt.wikipedia essay | native source |
| Gerundismo | Vamos estar enviando seu pedido. | A gente envia seu pedido hoje. | pt.wikipedia Gerundismo | single source |
| Calqued announcement lines | Estamos animados em anunciar nossa nova loja. Fique sintonizado! | Tem loja nova chegando! Fica ligado. | Stork post comments (ansioso); the rest is inference | inference |
| Translated email opener | Espero que esta mensagem o encontre bem. | Seu pedido saiu hoje e chega na quinta. | Sabbatini; Stork post comments | several sources |
| Wrong-variant default | Estamos a preparar novidades para o teu telemóvel. (in a BR post) | Estamos preparando novidade pro seu celular. | pt.wikipedia essay (LLMs default to European Portuguese) | native source |
| Chatbot leftovers | Claro! Aqui está uma legenda para o seu post: ... | Delete the wrapper. | pt.wikipedia essay (interface leaks) | native source |
| Generic promise | Uma experiência inesquecível e uma oportunidade única. | Jantar no terraço com vista pro mar, R$ 180 o casal. | Stork post comments | single source |

#### Purple or poetic phrasing

1. uma viagem de sabores, uma tapeçaria de cores, uma sinfonia de aromas. Fix: name the dish and one fact, for example "Baião de dois com queijo coalho, R$ 32."
2. onde a tradição encontra a modernidade. Fix: say what is old and what is new, for example "Receita da vó, forno novo."
3. cada detalhe conta uma história. Fix: give the detail, for example "Costurado à mão em 3 dias."
4. desperte seus sentidos, deixe-se levar. Fix: give the sensory fact, for example "Pão saindo do forno às 7h."
5. mergulhe no universo do café. Fix: "Café do Sul de Minas, torra da semana."

#### Natural vs robotic lines

Natural:
- pt-BR: Sextou com frete grátis: pedidos acima de R$ 99 até domingo, 23h59. Corre que é só até lá!
- pt-BR: Tá chovendo em SP? A gente entrega em até 40 minutos na zona sul, é só pedir pelo app.
- pt-PT: Portes grátis em encomendas acima de 30 €, até domingo. Aproveita para renovar o armário.
- pt-PT: Estamos a preparar uma surpresa para o fim de semana. Fica atento às stories na sexta às 18h.

Robotic, each with its fix:
- pt-BR robotic: No mundo atual, mergulhe no universo do café e leve sua rotina ao próximo nível.
  Fix: Café coado do Sul de Minas, torra desta semana. 250 g por R$ 34,90 no app.
- pt-BR robotic: Não é apenas um tênis, é uma experiência inesquecível. Marque aquele amigo que precisa de um!
  Fix: Tênis de corrida com 30% off até domingo. Tem do 34 ao 44 no site.
- pt-BR robotic: Prezado cliente, estamos animados em anunciar nossa nova loja. Vamos estar enviando os convites em breve.
  Fix: Loja nova na Vila Madalena! Abre sábado às 10h e os 50 primeiros ganham uma ecobag.
- pt-PT robotic: Apresse-se! Oferta por tempo limitado. Clique aqui e saiba mais.
  Fix: Só até domingo: dois cafés por 1,50 € em todas as lojas de Lisboa.

#### Could not verify (pt)

- Individual BR slang (bora, partiu, sextou, rolê, mó, tô, amei) and PT-PT malta, giro and telemóvel as social-copy markers: Dicionário Informal returned 403, and the search budget was gone.
- The brand voices of iFood, Nubank, Magalu, Mercado Livre, Netflix Brasil, Continente, Worten and MEO: no source opened.
- No Portuguese source was found for eleve, potencialize, fique sintonizado, tire vantagem or seja você X ou Y. They are linted on inference.

#### Sources

- Wikipédia:Sinais de texto gerado por inteligência artificial, pt.wikipedia.org (community essay), https://pt.wikipedia.org/wiki/Wikip%C3%A9dia:Sinais_de_texto_gerado_por_intelig%C3%AAncia_artificial (read 2026-09-24, read)
- O erro que faz seu texto parecer escrito por ChatGPT; Veja como evitar, Exame (2026-02-28), https://exame.com/carreira/o-erro-que-faz-seu-texto-parecer-escrito-por-chatgpt-veja-como-evitar/ (read 2026-09-24, read)
- Texto "chocho": como identificar a escrita da IA?, Substack (Marcelo Sabbatini, Brazil, 2024-12-10), https://iaedpraxis101.substack.com/p/texto-chocho-como-identificar-a-escrita (read 2026-09-24, read)
- Palavras que denunciam um texto escrito por IA, LinkedIn (Gustavo Stork, post and comments), https://pt.linkedin.com/posts/gustavo-stork_palavras-que-denunciam-um-texto-escrito-por-activity-7216509787105075200-rpRL (read 2026-09-24, read)
- As palavras que denunciam um texto escrito pelo ChatGPT, TargetHD, https://www.targethd.net/as-palavras-que-denunciam-um-texto-escrito-pelo-chatgpt/ (read 2026-09-24, read)
- 5 sinais de que um texto foi escrito pelo ChatGPT, ZÉducando, https://joserosafilho.wordpress.com/2024/01/24/5-sinais-de-que-um-texto-foi-escrito-pelo-chatgpt/ (read 2026-09-24, read)
- Gerundismo, pt.wikipedia.org, https://pt.wikipedia.org/wiki/Gerundismo (read 2026-09-24, read)
- Internetês, pt.wikipedia.org, https://pt.wikipedia.org/wiki/Internet%C3%AAs (read 2026-09-24, read)
- Português europeu, pt.wikipedia.org, https://pt.wikipedia.org/wiki/Portugu%C3%AAs_europeu (read 2026-09-24, read)
- Você, pt.wikipedia.org, https://pt.wikipedia.org/wiki/Voc%C3%AA (read 2026-09-24, read)
- bué, Dicionário Priberam, https://dicionario.priberam.org/bu%C3%A9 (read 2026-09-24, read)
- fixe, Dicionário Priberam, https://dicionario.priberam.org/fixe (read 2026-09-24, read)

### 4.5 French (fr)

#### Register guide

- Familier is the casual default on consumer social: short or verbless lines (Nouveau : ..., Petite faim ?), questions by intonation or ellipsis (Vous venez samedi ? Envie de goûter ?) instead of inversion (Venez-vous ?), on for nous, and in playful posts a dropped ne (C'est pas tous les jours...). Wikipédia's register article lists exactly these as familier, and inversion, long periods and rare words as soutenu. Projet Voltaire adds that AI French reads flat and lacks slangy or colloquial words. (native source)
- The brand speaks as on: On vous attend samedi reads warmer than Nous vous attendons. Keep nous for notices (recalls, apologies, legal hours). (inference)
- Clipped words are everyday French and fine in most captions: promo, dispo, resto, appli, apéro, ciné, perso, p'tit déj. Keep them out of banking, health and B2B. (native source for the category, inference for the list)
- Youth slang dates fast: de ouf, grave, trop (for very), tkt, mdr, cringe, flex and crush belong only to brands whose audience already talks that way, and never in a vous post. French marketing writers note that slang borrowed by brands turns ringard quickly. (several sources, snippets: MO&JO, Jennifer Garner blog)
- Franglais, nouns yes and hype verbs no: live, story, drop, collab, look, week-end, best-seller and click and collect are normal in France; English marketing verbs and idioms read translated (élevez votre, libérez votre potentiel, au prochain niveau, excités de). The Académie keeps proposing French words (frimousse for smiley); on social, follow usage, except in Québec. (inference; the Académie entry is a single source)
- Québec (fr-CA): take the Québec word where one exists: courriel, infolettre, magasiner, rabais, balado for podcast, fin de semaine (already in the guide). Québec consumer brands use tu more readily than French ones. `copyrules.py` already skips the space-before-punctuation check for fr-ca. The OQLF lists calques such as prendre action as errors. (single source for the calques, snippet; the rest inference)
- Playful replies are a French brand strength: Decathlon, Burger King France and SNCF are cited for a ton décalé, short witty answers to the actual comment rather than slogans. (several sources, snippets: JDN, IMCI)
- Emoji: one at a line end, not a bullet before every line; emoji bullets read as template copy. (single source for German, inference for French)
- Headlines in sentence case: French Wikipedia editors list superfluous capitals in titles as a sign of generated text, so Nouvelle collection maison, not Nouvelle Collection Maison. Now linted by the Title Case structure candidate. (native source)

#### Formal to everyday swaps

| formal | everyday | note | confidence |
|-|-|-|-|
| afin de | pour | fine in a letter, stiff in a caption | inference |
| au sein de | chez, dans | office register | inference |
| dans le cadre de | pour, pendant, avec | dans ce cadre is on a list of ChatGPT filler | single source |
| mettre en place, mettre en œuvre | lancer, installer, faire | listed as generic ChatGPT expressions | single source |
| il convient de | il faut | listed as ChatGPT filler | single source |
| l'appli vous permet de commander | avec l'appli, vous commandez en 2 clics | permettre de is a listed generic verb; put the reader in the subject slot | single source |
| effectuer un achat, procéder à un achat | acheter | nominal office style | inference |
| N'hésitez pas à nous contacter | Une question ? Écrivez-nous en MP | corporate formula; its English twin (please don't hesitate) is a listed chatbot phrase | inference |
| Nous avons le plaisir de vous annoncer | C'est officiel : ... | launch hype pushes the news back | inference |
| impacter | toucher, avoir un effet sur | the Académie française rejects impacter | several sources (snippets) |
| adresser un problème | régler, traiter un problème | calque of to address | several sources |
| faire du sens, faire sens | avoir du sens, c'est logique, ça se tient | calque of to make sense | several sources |
| prendre action | agir, passer à l'action | listed by the OQLF as a calque | single source (snippet) |
| Souhaitez-vous goûter notre nouveauté ? | Envie de goûter ? Vous venez goûter ? | inversion is soutenu; intonation and ellipsis are familier | native source |
| Ainsi avons-nous décidé de fermer le lundi | Du coup, on ferme le lundi | inversion after ainsi or aussi is soutenu | native source |

#### AI and translation tells

| tell | robotic example | natural fix | evidence | confidence |
|-|-|-|-|-|
| Immersion opener | Plongez dans l'univers de notre collection automne. | La collection automne arrive samedi : 40 pièces dès 19,90 €. | Blog du Modérateur (snippet); Redacteur.com (au cœur de); Spanish and German twins | several sources |
| Scene-setting opener | Dans un monde où tout va vite, prenez le temps. | Pause café ? Le latte est à 3,50 € jusqu'à 11 h. | Redacteur.com | single source |
| Filler lead-in and wrap-up | Il est important de noter que l'offre est limitée. En somme, à ne pas manquer. | Offre valable jusqu'à dimanche, dans la limite des stocks. | Daria Viktorova; Redacteur.com | several sources |
| Hype adjectives in clusters | Une formule révolutionnaire et captivante. | Sèche en 2 minutes, sans traces. | Daria Viktorova; Redacteur.com | several sources |
| Not X, it's Y, French form | Plus qu'un café, un rituel. | Un espresso serré, 1,80 € au comptoir. | Lilli Koisser (German twin); Daria Viktorova (non seulement X, mais Y) | inference |
| Sham breadth | Que vous soyez un amateur ou un expert, notre sélection saura vous combler. | Débutant ? Le cours de 18 h est fait pour vous. | unslop_ai (German twin) | inference |
| Calques | Ça fait du sens d'adresser ce problème. | C'est logique de régler ça. | Daria Viktorova; OQLF (snippet); franceinfo (snippet) | several sources |
| Experience and journey words | Embarquez pour un voyage culinaire unique. | Menu du marché à 24 €, servi midi et soir. | unslop_ai (embark, journey in English) | inference |
| Growth calques | Élevez votre routine beauté. | Une routine en 3 gestes, 5 minutes le matin. | the skill's English list; unslop_ai | inference |
| Poetic filler | Un instant suspendu, une promesse murmurée. | Coucher de soleil depuis la terrasse, dès 19 h. | Loumina | single source |
| Launch hype, excité as a calque | Nous sommes excités de vous annoncer notre ouverture. | C'est officiel : on ouvre à Lille le 3 octobre. | none found | inference |
| Title Case headline | Découvrez Notre Nouvelle Collection | Découvrez notre nouvelle collection | Wikipédia FR, AI help page | native source |
| Pasted chat reply | Bien sûr ! Voici trois propositions de légende. | delete the line | Wikipédia FR; Wikipedia DE; unslop_ai | several sources |
| Tag-a-friend bait | Identifie un ami qui adore le fromage ! | Plutôt comté ou brie ? Dis-le en commentaire. | none found | inference |
| Formal question hook | Êtes-vous prêt à vivre l'expérience ? | On vous garde une place samedi ? | Wikipédia FR registres (inversion is soutenu); unslop_ai (German Sind Sie bereit für) | several sources |

#### Purple or poetic phrasing

- instant suspendu, moment suspendu: give the time and place instead: Apéro sur le toit vendredi dès 18 h. (single source: Loumina)
- promesse murmurée, silencieuse or vibrante: state the actual promise: Livré en 24 h ou remboursé. (single source: Loumina)
- baigné de lumière: say what makes the light: trois grandes fenêtres plein sud. (single source: Loumina)
- le murmure du vent, des vagues: give the distance: à 200 m de la plage. (single source: Loumina)
- symphonie de saveurs, voyage gustatif: name the dish and the price: Tartare de daurade, 16 €. (inference)
- couleurs vibrantes, a calque of vibrant colours: couleurs vives, or name them: rouge brique, vert sapin. (inference)

#### Natural vs robotic lines

Natural (all pass the lint):

1. Nouveau chez nous : le pain au levain est à 3,20 €, dispo dès 7 h.
2. On vous attend samedi dès 10 h, place Bellecour, avec des crêpes à 2 €.
3. Petite pluie ? Nos parapluies pliables sont à 12,99 € en magasin et sur l'appli.
4. Ce samedi, on magasine local : 20 % de rabais sur tout le rayon jeux, de 9 h à 17 h. (fr-CA)

Robotic, each followed by its fix:

1. Plongez dans l'univers de notre gamme révolutionnaire et laissez-vous séduire.
   Fix: Nouvelle gamme soin : 4 produits dès 12,90 €, en boutique samedi.
2. Niché au cœur de Lyon, notre bistrot vous propose un véritable voyage culinaire. N'hésitez pas à réserver !
   Fix: Menu du midi à 19 €, rue Mercière à Lyon. On garde votre table jusqu'à 12 h 15, réservez en ligne.
3. Nous sommes ravis de vous annoncer notre ouverture ! Il est important de noter que les places sont limitées.
   Fix: C'est officiel : on ouvre à Nantes le 3 octobre. 40 places seulement, pensez à réserver !
4. Découvrez Notre Nouvelle Collection Pour Votre Maison. Élevez votre intérieur. En savoir plus
   Fix: Nouvelle collection maison : coussins en lin à 24 €, plaids à 39 €. Voir la collection

#### Sources

- Les tics de langage de ChatGPT, Daria décrypte l'IA (Daria Viktorova, 15 July 2025), https://dariadecrypteia.substack.com/p/les-tics-de-langage-de-chatgpt (read 2026-09-24, read)
- Comment éviter les tics de langage de ChatGPT ?, Redacteur.com (Céline Albarracin, 16 April 2024), https://www.redacteur.com/blog/eviter-tics-de-langage-chatgpt/ (read 2026-09-24, read)
- Reconnaître un texte d'IA : les tics de ChatGPT, Loumina (Simon Laroche, 20 September 2025), https://www.loumina.fr/blog-reconnaitre-un-texte-d-ia-les-tics-de-chatgpt (read 2026-09-24, read)
- Comment détecter un texte produit par ChatGPT ou une autre IA générative ?, Projet Voltaire, https://www.projet-voltaire.fr/ressources/detecter-texte-chatgpt-ia-generative/ (read 2026-09-24, read)
- Aide:Identifier l'usage d'une IA générative, Wikipédia, https://fr.wikipedia.org/wiki/Aide:Identifier_l%27usage_d%27une_IA_g%C3%A9n%C3%A9rative (read 2026-09-24, read)
- Registres de langue en français, Wikipédia, https://fr.wikipedia.org/wiki/Registres_de_langue_en_fran%C3%A7ais (read 2026-09-24, read)
- Dire, ne pas dire, entry Smiley, Académie française, https://www.dictionnaire-academie.fr/article/DNP0812 (read 2026-09-24, read)
- ChatGPT : quels sont les mots les plus utilisés par le chatbot ?, Blog du Modérateur, https://www.blogdumoderateur.com/chatgpt-mots-utilises-chatbot/ (read 2026-09-24, snippet)
- Le sens des mots. Impacter, un anglicisme réprouvé par l'Académie française, franceinfo, https://www.franceinfo.fr/replay-radio/le-sens-des-mots/le-sens-des-mots-impacter-un-anglicismereprouvepar-l-academie-francaise_4042587.html (read 2026-09-24, snippet)
- Les emprunts à l'anglais, OQLF Banque de dépannage linguistique, https://vitrinelinguistique.oqlf.gouv.qc.ca/banque-de-depannage-linguistique/les-emprunts-a-langlais (read 2026-09-24, snippet)
- Anglicismes masqués et calques, Françoise Nore, https://www.francoisenore.com/anglicismes-masques-et-calques (read 2026-09-24, snippet; the page refused the connection)
- Decathlon community manager article, Journal du Net, https://www.journaldunet.com/martech/1541639-rh1-decathlon-community-manager/ (read 2026-09-24, snippet)
- Le Top 10 des Community Managers les plus drôles sur Twitter, IMCI, https://imci-formation.com/blog/reseaux-sociaux/le-top-10-des-community-managers-les-plus-droles-sur-twitter/ (read 2026-09-24, snippet)
- Les 30 Expressions de la Génération Z en 2026, MO&JO, https://www.mo-jo.fr/blog/expressions-gen-z (read 2026-09-24, snippet)
- Tendances 2025 : Evitez le ringard en marketing !, jennifer-garner.org, https://www.jennifer-garner.org/tendances-2025-evitez-le-ringard-en-marketing/ (read 2026-09-24, snippet)
- Cross-language sources used for French twins (unslop_ai, Lilli Koisser, Wikipedia DE) are listed under German.

#### Could not verify

- No source found for laissez-vous séduire, sublimez, boostez, élevez votre, embarquez pour, que vous soyez, n'hésitez pas à, nous sommes ravis de vous annoncer, au prochain niveau, savant mélange, alliance parfaite or témoignage de; the lint keeps them as notes or marks them inference.
- Brand voices other than Decathlon, Burger King France and SNCF (snippets) were not checked; Le Monde, Libération and Numerama were not reached before the search budget ran out.

### 4.6 German (de)

#### Register guide

- Consumer social runs on du, short main clauses and modal particles: Schau mal vorbei, Probier's doch aus, Ist halt Herbst. A 2026 study of model output found that a higher rate of auch is the single strongest sign that German text was not translated, and that model German drifts back toward translated-text rates for such common words; particles and auch are what machine German leaves out. (single source for auch: Valentini et al.; the particle list is inference)
- Everyday verbs and shapes: gönn dir, hol dir, läuft, gibt's, schau mal vorbei, ab sofort, Feierabend; contractions (gibt's, geht's, aufs, ins); verbless headlines (Frisch aus dem Ofen: ...). (inference)
- Youth words (mega, krass, easy, safe, Digga, cringe) belong to youth brands only and date within a season. (inference)
- Regional voice works when it is real: BVG's prize-winning campaign „Weil wir dich lieben“ used Berliner Schnauze with great success. Moin (north), Servus (south and Austria) and Grüezi (Switzerland) fit inside a line or as a sign-off, but the no-greeting-opener rule still applies. (single source: Wikipedia DE; the rest inference)
- Denglisch: established loans are fine (Sale, Deal, Shop, Team, Event) when joined or hyphenated (Sommer-Sale, Onlineshop). Split compounds (Kunden Service) are wrong in German, spread with English loans in shop names and ads, and appear when machine translation keeps the English space (car wash becomes Auto Wäsche). Now linted. (native source: Wikipedia DE, Leerzeichen in Komposita)
- Nominalstil and Amtsdeutsch read like a letter from the authorities: noun chains, function-verb phrases (zur Anzeige bringen for anzeigen) and formula words (zwecks). Put an actor and a verb first: Wir liefern am Montag, not Die Lieferung erfolgt am Montag. (several sources: Wikipedia DE, Verwaltungssprache; unslop_ai)
- Sie is not stiffness by itself: a finance, health or B2B post in Sie can still be everyday with short sentences, verbs and one hard fact. (inference)
- Emoji and hashtags: emoji bullets before every line and blocks of three or more hashtags read as AI social template. (single source: unslop_ai)
- Austria and Switzerland: use the variant word (AT Jänner, Paradeiser, Topfen, Sackerl, heuer; CH Glace, Velo, parkieren, Znüni) and local prices (CHF 4.50 or 4.50 Fr.); a German-German word in an Austrian or Swiss post is a wrong-variant tell. (inference; ss and « » for Switzerland are already in the guide)
- Weight of evidence: one stock word proves nothing; German editors and the unslop_ai tiers treat a cluster of them in a thin text as the signal. (several sources: The Decoder, unslop_ai)

#### Formal to everyday swaps

| formal | everyday | note | confidence |
|-|-|-|-|
| zwecks | für, um ... zu | formula word of office German (zwecks Nachlassgewährung) | native source |
| bezüglich, hinsichtlich | zu, wegen, bei | office German | inference |
| seitens der Kundschaft | von Kundinnen und Kunden; Kunden sagen | office German | inference |
| Die Lieferung erfolgt am Montag | Wir liefern am Montag | nominal style hides the actor | several sources |
| zur Anzeige bringen | anzeigen | function-verb phrase from office German | native source |
| im Rahmen der Aktion | bei der Aktion, während der Aktion | appears in an AI rewrite example | single source |
| zeitnah | bald, diese Woche, bis Freitag | tier 2 AI word | single source |
| umgehend | sofort, gleich | office German | inference |
| die Inanspruchnahme | nutzen | office German | inference |
| beziehungsweise, bzw. | oder | stiff in a caption | inference |
| ein Problem adressieren | ein Problem angehen | anglicism in AI German | single source |
| eruieren | klären, rausfinden | elevated verb | single source |
| äußerst praktisch | echt praktisch, richtig praktisch | äußerst marks translated German in a 2026 study | single source |
| eine Vielzahl an, eine breite Palette an | viele; über 40 Sorten | named as a ChatGPT list opener in ad copy | single source |
| Wir freuen uns, Ihnen mitteilen zu dürfen | Neu ab Montag: ... | launch hype | inference |

#### AI and translation tells

| tell | robotic example | natural fix | evidence | confidence |
|-|-|-|-|-|
| Immersion opener | Tauchen Sie ein in die Welt unserer Aromen. | Neu: fünf Kaffeesorten aus Kolumbien, ab 7,90 €. | Ströer; Lilli Koisser; unslop_ai; The Decoder | several sources |
| Scene-setting opener | In der heutigen schnelllebigen Welt zählt jede Minute. | Mittagstisch in 10 Minuten, werktags ab 11:30 Uhr. | unslop_ai; Lilli Koisser; The Decoder | several sources |
| Filler lead-in and Fazit | Es ist wichtig zu beachten, dass die Aktion begrenzt ist. Fazit: zugreifen! | Gilt bis Sonntag, solange der Vorrat reicht. | Ströer; Lilli Koisser; unslop_ai; Wikipedia DE | several sources |
| Growth idioms | Bring dein Training auf das nächste Level und entfessle dein volles Potenzial. | Drei Kurse pro Woche, Probetraining gratis. | Lilli Koisser; unslop_ai | several sources |
| Buzzwords | nahtlose, ganzheitliche, maßgeschneiderte Lösungen mit echtem Mehrwert | Einrichtung in einem Tag, Support per Chat bis 20 Uhr. | unslop_ai; Lilli Koisser; ContentConsultants (snippet); The Decoder | several sources |
| Reveal antithesis | Das ist nicht nur ein Kaffee. Das ist ein Ritual. | Unser Espresso: 1,90 €, doppelt 2,60 €. | Lilli Koisser; unslop_ai | several sources |
| Significance padding and -ing participles | Unsere Röstung zeugt von Leidenschaft, die Qualität unterstreichend. | Wir rösten jeden Dienstag selbst. | Wikipedia DE; unslop_ai | several sources |
| Place and mood clichés | Im Herzen von Hamburg, eingebettet in pulsierendes Leben. | Mitten in Hamburg, Lange Reihe 12. | Wikipedia DE; unslop_ai; Ströer (Zauber der) | several sources |
| Pasted chat reply | Gerne! Hier sind drei Vorschläge für deinen Post. | delete the line | Wikipedia DE; unslop_ai | several sources |
| Launch hype | Wir freuen uns, Ihnen mitteilen zu dürfen, dass wir eröffnen. | Ab Montag neu in Köln, Ehrenstraße 5. | none found | inference |
| Title Case headline | Die Besten Angebote Für Dich | Die besten Angebote für dich | none found (the guide names the tell for Spanish, French and Portuguese) | inference |
| Split compounds | Kunden Service, Sommer Sale, Online Shop | Kundenservice, Sommer-Sale, Onlineshop | Wikipedia DE, Leerzeichen in Komposita | native source |
| Bait closers | Und das Beste daran? Lust auf mehr? Markiere einen Freund! | Welche Sorte zuerst, Apfel oder Zwetschge? | unslop_ai (Markiere: inference) | single source |
| No particles, no auch | Probiere den neuen Kuchen. | Probier doch mal den neuen Kuchen, der Apfel kommt auch vom Hof nebenan. | Valentini et al. 2026 (auch); particles: inference | single source |
| Translationese intensifier | äußerst lecker, äußerst praktisch | richtig lecker, echt praktisch | Valentini et al. 2026 (a translation marker; models mostly avoid it, machine and human translations do not) | single source |

#### Purple or poetic phrasing

- Tauche ein in eine Welt voller Genuss: say what is new: Neu: Chai Latte mit Hafermilch, 3,90 €. (several sources)
- der Zauber des Herbstes: Kürbissuppe ist zurück, 6,50 €. (single source: Ströer names Zauber der)
- ein Kaleidoskop der Farben: name them: Senfgelb, Tannengrün, Rostrot. (single source: The Decoder)
- ein reicher kultureller Teppich: list what is on: drei Bühnen, 40 Stände, Eintritt frei. (single source: Wikipedia DE)
- pulsierend, atemberaubend: give the fact: Blick auf den Hafen, 3. Stock. (several sources: Wikipedia DE, unslop_ai)
- unvergessliche Momente, pure Entspannung: Sauna bis 23 Uhr, Tageskarte 29 €. (inference)

#### Natural vs robotic lines

Natural (all pass the lint):

1. Frisch aus dem Ofen: Zimtschnecken für 2,50 €, nur heute bis 18 Uhr.
2. Schau mal vorbei: Am Samstag gibt's in Köln-Ehrenfeld Kaffee aufs Haus, ab 9 Uhr.
3. Neu in Zürich: Unser Glacestand hat bis 22 Uhr offen, eine Kugel kostet 4.50 Fr. (Switzerland)
4. Heute gibt's bei uns Kaiserschmarrn um 7,90 €, nur solange der Vorrat reicht. (Austria)

Robotic, each followed by its fix:

1. Entdecke die Welt der Aromen: Tauche ein und entfessle dein volles Potenzial!
   Fix: Neu bei uns: fünf Kaffeesorten aus Kolumbien, ab 7,90 € pro 250 g.
2. Das ist nicht nur ein Kaffee. Das ist ein Zeugnis unserer Leidenschaft.
   Fix: Wir rösten jeden Dienstag selbst. Probier doch mal den Espresso, 1,90 € an der Theke.
3. Liebe Kundinnen und Kunden, wir freuen uns, Ihnen mitteilen zu dürfen, dass unser Online Shop jetzt live ist.
   Fix: Unser Onlineshop ist live: Versand ab 29 € kostenlos, Lieferung in zwei Tagen.
4. Die Besten Angebote Für Dich: Jetzt Mehr Erfahren
   Fix: Die besten Angebote der Woche: Preise ansehen

#### Sources

- So erkennen Sie Texte von ChatGPT, Ströer Media (2023, updated 18 December 2024), https://www.stroeer-direkt.de/blog/2023/an-diesen-5-merkmalen-erkennen-sie-texte-von-chatgpt/ (read 2026-09-24, read)
- 12 typische Merkmale von KI-Texten erkennen: Blacklist und Tools, lillikoisser.at (Lilli Koisser, Austria, 23 April 2026), https://lillikoisser.at/ki-texte-erkennen/ (read 2026-09-24, read)
- unslop_ai, word-lists.md and pattern-catalog.md, GitHub (jlwin), https://github.com/jlwin/unslop_ai (read 2026-09-24, read)
- Reddit-Community sammelt Phrasen und Signalwörter, um ChatGPT-Texte zu erkennen, The Decoder (Matthias Bastian, 1 May 2024), https://the-decoder.de/reddit-community-sammelt-phrasen-und-signalwoerter-um-chatgpt-texte-zu-erkennen/ (read 2026-09-24, read)
- Wikipedia:Anzeichen für KI-generierte Inhalte, Wikipedia DE, https://de.wikipedia.org/wiki/Wikipedia:Anzeichen_f%C3%BCr_KI-generierte_Inhalte (read 2026-09-24, read)
- Leerzeichen in Komposita, Wikipedia DE, https://de.wikipedia.org/wiki/Leerzeichen_in_Komposita (read 2026-09-24, read)
- Verwaltungssprache, Wikipedia DE, https://de.wikipedia.org/wiki/Verwaltungssprache (read 2026-09-24, read)
- Berliner Verkehrsbetriebe, Wikipedia DE, https://de.wikipedia.org/wiki/Berliner_Verkehrsbetriebe (read 2026-09-24, read)
- An Investigation of Translationese in the Generations of Multilingual Large Language Models, arXiv 2608.17399 (Valentini, Wright, Granados, Colunga, von der Wense, 18 August 2026), https://arxiv.org/abs/2608.17399 (read 2026-09-24, read)
- KI-Texte erkennen: Typische Formulierungen und Muster, ContentConsultants (Udo Raaf), https://www.contentconsultants.de/ki-texte-erkennen-warum-man-texte-besser-selbst-schreibt/ (read 2026-09-24, snippet)

#### Could not verify

- No source found for egal ob, Genuss pur, Erlebe and Erleben Sie, the launch-hype formula, Markiere einen Freund, English Title Case in German headlines, the particle list or the youth words.
- Brand voices other than BVG were not checked; t3n, heise, Golem, Spiegel, Zeit and SZ were not reached.

### 4.7 Indonesian (id)

#### Register guide

- Casual social Indonesian is written the way people talk: short clauses that end in particles (nih, dong, deh, sih, kok, lho, kan, ya, yuk). The Indonesian anti-slop list says LLM text almost never uses them and that their total absence is a tell; Wikipedia's slang article gives their jobs (dong for the obvious, kok for disbelief, kan for shared ground). Several sources.
- Short everyday forms beat long meN- verbs: butuh, not membutuhkan (Microsoft Indonesian guide), pakai not menggunakan, udah, aja, banget, gimana, buat, cuma, nggak or gak. Single source plus inference.
- Address: kamu and -mu by default (already in the skill); kak or kakak in marketplace captions and shop replies; gue and lo only for a Jakarta youth persona; a community name (Sobat X, Kawan X) is native but should not open the post. Never mix Anda with kamu or kak in one post. Inference, backed by the anti-slop note that LLMs lock on Anda.
- English mixing is normal for commerce and lifestyle words: checkout, flash sale, restock, cashback, voucher, outfit, skincare, spill, healing. English verbs take Indonesian affixes: di-cancel, nge-cancel (Wikipedia slang). Heavy South Jakarta mixing (which is, literally, basically) is mocked, so keep it for personas that really talk that way. Single source.
- Slang a brand can use in 2024 to 2026, one per post: mager, gabut, gercep, baper, santuy, kuy, gaes (Wikipedia slang); racun (a review that makes you buy), spill, cus, buruan (inference).
- Numbers: Rp49.000, Rp25 ribu, 49rb and 99K are all native in e-commerce. A full stop marks thousands and a comma marks decimals (Microsoft guide). Single source.
- Sentence shape: a question hook (Mager masak?), one fact with a price or time, then one action with yuk, cus or buruan. Microsoft's guide drops "please" words (tolong, mohon, silakan) in product text; silakan still lives in shop chat. Single source plus inference.
- Baku register (meN- verbs, merupakan, Anda, passive voice) reads like a bank notice. Ivan Lanin describes social media as a hybrid: written, but delivered like speech, so even institutions aim for standard but not stiff. Snippet only.
- Emoji: e-commerce captions often carry a few (fire, cart); the skill's global cap still applies. Inference.

#### Formal to everyday swaps

| formal | everyday | note | confidence |
|:-|:-|:-|:-|
| membutuhkan, memerlukan | butuh, perlu | Microsoft Indonesian guide example | single source |
| disarankan | sebaiknya | Microsoft guide | single source |
| tolong, mohon, silakan (as please) | drop it | Microsoft guide, for product text; silakan is fine in shop chat | single source |
| namun demikian | namun, tapi | Microsoft guide shortens it | single source |
| memanfaatkan, menggunakan | pakai | anti-slop list gives menggunakan; pakai is the spoken form | single source plus inference |
| merupakan | adalah, or drop it | anti-slop list, copula avoidance | single source |
| oleh karena itu, dengan demikian | jadi, makanya | anti-slop list | single source |
| selain itu | juga, terus | anti-slop list | single source |
| Dalam era digital, banyak individu memanfaatkan AI | Sekarang banyak orang pakai AI | DIP Strategy's own before and after | single source |
| tidak | nggak, gak | ga in chat | inference |
| sangat murah | murah banget | banget follows the word | inference |
| hanya | cuma, aja | cuma Rp25 ribu | inference |
| sudah | udah | udah bisa dipesan | inference |
| untuk | buat | buat kamu | inference |
| bagaimana | gimana | gimana caranya? | inference |

#### AI and translation tells

| tell | robotic example | natural fix | evidence | confidence |
|:-|:-|:-|:-|:-|
| Era or landscape opener | Di era digital saat ini, belanja jadi lebih mudah. | Belanja bulanan sampai rumah dalam 2 jam. | Kiosmaya, DIP Strategy, Jawa Pos, anti-slop BI-2 | several sources |
| Essay signposts | Tak dapat dipungkiri bahwa kopi adalah kebutuhan. | Pagi tanpa kopi? Nggak dulu. | IDN Times (tidak dapat dipungkiri, penting untuk dicatat), Kiosmaya, anti-slop list | several sources |
| tidak hanya ... tetapi juga, bukan sekadar ... melainkan | Produk ini tidak hanya murah, tetapi juga awet. | Murah, dan udah 2 tahun masih awet. | anti-slop BI-3 | single source |
| merupakan salah satu | Bali merupakan salah satu destinasi terbaik. | Tiket PP ke Bali mulai Rp899 ribu. | anti-slop BI-4 | single source |
| di mana or yang mana as a relative pronoun | Aplikasi di mana kamu bisa pesan tiket. | Di aplikasi ini kamu bisa pesan tiket. | Narabahasa (interference from where and which), anti-slop BI-8 | native source |
| No particles, flat formal statements | Stok terbatas. Segera lakukan pembelian. | Stoknya tinggal dikit nih, buruan ya! | anti-slop BI-5, DIP Strategy | several sources |
| Nominalisation | Pelaksanaan pengiriman dilakukan setiap hari. | Kami kirim tiap hari. | anti-slop BI-7 | single source |
| Formal passive voice | Pesanan akan diproses setelah pembayaran diterima. | Begitu kamu bayar, pesanan langsung kami proses. | Tempo (formal, passive, monotone) | single source |
| Anda locked in, or mixed with kak | Anda bisa checkout sekarang, kak. | Checkout sekarang, kak. | anti-slop BI-9; the mixing is inference | single source |
| Experience calque | Rasakan pengalaman berbelanja yang tak terlupakan. | Belanja 2 jam sebelum tutup, diskon 20%. | none found | inference |
| Dive into and explore calques | Mari kita selami dunia kopi Nusantara. | Ada 6 biji kopi lokal, mulai Rp35 ribu. | none found | inference |
| Calqued stock lines | Jangan ragu untuk menghubungi kami. | Chat aja di WhatsApp, dibalas sampai jam 9 malam. | anti-slop chat artifacts | single source |
| Chatbot leftovers | Semoga membantu! Berikut adalah beberapa caption ... | delete it | anti-slop list | single source |
| English thousands separator | Rp 49,000 | Rp49.000 | Microsoft Indonesian guide | single source |
| Malaysian words | Tahniah, kamu menang voucher! | Selamat, kamu menang voucher! | Wikipedia comparison, Ling | several sources |

#### Purple or poetic phrasing

1. "Setiap tegukan menghadirkan kehangatan yang tak terlupakan." Fix: "Kopi panas, gula aren asli, Rp18 ribu."
2. "Harmoni sempurna antara tradisi dan modernitas." Fix, name both things: "Resep nenek, dimasak pakai air fryer."
3. "Sebuah perjalanan rasa yang memanjakan lidah." Fix: "Pedasnya level 1 sampai 5, pilih sendiri." (Memanjakan lidah is also an old human TV-ad cliché; either way it says nothing.)
4. "Wujudkan impianmu bersama kami." Fix: "Cicilan 0% 12 bulan, DP mulai Rp500 ribu."
5. "Temukan keajaiban di setiap sudut." Fix: "Ada 12 spot foto, buka jam 9 pagi."
6. "Menghadirkan kebahagiaan di setiap momen." Fix, name the moment: "Bekal anak tetap hangat sampai jam istirahat."

#### Natural vs robotic lines

Natural:
1. Flash sale jam 12 siang nanti, sneakers mulai Rp149.000. Pasang alarm ya, stoknya cuma 200 pasang!
2. Mager masak? Paket nasi ayam geprek plus es teh cuma Rp25 ribu, diantar kurang dari 30 menit.
3. Restock nih! Tote bag kanvas warna sage udah bisa dipesan lagi, Rp89 ribu, dikirim mulai Senin.
4. Nobar final di outlet Kemang Sabtu jam 7 malam, beli 2 burger gratis 1 es teh.

Robotic, each with a fix:
1. Di era digital saat ini, Anda bisa belanja kapan saja, jadi yuk kak checkout sekarang juga!
   Fix: Checkout sebelum jam 10 malam, kak, besok pagi udah sampai.
2. Kopi kami bukan sekadar minuman, melainkan sebuah perjalanan rasa yang menghangatkan hati.
   Fix: Kopinya pakai gula aren asli dari Banyumas, Rp18 ribu segelas.
3. Kami menghadirkan platform di mana Anda dapat menemukan ribuan produk mulai Rp 49,000 saja.
   Fix: Ribuan produk mulai Rp49.000, cek semuanya di app.
4. Selami dunia rasa autentik Nusantara dan temukan keajaiban di setiap gigitan.
   Fix: Rendang, gudeg dan coto Makassar masuk menu baru mulai Senin.

#### Hypotheses: verdicts

- Confirmed with sources: di era digital, tak dapat dipungkiri, penting untuk dicatat, merupakan, selain itu, oleh karena itu, dengan demikian, tidak hanya ... tetapi juga, di mana and yang mana as relatives, always-formal Anda.
- Refined: temukan and nikmati are native brand verbs (Temukan promo, Nikmati diskon 50%), so only purple objects are linted; jelajahi is linted only with objects like koleksi or dunia because travel brands use it natively; perjalanan is linted only with metaphor nouns (kecantikan, finansial, rasa), not mudik or ke Bali.
- dimana as one word: Narabahasa treats it as a spelling slip; it is common in casual human writing, so it is not an AI tell on its own. The lint targets the relative use, spelled either way.
- daripada misuse: no source found, and it is a human speech habit rather than a model habit (inference). Not linted.
- Not verified: selami, jelajahi, rasakan pengalaman and tingkatkan as AI words (no native source reached; kept as inference).

#### Sources

- 4 Ciri Tulisan yang Dihasilkan oleh ChatGPT, Tempo, https://www.tempo.co/digital/4-ciri-tulisan-yang-dihasilkan-oleh-chatgpt-2025609 (read 2026-09-24, read)
- 7 Ciri Konten Tulisan yang Dihasilkan AI, Kosong Tanpa Emosi, IDN Times, https://www.idntimes.com/tech/trend/ciri-konten-tulisan-yang-dihasilkan-ai-c1c2-01-w8826-wpg9lz (read 2026-09-24, read)
- Ciri-Ciri Artikel yang Terlihat Dibuat dengan ChatGPT, Kiosmaya, https://kiosmaya.com/ciri-ciri-artikel-yang-terlihat-dibuat-dengan-chatgpt/ (read 2026-09-24, read)
- Cara Membuat Artikel Menggunakan ChatGPT dan Membuatnya Terlihat Natural, DIP Strategy, https://dipstrategy.co.id/blog/cara-membuat-artikel-menggunakan-chatgpt-dan-membuatnya-terlihat-natural/ (read 2026-09-24, read)
- 7 Frasa Ciri Kenali Tulisan Khas ChatGPT yang Jadi Tanda Tulisan Buatan AI, Jawa Pos, https://www.jawapos.com/lifestyle/2609210076/7-frasa-ciri-kenali-tulisan-khas-chatgpt-yang-jadi-tanda-tulisan-buatan-ai?page=all (read 2026-09-24, read; only the first of seven phrases loaded, and the piece summarises an English YourTango article)
- Interferensi Bahasa: Di Mana dan Dimana, Narabahasa, https://narabahasa.id/artikel/linguistik-interdisipliner/sosiolinguistik/interferensi-bahasa-di-mana-dan-dimana/ (read 2026-09-24, read)
- Penggunaan Di Mana dan Yang Mana dalam Kalimat Bahasa Indonesia, Kantor Bahasa Maluku, https://kantorbahasamaluku.kemdikbud.go.id/2018/07/penggunaan-di-mana-dan-yang-mana-dalam-kalimat-bahasa-indonesia/ (read 2026-09-24, snippet; the host did not resolve)
- Bisakah yang Mana dan di Mana Dipakai sebagai Kata Sambung, Typo Online blog, https://blog.typoonline.com/bisakah-yang-mana-dan-di-mana-digunakan-sebagai-kata-sambung/ (read 2026-09-24, snippet)
- Takarir Media Sosial yang Baku, tetapi Tidak Kaku, Ivan Lanin on Medium, https://ivanlanin.medium.com/takarir-media-sosial-yang-baku-tetapi-tidak-kaku-c14b31fd351b (read 2026-09-24, snippet; Medium blocked the fetch)
- anti-slop-writing (Indonesian ban list and structural patterns BI-1 to BI-10), adenaufal on GitHub, https://github.com/adenaufal/anti-slop-writing (read 2026-09-24, read)
- Microsoft Indonesian Style Guide, Microsoft, https://aka.ms/indonesian-styleguide (read 2026-09-24, read)
- Indonesian slang, Wikipedia, https://en.wikipedia.org/wiki/Indonesian_slang (read 2026-09-24, read)
- Comparison of Indonesian and Standard Malay, Wikipedia, https://en.wikipedia.org/wiki/Comparison_of_Indonesian_and_Standard_Malay (read 2026-09-24, read)
- Malay and Indonesian: 5 Main Differences Summarized, Ling, https://ling-app.com/blog/malay-and-indonesian/ (read 2026-09-24, read)
- Cara Mendeteksi Tulisan Hasil ChatGPT, Ini Ciri-cirinya, CNN Indonesia, https://www.cnnindonesia.com/teknologi/20250711135904-185-1249601/cara-mendeteksi-tulisan-hasil-chatgpt-ini-ciri-cirinya (read 2026-09-24, snippet; fetch refused)
- 15+ Contoh Copywriting yang Menjual, Creativism, https://creativism.id/contoh-copywriting-iklan/ (read 2026-09-24, snippet; cites Gojek's casual, humorous copy)
- Tantangan ChatGPT dalam Bahasa Indonesia, GLAIR, https://glair.ai/blog-posts-id/tantangan-chatgpt-dalam-bahasa-indonesia (read 2026-09-24, read; about accuracy, nothing on register)

### 4.8 Malay, Malaysia (ms)

#### Register guide

- Everyday Malaysian Malay on social uses tak, nak, je, dah, kat, ni, tu and lah; the pronouns korang, kitorang and diorang replace kalian, kami and mereka (Wikipedia Malaysian Malay and Bahasa Rojak, Ling). Several sources.
- Bahasa rojak (Malay mixed with English) is normal for youth, food and e-commerce: weekend, sale, order, outlet, early bird, member, best, power. Slang: jom, best gila, mantap, boleh tahan, syok, cun, tapau, pergh, fuyoh (Ling slang list, Wikipedia Manglish). Several sources.
- The government has pushed standard Malay in the private sector since the late 1980s; TV3 renamed Karnival Sure Heboh to Karnival Jom Heboh in 2006 over rojak concerns (Wikipedia Bahasa Rojak). Banks, telcos and government-linked brands stay close to baku, and many Malaysian brands post bilingual Malay and English captions (inference). Single source plus inference.
- Address: anda in lowercase inside a sentence (the Microsoft Malay guide writes pronouns in small letters; Indonesian capitalises Anda). Casual posts use korang or drop the pronoun; awak is one-to-one; kamu can read Indonesian or like an elder talking down (inference). Brands should say saya or kami, not aku or gua (Microsoft guide). Single source plus inference.
- Do not write Indonesian: bisa (venom in Malay), gratis, ongkir, diskon, kualitas, karena, nggak, banget, yuk, or Indonesian festival terms. Use boleh, percuma, penghantaran percuma, diskaun, kualiti, kerana, tak, sangat or gila, jom, Aidilfitri, maaf zahir dan batin, Tahun Baharu Cina (Ling; Wikipedia comparison). Several sources.
- Numbers and dates: RM12.90 and RM1,299 (a full stop before sen, a comma for thousands; Ling on decimals). Months: Mac, Jun, Julai, Ogos, Disember (inference).
- Festive posts are a big genre (Raya, CNY, Deepavali, Merdeka). On social many Malaysians write Ramadhan and Aamiin, while the DBP standard is Ramadan and Amin (Wikipedia Bahasa Rojak): follow the audience here. Single source.
- Sentence shape: a hook (Jom tapau!, Raya dah dekat!), a fact with price and branch, one action (Tempah kat app, Order sebelum 2 petang). The Microsoft guide says avoid passive voice and the corporate "we're proud to introduce". Single source.

#### Formal to everyday swaps

| formal | everyday | note | confidence |
|:-|:-|:-|:-|
| tidak | tak | | single source |
| hendak, mahu | nak | | several sources |
| sahaja | je | RM9.90 je | single source |
| sudah | dah | | single source |
| di sana, di situ | kat sana, kat situ | kat outlet Bangsar | single source |
| kalian, kamu semua | korang | | several sources |
| kami | kitorang | a brand talking casually | several sources |
| walau bagaimanapun | tetapi, tapi | Microsoft Malay guide | single source |
| berpeluang | boleh, dapat | Microsoft Malay guide | single source |
| rujuk | lihat, tengok | Microsoft gives lihat; tengok is spoken | single source plus inference |
| pengguna (as address) | anda, or no pronoun | Microsoft calls pengguna formal and impersonal | single source |
| cantik, jelita | cun | youth register | single source |
| bungkus, bawa pulang | tapau | food posts | several sources |
| sangat bagus | best gila, power, mantap | Manglish | several sources |
| Dengan sukacitanya dimaklumkan | say the news: Kedai tutup 30 Mac | notice opener | inference |

#### AI and translation tells

| tell | robotic example | natural fix | evidence | confidence |
|:-|:-|:-|:-|:-|
| Indonesian slang and particles | Promo keren banget, yuk checkout! | Promo best gila, jom checkout! | Ling, Wikipedia Malaysian Malay | several sources |
| Indonesian shopping words | Dapatkan gratis ongkir dan diskon 20%. | Penghantaran percuma dan diskaun 20%. | Ling, Wikipedia comparison | several sources |
| Indonesian festival terms | Selamat Idulfitri, mohon maaf lahir dan batin. | Selamat Hari Raya Aidilfitri, maaf zahir dan batin. | Wikipedia comparison | single source |
| -itas spelling | Kualitas terbaik untuk keluarga anda. | Kualiti terbaik untuk keluarga anda. | Wikipedia comparison (loanword sources) | single source |
| Capital Anda mid-sentence | Hadiah istimewa untuk Anda. | Hadiah istimewa untuk anda. | Microsoft Malay guide | single source |
| Indonesian tech words | Unduh aplikasi dan masukkan kata sandi. | Muat turun app dan masukkan kata laluan. | Microsoft Malay guide sample uses kata laluan | single source |
| Indonesian number format | Harga RM1.299 sahaja. | Harga RM1,299 je. | Ling on decimals | single source |
| Fast-changing-world opener | Dalam dunia yang pantas berubah, kami ... | Buka 24 jam kat Bangsar mulai Isnin. | none found | inference |
| Not just X but Y | Bukan sekadar kopi, tetapi gaya hidup. | Kopi RM6, biji dari Cameron Highlands. | none found | inference |
| Experience calque | Rasai pengalaman membeli-belah yang tidak dapat dilupakan. | Beli sebelum 2 petang, sampai esok. | none found | inference |
| Corporate we | Kami bangga memperkenalkan menu baharu kami. | Menu baru dah sampai! Ayam madu pedas RM13.90. | Microsoft Malay guide | single source |
| Report connectors | Walau bagaimanapun, stok adalah terhad. | Tapi stok tak banyak. | Microsoft Malay guide | single source |
| Passive voice | Pesanan anda akan diproses dalam masa 24 jam. | Kami proses order korang dalam 24 jam. | Microsoft Malay guide | single source |
| Mixed address | Anda boleh tempah sekarang, korang jangan lepaskan! | Jom tempah sekarang, slot tinggal 20! | none found | inference |
| Chatbot leftovers | Semoga membantu! Berikut adalah beberapa kapsyen ... | delete it | none found | inference |

#### Purple or poetic phrasing

1. "Setiap hirupan membawa anda ke dunia kenikmatan." Fix: "Kopi panas RM6, gula melaka asli."
2. "Gabungan sempurna antara tradisi dan kemodenan." Fix, name both: "Kuih resipi nenek, dalam kotak kertas boleh kitar semula."
3. "Keindahan yang tiada tandingan menanti anda." Fix: "Pantai 5 minit jalan kaki dari hotel."
4. "Merealisasikan impian anda bersama kami." Fix: "Pinjaman peribadi, lulus dalam 24 jam."
5. "Menceriakan setiap detik bersama keluarga." Fix, name the moment: "Set 4 orang RM49, cukup untuk berbuka."

#### Natural vs robotic lines

Natural:
1. Jom tapau! Set nasi lemak ayam goreng RM9.90 je sepanjang minggu ni, kat semua cawangan Lembah Klang.
2. Korang dah cuba latte gula melaka kitorang? Sekarang RM12 je kat outlet Bangsar, sampai hujung bulan.
3. Raya dah dekat! Baju Melayu cotton siap jahit dari RM89, sampai sebelum 20 Mac kalau order minggu ni.
4. Tiket konsert Sabtu ni tinggal 300 je. Beli kat app sebelum pukul 10 malam, harga early bird RM129.

Robotic, each with a fix:
1. Dapatkan gratis ongkir untuk semua pesanan hari ini, yuk checkout sekarang!
   Fix: Penghantaran percuma untuk semua order hari ni, jom checkout!
2. Dalam dunia yang pantas berubah, kami komited untuk memberikan kualitas terbaik kepada Anda.
   Fix: Semua kek dibakar pagi tadi, ambil kat kedai lepas pukul 11.
3. Selamat Idul Fitri, mohon maaf lahir dan batin untuk semua pelanggan setia kami.
   Fix: Selamat Hari Raya Aidilfitri, maaf zahir dan batin. Kedai buka semula 3 April.
4. Harga istimewa hanya RM1.299 untuk anda, jangan teragak-agak untuk menghubungi kami.
   Fix: Set sofa RM1,299 je, WhatsApp kami untuk tengok warna lain.

#### Hypotheses: verdicts

- Confirmed: Indonesian leaks (gratis, ongkir, bisa, nggak, capital Anda, Idulfitri, lahir dan batin, Selamat sore) are real variant errors, with sources for the words and the lowercase anda rule.
- Refined: terokai is also used natively in travel posts (Jom terokai Sabah), so it is a note with high false-positive risk; temui was dropped because Temui kami di booth 12 (meet us) is normal Malay; bikin was dropped because bikin kecoh is Malaysian colloquial.
- Not verified: terokai, rasai pengalaman, dalam dunia yang pantas berubah and bukan sekadar as AI habits (no Malay article on ChatGPT text reached); kept as inference.

#### Sources

- Comparison of Indonesian and Standard Malay, Wikipedia, https://en.wikipedia.org/wiki/Comparison_of_Indonesian_and_Standard_Malay (read 2026-09-24, read)
- Malay and Indonesian: 5 Main Differences Summarized, Ling, https://ling-app.com/blog/malay-and-indonesian/ (read 2026-09-24, read)
- Malay slang words, Ling, https://ling-app.com/blog/malay-slang-words/ (read 2026-09-24, read)
- Malaysian Malay, Wikipedia, https://en.wikipedia.org/wiki/Malaysian_Malay (read 2026-09-24, read)
- Bahasa Rojak, Wikipedia, https://en.wikipedia.org/wiki/Bahasa_Rojak (read 2026-09-24, read)
- Manglish, Wikipedia, https://en.wikipedia.org/wiki/Manglish (read 2026-09-24, read)
- Microsoft Malay (Malaysia) Style Guide, Microsoft, https://aka.ms/malay-malaysia-styleguide (read 2026-09-24, read)
- ChatGPT Rakan Baik, Hasbullah Abu Bakar on Substack, https://hasbullahabubakar.substack.com/p/chatgpt-rakan-baik (read 2026-09-24, read; nothing on the quality of ChatGPT's Malay)

### 4.9 Urdu (ur)

#### Register guide
- **Spoken layer, not literary Urdu (single source).** Wikipedia's Urdu article says the Urdu spoken daily in Pakistan
  is close to neutral Hindustani, while formal Urdu takes literary, political and technical words from Persian and
  Arabic, and understanding drops as formality rises. Copy belongs in the spoken layer.
- **Microsoft's Urdu guide (native source).** Everyday conversational language, short sentences, no passive voice, no
  corporate "we", and a table of classic words to replace, led by the rule that most verb endings move from کیجئے to
  کریں (see the swaps table).
- **English in Urdu letters is normal brand Urdu (single source, first-hand).** Jazz's Urdu site writes English
  loanwords in Urdu script (ری چارج، آرڈر، آفرز، ڈیٹا، سبسکرائب کریں) and leaves brand and product names in Latin
  inside Urdu lines (Jazz 5G, Samsung Galaxy). Its hooks are short questions such as "بیلنس کم ہے؟". It also uses
  حاصل کریں and منتخب کریں, so those are not tells on their own.
- **Roman Urdu with English is the app voice (several sources).** Easypaisa's site sets English headlines next to Roman
  Urdu particles (toh, kyun) and light verbs, for example "scan karo, done karo", and a loan line ending in hasil karein.
  Wikipedia's Roman Urdu article says Pakistani advertising uses Roman Urdu slang and that Roman spelling is not
  standardised (the covered rule: one spelling list per brand).
- **Address (single source and inference).** آپ + کریں stays the default (covered). تم forms (کرو، جاؤ) appear in games
  and youth modules; Jazz ends a game promo on a جاؤ imperative. Easypaisa uses karo in one module and karein in
  another; inside one post keep one form.
- **Casual markers (inference).** Roman: yaar (peers only), bhai, scene, mazay, zabardast, kamaal, set hai, bas, toh,
  na, abhi, chalo, jaldi. Urdu script: زبردست، کمال، مزے، بس، تو، ابھی، چلو، جلدی. Shape: a question hook, then a price
  or a time. Emoji follow the global rule; 🌙 is tied to Ramzan and Eid posts.
- **Letters and digits (single source and first-hand).** Type Urdu ک (U+06A9), ی (U+06CC) and ہ (U+06C1), never the
  Arabic look-alikes ك (U+0643), ي (U+064A) or ه (U+0647); Wikipedia's Urdu alphabet article lists them as confusable
  glyphs that break search. Jazz prints prices with Western digits inside Urdu text, so Western digits are normal in
  Pakistani brand Urdu.
- **Pakistan first (inference).** Keep روپے or Rs., Pakistani cities and Pakistani occasions; Urdu readers in India see
  ₹ and more Hindi loans.

#### Formal to everyday swaps
| formal | everyday | note | confidence |
|:-|:-|:-|:-|
| کیجئے (most verb endings) | کریں | Microsoft Urdu guide | native source |
| تشریف لے جائیے | جائیں | same table | native source |
| تنصیب فرمائیے | انسٹال کریں (guide: نصب کریں) | same table | native source |
| ملاحظہ فرمائیے | دیکھیں (guide: نوٹ) | same table | native source |
| اگر طبع نازک پر گراں نہ گزرے | اگر آپ کو برا نہ لگے | same table | native source |
| پند و نصائح پر عمل کیجئے | نصیحت پر عمل کریں | same table | native source |
| گراں قدر معلومات | اہم معلومات | same table | native source |
| بدرجہ اتم | بہت زیادہ | same table | native source |
| منتفع ہوں, مستفید ہوں | استعمال کریں، فائدہ اٹھائیں | the guide lists the first (as extracted from its PDF); banks still use the second | native source, inference |
| لطف اندوز ہوں | مزے کریں، مزہ لیں | | inference |
| علاوہ ازیں | اور، ساتھ ہی | | inference |
| لہٰذا | اس لیے | Microsoft's Hindi guide makes the same swap for अतः | inference |
| فراہم کرتے ہیں | دیتے ہیں | corporate "we provide" | inference |
| یقینی بنائیں | دھیان رکھیں، پکا کر لیں | right in news and notices | inference |
| ازراہ کرم، برائے مہربانی | cut it, or براہ کرم once | Microsoft's own samples use براہ کرم | inference |

#### AI and translation tells
| tell | robotic example | natural fix | evidence | confidence |
|:-|:-|:-|:-|:-|
| "not X but Y" | یہ صرف ایک برگر نہیں بلکہ ایک احساس ہے۔ | ڈبل پیٹی برگر، 650 روپے۔ | Hindi twin in India TV Hindi | inference |
| "experience" or "enjoy" | اپنی پسندیدہ ڈش کا تجربہ کریں۔ | آج ہی چکھیں، 30 منٹ میں ڈیلیوری۔ | none found | inference |
| "discover" | نئے ذائقے دریافت کریں۔ | نئے فلیورز آزمائیں، تین کے ساتھ ایک مفت۔ | none found | inference |
| "to new heights" | اپنے کاروبار کو نئی بلندیوں تک لے جائیں۔ | دکان کا حساب اب ایپ پر، مفت۔ | none found | inference |
| journey metaphor | ذائقے کا سفر شروع کریں۔ | 12 شہروں کی 40 ڈشز، ایک مینو میں۔ | none found | inference |
| "ensure" | یقینی بنائیں کہ آپ آفر سے فائدہ اٹھائیں۔ | آفر اتوار رات 12 بجے ختم۔ | none found | inference |
| corporate "we provide" | ہم بہترین سروس فراہم کرتے ہیں۔ | شکایت؟ واٹس ایپ کریں، 10 منٹ میں جواب۔ | Microsoft Urdu guide (corporate "we") | native source for the rule |
| passive with an agent | ہمارے شیف کی جانب سے ہر ڈش تیار کی جاتی ہے۔ | ہمارے شیف ہر ڈش آرڈر کے بعد بناتے ہیں۔ | Microsoft Urdu guide (avoid passive) | native source for the rule |
| classic honorific verbs | ہماری ویب سائٹ ملاحظہ فرمائیں۔ | ویب سائٹ دیکھیں۔ | Microsoft Urdu guide | native source |
| Arabic look-alike letters | a line typed with ك and ي | the same line with ک and ی | Wikipedia, Urdu alphabet | single source |
| busy-world opener | آج کی تیز رفتار زندگی میں صحت اہم ہے۔ | لنچ رہ جاتا ہے؟ 15 منٹ میں سلاد۔ | none found | inference |
| letter opener | محترم صارفین، عید آفر شروع ہو گئی ہے۔ | عید آفر شروع: ہر آرڈر پر 200 روپے کیش بیک۔ | none found | inference |
| engagement bait | اپنے دوستوں کو ٹیگ کریں! | آپ کی پسند کون سی ہے، کڑک یا ملائی والی؟ | none found | inference |
| chatbot framing | یقیناً! یہ رہا آپ کا کیپشن: | delete it | none found | inference |
| Roman textbook calques | Naye zaiqay daryaft karein aur tajurba karein. | Naya menu try karo, Rs. 650 se. | none found | inference |

#### Purple or poetic phrasing
- ذائقوں کی دنیا، ذائقے کا سفر: name the dish.
- ہر لمحے کو یادگار بنائیں: name the moment (افطار کے بعد کی چائے).
- خوابوں کو حقیقت کا روپ دیں: give the concrete result (قسط 2,500 روپے ماہانہ).
- روایت اور جدت کا حسین امتزاج: say what is old and what is new.
- دل کو چھو لینے والا: give one detail.
Confidence: inference.

#### Natural vs robotic lines
Natural:
- لاہور کے ڈی ایچ اے فیز 6 میں نئی برانچ کھل گئی! پہلے ہفتے ہر آرڈر پر ڈیلیوری مفت۔
- Bijli ka bill due hai? App se 2 minute mein pay karo, 50 rupay cashback bhi.
- Weekend pe biryani ka plan? Karachi mein Rs. 699 wali family deal sirf Sunday tak.
- آسان قسطوں پر نیا فون، صرف 2,500 روپے ماہانہ سے۔ آج ہی قریبی شاپ پر آئیں۔

Robotic, each with a fix:
- یہ صرف ایک چائے نہیں بلکہ سکون کا احساس ہے۔
  Fix: کڑک الائچی چائے، صرف 80 روپے۔ شام 5 سے 7 بجے تک سموسہ مفت۔
- ہمارے نئے مینو کے ساتھ ذائقے کا سفر شروع کریں اور لطف اندوز ہوں۔
  Fix: نیا مینو آ گیا: 12 نئی ڈشز، 450 روپے سے۔ آج ہی چکھیں۔
- محترم صارفین، ہم آپ کو بہترین سروس فراہم کرتے ہیں۔
  Fix: آرڈر میں مسئلہ؟ واٹس ایپ کریں، 10 منٹ میں جواب ملے گا۔
- Apne pasandeeda khane ka tajurba karein aur naye zaiqay daryaft karein.
  Fix: Naya menu aa gaya! Chicken burger combo sirf Rs. 650, aaj hi try karo.

#### Hypothesis check
- Confirmed as a class (native source): the classic formal register (فرمائیے، ملاحظہ، طبع نازک، گراں قدر، بدرجہ اتم،
  the کیجئے ending), from Microsoft's Urdu guide.
- Kept as inference: تجربہ کریں، دریافت کریں، لطف اندوز ہوں، سفر as a metaphor، نئی بلندیوں، صرف X نہیں بلکہ Y، فراہم
  کرنا، یقینی بنائیں، علاوہ ازیں، لہٰذا، بذریعہ، ازراہ کرم and برائے مہربانی، آپ کا in every phrase.
- Refined: مستفید ہوں is a note, not a warning (banks use it). براہ کرم is standard; only the ornate forms are flagged.
- Rejected as tells: حاصل کریں and منتخب کریں (Jazz uses both in its own Urdu copy).
- Brands: Jazz (Urdu site) and Easypaisa (Roman Urdu) were read. Foodpanda PK and JazzCash returned no readable copy;
  Daraz PK and Careem were not checked. Of the Roman casual words, only toh and kyun were seen on a brand page.

#### Sources
- Urdu Style Guide, Microsoft Localization Style Guides, https://aka.ms/urdu-styleguide (read 2026-09-24, read)
- Urdu, Wikipedia, https://en.wikipedia.org/wiki/Urdu (read 2026-09-24, read)
- Roman Urdu, Wikipedia, https://en.wikipedia.org/wiki/Roman_Urdu (read 2026-09-24, read)
- Urdu alphabet, Wikipedia, https://en.wikipedia.org/wiki/Urdu_alphabet (read 2026-09-24, read)
- Jazz Urdu homepage, jazz.com.pk, https://jazz.com.pk/ur (read 2026-09-24, read)
- Easypaisa homepage, easypaisa.com.pk, https://easypaisa.com.pk/ (read 2026-09-24, read)
- Hindi twin of the "not X but Y" pattern: India TV Hindi, https://www.indiatv.in/explainers/how-to-detect-ai-written-text-6-language-patterns-that-reveal-machine-writing-2026-08-25-1239356 (read 2026-09-24, read)

### 4.10 Tamil (ta)

#### Register guide

- Spoken forms carry social copy. Present and future: இருக்கு, வருது, கிடைக்கும், தர்றோம் (not இருக்கிறது, வருகிறது, வழங்குகிறோம்). Spoken plurals and pronouns end in -ங்க: அவங்க, நீங்க, நாங்க. The linguist Harold Schiffman notes that literary Tamil is never used for informal talk and that the shared spoken standard spreads through films, TV and college hostels; he also gives வேண்டும் becoming வேணும். ProofTamil and Sariya list the same written vs spoken pairs. Confidence: native source (linguist) plus several sources.
- Commands and CTAs: spoken -ங்க (பண்ணுங்க, வாங்க, பாருங்க, குடுங்க) and the negative -ாதீங்க (மிஸ் பண்ணிடாதீங்க). Written -உங்கள், -ஆதீர்கள் and infinitive -வும் commands (பார்வையிடவும்) are notice and UI forms; Microsoft's Tamil UI guide uses them, which suits software and not a caption. Confidence: single source plus inference.
- Code-mixing rule: English nouns stay English and take Tamil case endings (ஆர்டருக்கு, store-la, weekend-ku); English verbs take பண்ணு (ஆர்டர் பண்ணுங்க, ட்ரை பண்ணி பாருங்க, wait pannunga). Wikipedia's Tanglish article gives drive paṇṇu, driver-kku, journey-ai and the -u added to English nouns; Schiffman records whole lectures in this mix (English verb plus pannaa); Sariya gives வெயிட் பண்ணு for காத்திரு. Everyday loans in ads: ஆஃபர், டீல், ஃப்ரீ, டெலிவரி, காம்போ, ஸ்பெஷல், ஸ்டாக், சைஸ். Confidence: several sources.
- Script choice: Roman Tanglish is normal for youth posts on Instagram and X; Tamil script with English loans spelled in Tamil letters (ஃப்ரீ, ஆஃபர்) reaches a wider Tamil Nadu audience. Wikipedia notes that ads often print Tamil in the Latin alphabet and that some worry about script loss; a 2010 Chennai student column in The Hindu describes Tanglish (with the -fy suffix and yaa) as what almost every teenager uses. Keep one script per line; brand names can stay Latin. Confidence: several sources for use, inference for the rule.
- Slang, one per post at most: செம or semma (spoken form of செம்மை, awesome or an intensifier, per Wiktionary); mass, vera level, kalakkunga and gethu are common but unsourced here (inference). Peer words machan and machi (Wiktionary gives மச்சான் as informal best friend) fit a youth persona only. Thalaivar is tied to Rajinikanth fandom (inference). CSK's anthem and fan club name Whistle Podu (Wikipedia) show a big brand running on a Tanglish slogan.
- Vocabulary layer: spoken Tamil keeps many Sanskrit origin words (சந்தோஷம், ஆரம்பம், சுலபம்) while pure Tamil coinages (மகிழ்ச்சி, தொடக்கம், இணையவழி) sound official. Wikipedia's Tanglish article says formal Tamil draws on pure Tamil and colloquial Tamil on Prakrit and Sanskrit loans; the Tanittamil (pure Tamil) movement explains why government and cooperative brands lean pure Tamil. Some words sit well in both registers: தள்ளுபடி (discount), இலவசம் (free). Confidence: single source plus inference.
- Sri Lanka: written Tamil is shared across countries but spoken varieties differ considerably, and Sri Lankan dialects are more conservative (Wikipedia). Skip Chennai slang; a light written or neutral spoken register is safer. Jaffna traits such as polite -ங்கோ endings and ஓம் for yes are inference, so get a local check.
- Singapore and Malaysia: in Singapore, Tamil is an official language with a state channel (Vasantham) and a daily (Tamil Murasu), and Schiffman found the spoken standard used even in Singapore classrooms; many readers are English dominant, so short Tamil with English terms works (inference). Malaysian Tamil vocabulary differs from Indian Tamil, for example காடி (car), கூட்டாளி (friend), தே தாரிக் (teh tarik), கோசம் (zero, from Malay kosong) (Wikipedia); use local words, not Chennai slang.
- Emoji habits (inference): 🔥 for deals, 😍 for food, 🙏 for festival wishes; stay inside the skill's limits.
- Numbers for designers (inference): ₹199 or ரூ.199; Indian digit grouping ₹1,00,000; time as இரவு 9 மணி, or 9 PM in Tanglish; Sri Lanka Rs., Singapore S$, Malaysia RM.

#### Formal to everyday swaps

| formal | everyday | note | confidence |
|:-|:-|:-|:-|
| இருக்கிறது | இருக்கு | spoken present drops கிற | several sources (Schiffman, ProofTamil) |
| கிடைக்கிறது | கிடைக்கும், கிடைக்குது | "now available" lines | inference from the same pattern |
| உள்ளது, உள்ளன | இருக்கு, இருக்காங்க | also perfect -துள்ளது becomes -ஆச்சு (வந்தாச்சு) | inference |
| வேண்டும் | வேணும் | வேண்டாம் stays in speech | native source (Schiffman), Sariya |
| செய்யுங்கள் | பண்ணுங்க | always பண்ணு after an English verb | several sources (Wikipedia Tanglish, Sariya) |
| வாருங்கள் | வாங்க | CTA to a shop or event | inference |
| காத்திருங்கள் | வெயிட் பண்ணுங்க | | single source (Sariya) |
| கொடுங்கள் | குடுங்க | | single source (Sariya) |
| தவறவிடாதீர்கள் | மிஸ் பண்ணிடாதீங்க | formal negative imperative | inference |
| அவர்கள், நீங்கள் | அவங்க, நீங்க | -nga plural of pronouns | native source (Schiffman) |
| என்னுடைய, உங்களுடைய | என்னோட, உங்களோட | written vs spoken possessive | single source (ProofTamil) |
| என்று | -ன்னு | quotative | single source (ProofTamil) |
| செய்யக்கூடியதாக இருக்கும் | செய்யலாம் | Microsoft's old vs new table | single source (Microsoft) |
| அத்தியாவசியமானது | தேவை | Microsoft's old vs new table | single source (Microsoft) |
| வழங்கப்படும் | தர்றோம், கிடைக்கும் | active voice | single source (Microsoft, avoid passive) |

#### AI and translation tells

Native readers do complain: a Tamil Quora thread asks why ChatGPT's Tamil is so full of errors (search snippet only; the page returned 403).

| tell | robotic example | natural fix | evidence | confidence |
|:-|:-|:-|:-|:-|
| Written verb forms in a caption | புதிய சுவை இப்போது கிடைக்கிறது. | புது ஃப்ளேவர் வந்தாச்சு! | Sariya: Google gives formal written Tamil where spoken is needed; Schiffman on diglossia | several sources |
| English loan verb with செய் | இப்போதே ஆர்டர் செய்யுங்கள் | இப்பவே ஆர்டர் பண்ணுங்க | Wikipedia Tanglish, Schiffman, Sariya give the பண்ணு pattern | several sources for the natural form; the tell is inference |
| -ப்படு passive | இலவச டெலிவரி வழங்கப்படும் | டெலிவரி ஃப்ரீ | Microsoft Tamil guide: avoid passive, rewrites அமைக்கப்பட்டிருந்தால் as அமை | single source |
| Stiff formal auxiliaries | செய்யக்கூடியதாக இருக்கும், அத்தியாவசியமானது | செய்யலாம், தேவை | Microsoft Tamil guide, words to avoid | single source |
| Calqued marketing verbs (Experience, Discover, Explore, Enjoy) | எங்கள் புதிய கலெக்ஷனை கண்டறியுங்கள் | புது கலெக்ஷன் வந்தாச்சு, கடைக்கு வந்து பாருங்க | none found | inference |
| Journey metaphor | உங்கள் ஃபிட்னஸ் பயணத்தைத் தொடங்குங்கள் | முதல் வாரம் ஜிம் ஃப்ரீ, காலை 6 மணில இருந்து | none found | inference |
| Not just X, it is Y | இது வெறும் சேலை அல்ல, இது ஒரு பாரம்பரியம் | காஞ்சிபுரம் பட்டு, கையால நெய்தது, ₹8,500ல இருந்து | Wikipedia Signs of AI writing (English negative parallelism); Tamil form mine | inference |
| To new heights | உங்கள் வணிகத்தை புதிய உயரங்களுக்கு கொண்டு செல்லுங்கள் | உங்க கடைக்கு ஆன்லைன் ஆர்டர் இன்னைக்கே ஆரம்பிங்க | none found | inference |
| Written pronouns and your in every line | உங்கள் சருமத்திற்கு உங்கள் விருப்பமான கிரீம் | உங்க ஸ்கின்னுக்கு ஏத்த கிரீம், ₹299 | ProofTamil (written vs spoken possessive) | single source plus inference |
| Literal idioms | a piece of cake as கேக் துண்டு போல எளிது | ரொம்ப ஈஸி | Sariya (idioms translated word for word); Microsoft (translate the intent) | several sources |
| Sandhi slips in formal copy | தமிழ் பண்பாடு | தமிழ்ப் பண்பாடு | Sariya | single source; only check formal copy, since spoken style often drops the doubling |
| Notice opener and generic CTA | அன்புள்ள வாடிக்கையாளர்களே ... மேலும் அறிய | lead with the offer, one specific CTA | none found | inference |
| Are you ready opener | நீங்கள் தயாரா? | drop it and start with the fact | none found | inference |

#### Purple or poetic phrasing

All my own examples (inference).

- சுவையின் சொர்க்கம் (a paradise of taste). Fix: நெய் ரோஸ்ட் தோசை ₹90, மொறுமொறுன்னு.
- ஒவ்வொரு துளியிலும் அன்பு (love in every drop). Fix: காலை 6 மணிக்குள்ள பால் வீட்டுக்கே.
- காலத்தால் அழியாத அழகு (beauty time cannot erase). Fix: 20 வருஷமா அதே ஜரிகை தரம்.
- கனவுகளுக்கு சிறகுகள் (wings for your dreams). Fix: EMI மாசம் ₹999ல இருந்து.
- மறக்க முடியாத தருணங்கள் (unforgettable moments). Fix: பர்த்டே பார்ட்டிக்கு 20 பேர் வரைக்கும் ஹால் ஃப்ரீ.

#### Natural vs robotic lines

Natural:

1. அண்ணா நகர் ஷோரூம்ல ஞாயிறு வரைக்கும் எல்லா சேலைக்கும் 30% தள்ளுபடி!
2. Weekend plan illaya? Saturday night 7 mani-ku Besant Nagar beach-la live music, entry free, vaanga!
3. செம டீல்! ரெண்டு பீட்சா வாங்குனா ஒண்ணு ஃப்ரீ, இந்த வெள்ளிக்கிழமை மட்டும் தான்.
4. Diwali sweets box semma mass! 1 kg box ₹599 mattum, T. Nagar store-la stock irukku, seekiram vaanga.

Robotic, each with its fix:

1. எங்கள் புதிய மெனுவை இன்றே அனுபவியுங்கள்!
   Fix: புது மெனு வந்தாச்சு! காம்போ ₹199 தான், இன்னைக்கே டேஸ்ட் பண்ணி பாருங்க.
2. இது வெறும் காபி அல்ல, இது ஒரு அனுபவம்.
   Fix: கும்பகோணம் டிகிரி காபி, காலை 6 மணிக்கே ரெடி, ஒரு கப் ₹35.
3. அனைத்து ஆர்டர்களுக்கும் இலவச டெலிவரி வழங்கப்படுகிறது.
   Fix: எல்லா ஆர்டருக்கும் டெலிவரி ஃப்ரீ, இந்த வாரம் முழுக்க.
4. அன்புள்ள வாடிக்கையாளர்களே, எங்கள் புதிய கிளை திறக்கப்பட்டுள்ளது.
   Fix: வேளச்சேரில நம்ம புது கிளை திறந்தாச்சு! முதல் 100 பேருக்கு ஸ்வீட் ஃப்ரீ.

#### Sources

- Standardization or Restandardization: the case for Standard Spoken Tamil (Harold F. Schiffman), University of Pennsylvania, http://ccat.sas.upenn.edu/~haroldfs/public/stantam/STANTAM.HTM (read 2026-09-24, read)
- Tanglish, Wikipedia, https://en.wikipedia.org/wiki/Tanglish (read 2026-09-24, read)
- Enter, Tanglish (Hiranmayi Narayanan, 2010), The Hindu, https://www.thehindu.com/features/metroplus/nxg/Enter-Tanglish/article16371444.ece (read 2026-09-24, read)
- Why Google Translate Fails at Tamil, and What to Use Instead (2026-03-19, vendor blog), Sariya, https://www.sariya.app/blog/why-google-translate-fails-tamil (read 2026-09-24, read)
- 25 Essential Tamil Verbs: Spoken vs Formal, Sariya, https://www.sariya.app/dictionary/tamil-common-verbs (read 2026-09-24, read)
- 10 Common Tamil Grammar Mistakes (2026-04-25), ProofTamil, https://www.prooftamil.com/blog/common-tamil-grammar-mistakes (read 2026-09-24, read)
- Tamil Localization Style Guide (PDF tam-tam-StyleGuide.pdf), Microsoft, https://aka.ms/tamil-styleguide (read 2026-09-24, read)
- Signs of AI writing, Wikipedia, https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing (read 2026-09-24, read)
- செம்ம, Wiktionary, https://en.wiktionary.org/wiki/செம்ம (read 2026-09-24, read)
- மச்சான், Wiktionary, https://en.wiktionary.org/wiki/மச்சான் (read 2026-09-24, read)
- Chennai Super Kings, Wikipedia, https://en.wikipedia.org/wiki/Chennai_Super_Kings (read 2026-09-24, read)
- Madras Bashai, Wikipedia, https://en.wikipedia.org/wiki/Madras_Bashai (read 2026-09-24, read)
- Tanittamil Iyakkam, Wikipedia, https://en.wikipedia.org/wiki/Pure_Tamil_movement (read 2026-09-24, read)
- Sri Lankan Tamil dialects, Wikipedia, https://en.wikipedia.org/wiki/Sri_Lankan_Tamil_dialects (read 2026-09-24, read)
- Malaysian Tamil, Wikipedia, https://en.wikipedia.org/wiki/Malaysian_Tamil (read 2026-09-24, read)
- South Asian languages in Singapore, Wikipedia, https://en.wikipedia.org/wiki/South_Asian_languages_in_Singapore (read 2026-09-24, read)
- ChatGPT-இன் தமிழ் இவ்வளவு பிழைகளாக இருப்பது ஏன்?, Quora Tamil, https://ta.quora.com/ChatGPT-%E0%AE%87%E0%AE%A9%E0%AF%8D-%E0%AE%A4%E0%AE%AE%E0%AE%BF%E0%AE%B4%E0%AF%8D-%E0%AE%87%E0%AE%B5%E0%AF%8D%E0%AE%B5%E0%AE%B3%E0%AE%B5%E0%AF%81 (read 2026-09-24, snippet; fetch returned 403)
- How brands are hurting themselves with pan-India Hinglish ads, Quartz, https://qz.com/india/1767016/indian-brands-must-move-from-hinglish-to-tamil-telugu-malayalam (read 2026-09-24, snippet; fetch returned 403)
- Instagram Marketing in Tamil and Tanglish, sociall.in, https://www.sociall.in/instagram-marketing-in-tamil-and-tanglish-reaching-audiences-with-local-flavor (read 2026-09-24, snippet; the page now returns 404)

#### Could not verify

- No real 2024 to 2026 brand posts were read (Aavin, Saravana Stores, Pothys, Sun NXT, Swiggy and Zomato Tamil ads); Instagram, Facebook, Reddit, Quora and HiNative were blocked.
- mass, vera level, gethu, kalakku and thalaivar; the Sri Lankan -ங்கோ and ஓம்; every Tamil AI calque in the tells table except the passive and the formal auxiliaries.

### 4.11 Chinese (zh)

#### Register guide

- Casual markers (CN): short clauses, the concrete fact (price, time, place) in the first line, then a personal reaction. Sentence-final 啊 / 呀 / 吧 / 啦 / 哦 / 嘛 / 呢; intensifiers 超 / 巨 / 真的 / 太…了吧; hooks such as 救命 / 谁懂 / 咱就是说. Xiaohongshu guides model lines built on 宝子们 plus 冲, first-person 咱, and emoji to cut dryness. Confidence: several sources (数英 2022, 新周刊 2021 for 咱就是说); the particle list is inference.
- Address beyond 你 / 您: the safe default is no vocative at all. 姐妹们 and 宝子们 fit only female-skewed beauty, fashion and food accounts on 小红书; 家人们 now reads as livestream selling; 亲 reads as Taobao customer service; 尊敬的客户 and 亲爱的用户 read as SMS or email notices. Confidence: inference.
- Slang ages fast. 绝绝子 and yyds fell out of use within a few months of their 2021 peak (新周刊). Words that still read current in 2024 to 2026: 松弛感, 班味, city不city, 硬控 (咬文嚼字 2024 list), 活人感, 预制XX, 从从容容 游刃有余 (咬文嚼字 2025 list), and 活人感, 反精致, 抽象力 in 千瓜's 2026 Xiaohongshu keyword report. Use at most one trend word per post, and only where the audience already uses it. Confidence: native source (咬文嚼字 is a language magazine; 新周刊 on decay).
- 活人感 is the 2025 answer to AI flavour: accounts that post like a real person (self-deprecating replies, a visible founder, a mascot with a personality) beat polished official tone. Confidence: several sources (星风传媒 2025, 咬文嚼字 2025 citing AI as the reason the word rose).
- Code-mixing: a small set of Latin-letter English is native in CN posts (city, citywalk, vlog, OOTD, emo, MBTI, i人 / e人, get, app). Write them the way natives do, lowercase and inside a Chinese sentence. Untranslated technical English where Chinese has an everyday word (context, cache, claim) is an AI translationese sign. No whole English sentences. Confidence: single source (yage.ai 2026) plus inference.
- Emoji: 小红书 uses emoji as line markers and in titles, but stacked emoji bullets (✅💡🚀 before each point) are named as an AI sign by Chinese Wikipedia editors and by the Taiwanese speak-human-tw rules. One emoji family per post, inside the global caps. 微博 bracket codes such as [doge] and 小红书 sticker codes do not survive copy-paste to other platforms. Confidence: several sources; the sticker point is inference.
- zh-TW: particles 喔 / 啊 / 耶 / 欸 / 啦 / 嘛 (zh.wikipedia 臺灣國語). Vocabulary 影片, 品質, 資訊, 創作者, not 视频, 质量, 信息, 博主 (speak-human-tw lists 60+ such pairs). Brand admins call themselves 小編; posts talk about 粉專, 貼文, 限動, 留言. "der" for 的 now reads dated and cutesy. Confidence: several sources for particles and vocabulary; 小編 and der are inference.
- zh-HK: posts for locals are usually in written Cantonese (嘅, 咗, 啲, 喺, 嚟, 唔, 係, 冇, 㗎, 啦), while formal notices, legal text and serious news use standard written Chinese (zh.wikipedia 粵語白話文). HK says 勁 where CN and TW say 超 (星島 2024). English mixing is native (book位, check下, sale, chill). Keep one register per sentence: 我哋嘅 or 我們的, never 我們嘅. Confidence: several sources for the register split and 勁; the English list and the mixing rule are inference.
- Sentence shape: real posts lead with the thing and a reaction; AI posts open with an era frame, march through 首先 / 其次, and close on an uplift or a summary. Replace vague time words with dates and numbers (2026年3月, not 近年来). Confidence: several sources (翔宇 2025, JameCling 2026, qu-ai-wei).

#### Formal to everyday swaps

| formal | everyday | note | confidence |
|:-|:-|:-|:-|
| 进行购买 / 进行预约 | 买 / 约 | drop 进行, keep the verb | native source (余光中 1987; JameCling) |
| 购买 | 买 | | single source (JameCling) |
| 使用 | 用 | | single source (JameCling) |
| 非常 / 极其 | 很, 超, 巨 | 超 and 巨 are casual CN; HK uses 勁 | single source (JameCling) plus inference |
| 例如 | 比如 | | single source (JameCling) |
| 值得注意的是 | 还有一点 / 注意 | or just say it | single source (翔宇) |
| 旨在 | 就是为了 | | single source (翔宇) |
| 因而 / 鉴于上述分析 | 所以 / 说白了 | | single source (翔宇) |
| 此外 | 还有 / 而且 | | single source (翔宇) |
| 由于…使得… | 因为…所以…, or drop | 由于贫穷，使得休学 → 家里穷，只好休学 | native source (余光中) |
| 有关 / 关于 + noun | drop | 有关问题 → 问题 | native source (余光中) |
| 于9月24日开售 | 9月24日开卖 / 24号开卖 | 于 is fine in formal notices | inference |
| 该产品 / 本产品 | 这款 / 它 | | inference |
| 届时 | 到时候 | | inference |
| 予以 / 给予 | 给 | | inference |

#### AI and translation tells

| tell | robotic example | natural fix | evidence | confidence |
|:-|:-|:-|:-|:-|
| Era opener | 在当今快节奏的时代，一杯好咖啡很重要。 | 早上7点开门，美式12元。 | 新智元 via 腾讯新闻 2026; JameCling; speak-human-tw | several sources |
| Negate then lift | 这不仅仅是一双鞋，更是一种态度。 | 鞋底加厚3毫米，走一天脚不酸。 | AI内参 2026; 朱宥勳 (cited on zh.wikipedia); Threads posts | several sources |
| Essay connectors and closers | 值得注意的是… / 总而言之… / 综上所述… | cut, or 还有 / 另外 | 翔宇; JameCling; Threads @chi_digital_writing | several sources |
| Numbered scaffolding | 首先…其次…最后… | one point per line | qu-ai-wei; speak-human-tw | several sources |
| Jargon cluster | 为品牌赋能，打造全链路闭环 | 上传一张图，3分钟出5张主图 | qu-ai-wei; JameCling | several sources |
| 进行 + verb | 欢迎进行预约 | 可以约了 | 余光中; JameCling | native source |
| Padding | 通过线上的方式购买 | 网上就能买 | qu-ai-wei | single source |
| 是一个非常 | 这是一个非常实用的礼物 | 这个礼物很实用 | 余光中 covers the wider pattern | inference |
| Importance inflation | 至关重要 / 不可或缺 / 意义重大 | the one fact | zh.wikipedia AI page | native source (editor community) |
| 2026 chatbot tics | 这一杯稳稳接住你的疲惫 | 加班到十点，楼下还有热汤面 | CTWANT 2026; zh.wikipedia | several sources |
| Over-elevation | 一条老街成了城市韧性的象征 | 老街周六有市集，10点开 | AI内参 2026 | single source |
| Superlative pile | 最好喝、最温暖、最治愈的一杯 | 一个事实: 少糖也不寡淡 | AI内参 2026 | single source |
| Push ending | 还在等什么？赶快行动吧！ | 周五前下单，周六到 | speak-human-tw (勸誡反問收尾) | single source |
| Auto-converted variant | 視頻 / 質量 in a Taiwan post | 影片 / 品質 (TW), 影片 / 質素 (HK) | speak-human-tw | single source |
| Chatbot leftovers | 以下是为你生成的文案： / 希望对你有帮助 | delete | zh.wikipedia AI page | native source (editor community) |

Background: an ACL 2025 paper found multilingual LLMs carry English-influenced vocabulary and grammar into Chinese output (French and Chinese benchmark). Confidence: single source.

Hypotheses checked and not linted: 沉浸式 (a native vlog genre, 沉浸式护肤), 解锁 (解锁新吃法 is native), 打造, 极致, 助力 (native in CN ads and headlines), 探索, 作为一个 (作为一个吃货 is a native meme), 让我们一起 (native in campaigns). Keep them in the guide, not the lint. 被 and 一个 overuse are real translationese but cannot be linted by string.

#### Purple or poetic phrasing

1. The Chinese tapestry: 画卷, 织就, 交织成. 老街交织成一幅温暖的画卷 → 老街周六有市集，十点开。 (新智元 lists tapestry among AI words; the Chinese forms are inference.)
2. 承载着记忆, 根植于, 见证, 标志着. 这家店承载着城市的记忆 → 这家店开了二十年，还是老价钱。 (zh.wikipedia lists 见证, 根植于, 标志着.)
3. 温度 as an abstraction: 做有温度的品牌 → 下雨天到店送伞。 (inference)
4. Pseudo-deep "DeepSeek flavour": 时间的褶皱, 赛博, 量子, 熵增. Cut them. (Search snippets describe the backlash against DeepSeek-style "false sophistication"; the word list is inference.)
5. 绽放, 诠释, 璀璨: 诠释秋日的浪漫 → 桂花拿铁回来了，中杯18元。 (inference)

#### Natural vs robotic lines

Natural:
- zh-CN: 新品桂花拿铁今天上架，中杯18元，下午3点前第二杯半价。
- zh-CN: 救命，这个杯子也太能装了吧，750ml塞进包里刚好，现在39.9包邮。
- zh-TW: 中秋禮盒開賣囉！蛋黃酥6入480元，9/30前下單全台免運。
- zh-HK: 今個星期六喺銅鑼灣店有試食，12點開始，嚟就有得試。

Robotic, each with its fix:
- zh-CN robotic: 在当今快节奏的时代，这杯咖啡不仅仅是饮品，更是承载着城市记忆的温暖画卷。
  Fix: 早上赶地铁？门店7点开，美式12元，出门前拿一杯。
- zh-CN robotic: 首先，我们通过数字化的方式为品牌赋能；其次，打造全链路闭环。
  Fix: 上传商品图，3分钟出5张主图，不用再等设计排期。
- zh-TW robotic: 總而言之，這是一個非常值得收藏的好物，還在等什麼？
  Fix: 保溫12小時，早上裝的熱水下班還燙口，這週999元。
- zh-HK robotic: 我們嘅新店將為您帶來無縫體驗，敬請期待！
  Fix: 旺角新店10月3號開，開幕三日全單九折。

#### Sources (zh)

- 全网疯转，AI大神公开"去AI味"秘籍 (新智元, 2026-02-18), 腾讯新闻, https://news.qq.com/rain/a/20260218A05JKN00 (read 2026-09-24, read)
- 你写的文案被鉴定为"AI味"了？这份2026版去味指南请收好 (2026-05-25), AI内参, https://www.neican.ai/insights/ai2026-20260525201003328-0/ (read 2026-09-24, read)
- 8 个特征识别和消除 AI 味 (翔宇, 2025-04-03), 翔宇工作流, https://xiangyugongzuoliu.com/ai-style-writing-8-common-giveaways/ (read 2026-09-24, read)
- 写作中的AI味是哪儿来的 (鸭哥, 2026-04-18), yage.ai, https://yage.ai/share/ai-chinese-translationese-20260418.html (read 2026-09-24, read)
- qu-ai-wei: 去除简体中文 AI 写作痕迹, GitHub, https://github.com/LifelongLazyLearner/qu-ai-wei (read 2026-09-24, read)
- 中文去 AI 味写作指南 (JameCling, 2026-05-27), 格律诗的软件世界, https://www.jamecling.com/archives/1175 (read 2026-09-24, read)
- AI 写作最尴尬的地方，是它自己不知道自己有味 (2026-07-21), 腾讯云开发者社区, https://developer.cloud.tencent.com/article/2713102 (read 2026-09-24, read)
- 余光中：怎样改进英式中文？论中文的常态与变态 (1987 essay, repost), 博客园, https://www.cnblogs.com/poterliu/p/12131998.html (read 2026-09-24, read)
- Wikipedia:AI生成文的特徵, 中文维基百科, https://zh.wikipedia.org/wiki/Wikipedia:AI生成文的特徵 (read 2026-09-24, read)
- speak-human-tw 說人話 (Raymond Hou), GitHub, https://github.com/Raymondhou0917/speak-human-tw (read 2026-09-24, read)
- AI文一眼看穿？網曝常見口頭禪「接住、撐住、穩住」 (2026-04-27), CTWANT, https://www.ctwant.com/article/478834/ (read 2026-09-24, read)
- 为何它们成为2025年十大流行语？ (2025-12-02), 中新网, https://www.chinanews.com.cn/cul/2025/12-02/10525514.shtml (read 2026-09-24, read)
- 才两个月，你就把"绝绝子"彻底忘了 (新周刊, 2021-12-09), 人人都是产品经理, https://www.woshipm.com/it/5244303.html (read 2026-09-24, read)
- 4000字长文，拆解小红书爆文流量密码 (2022-04-14), 数英, https://www.digitaling.com/articles/757154.html (read 2026-09-24, read)
- 2025 抖音、小红书、微博都在玩的"活人感" (2025-08-05), 星风传媒, https://www.xgccm.com/article/detail/5141 (read 2026-09-24, read)
- 粵語白話文, 中文维基百科, https://zh.wikipedia.org/wiki/粵語白話文 (read 2026-09-24, read)
- 臺灣國語, 中文维基百科, https://zh.wikipedia.org/wiki/臺灣國語 (read 2026-09-24, read)
- 小紅書熱議香港人3大類口頭禪 (2024-12-11), 星島頭條, https://www.stheadline.com/lifetips/3409806/%E5%B0%8F%E7%B4%85%E6%9B%B8%E7%86%B1%E8%AD%B0%E9%A6%99%E6%B8%AF%E4%BA%BA3%E5%A4%A7%E9%A1%9E%E5%8F%A3%E9%A0%AD%E7%A6%AA-%E6%BD%AE%E8%AA%9E%E7%B6%93%E5%85%B8%E5%BB%A3%E5%91%8A%E5%B0%88%E7%94%A8%E8%A1%93%E8%AA%9E-1%E7%94%A8%E5%AD%97%E6%83%B9%E4%B8%AD%E6%B8%AF%E7%B6%B2%E6%B0%91%E5%85%B1%E9%B3%B4%E5%B0%8D%E9%80%99%E5%80%8B%E5%AD%97%E7%89%B9%E5%88%A5%E6%9C%89%E5%8D%B0%E8%B1%A1 (read 2026-09-24, read)
- Do Large Language Models have an English Accent? (Guo et al., ACL 2025), ACL Anthology, https://aclanthology.org/2025.acl-long.193/ (read 2026-09-24, read)
- 《咬文嚼字》"2024年十大流行语", 新华网, http://www.news.cn/politics/20241202/59496b2d344b4382b6c12d03d78b8f13/c.html (read 2026-09-24, snippet)
- 报告解读｜《2026小红书平台"十大热词"洞察数据报告》, 网易, https://m.163.com/dy/article/KQUHNKA30531B128.html (read 2026-09-24, snippet)
- 10 個 AI 文章會用的文字/句型, Threads @chi_digital_writing, https://www.threads.com/@chi_digital_writing/post/DWAqoLljlA2 (read 2026-09-24, snippet)
- 對「AI腔」厭煩了嗎？分析AI生成文字的經典句型 (朱宥勳, 文字診療室), YouTube, https://www.youtube.com/watch?v=9uuX6cb81C8 (read 2026-09-24, snippet; also cited on zh.wikipedia)
- 小红书爆款标题玩法01：你一定要学会的情绪化表达, 人人都是产品经理, https://www.woshipm.com/operate/6009458.html (read 2026-09-24, snippet)
- 为什么越来越多人反感"DeepSeek味文案"？, CSDN, https://blog.csdn.net/AIria2022/article/details/148231503 (read 2026-09-24, snippet; page fetch blocked)

#### Could not verify

- Whether 小红书 or 抖音 cut reach for 诱导互动 bait (@好友, 评论区扣1): kept as a note.
- The DeepSeek-style purple list (褶皱, 赛博, 量子, 熵增): the CSDN page was blocked; only snippets on the backlash.
- Whether 余光中 names 一个 and 当…的时候 in that essay: the fetched text did not show them.

### 4.12 Japanese (ja)

#### Register guide

- Default brand voice: soft です・ます with ね / よ, mixed with 体言止め and short plain asides. AI Japanese ends sentence after sentence in 〜ます。 and reads like a textbook or manual; human copy varies endings and adds 正直, やっぱり, 個人的には. Confidence: several sources (くらべるAI, hachimakivenda 2025).
- 中の人 voice: Japanese brand accounts on X often post as a named operator in first person, with jokes and replies. SHARP's account wrote in the operator's personal voice and 井村屋's account shared a fan's joke post, but SHARP's personal-voice post rating a rival's product also caused a 炎上. Use plain-form asides (〜かも, 〜しちゃった, 正直びっくり) only when the client already runs a 中の人 persona. Confidence: single source (ja.wikipedia) plus inference.
- Current casual words (三省堂 今年の新語): 2025 winner ビジュ, then オールドメディア, えっほえっほ, しゃばい; editors also picked 推し活, 強火, 今これ, チャッピー; the 2024 list included メロい, 横転, しごでき, 界隈. Youth slang loses its appeal once it goes public (金田一秀穂, cited on ja.wikipedia 若者言葉), so borrow at most one word and never stack them. 没入感 was an editor's 2025 pick, so 没入 alone is native, not an AI tell. Confidence: native source.
- Code-mixing: everyday katakana loans are fine (セール, コスパ, タイパ, 推し). Business katakana (ソリューション, エンゲージメント, シナジー) reads like a slide deck; a NINJAL survey found 55.3% did not want more loanwords and 46.7% said they cause misunderstanding. Latin letters for product names, hashtags and OK; no English sentences. Confidence: single source (ja.wikipedia on the NINJAL proposals) plus inference.
- Emoji and kaomoji: one or two emoji at phrase ends is normal. Heavy emoji plus katakana endings (〜カナ？) and 、、、 read as おじさん構文 (No. 2 in 三省堂's 2022 new words). Emoji bullets such as ✅💡🚀 before list items are flagged as AI formatting by textlint-ja. Kaomoji such as (^^) fit a 中の人 persona, not a premium brand. Confidence: several sources; the kaomoji point is inference.
- Keigo, beyond the covered です・ます rule: drop needless させていただきます and every 二重敬語 (お越しになられる), both called out by the Agency for Cultural Affairs. マニュアル敬語 (〜になります for です, よろしかったでしょうか, 〜からお預かりします) belongs at the shop counter, not in written copy. Confidence: native source (文化庁 2007; ja.wikipedia バイト敬語).
- Address, beyond no あなた: speak to a segment with 〜の方 (お近くの方, 初めての方) or 皆さん in casual posts; お客様 suits service notices; お客様各位 and 皆様こんにちは read like a circular. Confidence: inference.
- AI tone in 2025 to 2026 Japanese: lecture framing (〜について探っていきましょう), hedges (〜と言えるでしょう, 〜と考えられます), 第一に / 第二に, 結論として, hopeful grand endings and sudden disclaimers; Claude's own habit is over-gentle empathy, Gemini's is headers, bold and bullets. Confidence: several sources (Qiita 2026, くらべるAI, hachimakivenda).

#### Formal to everyday swaps

| formal | everyday | note | confidence |
|:-|:-|:-|:-|
| 本日、休業させていただきます | 本日は休業いたします / 今日はお休みです | the 文化庁 example itself | native source |
| 〜することができます | 〜できます | | native source (textlint-ja) |
| 〜することが可能です | 〜できます | | single source (aitip) |
| 〜と言えるでしょう / 〜と考えられます | 〜です, or cut | | several sources |
| 以上のことから / 結論として | cut | | several sources |
| 〜という点において | 〜なら / 〜で | | single source (aitip) |
| お越しになられる | お越しになる / いらっしゃる | 二重敬語 | native source (文化庁) |
| こちらが新作になります | こちらが新作です | マニュアル敬語; views differ | single source (ja.wikipedia) |
| 〜を実現します | the concrete result | | single source (magicss note 2025) |
| 非常に重要です | 大事です, or cut | | several sources (くらべるAI, magicss) |
| ソリューション | 解決策, or what it fixes | | single source plus inference |
| 本日 | 今日 | 本日 is fine in notices | inference |
| 実施いたします | やります / 開催します | | inference |
| ご確認ください | 見てみてください | | inference |
| 誠にありがとうございます | ありがとうございます！ | | inference |

#### AI and translation tells

| tell | robotic example | natural fix | evidence | confidence |
|:-|:-|:-|:-|:-|
| Changing-world opener | 今日の急速に変化する世界において… | 秋の新作、今日から全店で。 | aitip flags において-style 翻訳調 | inference |
| Not-just frame | 単なるバッグではなく、生き方です。 | 13インチPCが入って、重さは480g。 | none found | inference |
| Lecture framing | 新作について探っていきましょう | 新作は栗とほうじ茶のパフェです。 | Qiita @robitan 2026 | single source |
| Hedges | 今年いちばんの一品と言えるでしょう | 今年いちばん売れています。 | Qiita; くらべるAI; hachimakivenda | several sources |
| Numbered scaffolding | 第一に軽さ、第二に価格 | 軽い。しかも3,980円。 | Qiita; textlint-ja | several sources |
| Hype | 可能性を解き放つ / 魔法のように / ゲームチェンジャー | 予約が3タップで終わる | textlint-ja no-ai-hype-expressions | native source |
| Wordy ability form | アプリからご利用することができます | アプリで使えます | textlint-ja; aitip | several sources |
| Colon lead-in | 新作をご紹介します： | 新作は3つです。 | textlint-ja no-ai-colon-continuation | native source |
| Monotone endings | 〜ます。〜ます。〜ます。 | mix です, 体言止め, よ / ね | くらべるAI | single source |
| Emoji bullets | ✅軽い ✅安い ✅丈夫 | 軽くて丈夫、3,980円。 | textlint-ja no-ai-list-formatting | native source |
| Abstract business nouns | 本質的な課題の最適化を実現します | 待ち時間が10分短くなります | magicss note 2025 | single source |
| Chatbot leftovers | 以下はInstagram投稿文の案です | delete | Chinese Wikipedia lists the same pattern for Chinese | inference |
| Calque hooks | さあ、今すぐ始めましょう！ / 準備はできていますか？ | 土曜10時から渋谷店で。 | none found | inference |
| Double keigo | お越しになられる際は | お越しの際は | 文化庁 2007 | native source |
| Blog sign-off | いかがでしたか？ | end on the offer | seen only in a search summary | inference |

Hypotheses checked and not linted: 体験, 没入 (native; 没入感 is a 2025 new-word pick), 唯一無二 (native idiom), 革新的 and 次世代 (common in native PR), 最大限に活用, 〜になります (valid in price lines). シームレス alone flags the product word シームレスブラ, so the lint uses シームレスな.

#### Purple or poetic phrasing

All inference: these phrases also appear in native travel and food copy, so the lint only nudges.

1. 至福のひととき → 3時のおやつにちょうどいい甘さ
2. 五感で楽しむ → name the one sense that matters: 焼きたての香りが店の外まで
3. 物語を紡ぐ / 織りなす → say who made it and how: 職人2人で1日30個だけ
4. 心躍る / 彩る → the fact: 新色は3色、限定1,000個
5. 〜の世界へようこそ / 新たな扉を開く → just the offer: 新作パフェ、今日から

#### Natural vs robotic lines

Natural:
- ja: 秋の新作「栗とほうじ茶のパフェ」、今日から全店で販売スタート！1,280円です。
- ja: 9月26日(土)は渋谷店で試食会やります。13時からなので、お近くの方はぜひ。
- ja: 台風の影響で、本日は18時で閉店します。ご来店予定の方はお気をつけて。
- ja: 中の人、今日のランチは新作のカレーパンでした。サクサクで正直びっくり。

Robotic, each with its fix:
- ja robotic: 今日の急速に変化する世界において、私たちのコーヒーは単なる飲み物ではなく、ライフスタイルそのものです。
  Fix: 朝7時から開いてます。ブレンドは1杯380円、テイクアウトもどうぞ。
- ja robotic: このアプリはあなたの可能性を解き放ち、毎日を魔法のように変えます。
  Fix: 予約は3タップで完了。前日21時まで変更できます。
- ja robotic: 当店では送料無料とさせていただきます。お越しになられる際はご注意ください。
  Fix: 10月末まで送料無料です。店舗は駐車場がないので、電車でどうぞ。
- ja robotic: 皆様こんにちは、、新サービスはアプリからご利用することができます。詳しくはこちら。
  Fix: 新サービス、今日からアプリで使えます。最初の1回は無料です。

#### Sources (ja)

- 「この日本語記事はどのAIが書いたのか？」をなんとなく見分ける１０の方法 (@robitan, 2026-02-26), Qiita, https://qiita.com/robitan/items/76af9fa8b82c0f9c739f (read 2026-09-24, read)
- textlint-rule-preset-ai-writing (azu; rules no-ai-hype-expressions, no-ai-colon-continuation, no-ai-list-formatting, ai-tech-writing-guideline), GitHub textlint-ja, https://github.com/textlint-ja/textlint-rule-preset-ai-writing (read 2026-09-24, read)
- ChatGPTの文章から「AIっぽさ」を消す！自然な文章にする5つの実践テクニック (2025-05-12), note AIライティング研究所, https://note.com/magicss_ai/n/n2cd21cc78243 (read 2026-09-24, read)
- ChatGPTの日本語が不自然になる原因と自然な文章に直す方法【2026年最新】 (2026-06-20), aitip, https://aitip.jp/chatgpt-japanese-unnatural/ (read 2026-09-24, read)
- ChatGPTのAIっぽさをなくすプロンプト術！自然な文章にする5つのコツ, くらべるAI, https://kuraberuai.fioriera.co.jp/useful-content/remove-ai-like/ (read 2026-09-24, read)
- ChatGPT文章校正・作成で「AIっぽさ」をゼロにする実践プロンプト術 (2025-08-10), hachimakivenda, https://www.hachimakivenda.com/3591 (read 2026-09-24, read)
- ChatGPTの日本語がおかしい？誤字や不自然な文章の原因と対処法 (2025-08-17), Taskhub, https://taskhub.jp/useful/chatgpt-japanese-error/ (read 2026-09-24, read)
- ChatGPTの日本語が不自然になる原因5選と改善策, C-BA AI-memo, https://ai.cbagames.jp/2025/10/10/chatgpt-japanese-error-fix/ (read 2026-09-24, read)
- 敬語の指針 (文化審議会答申, 2007), 文化庁, https://www.bunka.go.jp/seisaku/bunkashingikai/kokugo/hokoku/pdf/keigo_tosin.pdf (read 2026-09-24, read)
- バイト敬語, ja.wikipedia, https://ja.wikipedia.org/wiki/バイト敬語 (read 2026-09-24, read)
- 辞書を編む人が選ぶ「今年の新語2025」ベスト10, 三省堂, https://dictionary.sanseido-publ.co.jp/shingo/2025/best10/index.html (read 2026-09-24, read)
- 辞書を編む人が選ぶ「今年の新語2025」 (lists 2024 examples), 三省堂, https://dictionary.sanseido-publ.co.jp/shingo/2025/ (read 2026-09-24, read)
- 新語・流行語大賞 2025, 自由国民社, https://www.jiyu.co.jp/singo/ (read 2026-09-24, read)
- 若者言葉, ja.wikipedia, https://ja.wikipedia.org/wiki/若者言葉 (read 2026-09-24, read)
- おじさん構文, ja.wikipedia, https://ja.wikipedia.org/wiki/おじさん構文 (read 2026-09-24, read)
- 「外来語」言い換え提案, ja.wikipedia, https://ja.wikipedia.org/wiki/「外来語」言い換え提案 (read 2026-09-24, read)
- シャープ (section on the official Twitter account), ja.wikipedia, https://ja.wikipedia.org/wiki/シャープ (read 2026-09-24, read)
- 井村屋グループ, ja.wikipedia, https://ja.wikipedia.org/wiki/井村屋グループ (read 2026-09-24, read)
- 原因はいったい何？ChatGPTの日本語がおかしい時の解決策, @DIME, https://dime.jp/genre/1962646/ (read 2026-09-24, snippet)

#### Could not verify

- Japanese brand voice on X beyond the Wikipedia entries: no marketing-press source was reachable.
- Every purple phrase, the calque hooks, いかがでしたか and the chatbot-leftover pattern: no native source.

### 4.13 Turkish (tr)

#### Register guide

- Social copy should read like spoken Turkish. Drop the written -mAktAdIr tense and the extra -DIr ending. Drop pronouns too, because the verb ending already shows who is meant. Translator Savaş Kılıç makes both points in two notes for ÇEVBİR, the Turkish translators' union. He says +DIr belongs in formal and reference writing and normal speech leaves it out, and that Turkish is a pro-drop language (it routinely leaves out subject pronouns). Confidence: native source.
- Casual markers:
  - Particles: ya, yani, işte, bak, hadi, gel, bi' (for bir). A mı/mi question makes a good hook.
  - Interjections: valla (TDK labels it colloquial), cidden, resmen.
  - Youth forms of address, for youth brands only: kanka (TDK: informal speech) and moruk (TDK: slang).
  - Praise words: efsane, bayıldık, tam senlik.
  - Shop phrases that sound native: sepette %30 indirim, kargo bedava, kapında, son gün, stoklarla sınırlı.
  - Confidence: native source (TDK labels), inference for the rest.
- Sentence shape: a question as the hook, then one line with the number, the time and the place. Phrases with no verb are normal (Kargo bedava. Sepette %30.). Use -Ip or -ArAk instead of chains of ve, and do not start a sentence with Ve (translator Tuncay Birkan, ÇEVBİR). Confidence: native source (ve), inference (rest).
- Address: the skill already covers siz and sen. On top of that:
  - The siz imperative is -(y)In (kaçırmayın, deneyin).
  - The -(y)InIz form (tıklayınız, başvurunuz) is official-letter style. Avoid it on social.
  - The sen imperative is the bare stem (kaçırma, dene).
  - Confidence: inference.
- Whether to use sen or siz depends on the audience. Consumer brands usually start with siz and move to sen later. Forced closeness draws negative comments (Mutlu Çavuş, BT Günlüğü, 2017). Confidence: single source (native, older).
- Mixing in English: everyday English nouns are normal (story, reels, link, online, outfit, brunch, cookie) and take Turkish suffixes, with an apostrophe after proper names, abbreviations and numbers (23.59'a, 49,90 TL'ye). An English verb plus etmek (update etmek, confirm etmek) is plaza dili, office jargon that many readers mock (Vikipedi, Plaza dili). Keşfet is native social vocabulary (it is the name of Instagram's Explore tab), so on its own it is not a tell. Confidence: single source (plaza dili), inference (rest).
- Brand voice trend: columnist Salih Keskin (İstanbul Ticaret Gazetesi, August 2025) credits much of Getir's early growth to customers' own surprised posts about delivery speed. He says brands now prefer relaxed, humorous voices. Confidence: single source (native).

#### Formal to everyday swaps

| Formal or translated | Everyday | Note | Confidence |
|:-|:-|:-|:-|
| Yeni koleksiyonumuz sizlerle buluşmaktadır | Yeni sezon geldi | drop -mAktAdIr | native source |
| Mağazamız hizmet vermektedir | Açığız | spoken present | native source |
| Mağazamız Kadıköy'dedir | Mağaza Kadıköy'de | drop the extra -DIr | native source |
| Sizin için özel olarak hazırladık | Size özel hazırladık / Sana özel | one pronoun at most | native source |
| Siparişini ver ve arkana yaslan | Siparişini verip arkana yaslan | -Ip instead of ve | native source |
| Bir kahve, güne başlamanın bir yoludur | Kahve, güne başlamanın yolu | no English-style "bir" | native source |
| Yeni lezzeti deneyimleyin | Yeni lezzetin tadına bakın / Deneyin | TDK marks deneyimlemek as intransitive | native source |
| Güçlü bir bataryaya sahip | Bataryası güçlü / Güçlü bataryalı | TDK: sahip olmak means to own or hold | single source + inference |
| Şeflerimiz tarafından hazırlanan | Şeflerimizin hazırladığı | genitive and active verb | inference |
| Basitçe en iyisi | Düpedüz en iyisi | ÇEVBİR solutions bank | native source |
| Hayır, teşekkürler | Kalsın / Gerek yok | ÇEVBİR solutions bank | native source |
| Daha fazla bilgi için tıklayınız | Detaylar linkte | one real CTA | inference |
| Etkinlik cumartesi gerçekleştirilecektir | Cumartesi buradayız | no gerçekleştirmek | inference |
| Kampanya belirtilen tarihler arasında geçerlidir | Pazar gecesine kadar geçerli | name the day | inference |
| Değerli müşterilerimiz, ... | start with the news | no greeting opener | inference |

#### AI and translation tells

| Tell | Robotic example | Natural fix | Evidence | Confidence |
|:-|:-|:-|:-|:-|
| -mAktAdIr tense | Ürünlerimiz tüm mağazalarda satılmaktadır | Tüm mağazalarda var | Savaş Kılıç (ÇEVBİR); Doğal Metin's sample AI text uses -mAktAdIr throughout | several sources |
| Stock phrases from reports | Kahve, hayatımızda önemli bir rol oynamaktadır | Sabah kahven 3 dakikada hazır | Marketing Türkiye (İrem Alimoğlu, Dec 2025) lists "Bu durum, X'i beraberinde getiriyor" and similar phrases; Doğal Metin's sample uses önemli bir rol oynamaktadır | several sources |
| Günümüzde opener | Günümüzde herkes hız istiyor | 15 dakikada kapında | Marketing Türkiye | native source |
| sadece X değil, aynı zamanda Y | Bu sadece bir ayakkabı değil, bir yaşam tarzı | Taban yumuşak, bütün gün rahat | Turkish form of a generic tell | inference |
| bir X'ten fazlası | Bir kahveden çok daha fazlası | Kahve, yanında taze kurabiye | Turkish form of a generic tell | inference |
| deneyimleyin | Yeni kokuyu deneyimleyin | Mağazada kokla, beğenirsen al | TDK marks the verb intransitive | native source |
| sahip olun | Hayalinizdeki saçlara sahip olun | Saçın ilk yıkamada yumuşasın | TDK; inference | single source |
| Too many pronouns | Sizin için seçtiğimiz ürünleri size sunuyoruz | Size özel seçtik | Savaş Kılıç (ÇEVBİR) | native source |
| Sentence starting with Ve | Ve indirim başladı | Üstelik indirim de var | Tuncay Birkan (ÇEVBİR) | native source |
| Unneeded bir | Harika bir fiyata bir kalite | Hem ucuz hem sağlam | ÇEVBİR note on articles | native source |
| Word-for-word adverbs | Doğal olarak, en iyisini seçtik | Haliyle en iyisini seçtik | ÇEVBİR solutions bank | native source |
| "Next level" and "dive in" calques | Tarzınızı bir üst seviyeye taşıyın, yaz dünyasına dalın | say the change: Keten gömlek, 599 TL | none found | inference |
| yolculuk as a metaphor | Bir lezzet yolculuğuna çıkın | Antep usulü lahmacun, 20 dakikada kapında | none found | inference |
| Plaza verbs | Siparişinizi confirm edin | Siparişini onayla | Vikipedi, Plaza dili | single source |
| Even, overly smooth rhythm | every sentence the same length, balanced paragraphs | vary length; one short line | Marketing Türkiye; Habere Güven (translated from The Conversation, Sep 2026) | several sources |

#### Purple or poetic phrasing

1. Damaklarda iz bırakan lezzet. Fix: Közde pişen Adana, 320 TL.
2. Ruhunuzu besleyen bir atmosfer. Fix: Bahçede 40 kişilik yer, cuma 21.00'de canlı müzik.
3. Zamansız şıklık. Fix: Klasik kesim, %100 yün.
4. Tutkuyla harmanlanmış kahve. Fix: Etiyopya ve Brezilya çekirdeği, orta kavrum.
5. Eşsiz bir lezzet yolculuğu. Fix: name the dish and the area, for example Kadıköy'de İskender, 20 dakikada kapında.
6. Sihirli bir dokunuş. Fix: name the feature, for example 10 dakikada kuruyan oje.

#### Natural vs robotic lines

Natural:

1. Hafta sonu kahvaltısı 15 dakikada kapında, simit ve çay 49,90 TL 🥯
2. Sepette %30 indirim başladı, pazar gecesi 23.59'a kadar geçerli
3. Lahmacun mu çekti canın? Kadıköy şubesinden 20 dakikada kapına gelsin
4. Kanka bu cuma 2 kahve alana 1 cookie bizden, Moda şubesinde saat 18.00'e kadar

Robotic, each with a fix:

1. Değerli müşterilerimiz, yeni koleksiyonumuz sizlerle buluşmaktadır
   Fix: Yeni sezon geldi, ilk 3 gün sepette %20 indirim
2. Günümüzün hızla değişen dünyasında kahve, hayatımızda önemli bir rol oynamaktadır
   Fix: Kahven sabah 8'de hazır, uygulamadan sipariş ver, sıra bekleme
3. Uzman şeflerimiz tarafından hazırlanan menümüzle bir lezzet yolculuğuna çıkın
   Fix: Şeflerimizin yeni menüsü bu akşam Nişantaşı'nda, kişi başı 850 TL
4. Yaz koleksiyonumuzu deneyimleyin ve tarzınızı keşfedin
   Fix: Yaz koleksiyonu mağazalarda, keten gömlekler 599 TL

#### Sources

- Bir Metnin Yapay Zeka Tarafından Yazıldığı Nasıl Anlaşılır? (İrem Alimoğlu, 21 Dec 2025), Marketing Türkiye, https://www.marketingturkiye.com.tr/haberler/yazinin-yeni-suphesi-bu-metni-kim-yazdi/ (read 2026-09-24, read)
- +DIr: Her Zaman Gerekli Midir? (Savaş Kılıç), ÇEVBİR Türkçe Notları, https://cevbir.org.tr/turkce-notlari/dir-her-zaman-gerekli-midir/ (read 2026-09-24, read)
- O / Onlar: O ve Onlar Zamirlerinin Yanlış Kullanımı ve Zamir Düşürme, Kendi Zamiri (Savaş Kılıç), ÇEVBİR Türkçe Notları, https://cevbir.org.tr/turkce-notlari/o-onlar-o-ve-onlar-zamirlerinin-yanlis-kullanimi-ve-zamir-dusurme-kendi-zamiri/ (read 2026-09-24, read)
- AND/UND/ET = VE Denklemi Yanlıştır (Tuncay Birkan), ÇEVBİR Türkçe Notları, https://cevbir.org.tr/turkce-notlari/andundet-ve-denklemi-yanlistir/ (read 2026-09-24, read)
- Türkçede Artikelin (Tanımlık, Harfitarif) Bulunmayışı, ÇEVBİR Türkçe Notları, https://cevbir.org.tr/turkce-notlari/turkcede-artikelin-tanimlik-harfitarif-bulunmayisi (read 2026-09-24, read)
- Has Türkçe / Güzel Çözümler Bankası (PDF), ÇEVBİR, https://cevbir.org.tr/hasturkce (read 2026-09-24, read)
- Güncel Türkçe Sözlük entries deneyimlemek, sahip olmak, kanka, moruk, valla, TDK, https://sozluk.gov.tr/gts?ara=deneyimlemek (same endpoint for each word) (read 2026-09-24, read)
- Plaza dili, Vikipedi, https://tr.wikipedia.org/wiki/Plaza_dili (read 2026-09-24, read)
- Yapay Zeka Metin İnsanlaştırıcı (sample AI text), Doğal Metin, https://dogalmetin.com.tr/yapay-zeka-metin-insanlastirici (read 2026-09-24, read)
- Markayı kendisi değil müşteri anlatıyor (Salih Keskin, 1 Aug 2025), İstanbul Ticaret Gazetesi, https://istanbulticaretgazetesi.com/yazarlar/salih-keskin/markayi-kendisi-degil-musteri-anlatiyor (read 2026-09-24, read)
- Sektöre göre sosyal medya dili nasıl olmalı? (Mutlu Çavuş, 2017), BT Günlüğü, https://www.btgunlugu.com/sosyal-medya-dili-nasil-olmali/ (read 2026-09-24, read)
- Yapay zekâ tarafından yazılan metinleri anlamak mümkün mü? (translated from The Conversation, 1 Sep 2026), Habere Güven, https://www.habereguven.com/yapay-zeka-tarafindan-yazilan-metinleri-anlamak-mumkun-mu (read 2026-09-24, read)

#### Could not verify

- Ekşi Sözlük sits behind a bot check and was not read.
- Trendyol, Getir, Yemeksepeti and Hepsiburada pages returned empty, so brand wording (the sepette labels) is inference.
- No native source for tarafından, yolculuk, bir üst seviyeye or the essay connectors (bununla birlikte, sonuç olarak); they are inference.

### 4.14 Filipino and Taglish (tl)

#### Register guide

- Taglish is the normal written register online. Tagalog Wikipedia calls it common on the Internet, especially among the young; English Wikipedia calls it the normal acceptable style of speaking and writing in informal settings. All-Tagalog copy reads like a school text or a translation. Several sources.
- English verbs and nouns take Tagalog affixes with a hyphen: mag-order, i-download, na-deliver, paki-share, magpa-deliver, nag-shopping, ma-save (Microsoft Filipino guide; Wikipedia Filipino orthography gives pa-cute and ipa-cremate). A few that sound Tagalog drop it (magmonitor), but the guide's i-ban versus iban shows why the hyphen matters. Several sources.
- Particles carry the tone: na, pa, lang, naman, talaga, ba, din or rin, nga, kasi, eh, po or opo (Wikipedia Tagalog grammar lists them). Everyday hooks: Order na!, Tara na!, Sulit!, Grabe!, G ka ba?, Kita-kits!, and prices as "₱99 lang" (inference). Single source plus inference.
- Address: ka and mo in ads and app copy; the Microsoft guide says "ka, iyo (do not use formal 'kayo' or 'inyo')". Po and opo mark respect (Ling) and belong in customer-service replies and in copy for older readers. Community names such as mga Kapuso or mga ka-[brand] are native (inference). Single source plus inference.
- Current slang (Ling, updated 2026): charot or char, keri, bes or beshie, jowa, chika, forda, dasurv, eme, sheesh, mid. Lodi, petmalu and werpa peaked around 2017 and now read dated (inference). Single source plus inference.
- The formal written order uses ay (Ang aming kape ay ...); everyday Tagalog puts the predicate first (Wikipedia Tagalog grammar: subject-first order in formal contexts). Single source.
- Conjunctions: pero, para, dahil or kasi, ayon sa. The old forms ngunit, subalit, datapwat, upang, sapagkat and alinsunod sa read formal (Microsoft Filipino guide). Single source.
- Purist coinages (salumpuwit, salipawpaw, sipnayan, dagitab), the kind of word the 1960s purist movement made to replace loanwords, read as jokes to most readers (inference); never reach for them to avoid English (Wikipedia Filipino language on 1960s purism; Ling lists salumpuwit, dagitab and aklat-palaan against silya, kuryente, library). Several sources for the words, inference for the reaction.
- Market: national brands write Tagalog-based Taglish; Cebu and Davao audiences may prefer Bisaya or English (inference). Coño English (heavy English with Tagalog glue) is a recognised variant and reads as parody unless the persona is built on it (Wikipedia Taglish).

#### Formal to everyday swaps

| formal | everyday | note | confidence |
|:-|:-|:-|:-|
| ngunit, subalit, datapwat | pero | Microsoft Filipino guide | single source |
| upang | para | Microsoft guide | single source |
| sapagkat | dahil, kasi | Microsoft gives dahil | single source plus inference |
| alinsunod sa | ayon sa | Microsoft guide | single source |
| makipag-ugnayan | kontakin, i-message | Microsoft: kontakin for informal effect | single source |
| nakararanas ng mga problema | nagkakaproblema | Microsoft guide | single source |
| hindi ka pinahihintulutang | hindi ka puwedeng | Microsoft guide | single source |
| sa pamamagitan ng paggamit ng telepono | gamit ang telepono | Microsoft guide | single source |
| maaaring gumugol ng mahabang oras | baka matagalan | Microsoft guide | single source |
| lamang | lang | Wikipedia Tagalog grammar: lang is the contraction | single source |
| kayo, inyo (to one reader) | ka, mo, iyo | keep po in service replies | single source |
| ipaunawa, ipaliwanag | i-explain | Wikipedia Taglish, en and tl | several sources |
| magmamaneho | magda-drive | Wikipedia Taglish | several sources |
| takdang-aralin, pamilihan | homework, mall | Wikipedia Taglish | several sources |
| mangyaring | paki-, or drop it | machine-translation style please | inference |

#### AI and translation tells

| tell | robotic example | natural fix | evidence | confidence |
|:-|:-|:-|:-|:-|
| Deep verbs for discover and explore | Tuklasin ang aming bagong koleksyon. | Bagong collection na, i-check sa app! | none found | inference |
| Experience calque | Maranasan ang pinakamasarap na burger sa bayan. | Crispy pa rin kahit i-deliver, ₱99 lang. | none found | inference |
| Journey metaphor | Simulan ang iyong paglalakbay tungo sa kalusugan. | Simulan sa 7 araw na trial, libre ang unang linggo. | none found | inference |
| hindi lamang ... kundi pati na rin | Hindi lamang masarap kundi pati na rin abot-kaya. | Masarap na, sulit pa! | none found; casual hindi lang ... pa is native | inference |
| Fast-world opener | Sa mabilis na mundo ngayon, kailangan mo ng mabilis na serbisyo. | Busy? Ready-to-eat na ang ulam, ₱89 lang. | none found | inference |
| mangyaring as please | Mangyaring bisitahin ang aming website. | I-check ang website namin. | Microsoft guide on unnecessary formality | inference |
| Old conjunctions | Mura ngunit matibay, upang tumagal. | Mura pero matibay, tatagal talaga. | Microsoft Filipino guide | single source |
| Formal verb phrases | Maaari mong pakinggan ang mensahe sa pamamagitan ng paggamit ng telepono. | Mapapakinggan mo ang mensahe gamit ang telepono. | Microsoft guide's own before and after | single source |
| ay inversion | Ang aming tindahan ay bukas na. | Bukas na ang store namin! | Wikipedia Tagalog grammar | single source |
| All-Tagalog where Taglish uses English | Magmamaneho ka ba papunta sa pamilihan? | Magda-drive ka ba papuntang mall? | Wikipedia Taglish | several sources |
| Formal kayo and inyo to one reader | Maaari ninyong i-download ang app. | I-download mo na ang app. | Microsoft Filipino guide | single source |
| Missing hyphen | Magorder na! | Mag-order na! | Microsoft Filipino guide, Wikipedia Filipino orthography | several sources |
| Purist coinage | Bagong salumpuwit, 20% off! | Bagong upuan, 20% off! | Ling, Wikipedia Filipino language | several sources |
| Calqued stock lines | Huwag mag-atubiling makipag-ugnayan sa amin. | May tanong? I-message lang kami. | none found | inference |
| Chatbot leftovers | Narito ang ilang caption para sa inyong promo. | delete it | none found | inference |

#### Purple or poetic phrasing

1. "Isang paglalakbay ng lasa na magdadala sa iyo sa langit." Fix: "Crispy sa labas, juicy sa loob, ₱99."
2. "Ang perpektong pagsasanib ng tradisyon at modernong istilo." Fix, name both: "Barong na piña, slim fit na."
3. "Hayaang maghari ang saya sa bawat kagat." Fix: "Extra cheese na, walang dagdag bayad."
4. "Tuklasin ang hiwaga ng bagong lasa." Fix: "Ube cheese ang bagong flavor, ₱65 lang."
5. "Damhin ang tamis ng bawat sandali." Fix: "Leche flan na hindi masyadong matamis, ₱120 isang llanera."

#### Natural vs robotic lines

Natural:
1. Order na! Fried chicken bucket na may 6 pcs, ₱499 lang ngayong weekend sa lahat ng branches sa Metro Manila.
2. Sulit 'to! 20GB data for 7 days, ₱99 lang. I-register mo lang sa app, active agad.
3. Tara na sa Glorietta ngayong Sabado, 50% off ang sneakers mula 10AM. Kita-kits!
4. Uwian na? Dumaan ka muna, mainit pa ang pandesal hanggang 8PM, ₱5 isa.

Robotic, each with a fix:
1. Tuklasin ang aming bagong koleksyon at galugarin ang mundo ng istilo. Alamin pa sa aming website.
   Fix: Bagong collection na! 30 designs, ₱399 pataas, i-check sa app.
2. Ang aming kape ay hindi lamang inumin kundi pati na rin isang karanasan.
   Fix: Barako mula Batangas, ₱120 ang 250g. Pang-almusal talaga.
3. Sa mabilis na mundo ngayon, mangyaring bisitahin ang aming website upang malaman ang higit pa.
   Fix: Busy? I-order mo na online, darating sa loob ng 2 oras.
4. Mahal naming mga customer, huwag mag-atubiling makipag-ugnayan sa amin para sa inyong mga katanungan.
   Fix: May tanong? I-message kami dito, sasagot kami hanggang 10PM.

#### Hypotheses: verdicts

- Confirmed with sources: formal conjunctions (ngunit, subalit, upang, sapagkat), hyphenated English verbs, ka and mo over kayo and inyo for one reader, purist coinages as a register error, Taglish as the online norm.
- Refined: the casual "Hindi lang masarap, sulit pa!" is native Taglish, so only the textbook hindi lamang ... kundi pati na rin is linted; paglalakbay is linted only as a metaphor, since airline thank-yous use it literally; damhin is a note, because travel and Christmas ads use it natively.
- Not verified: tuklasin, galugarin, maranasan, sa mabilis na mundo ngayon and mangyaring as machine-translation output (no Filipino article or r/Tagalog thread was reachable); kept as inference.

#### Sources

- Taglish, Wikipedia (English), https://en.wikipedia.org/wiki/Taglish (read 2026-09-24, read)
- Taglish, Wikipedia (Tagalog), https://tl.wikipedia.org/wiki/Taglish (read 2026-09-24, read)
- Filipino orthography, Wikipedia, https://en.wikipedia.org/wiki/Filipino_orthography (read 2026-09-24, read)
- Filipino language, Wikipedia, https://en.wikipedia.org/wiki/Filipino_language (read 2026-09-24, read)
- Tagalog grammar, Wikipedia, https://en.wikipedia.org/wiki/Tagalog_grammar (read 2026-09-24, read)
- Swardspeak, Wikipedia, https://en.wikipedia.org/wiki/Swardspeak (read 2026-09-24, read)
- Microsoft Filipino Style Guide, Microsoft, https://aka.ms/filipino-styleguide (read 2026-09-24, read)
- Tagalog slang words, Ling, https://ling-app.com/blog/tagalog-slang-words/ (read 2026-09-24, read)
- Tagalog vs Filipino, Ling, https://ling-app.com/blog/tagalog-vs-filipino/ (read 2026-09-24, read)

### 4.15 Vietnamese (vi)

#### Register guide

- Particles carry the warmth, one per sentence: nha (Central and Southern), nhé (chiefly Northern, standard in writing, can feel cutesy to Southerners), nè (Southern, look here), plus đó, thôi, á for emphasis. Shops add ạ when answering a customer (inference). Source: Wiktionary entries. Confidence: single source.
- Address: bạn is the everyday term among young people and quý khách the elevating one (Wikipedia, Pronouns in Vietnamese); mọi người or cả nhà for the audience. Brand self reference: mình, tụi mình, nhà mình or the brand name. Wikipedia calls singular mình intimate, but on fan pages and shops it is the default friendly voice (inference; the source disagrees). Segment words (inference): nàng for women's fashion, chị em for beauty and home, anh em or ae for gaming and football, khách iu for cute retail. Avoid chúng tôi in casual posts.
- English mixing: English words slot in unchanged, since Vietnamese has no inflection: order, ship, freeship, sale, deal, combo, size, review, feedback, check in, ib (inbox). Wiktionary records freeship as a Vietnamese neologism, quoted from a 2021 Vietnamese Facebook marketing book; Microsoft's guide keeps familiar English words and uses "online" in UI text. The calques to avoid are in grammar (passives, possessive chains), not in the loanwords. Confidence: several sources.
- E-commerce words (inference except freeship): chốt đơn, săn sale, mã giảm giá, flash sale, hàng mới về, còn size, giá hạt dẻ, ib shop.
- Gen Z slang, sparingly and matched to the audience: xịn xò (colloquial, fancy), u là trời (Internet slang, oh my god), khum and hông for không, đỉnh, chill, rén (scared), 8386 (a wish for luck). Sources: Wiktionary and Vietcetera's slang explainers. Slay and keo as current slang: not verified.
- Teencode (ko, đc, bt) belongs in comments and DMs, not on banners; the Vietnamese Wikipedia teencode article cites linguist Phạm Văn Tình saying heavy use erodes standard Vietnamese. Vietcetera traces không through ko, hok, k, hông and khum. Since k also means nghìn in prices (29k), never write k for không near a price.
- Sentence shape: short clauses joined by commas, price and deadline early, a particle at the end, a question tag (chưa?, hông?, nè?) instead of a formal CTA (inference).
- Formal register: Sino-Vietnamese and administrative words (thực hiện, tiến hành, sử dụng, nhằm, quý khách, vui lòng, kính gửi) belong to notices. Microsoft's Vietnamese guide asks for the language of everyday conversation and lists modern swaps (Không tải được, Xin chờ, theo cách sau). The translator and linguist Cao Xuân Hạo complained in 2003 that translators render too literally and never reread the Vietnamese, which still describes MT output. Confidence: several sources.
- Regions (inference): North vs South, nhé vs nha, không vs hông, cốc vs ly, bát vs chén. For a national brand, nha and nhé both read fine in writing.
- Emoji (inference): 🔥, 😍, 🥰, ⚡ for flash sales, 🎁; hearts are common; stay inside the skill's limits.

#### Numbers, prices and dates for designers

- Thousands take a period and decimals a comma: 1.526 and 5,25 (Microsoft Vietnamese guide). Prices: 99.000đ or 99.000 ₫ in formal layouts; the sign is ₫, informally đ, code VND (Wikipedia). Social shorthand 99k (inference, very common). Never 99,000đ.
- Larger prices: 1.299.000đ; casual posts also write 1tr3 or 1,3 triệu (inference).
- Dates put the day first: 9/1/2021 is 9 January; dd/mm/yyyy, d-m-yyyy or 9 tháng 1 năm 2021 (Wikipedia). Double dates such as 9.9, 11.11 and 12.12 are sale campaign names (inference).
- Time is 24-hour in writing: 13h15 or 13:15, whole hours as 6h (Wikipedia); casual copy says 8 giờ tối or 12h đêm. Avoid AM and PM.

#### Formal to everyday swaps

| formal | everyday | note | confidence |
|:-|:-|:-|:-|
| Kính gửi Quý khách, | (drop it and open with the news) | letter and notice opener | inference |
| Quý khách | bạn, mọi người, cả nhà, nàng | keep quý khách for banks and airlines | single source (Wikipedia pronouns) plus inference |
| chúng tôi, của chúng tôi | mình, tụi mình, nhà mình, the brand name | | inference |
| Vui lòng liên hệ | Nhắn shop nha, ib shop | | inference |
| Vui lòng đợi | Xin chờ, chờ xíu nha | Microsoft lists Xin chờ as the modern form | single source (Microsoft) |
| Tải về không thành công | Không tải được | | single source (Microsoft) |
| theo các bước sau đây | theo cách sau | | single source (Microsoft) |
| Bởi vì ... được hình thành ... được mã hóa | Nhờ ... | Microsoft's old vs new conjunction example | single source (Microsoft) |
| sử dụng | dùng | | inference |
| thực hiện, tiến hành | làm | | inference |
| miễn phí vận chuyển | freeship | | single source (Wiktionary) |
| đặt hàng | chốt đơn, order | | inference |
| nhằm (mục đích) | để | | inference |
| tuy nhiên, do đó | nhưng, nên | | inference |
| trong thời gian sớm nhất | liền, trong ngày | | inference |

#### AI and translation tells

Brands Vietnam's help desk tested ChatGPT and Gemini and names the typical opener as "Trong bối cảnh ngành [XYZ] đang phát triển không ngừng…" (Brands Vietnam, 2025). Brands Vietnam and Việt Giải Trí also report the long dash as a recognised AI sign among Vietnamese readers, which supports the existing global rule (not a new finding).

| tell | robotic example | natural fix | evidence | confidence |
|:-|:-|:-|:-|:-|
| Context opener | Trong bối cảnh ngành F&B đang phát triển không ngừng, ... | Cà phê muối về lại menu, 29k tới 14h. | Brands Vietnam | native source |
| không chỉ là ... mà còn là | Đây không chỉ là ly cà phê mà còn là phong cách sống. | Cà phê phin rang mộc, ly lớn 25k. | Brands Vietnam; Wikipedia Signs of AI writing | native source |
| Essay connectors and summaries | Hơn nữa, ... Thêm vào đó, ... Tóm lại, ... | one idea per line, no connectors | Brands Vietnam | native source |
| Chatbot list opener and leftovers | Dưới đây là một số gợi ý caption cho quán của bạn | delete | Brands Vietnam (prompts left in text) | native source |
| Passive được ... bởi | Được yêu thích bởi hàng triệu khách hàng | Hơn 1 triệu khách đã mua lại | TEX lists bởi among ChatGPT's overused words; Microsoft rewrites a được-heavy sentence with Nhờ | several sources |
| điều này, việc này fillers | Điều này giúp bạn tiết kiệm thời gian. | Vậy là khỏi chờ. | TEX | single source |
| Relative clause with nơi | Ghé quán, nơi bạn có thể thư giãn sau giờ làm. | Tan làm ghé quán ngồi chill nha, mở tới 23h. | TEX (nơi) | single source |
| một cách plus adjective | Giao hàng một cách nhanh chóng | Giao trong 2h nội thành | none found | inference |
| của bạn in every clause | Nâng cấp làn da của bạn với bí quyết của bạn | Da khô cỡ nào cũng mướt sau 7 ngày | none found | inference |
| Word for word strings | Lưu hình ảnh thất bại | Không lưu được hình ảnh | Microsoft Vietnamese guide | single source |
| Hollow terms and calqued idioms | tạo giá trị, đồng bộ hoá mục tiêu, bước tiến đúng hướng, phần nổi của tảng băng chìm | a concrete benefit with a number | Brands Vietnam; TEX | several sources |
| Journey and immersion metaphors | hành trình vị giác, đắm chìm, khám phá thế giới thời trang | name the flavour, the place, the price | none found | inference |
| English number, time and date formats | 99,000đ, 8:00 PM, 09/30/2026 | 99.000đ, 20h, 30/9/2026 | Microsoft; Wikipedia date notation; Wikipedia đồng | several sources |
| Translated corporate lines | Sự hài lòng của quý khách là ưu tiên hàng đầu của chúng tôi | Không ưng thì đổi trong 7 ngày | none found | inference |

Careful: trải nghiệm, khám phá ngay, nâng tầm, đồng hành cùng bạn and Đừng bỏ lỡ are also everyday human Vietnamese marketing, so the lint only flags narrow shapes of them or keeps them at note level.

#### Purple or poetic phrasing

All my own examples (inference).

- bản giao hưởng hương vị (a symphony of flavour). Fix: name them, bơ, sữa, chút muối biển.
- đánh thức mọi giác quan (awakens every sense). Fix: thơm bơ, giòn rụm, ăn nóng ngon nhất.
- chạm đến trái tim (touches the heart). Fix: gói quà miễn phí, ghi thiệp tay.
- tinh hoa hội tụ (the quintessence gathers). Fix: làm từ cà phê Cầu Đất, rang mỗi tuần.
- nơi cảm xúc thăng hoa (where feelings soar). Fix: mở tới 23h, acoustic tối thứ 7.
- tận hưởng từng khoảnh khắc (savour every moment). Fix: ngồi bao lâu cũng được, wifi mạnh.

#### Natural vs robotic lines

Natural:

1. Trưa nay ghé quán làm ly cà phê muối nha, giảm còn 29k tới 14h thôi đó!
2. Chốt đơn trước 12h đêm nay là freeship toàn quốc nhé mọi người.
3. Áo khoác dù mới về đủ size S tới XL, giá 189k, nàng nào ưng thì ib shop liền nha.
4. Sale 9.9 nè! Nhập mã GIAM50 giảm 50k cho đơn từ 299k, hạn tới hết ngày 9/9.

Robotic, each with its fix:

1. Sản phẩm được thiết kế bởi đội ngũ chuyên gia hàng đầu của chúng tôi.
   Fix: Mẫu này do team nhà mình vẽ tay, chỉ làm 200 cái thôi.
2. Đây không chỉ là một ly trà sữa, mà còn là một hành trình vị giác khó quên.
   Fix: Trà sữa oolong nướng mới ra, size M 39k, uống thử là ghiền.
3. Kính gửi Quý khách, combo chỉ còn 99,000đ đến 8:00 PM ngày 09/30/2026.
   Fix: Combo chỉ còn 99.000đ tới 20h ngày 30/9 thôi nha mọi người.
4. Hơn nữa, sự hài lòng của quý khách luôn là ưu tiên hàng đầu của chúng tôi.
   Fix: Không ưng thì đổi size trong 7 ngày, shop lo phí ship.

#### Sources

- Dấu hiệu nhận biết nội dung được viết bởi AI (2025-09-23), Brands Vietnam Help Desk, https://help.brandsvietnam.com/vi/article/dau-hieu-nhan-biet-noi-dung-duoc-viet-boi-ai-3zy07d/ (read 2026-09-24, read)
- Làm thế nào để nhận diện nội dung do AI viết? Mức độ tin cậy đến đâu?, TEX Việt Nam, https://tex.vn/ai-infor/lam-the-nao-de-nhan-dien-noi-dung-do-ai-viet-muc-do-tin-cay-den-dau-1021 (read 2026-09-24, read)
- ChatGPT cập nhật tính năng mới để tránh dấu hiệu nhận diện AI (2025-11-16), Việt Giải Trí, https://vietgiaitri.com/chatgpt-cap-nhat-tinh-nang-moi-de-tranh-dau-hieu-nhan-dien-ai-20251116i7576453 (read 2026-09-24, read)
- Vietnamese Localization Style Guide (PDF vie-vnm-StyleGuide.pdf), Microsoft, https://aka.ms/vietnamese-styleguide (read 2026-09-24, read)
- Dịch giả Cao Xuân Hạo: Tiếng Việt đang lâm nạn (2003), Tuổi Trẻ, https://tuoitre.vn/dich-gia-cao-xuan-hao-tieng-viet-dang-lam-nan-7322.htm (read 2026-09-24, read)
- Teencode, Wikipedia tiếng Việt, https://vi.wikipedia.org/wiki/Teencode (read 2026-09-24, read)
- Pronouns in Vietnamese, Wikipedia, https://en.wikipedia.org/wiki/Vietnamese_pronouns (read 2026-09-24, read)
- Vietnamese đồng, Wikipedia, https://en.wikipedia.org/wiki/Vietnamese_%C4%91%E1%BB%93ng (read 2026-09-24, read)
- Date and time notation in Vietnam, Wikipedia, https://en.wikipedia.org/wiki/Date_and_time_notation_in_Vietnam (read 2026-09-24, read)
- Signs of AI writing, Wikipedia, https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing (read 2026-09-24, read)
- nha, nhé, nè, hông, khum, xịn xò, u là trời, freeship, Wiktionary, https://en.wiktionary.org/wiki/nha (and the matching entry pages) (read 2026-09-24, read)
- Khum: Từ chối nhẹ nhàng thôi (Đông Hà), Vietcetera, https://vietcetera.com/vn/khum-tu-choi-nhe-nhang-thoi (read 2026-09-24, read)
- Chữ Với Nghĩa slang explainer series (titles only), Vietcetera, https://vietcetera.com/vn/bo-suu-tap/chu-voi-nghia (read 2026-09-24, read)
- ChatGPT xóa dấu vết AI, Znews, https://znews.vn/chatgpt-xoa-dau-vet-ai-post1603036.html (read 2026-09-24, snippet; fetch returned 404)
- Cách nhận biết bài viết có được viết bởi ChatGPT hay không?, SCTT, https://sctt.net.vn/cach-nhan-biet-bai-viet-co-duoc-viet-boi-chatgpt-hay-khong/ (read 2026-09-24, snippet; fetch returned 404)

#### Could not verify

- No real brand posts were read (Shopee VN, Highlands Coffee, Vinamilk, Grab VN, MoMo, The Coffee House, Viettel, Tiki).
- chốt đơn, săn sale, khách iu, nàng, keo and slay as slang; ạ in shop replies; một cách and của bạn as AI tells; the Northern and Southern word pairs.

### 4.16 Thai (th)

#### Register guide

- **Voice and particles.** Brand pages talk like a person, often as "แอด" or "แอดมิน", with one fixed particle set: ค่ะ, คะ and นะคะ for a female persona, or ครับ and นะครับ for a male one. Neutral pages lean on นะ, จ้า, น้า and เลย. Particles belong to spoken Thai and are not used in elegant written Thai, which is why a caption without any sounds like a notice. Do not put a particle on every sentence, and never mix ค่ะ and ครับ in one caption. Confidence: several sources (particles and register); inference (the admin persona, the mixing tell).
- **Casual markers.** นะ softens a request; จ้า and จ้ะ are friendly; สิ can sound bossy; เลย urges (สั่งเลย, ทักแชทได้เลย); มั้ย or ไหม for questions; ปะ is very casual. Stretched endings (ค่าาา, น้าาา) add warmth (inference). 555 is laughter, because ห้า sounds like "ha". Emoji usually go at the end of a line. Confidence: single source (555, particle meanings); inference (the rest).
- **Stable commerce words.** โปร, ส่งฟรี, ลดราคา, ของมันต้องมี, ป้ายยา, ตำ (buy it), จัดไป, ทักแชท, กดสั่ง, ปัง, ฟิน, เกินต้าน, ฉ่ำ. Confidence: inference.
- **Slang with an expiry date.** ตะโกน as an intensifier peaked around 2022 to 2023. มงลง, ต๊าช and จึ้ง are pageant and fandom slang from about 2019 to 2022. ตัวมารดา and ตัวแม่ peaked around 2023 to 2024, and ปังปุริเย่ is 2010s and dated. Use these only in a meme-led voice. I found no dated native source; English Wiktionary lists no slang sense for ตะโกน. Confidence: inference, so check with a native reviewer.
- **Address.** Mostly omit คุณ. Address groups instead: ลูกค้าทุกคน, ทุกคน, เพื่อน ๆ, ใครที่..., สายหวาน or สายคาเฟ่. คุณ is fine now and then (เพื่อคุณ), but ของคุณ in every clause mirrors English "your". ท่าน belongs to formal notices. Thai Wikipedia's style guide also tells writers not to address the reader as คุณ. Confidence: single source plus inference.
- **Code-mixing.** Write English loans in Thai script (โปร, เซล, ช้อป, รีวิว, ไลฟ์, โค้ด, ไซซ์, ออเดอร์). Use Latin for brand and place names, sizes, promo codes, SALE stickers and double-date sales (11.11). Pick one form per word and keep it: a Thai-built humanizer flags random switching between transliteration and English as an AI habit. Confidence: single source plus inference.
- **Spacing and punctuation.** Thai puts no spaces between words; a space marks a phrase or sentence break, so a Thai sentence does not end with a full stop. Lists are separated by spaces, and commas appear only when items contain spaces. There is no comma between place names (กรุงเทพมหานคร ประเทศไทย). Put spaces around numbers (ราคา 500 บาท). Formal style spaces ไม้ยมก (ดี ๆ), while social posts often write ดีๆ. ! and ? are normal on social, although the encyclopedia style avoids ?. Confidence: several sources.
- **Money and numbers.** Use Arabic numerals, with a comma every three digits except in years (1,290 บาท, พ.ศ. 2569). Write prices as 99 บาท, as ฿99 with no space when space is tight, or as the retail tag 99.- ; บ. is the short form. Use 50% on social and ร้อยละ in formal text. Confidence: several sources (numerals, commas, ฿, บ.); inference (99.-).
- **Dates and time.** Buddhist Era = CE + 543, so 2026 is พ.ศ. 2569. Short dates such as 24 ก.ย. 69 and month abbreviations ม.ค. to ธ.ค. are everyday forms. Never write ปี and พ.ศ. together. Write time as 10:00 น. (style guide); 10.00 น. is common in notices. Confidence: several sources (the BE offset, the ปี rule, the colon style); inference (short forms, the dot style).

#### Formal to everyday swaps

| Formal | Everyday | Note | Confidence |
|:-|:-|:-|:-|
| รับประทาน | กิน / ทาน | formal and polite vs common verb | several sources |
| ถูกออกแบบมาเพื่อ | ทำมาเพื่อ / ออกแบบให้ | neutral ถูก passive began as an Anglicism | several sources |
| มีความสามารถในการกันน้ำ | กันน้ำได้ | ความ and การ chain | single source |
| ณ ขณะนี้ / ในเวลานี้ | ตอนนี้ | bookish time words | single source |
| เนื่องด้วยข้อเท็จจริงที่ว่า / เนื่องจาก | เพราะ | wordy connector | single source |
| ในกรณีที่ | ถ้า | wordy conditional | single source |
| เป็นจำนวนมาก | เยอะ / เพียบ | bookish quantity | single source |
| ประสบการณ์ที่ราบรื่น | ใช้ง่าย ลื่น ไม่สะดุด | translated abstraction | single source |
| ลูกค้าผู้มีอุปการคุณ | ลูกค้าทุกคน / ทุกคน | letter salutation | single source |
| ท่าน | (omit) / ลูกค้า | formal pronoun | inference |
| ทางร้านขอแจ้งให้ทราบว่า | แจ้งนะคะ / บอกก่อนนะ | notice opener | inference |
| ดำเนินการสั่งซื้อ | กดสั่งได้เลย | officialese verb | inference |
| จัดส่งโดยไม่มีค่าใช้จ่าย | ส่งฟรี | officialese phrase | inference |
| ผลิตภัณฑ์ | สินค้า / ของ / the product name | formal noun | inference |
| กรุณาติดต่อ | ทักแชทมาได้เลย | request tone | inference |

#### AI and translation tells

| Tell | Robotic example | Natural fix | Evidence | Confidence |
|:-|:-|:-|:-|:-|
| ถูก passive for good news | สินค้านี้ถูกคัดสรรมาอย่างพิถีพิถัน | ร้านคัดมาเองทุกล็อต | Wikipedia (Thai language) citing Prasithrathsint: neutral ถูก arose as an Anglicism, while โดน keeps the adverse sense; thai-humanizer | several sources |
| ไม่ใช่แค่ X แต่ยัง Y / ไม่เพียงแต่ | ไม่ใช่แค่สวย แต่ยังใช้งานได้จริง | สวย แถมใช้งานได้จริง | thai-humanizer (pattern 4) | single source |
| Sentence-initial connectors | นอกจากนี้ ... อีกทั้ง ... ยิ่งไปกว่านั้น ... | แถม ... ที่สำคัญ ... | thai-humanizer calls this the top Thai AI tell | single source |
| Era framing | ในยุคปัจจุบันที่ทุกอย่างเปลี่ยนแปลงอย่างรวดเร็ว | (cut) โปรนี้ถึงสิ้นเดือน | thai-humanizer | single source |
| คุณ and ของคุณ everywhere | ผิวของคุณสมควรได้รับสิ่งที่ดีที่สุดสำหรับคุณ | ใครผิวแห้ง ตัวนี้ช่วยได้ | Thai Wikipedia style guide (avoid คุณ); none found for ads | single source plus inference |
| มันคือ ... ที่ cleft | มันคือความสุขที่คุณสัมผัสได้ | อร่อยจนต้องสั่งซ้ำ | thai-humanizer (pattern 3) | single source |
| การ and ความ nominal chains | เพื่อที่จะทำให้การดูแลผิวมีความง่ายดาย | ดูแลผิวง่ายขึ้น | thai-humanizer | single source |
| Formula rhetorical opener | คุณเคยสงสัยไหมว่าทำไมผิวถึงแห้ง | อากาศเย็นลง ผิวแห้งง่าย | thai-humanizer (pattern 9) | single source |
| Calqued verbs | ยกระดับประสบการณ์ / ปลดล็อกศักยภาพ / ค้นพบประสบการณ์ใหม่ | ชาร์จเต็มใน 30 นาที / ลองชิมที่ร้าน | Thai Wikipedia AI-signs page lists ยกระดับ (translated list); thai-humanizer example | single source plus inference |
| Puffery | รสชาติลงตัวอย่างไร้ที่ติ บริการเหนือระดับ | หวานน้อย เข้มกำลังดี | thai-humanizer examples | single source |
| Particle problems | ใหม่ค่ะ ลดค่ะ ส่งฟรีค่ะ สั่งเลยครับ | ของใหม่ ลดแล้ว ส่งฟรีด้วยนะคะ | thai-humanizer (particles only where natural); Wikipedia (particles) | single source plus inference |
| English punctuation | ส้ม, มะม่วง, และแตงโม. | ส้ม มะม่วง แตงโม | Thai script (Wikipedia); Thai Wikipedia style guide | several sources |
| Chatbot residue | หวังว่าจะเป็นประโยชน์นะคะ หากมีคำถามเพิ่มเติมแจ้งได้เลย | (delete) | thai-humanizer (patterns 14 and 15) | single source |
| Letter opener | เรียน คุณลูกค้าที่เคารพ | (start with the news) | thai-humanizer business email example | single source |
| Bold label bullets and emoji bullets | ✅ **ประหยัด:** ... ✅ **ทนทาน:** ... | ประหยัดไฟ ใช้ได้นาน | thai-humanizer (patterns 11 and 12) | single source |

On English punctuation: a Thai-built humanizer says English rules such as "no em dash" miss Thai AI tells. The Thai list above is therefore mostly about connectors, puffery and calques, not punctuation.

#### Purple or poetic phrasing

- ดื่มด่ำกับช่วงเวลาแห่งความสุข → นั่งริมหน้าต่าง เห็นแม่น้ำ อยู่ได้ถึงสองทุ่ม
- ปลุกทุกประสาทสัมผัส → เปิดประตูร้านก็หอมกาแฟแล้ว
- รังสรรค์ด้วยความใส่ใจในทุกรายละเอียด → เย็บมือทุกใบ ใบละ 3 ชั่วโมง
- มนต์เสน่ห์ที่ไม่มีวันจางหาย → ขายมา 30 ปี สูตรเดิม
- ความงามที่เปล่งประกายจากภายใน → ทาแล้วผิวดูฉ่ำ ไม่เหนียวเหนอะ

Confidence: inference, supported by thai-humanizer's before and after examples, which cut puffery to concrete detail.

#### Natural vs robotic lines

Natural:
1. โปรเดือนนี้ ชาไทยแก้วใหญ่ 45 บาท ถึง 30 ก.ย. นี้เท่านั้นนะคะ
2. ส่งฟรีทุกออเดอร์ขั้นต่ำ 199 บาท สั่งก่อนบ่ายสองได้ของวันนี้เลยครับ
3. เมนูใหม่มาแล้วจ้า ข้าวกะเพราไข่ดาว 69.- เฉพาะสาขาสยาม
4. แอดชิมแล้ว หวานน้อยกำลังดี ใครไม่ชอบหวานจัดลองสั่งแบบนี้ได้เลยค่ะ

Robotic, each followed by its fix:
1. เซรั่มนี้ถูกออกแบบมาเพื่อยกระดับประสบการณ์การดูแลผิวของคุณ
   Fix: เซรั่มตัวนี้ทำมาเพื่อผิวแพ้ง่าย เนื้อบางซึมไว ขวดละ 590 บาท
2. ไม่ใช่แค่กาแฟ แต่คือการเดินทางแห่งรสชาติที่ไร้ขีดจำกัด
   Fix: เมล็ดใหม่จากเชียงราย คั่วกลาง หอมถั่ว ๆ แก้วละ 65 บาท
3. นอกจากนี้ รองเท้ารุ่นนี้ยังมีความสามารถในการกันน้ำได้ดีเยี่ยม
   Fix: รองเท้ารุ่นนี้กันน้ำได้ ลุยฝนไปทำงานสบาย
4. เรียนลูกค้าผู้มีอุปการคุณ ร้านจะปิดปรับปรุงวันที่ 1 ต.ค. ค่ะ
   Fix: ร้านปิดปรับปรุงวันที่ 1 ต.ค. วันเดียวนะคะ วันที่ 2 เปิดตามปกติค่ะ

#### Sources (Thai)

- thai-humanizer: SKILL.md, references/banned-words-th.md, references/examples-th.md (created 2026-06), GitHub citelogics-th, https://github.com/citelogics-th/thai-humanizer (read 2026-09-24, read)
- Thai language: sections Passive, Particles, Register, English Wikipedia, https://en.wikipedia.org/wiki/Thai_language (read 2026-09-24, read)
- The Establishment of the Neutral Passive and the Persistence of the Adversative Passive in Thai (Amara Prasithrathsint, 2001), Manusya, Chulalongkorn University, https://digital.car.chula.ac.th/manusya/vol4/iss2/6 (read 2026-09-24, read; abstract only)
- วิกิพีเดีย:คู่มือการเขียน (Thai Wikipedia manual of style: punctuation, numbers, years, คุณ), Thai Wikipedia, https://th.wikipedia.org/wiki/วิกิพีเดีย:คู่มือการเขียน (read 2026-09-24, read)
- วิกิพีเดีย:สัญญาณของการเขียนด้วยปัญญาประดิษฐ์, Thai Wikipedia, https://th.wikipedia.org/wiki/วิกิพีเดีย:สัญญาณของการเขียนด้วยปัญญาประดิษฐ์ (read 2026-09-24, read; mostly a translation of the English page with English Wikipedia examples, so it is used only for the Thai wording of listed words)
- Thai script: section Punctuation, English Wikipedia, https://en.wikipedia.org/wiki/Thai_script (read 2026-09-24, read)
- Thai solar calendar, English Wikipedia, https://en.wikipedia.org/wiki/Thai_solar_calendar (read 2026-09-24, read)
- Thai baht (sign ฿ or บ.), English Wikipedia, https://en.wikipedia.org/wiki/Thai_baht (read 2026-09-24, read)
- 555, English Wiktionary, https://en.wiktionary.org/wiki/555 (read 2026-09-24, read)
- ตะโกน, English Wiktionary, https://en.wiktionary.org/wiki/ตะโกน (read 2026-09-24, read; lists no slang sense)
- Songkran copy frameworks (2026-04-12), Marketing Oops, https://www.marketingoops.com/how-to-4/songkran-copy/ (read 2026-09-24, read; checked and found no language-level guidance)

#### Could not verify

- No native source (Pantip, the Royal Society, an agency blog) on ภาษาแปล in ads, on ซึ่ง overuse, or on which slang is dated in 2026; the search budget ran out before the Thai searches.
- The Thai evidence rests on one Thai-built GitHub humanizer, Wikipedia pages and one linguistics abstract.
- Thai Wikipedia's AI-signs page is a translation of the English page, so it was used only for Thai wording.

### 4.17 Korean (ko)

#### Register guide

- **Speech level.** Default to 해요체 (~해요, ~이에요/예요, ~세요). Toss writes all product copy in 해요체 and avoids 니다체 (합쇼체) and bookish Sino-Korean. Keep 합쇼체 (~습니다) for formal notices such as delivery delays, recalls or price changes. A Mobiinside analysis of brand Facebook posts found polite speech won more likes on hard topics and made no difference on easy ones. Use 반말 only for a deliberate character account (a witty "friend" persona in the Baemin style, or a teen sub-account). Confidence: several sources.
- **Casual markers.** Sentence ends such as ~요!, ~죠, ~네요 and ~거든요. ㅎㅎ is the softer, brand-safe laugh; ㅋㅋ is funnier and more personal. A tilde tail (놀러 오세요~) and short noun fragments work well (신메뉴 출시!, 선착순 100명!). Drop subjects and objects, and vary sentence length. Korean writers name full subjects and objects in every sentence, and sentences of equal length, as AI habits. Emoji: 0 to 2 per caption, usually at a line end. Confidence: native source (sentence shape); inference (particles, laughs, emoji).
- **Stable commerce words (safe in 2026).** 신상, 무배 (무료배송), 핫딜, 오픈런, 품절 임박, 재입고, 선착순, 1+1, 꿀팁, 찐 (찐맛집), 역대급, 가성비. Confidence: inference.
- **Trend slang: use sparingly.** Korean coverage in 2025 describes brand slang backfiring when the brand misses a word's origin or context: GS25 and others with 싹싹김치 in 2025, and OB's 필굿 with 갓생 and 인싸템 in 2019. A 2026 slang dictionary still lists 갓생, 킹받다, 중꺾마, 럭키비키, 원영적 사고 and 추구미 as in use. My read is that 럭키비키 (2024) and 중꺾마 (2022) now sound try-hard in brand copy unless the account is meme-led (inference). Avoid 존맛, JMT and 존맛탱: the root is vulgar, and Korean press covered their spread as a slang controversy. Toss's rule is to prefer universal words over slang and memes. Confidence: several sources (backlash, currency list); inference (which words feel dated).
- **Address.** Drop "you". Use 여러분 for broadcast posts, 고객님 in service and CS lines, ~님 with names, or a community nickname: Korean accounts praised in 2025 call followers by brand nicknames such as 애즈오너 and 낼나러. Avoid 당신. It is a translation habit, and only a few famous native slogans carry it. Confidence: several sources.
- **Code-mixing.** Write loanwords in Hangul by default (세일, 쿠폰, 굿즈, 팝업, 오픈, 콜라보, 리뷰). Use Latin only for brand and product names, short sticker words (NEW, SALE, BEST, D-3) and codes. Do not repeat an English gloss in brackets after every Korean term, and do not leave English buzzwords (seamless, premium lifestyle) untranslated. Confidence: single source (the gloss and buzzword rules); inference (the Hangul default).
- **Punctuation.** Korean uses Western marks (. , ! ?). Write ranges with the tilde: 9/24~9/30 (국립국어원 treats ~ as the rule and allows a hyphen). Use the middle dot for pairs (쿠폰·적립금), single quotes for emphasis, and brackets for the weekday: 9월 30일(수). Avoid 줄표 (the dash): a Korean media critic lists dashes used in place of commas as a ChatGPT tell. No comma after connective endings (가볍지만, / 촉촉해서,), which is the strongest measured orthographic marker of LLM Korean. Confidence: several sources.
- **Numbers.** Write 9,900원 with the numeral attached to 원 (한글 맞춤법 43항 allows units to attach to Arabic numerals). Use 1만 원 or 1만원; for exact prices prefer 29,900원 over 2만 9,900원. Percents: 20% 할인, 최대 50%. Dates: 9월 24일(목) or 9.24(목), year first (2026년). Time: 오후 2시 or 14:00. ₩ and KRW look foreign in consumer copy. Confidence: snippet (43항); inference (the rest).

#### Formal to everyday swaps

| Formal | Everyday | Note | Confidence |
|:-|:-|:-|:-|
| 구매하실 수 있습니다 | 살 수 있어요 / 구매 가능해요 | 합쇼체 plus stacked honorifics become 해요체 | several sources |
| 보습력을 가지고 있습니다 | 보습력이 좋아요 | the "have" calque becomes a predicate | native source |
| 전문가에 의해 제작된 | 전문가가 만든 | the "by" passive becomes active | native source |
| 여름철 피부 관리에 있어서 | 여름철 피부 관리는 | ~에 있어서 becomes ~에서 or ~는 | native source |
| 엄선되어진 원두 | 직접 고른 원두 | double passive becomes an active verb | single source |
| 다음과 같습니다 | (cut; list directly) | enumeration preamble | single source |
| 혜택을 제공합니다 | 혜택 드려요 | 제공하다 is a catch-all verb | inference |
| 이벤트가 진행됩니다 | 이벤트 해요 / 이벤트 열려요 | notice passive | inference |
| 이용해 주시기 바랍니다 | 이용해 주세요 | letter tone | inference |
| 문의 바랍니다 | 궁금하면 DM 주세요 | notice to chat | inference |
| 금일 / 익일 | 오늘 / 내일 (다음 날) | Sino-Korean notice words | inference |
| 해당 제품 / 상기 제품 | 이 제품 | officialese | inference |
| 수령하세요 | 받아 가세요 | Sino-Korean verb | inference |
| 섭취하세요 | 드세요 | Sino-Korean verb | inference |

#### AI and translation tells

| Tell | Robotic example | Natural fix | Evidence | Confidence |
|:-|:-|:-|:-|:-|
| 단순한 X가 아니라 Y (local "not X, it's Y"); also X를 넘어 Y로 | 단순한 텀블러가 아니라 당신의 라이프스타일입니다 | 보온 12시간, 차 컵홀더에 쏙 들어가요 | im-not-ai corpus study: 9.2x more frequent in AI text across three model families; OhmyNews critic | native source (measured) |
| ~를 가지고 있다 ("have") | 이 립밤은 놀라운 보습력을 가지고 있습니다 | 이 립밤, 보습력이 좋아요 | 김순영 2012 (국립국어원); 한글문화연대 | native source |
| ~에 의해 and ~되어지다 | 장인에 의해 엄선되어진 가죽 | 장인이 직접 고른 가죽 | 김순영 2012; im-not-ai A-8, A-9 | native source |
| ~에 있어서 | 여름 스킨케어에 있어서 가장 중요한 것 | 여름 스킨케어는 보습이 먼저예요 | 한글문화연대; im-not-ai A-3 | native source |
| 당신 and 당신의 in every line | 당신의 아침을 깨우는 당신만의 커피 | 아침 한 잔으로 잠 깨기 딱 좋아요 | 김혜영 2009 (pronouns separate translated from native text, via im-not-ai); 나무위키 (snippet) | several sources |
| ~들 on every plural | 다양한 제품들과 혜택들을 만나 보세요 | 여러 제품과 혜택을 한 번에 | 김순영 2012 | native source |
| Stock importance and hedge endings | 피부 장벽을 지키는 것이 중요합니다 | 장벽 크림부터 바르세요 | Maven (브런치); IT 살림백서 | several sources |
| Sentence-initial 또한, 결론적으로 | 또한, 이번 신제품은 향도 좋습니다 | 향도 좋아요 | IT 살림백서; im-not-ai D-1, H-1 | several sources |
| Comma after a connective ending | 가볍지만, 따뜻하고, 부드러워요 | 가볍고 따뜻하고 부드러워요 | im-not-ai C-11 citing KatFish (ACL 2025, 4.84x) | single source |
| Every subject and object spelled out; equal sentence length | 저희 브랜드는 고객님께 최고의 제품을 제공합니다. 저희는 품질을 약속합니다. | 좋은 것만 골라 팔아요. 품질은 자신 있어요! | Maven (브런치) | native source |
| Era framing | 오늘날 빠르게 변화하는 세상에서 | (cut) 이번 주 금요일부터 | none found | inference |
| Experience and Discover imperatives | 새로운 맛을 발견하세요 | 새로 나온 맛, 한번 드셔 보세요 | none found | inference |
| Journey metaphor | 당신의 뷰티 여정을 함께합니다 | 4주 동안 매일 아침 한 번이면 돼요 | none found | inference |
| Hype adjectives | 혁신적이고 획기적인 전례 없는 텍스처 | 바르자마자 쏙 스며들어요 | im-not-ai D-4 | single source |
| 반말 and 존댓말 mixed in one caption | 신메뉴를 출시합니다. 꼭 먹어 봐! | 신메뉴 나왔어요. 꼭 드셔 보세요! | im-not-ai E-7 (estimated); Toss | several sources |

Do not lint single uses of ~을 통해 or ~것이다. The im-not-ai corpus study found native writers use both more than models do, so a ban would mostly hit human copy (single source).

#### Purple or poetic phrasing

A Korean media critic says ChatGPT copy spends more words on metaphor than on content and stacks short quote-like lines (native source). Plain fixes:

- 당신의 일상에 스며드는 향기 → 퇴근할 때까지 은은하게 남는 향
- 시간이 멈춘 듯한 공간 → 창가 자리에서 한강이 보여요
- 한 모금에 담긴 가을 → 가을 한정 밤라떼, 6,000원
- 빛나는 순간을 선사합니다 → 조명 자리에서 찍으면 사진이 잘 나와요
- 감성을 깨우는 특별한 경험 → 토요일 오후 2시엔 원데이 클래스도 열어요

#### Natural vs robotic lines

Natural:
1. 오늘부터 가을 신메뉴 3종 출시! 단호박 라떼는 5,500원이에요.
2. 성수점 팝업은 토요일 오전 11시 오픈이에요. 선착순 100분께 굿즈 드려요.
3. 품절됐던 무화과 크림치즈 다시 들어왔어요 ㅎㅎ 1인 2개까지 살 수 있어요.
4. 무료배송 기준이 3만 원에서 2만 원으로 내려갔어요. 장바구니 한 번 더 확인해 보세요!

Robotic, each followed by its fix:
1. 당신의 피부를 위한 새로운 차원의 보습을 경험하세요.
   Fix: 건조한 날엔 이 크림 하나면 돼요. 이번 주는 1+1이에요.
2. 단순한 커피가 아니라 하루를 여는 특별한 여정입니다.
   Fix: 아침 8시 전에 주문하면 아메리카노 2,000원이에요.
3. 모든 원두는 전문 로스터에 의해 신중하게 선별되어지고 있습니다.
   Fix: 원두는 매주 월요일 로스터가 직접 골라요.
4. 존경하는 고객님, 추석 연휴 배송 일정을 안내해 드립니다.
   Fix: 연휴 전에 받으려면 목요일 오후 2시까지 주문해 주세요.

#### Sources (Korean)

- AI 특유의 뻔한 말투 지우는 프롬프트 (Maven, 2026-06-26), 브런치, https://brunch.co.kr/@maven/527 (read 2026-09-24, read)
- 챗GPT에게 맡긴 글은 명백하게 티가 난다, 왜냐하면 (신상호, 2026-09-06), 오마이뉴스, https://www.ohmynews.com/NWS_Web/View/at_pg.aspx?CNTN_CD=A0003264627 (read 2026-09-24, read)
- 챗GPT가 자주 쓰는 말: AI 티 나는 초안을 내 글로 다듬는 교정 프롬프트 모음 (2026-07; original title uses a dash), IT 살림백서, https://itsallim.blogspot.com/2026/07/ai-draft-humanize-prompts.html (read 2026-09-24, read)
- 영한 번역에 나타난 번역투 문장 (김순영), 새국어생활 22권 1호 2012, 국립국어원, https://www.korean.go.kr/nkview/nklife/2012_1/22_0105.pdf (read 2026-09-24, read)
- 외국어 번역에서 온 잘못된 습관, '번역 투' (김민지, 2023-09-19), 한글문화연대, https://www.urimal.org/4544 (read 2026-09-24, read)
- im-not-ai (humanize-korean): taxonomy, quick rules, evidence (corpus study measured 2026-07), GitHub epoko77-ai, https://github.com/epoko77-ai/im-not-ai (read 2026-09-24, read)
- 토스의 8가지 라이팅 원칙들 (김자유, 2022-11-15), Toss Tech, https://toss.tech/article/21022 (read 2026-09-24, read)
- '존댓말? 반말?' 콘텐츠 메시지, 어떻게 쓸까요? (전형준, 2021-02-23), 브런치 모비인사이드, https://brunch.co.kr/@mobiinside/2828 (read 2026-09-24, read)
- 2025년 Z세대가 주목한 인스타그램 운영 맛집은? (2025-01-21), 고구마팜, https://gogumafarm.kr/2025%EB%85%84-z%EC%84%B8%EB%8C%80%EA%B0%80-%EC%A3%BC%EB%AA%A9%ED%95%9C-%EC%9D%B8%EC%8A%A4%ED%83%80%EA%B7%B8%EB%9E%A8-%EC%9A%B4%EC%98%81-%EB%A7%9B%EC%A7%91%EC%9D%80-sns-%EB%8B%B4%EB%8B%B9%EC%9E%90/ (read 2026-09-24, read)
- '싹싹김치'부터 '갓생'까지, 논란 휘말린 기업들 신조어 마케팅 역풍 (2025-04-15), 르데스크, https://www.ledesk.co.kr/view.php?uid=12565 (read 2026-09-24, read)
- 트렌드 따라간 신조어 마케팅, 소비자는 왜 불편함을 느끼나 (2025-03-05), 소비자평가, http://www.iconsumer.or.kr/news/articleView.html?idxno=27459 (read 2026-09-24, read)
- 2026 신조어 사전, 캐해랩, https://kaehaelab.com/sinjo (read 2026-09-24, read)
- 일본 식당에 '존맛탱(JMT)', 해외서도 쓰이는 한국어 속어 '논란' (2024-10), YTN, https://www.ytn.co.kr/_ln/0103_202410111050045004 (read 2026-09-24, snippet)
- 온라인가나다: 한글 맞춤법 제43항 띄어쓰기, 국립국어원, https://www.korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&qna_seq=321914&pageIndex=1 (read 2026-09-24, snippet)
- 문장 부호 해설, 국립국어원, https://www.korean.go.kr/front/etcData/etcDataView.do?mn_id=46&etc_seq=431 (read 2026-09-24, snippet)
- 'have'의 번역 투 '가지다' 순화, IT 글쓰기와 번역 노트 (wikidocs), https://wikidocs.net/165392 (read 2026-09-24, snippet; the page itself was blocked)
- 당신, 나무위키, https://namu.wiki/w/%EB%8B%B9%EC%8B%A0 (read 2026-09-24, snippet)

#### Could not verify

- 경험하세요, 발견하세요, 여정, 새로운 차원, 오늘날 and the letter salutations rest on the researcher's judgment; no native article names them, although the structural tells around them are measured.

### 4.18 Nepali (ne)

#### Register guide
- **Honorific ladder (several sources).** Wikipedia lists five grades: तँ (low), तिमी (medium), तपाईं (high), हजुर
  (very high) and मौसुफ (royal); its grammar article gives the imperatives गर्, गर and गर्नुहोस्. Brand default:
  तपाईं with the polite imperative. Microsoft's Nepali guide calls तपाईं the widely used form and allows तिमी. Never
  तँ; हजुर suits customer-service replies (inference).
- **Imperative forms (single source and inference).** Wiktionary lists गर्नुहोस् and the contracted गर्नोस् for the high
  grade. The spoken contraction गर्नुस् is what most casual posts say (inference; it is not in these references). Use
  गर्नुहोस् for UI, forms and notices, गर्नुस् or गर्नोस् in captions, one form per post.
- **Everyday over formal (native source).** Microsoft's Nepali guide asks for everyday conversational language and lists
  formal verbs to swap (रूपान्तर गर्नुहोस्, उपयोग गर्नुहोस्, हासिल गर्नुहोस्). Its replacements (परिवर्तन, प्रयोग,
  प्राप्त) are UI-neutral; a caption can go one step further (बदल्नुस्, चलाउनुस्, पाउनुस्).
- **Tatsam marks the bookish layer (single source and inference).** Nepali Wikipedia defines तत्सम words as Sanskrit
  words used unchanged. Notices stack them with the written present in दछ (गर्दछ, पर्दछ) and formulas such as
  जानकारी गराइन्छ; social copy uses गर्छ, पर्छ and plain words.
- **Code-mixing and Roman script (several sources).** A 2014 code-switching shared task built its Nepali-English corpus
  from Romanised Nepali tweets and public Facebook pages (FM stations, news, public figures) and found many users were
  regular code-switchers. Khalti names a product in Roman Nepali (Khalti Ma Bridge Course). Daraz Nepal's Nepali
  interface transliterates English (फ्ल्यास सेल) and uses the polite imperative (किन्नुहोस्) and "तपाईको लागि मात्र".
- **English words take गर्नु (inference, partly first-hand).** अर्डर गर्नुस्, रिचार्ज गर्नुस्, डाउनलोड गर्नुस्; in
  Roman, order garnus, recharge garnu hos. Normal loans: अफर, सेल, डेलिभरी, फ्री, क्यासब्याक, डाटा, एप, प्याक.
- **Casual markers (inference).** Particles ल (ल, आजै अर्डर गर्नुस्), नि (सस्तो नि), त (आज त), है as a friendly tag
  (आउनुहोला है), अनि; words एकदम, राम्रो, सस्तो, छिटो, मस्त; youth slang खत्रा, बबाल, दामी (Roman khatra, babal,
  dami); Roman chat openers such as k cha; दाइ and दिदी as warm address in service copy. 🙏 reads as namaste or thanks.
- **Numbers and marks (inference).** Devanagari digits in Nepali-script posts (रु. ९९९), Western digits in Roman posts
  (Rs 999); lakh grouping (रु. १,००,०००); । ends a statement; ? and ! as in English.
- **Hindi leakage (inference).** Nepali shares script and much vocabulary with Hindi, so tools slip in हैं, और, नहीं,
  आपका, करें. Nepali says छन्, र or अनि, छैन or होइन, तपाईंको, गर्नुहोस्. The lint skips है, which Nepali uses as a tag.
- **Nepal first (single source).** Nepali is also written in Darjeeling and Sikkim (the 2014 corpus notes it); keep
  NPR, Nepal places and Nepal festivals (Dashain, Tihar) for Nepal.

#### Formal to everyday swaps
| formal | everyday | note | confidence |
|:-|:-|:-|:-|
| रूपान्तर गर्नुहोस् | परिवर्तन गर्नुहोस् (UI), बदल्नुस् (post) | Microsoft Nepali guide | native source, inference |
| उपयोग गर्नुहोस् | प्रयोग गर्नुहोस् (UI), चलाउनुस् (post) | same table | native source, inference |
| हासिल गर्नुहोस् | प्राप्त गर्नुहोस् (UI), पाउनुस् or लिनुस् (post) | same table | native source, inference |
| गर्दछ, पर्दछ | गर्छ, पर्छ | written present | inference |
| प्रदान गर्दछौं | दिन्छौं | corporate "we provide" | inference |
| उपलब्ध गराउँछौं | पाइन्छ, दिन्छौं | plain उपलब्ध छ is fine | inference |
| सुनिश्चित गर्नुहोस् | पक्का गर्नुस्, ध्यान दिनुस् | | inference |
| सम्पूर्ण ग्राहक महानुभावहरूमा जानकारी गराइन्छ | say the news (शनिबार सेवा बन्द हुन्छ) | right for a formal notice | inference |
| यथाशीघ्र | छिटो, चाँडै | | inference |
| अत्यन्त | एकदम, धेरै | | inference |
| निःशुल्क | फ्री, सित्तैमा | | inference |
| हेतु, निमित्त | लागि | | inference |
| सम्पर्क राख्नुहोस् | फोन गर्नुस्, म्यासेज गर्नुस् | | inference |
| अनुभव गर्नुहोस् | चाख्नुस्, लगाएर हेर्नुस् | | inference |

#### AI and translation tells
| tell | robotic example | natural fix | evidence | confidence |
|:-|:-|:-|:-|:-|
| "not just X, it is Y" | यो केवल एउटा चिया होइन, यो आरामको अनुभव हो। | कडा अलैंची चिया, रु. ५० मात्र। | Hindi twin in India TV Hindi | inference |
| "experience" | स्वादको यात्रा अनुभव गर्नुहोस्। | नयाँ मेनु आयो, आजै चाख्नुस्। | none found | inference |
| "discover" or "explore" | नयाँ स्वादहरू पत्ता लगाउनुहोस्। | नयाँ फ्लेभर ट्राई गर्नुस्, तीनवटामा एउटा फ्री। | none found | inference |
| "to new heights" | व्यवसायलाई नयाँ उचाइमा लैजानुहोस्। | पसलको हिसाब अब एपमै, फ्री। | none found | inference |
| Hindi words in Nepali | हाम्रो एपले आपका समय बचाउँछ और जीवन सजिलो बनाउँछ। | एपबाट २ मिनेटमै बिल तिर्नुस्। | none found | inference |
| written present and "we provide" | हामी उत्कृष्ट सेवा प्रदान गर्दछौं। | समस्या? म्यासेज गर्नुस्, १० मिनेटमै जवाफ दिन्छौं। | none found | inference |
| notice formula as a post | ग्राहक महानुभावहरूमा जानकारी गराइन्छ कि... | शनिबार सेवा बन्द, आइतबार बिहान १० बजेदेखि खुल्छ। | none found | inference |
| "ensure" | अफर लिन सुनिश्चित गर्नुहोस्। | अफर शुक्रबार राति १२ बजे सकिन्छ। | none found | inference |
| busy-world opener | आजको व्यस्त जीवनशैलीमा स्वास्थ्य महत्त्वपूर्ण छ। | अफिसमा खाना छुट्छ? १५ मिनेटमै सलाद। | none found | inference |
| तपाईंको in every phrase | तपाईंको लागि, तपाईंको परिवारको लागि, तपाईंको खुसीको लागि। | ४ जनाको फेमिली कम्बो, रु. १,२९९। | none found | inference |
| letter opener | प्रिय ग्राहक, दशैं अफर सुरु भयो। | दशैं अफर सुरु: हरेक अर्डरमा रु. २०० क्यासब्याक। | none found | inference |
| engagement bait | साथीहरूलाई ट्याग गर्नुहोस्! | तपाईंलाई कुन मन पर्छ, चिकेन कि भेज? | none found | inference |
| chatbot framing | पक्कै पनि! यहाँ केही क्याप्सनहरू छन्: | delete it | none found | inference |
| formal UI verbs in a post | एप उपयोग गर्नुहोस्। | एप चलाउनुस्। | Microsoft Nepali guide | native source |

#### Purple or poetic phrasing
- स्वादको यात्रा, स्वादको संसार: name the dish.
- हरेक पललाई विशेष बनाउनुहोस्: name the moment (बेलुकाको चियासँग).
- सपनालाई पखेटा दिनुहोस्: give the concrete result (किस्ता रु. २,५०० महिनाबाट).
- परम्परा र आधुनिकताको अनुपम संगम: say what is old and what is new.
- मन छुने अनुभव: give one detail.
Confidence: inference.

#### Natural vs robotic lines
Natural:
- दशैंको अफर सुरु भयो! रु. ५,००० भन्दा बढीको किनमेलमा रु. ५०० क्यासब्याक।
- ल, आजै अर्डर गर्नुस्! साँझ ६ बजेसम्मको अर्डर भोलि बिहानै घरमा।
- Data sakiyo? Rs 99 ma 3GB, 7 din samma chalcha.
- तिहारका लागि मिठाई प्याक रु. ९९९ देखि, ललितपुरका सबै शाखामा पाइन्छ।

Robotic, each with a fix:
- यो केवल एउटा चिया होइन, यो आरामको अनुभव हो।
  Fix: कडा अलैंची चिया, रु. ५० मात्र। बेलुका ५ देखि ७ बजेसम्म समोसा फ्री।
- हाम्रो नयाँ मेनुसँग स्वादको यात्रा अनुभव गर्नुहोस्।
  Fix: नयाँ मेनु आयो: १२ नयाँ परिकार, रु. ३५० देखि। आजै चाख्नुस्।
- आदरणीय ग्राहक महानुभावहरूमा जानकारी गराइन्छ कि हामी उत्कृष्ट सेवा प्रदान गर्दछौं।
  Fix: अर्डरमा समस्या? म्यासेज गर्नुस्, १० मिनेटमै जवाफ दिन्छौं।
- हाम्रो एपले आपका समय बचाउँछ और जीवन सजिलो बनाउँछ।
  Fix: बिल तिर्न लाइन बस्नु पर्दैन: एपबाट २ मिनेटमै तिर्नुस्।

#### Hypothesis check
- Refined: गर्नुहोस् (written) versus गर्नुस् (spoken polite). The references show गर्नुहोस् and गर्नोस्; गर्नुस् is
  inference.
- Rejected as tells: उपलब्ध (only उपलब्ध गराउँछौं is flagged) and "X मात्र होइन, Y पनि", which is ordinary Nepali.
- Refined: प्राप्त गर्नुहोस् is a note with high false-positive risk, since Microsoft prefers it for UI.
- Kept as inference: अनुभव गर्नुहोस्, पत्ता लगाउनुहोस्, अन्वेषण, यात्रा as a metaphor, नयाँ उचाइ.
- Confirmed: the honorific ladder, Romanised Nepali code-switching (2014 corpus), the Daraz and Khalti samples.
- Not verified: the Roman casual words (k cha, ekdam, ramro, sasto, chito, khatra, babal) and the brand voices of
  Foodmandu and eSewa (no copy returned), Ncell (fetch failed), Nepal Telecom (only a menu label) and Pathao Nepal (not
  tried).

#### Sources
- Nepali Style Guide, Microsoft Localization Style Guides, https://aka.ms/nepali-styleguide (read 2026-09-24, read)
- Nepali language, Wikipedia, https://en.wikipedia.org/wiki/Nepali_language (read 2026-09-24, read)
- Nepali grammar, Wikipedia, https://en.wikipedia.org/wiki/Nepali_grammar (read 2026-09-24, read)
- गर्नु, Wiktionary, https://en.wiktionary.org/wiki/गर्नु (read 2026-09-24, read)
- तत्सम, Nepali Wikipedia, https://ne.wikipedia.org/wiki/तत्सम (read 2026-09-24, read)
- Overview for the First Shared Task on Language Identification in Code-Switched Data (Solorio et al., 2014), ACL Anthology, https://aclanthology.org/W14-3907.pdf (read 2026-09-24, read)
- Daraz Nepal homepage, daraz.com.np, https://www.daraz.com.np/ (read 2026-09-24, read)
- Khalti homepage, khalti.com, https://khalti.com/ (read 2026-09-24, read)
- Hindi twin of the "not X but Y" pattern: India TV Hindi, https://www.indiatv.in/explainers/how-to-detect-ai-written-text-6-language-patterns-that-reveal-machine-writing-2026-08-25-1239356 (read 2026-09-24, read)

## 5. Method and sources for sections 1 to 3

Method. Eight research passes ran in parallel on 2026-09-24, one per language group (Hindi, Urdu and Nepali; Arabic
and Turkish; Spanish and Portuguese; French and German; Indonesian, Malay and Filipino; Chinese and Japanese; Korean
and Thai; Tamil and Vietnamese). Each wrote its own candidates and calibration lines and had to pass the same harness
before handing in. The merge then re-ran every check on the combined file, added the hard negatives, narrowed two
candidates (the Vietnamese chatbot rule no longer fires on a bare "Chắc chắn rồi!", and the Urdu Arabic-letter rule
became a warning that skips Arabic quotations) and ran the current `copyrules.py` over the natural lines for §3. The
working files (harness, merge script, the eight part files) are in `research-voice/lang-parts/`.

Sources (all read 2026-09-24):
- Do Large Language Models have an English Accent? Evaluating and Improving the Naturalness of Multilingual LLMs
  (Guo, Conia, Zhou, Li, Potdar, Xiao), ACL 2025, https://aclanthology.org/2025.acl-long.193/ (snippet)
- Paper note on the same paper, papernotes, https://en.papernotes.org/ACL2025/multilingual_mt/multilingual_llm_english_accent/ (read)
- An Investigation of Translationese in the Generations of Multilingual Large Language Models (Valentini, Wright,
  Granados, Colunga, von der Wense, August 2026), arXiv 2608.17399, https://arxiv.org/html/2608.17399 (read)
- Translationese Remains a Challenge for Large Language Models, Study Finds, Slator, on arXiv 2503.04369,
  https://slator.com/translationese-remains-challenge-for-large-language-models-study-finds/ (read)
- Language links of Wikipedia:Signs of AI writing (German, French, Portuguese, Chinese and Thai editions have their own
  pages), English Wikipedia API,
  https://en.wikipedia.org/w/api.php?action=query&titles=Wikipedia:Signs_of_AI_writing&prop=langlinks&lllimit=500 (read)
- Local, read 2026-09-24: `~/.claude/skills/codex-design/references/copy.md` §1 to §4,
  `references/research/copy-transcreation.md`, `references/research/copy-ai-tells.md` and `scripts/copyrules.py`
  (the checks in §3 were run against this file as it stood on 2026-09-24).
