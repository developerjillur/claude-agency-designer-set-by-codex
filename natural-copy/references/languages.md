# Natural copy in 18 more languages

Hindi, Urdu, Nepali, Arabic, Turkish, Spanish, Portuguese, French, German, Indonesian, Malay, Filipino (Taglish),
Chinese, Japanese, Korean, Thai, Vietnamese and Tamil. Bangla is in `bangla.md`, English in `voice.md`.

How to use this file:
- Read §1 to §7 once: the mistakes are the same in every language, so the checks are too.
- Before writing, read the language's own entry in §8 and the matching row of `codex-design/references/copy.md` §4
  (register, address, locale and punctuation for the first twelve).
- Lint with the language tag: `design.py copylint --caption post.txt --lang id`. The lint carries 17 to 20 rules per
  language (`codex-design/scripts/voice_rules.json`), each calibrated so natural lines draw no finding.
- A native reader signs off every language you cannot read yourself. Every example line here was written for the
  research, not copied from a brand.

The evidence, with every source and confidence mark: `codex-design/references/research/voice-languages.md`.

## 1. The "English accent" (why a word list is not enough)

- Model text in other languages is further from human text than model English is, and the syntax gap is bigger than
  the vocabulary gap; Chinese was furthest in one study (Guo et al., ACL 2025).
- Classifiers spot translated-sounding model German, Spanish, Greek and Pashto 45 to 60 % of the time; native
  annotators only 28 to 37 % (Valentini et al., 2026). A quick skim misses most of it.
- Over 40 % of GPT-4 translations in one study had translationese errors; a second "rewrite it the way a native would
  post it" pass cut that from 43 % to 25 %. Always run that pass, then the lint, then the native reader.

Two checks work in every language:
1. **Does the line have the market's spoken layer** (particles, contractions, spoken verb forms; §4)?
2. **Does every sentence have a doer and a verb**, instead of a noun chain or a passive (§3)?

## 2. The same English moves, calqued

Models translate the same handful of English marketing moves into every language. Cut them all; say the fact
instead. "Native" marks a word real people use, which the lint leaves alone.

| Language | Dive in, discover | Experience, journey | Next level, unlock | Not just X, it's Y | Era opener |
|:-|:-|:-|:-|:-|:-|
| Hindi | खोजें, अन्वेषण करें | अनुभव करें, का आनंद लें; स्वाद की यात्रा | नई ऊँचाइयों पर | सिर्फ़ X नहीं, बल्कि Y | आज की भागदौड़ भरी ज़िंदगी में |
| Urdu | دریافت کریں | تجربہ کریں، لطف اندوز ہوں; ذائقے کا سفر | نئی بلندیوں تک | صرف X نہیں بلکہ Y | آج کی تیز رفتار زندگی میں |
| Nepali | पत्ता लगाउनुहोस्, अन्वेषण | अनुभव गर्नुहोस्; स्वादको यात्रा | नयाँ उचाइमा | केवल X होइन, यो Y हो | आजको व्यस्त जीवनशैलीमा |
| Arabic | انغمس في (اكتشف native in Gulf ads) | تجربة فريدة من نوعها; رحلة من النكهات | ارتقِ بـ، أطلق العنان لـ | ليس مجرد X بل Y | في عالم اليوم المتسارع |
| Turkish | dalın (Keşfet native) | deneyimleyin; lezzet yolculuğu | bir üst seviyeye taşıyın | sadece X değil; bir X'ten fazlası | günümüzün hızla değişen dünyasında |
| Spanish | sumérgete, adéntrate, embárcate | vive una experiencia única; un viaje de sabores | al siguiente nivel, eleva tu, potencia tu | No es solo X, es Y | en el vertiginoso mundo de |
| Portuguese | mergulhe no universo de | experiência inesquecível; jornada | ao próximo nível, eleve, potencialize | não é apenas X, é Y | no mundo atual, no cenário atual |
| French | plongez dans l'univers de (Découvrez native) | vivez une expérience unique; voyage culinaire | élevez votre, libérez votre potentiel | plus qu'un X, un Y | dans un monde où, à l'ère du numérique |
| German | tauche ein (Entdecke native) | erlebe unvergessliche... | auf das nächste Level, entfessle dein Potenzial | Das ist nicht nur X. Das ist Y. | in der heutigen schnelllebigen Welt |
| Indonesian | selami dunia (temukan native) | rasakan pengalaman; perjalanan rasa | wujudkan impianmu | bukan sekadar X, melainkan Y | di era digital saat ini |
| Malay | terokai (native in travel) | rasai pengalaman | merealisasikan impian | bukan sekadar X, tetapi Y | dalam dunia yang pantas berubah |
| Filipino | tuklasin, galugarin | maranasan; paglalakbay tungo sa | | hindi lamang X kundi pati na rin Y | sa mabilis na mundo ngayon |
| Chinese | 探索 (native) | 开启…之旅 | 赋能 | 不仅仅是X，更是Y | 在当今快节奏的时代 |
| Japanese | 〜の世界へようこそ | 物語を紡ぐ (体験 native) | 可能性を解き放つ, 新たな高みへ | 単なるXではなく | 今日の急速に変化する世界において |
| Korean | 발견하세요, 탐험하세요 | 경험하세요; 여정 | 새로운 차원 (차원이 다른 native) | 단순한 X가 아니라 Y | 오늘날 빠르게 변화하는 세상에서 |
| Thai | ดื่มด่ำ, ค้นพบประสบการณ์ | การเดินทางแห่ง... | ยกระดับประสบการณ์, ปลดล็อกศักยภาพ | ไม่ใช่แค่ X แต่ยัง Y | ในยุคปัจจุบัน |
| Vietnamese | đắm chìm (khám phá ngay native) | hành trình vị giác (trải nghiệm native) | (nâng tầm native) | không chỉ là X mà còn là Y | trong bối cảnh ngành X đang phát triển |
| Tamil | கண்டறியுங்கள் | அனுபவியுங்கள்; பயணம் | புதிய உயரங்களுக்கு | வெறும் X அல்ல | |

## 3. Translated structure

The grammar habits behind the accent. Fix each one by putting a person and a plain verb first.

- **Agent passives ("made by our experts"):** ar من قبل and بواسطة, tr tarafından, hi द्वारा, ur کی جانب سے, ko 에 의해 and
  되어지다, th ถูก...มา, vi được ... bởi, id and ms formal passives. Fix: "our chefs make it every morning".
- **Light verbs and noun chains:** es realizar su pedido, pt efetuar o pagamento, fr effectuer un achat, de "Die
  Lieferung erfolgt", ar تم + noun and قام بـ, tr gerçekleştirilecektir, hi and ne प्रदान करना, ur فراہم کرنا, zh 进行购买,
  ko 진행됩니다, th ดำเนินการ, vi thực hiện, id pelaksanaan ... dilakukan. Fix: the verb itself (pide, pagar, wir
  liefern, 买, กดสั่ง).
- **The "have" calque:** tr ...'e sahip, ko ~를 가지고 있다, pt possui and conta com, es contamos con. Fix: the plain
  "is" or "has" (tem, var, 좋아요).
- **Essay connectors:** es cabe destacar, pt vale ressaltar, fr il est important de noter, de es ist wichtig zu
  beachten, ar علاوة على ذلك, tr bununla birlikte, id tak dapat dipungkiri, ms walau bagaimanapun, zh 值得注意的是 and
  总而言之, ja と言えるでしょう, ko 또한 and 결론적으로 opening a sentence, th นอกจากนี้, vi Hơn nữa. Fix: cut them; ads
  need no summary.
- **English punctuation and case:** Title Case headlines in es, pt, fr and de; the English list comma before "and" in
  Arabic (برجر، بيتزا، وحلا); a full stop ending a Thai sentence; a comma after Korean connective endings (가볍지만,);
  English thousand separators in Vietnamese (99,000đ), Indonesian (Rp 49,000) and Malay (RM1.299).
- **Wrong variant:** European Portuguese in a Brazilian post (models default to it), Indonesian words in Malaysian
  copy (gratis, ongkir, bisa), Hindi words in Nepali (और, हैं, नहीं), mainland words in Taiwan posts (视频 for 影片),
  Arabic letters in Urdu (ك and ي for ک and ی).
- **"You" and "your" in every clause:** 당신의, ของคุณ, của bạn, तपाईंको, உங்கள், Sizin için ... size. Most of these
  languages drop the pronoun; address a group (ลูกค้าทุกคน, 여러분) or nobody.

## 4. The spoken layer: what natural copy has and machine copy lacks

Machine copy is grammatical but written. Natural social copy has the particles and contractions of speech; the total
absence of particles in a long casual caption is itself a tell (the Indonesian anti-slop list says so, and model
German underuses "auch"). One particle a sentence at most; a pile of them is fake casual.

| Language | Spoken markers a natural caption carries |
|:-|:-|
| Hindi | तो / toh, ना / na, बस / bas, ही / hi, भी / bhi; अरे, चलो; एकदम, पक्का |
| Urdu | toh, na, bas, abhi, chalo; تو، بس، ابھی، چلو |
| Nepali | ल, नि, त, है as a tag, अनि; the spoken imperative गर्नुस् |
| Arabic | one dialect only: Gulf الحين، وش، زين، واجد، علينا; Egyptian دلوقتي، عايز، أوي، بجد; Levantine هلق، شو، كتير، منيح; Moroccan دابا، بزاف، واخا |
| Turkish | ya, yani, işte, bak, hadi, gel, bi'; valla, cidden, resmen; verbless lines (Kargo bedava.) |
| Spanish | ES finde, pásate, vale; MX se te antoja; AR voseo pedí, probá; jajaja |
| Portuguese | BR tá, pra, a gente, bora, vem, corre, sextou; PT fixe, bué; kkkk |
| French | on for nous, a dropped ne (c'est pas), questions by intonation, clipped words (dispo, promo, resto, appli) |
| German | mal, doch, halt, eben, ja, auch; gibt's, geht's; gönn dir, hol dir, schau mal vorbei |
| Indonesian | nih, dong, deh, sih, kok, lho, kan, ya, yuk; udah, aja, banget, gimana, buat, cuma, nggak |
| Malay | lah, je, tak, nak, dah, kat, ni, tu; korang, kitorang; jom |
| Filipino | na, pa, lang, naman, talaga, ba, din or rin, nga, kasi, eh; po and opo in replies |
| Tamil | spoken endings: இருக்கு, வந்தாச்சு, பண்ணுங்க, வாங்க, -ன்னு |
| Chinese | 啊, 呀, 吧, 啦, 哦, 嘛, 呢; 超, 巨, 真的 (CN); 喔, 耶, 欸 (TW); 嘅, 咗, 啲 (HK) |
| Japanese | ね and よ, 体言止め, short plain asides (正直, やっぱり) mixed into です・ます |
| Korean | 해요체 endings ~요, ~죠, ~네요, ~거든요; ㅎㅎ; a tilde tail (놀러 오세요~) |
| Thai | นะ, จ้า, น้า, เลย, สิ, มั้ย; one polite set per persona (ค่ะ or ครับ) |
| Vietnamese | nha, nhé, nè, đó, thôi, á; ạ in replies to customers |

Headlines, notices, prices and legal lines stay particle-free.

## 5. Template lines in every language

The same four templates exist everywhere. Letter salutations are warnings; plain hellos are notes (some local brands
do open that way, but the news should come first); a chatbot leftover is an error.

| Language | Letter opener | Engagement bait | Generic CTA | Chatbot leftover |
|:-|:-|:-|:-|:-|
| Hindi | प्रिय ग्राहकों, नमस्ते दोस्तों | दोस्तों को टैग करें, लाइक और शेयर | और जानें | यहाँ आपके लिए कुछ कैप्शन दिए गए हैं |
| Urdu | محترم صارفین | اپنے دوستوں کو ٹیگ کریں | مزید جانیں | یقیناً! یہ رہا آپ کا کیپشن |
| Nepali | प्रिय ग्राहक, आदरणीय ग्राहक महानुभावहरू | साथीहरूलाई ट्याग गर्नुहोस् | | पक्कै पनि! यहाँ केही क्याप्सनहरू छन् |
| Arabic | عملاءنا الكرام، يسعدنا أن نعلن | منشن لصديقك، اكتب تم في التعليقات | اعرف المزيد، لا تفوت الفرصة | |
| Turkish | Değerli müşterilerimiz | arkadaşını etiketle | Daha fazla bilgi için | |
| Spanish | Estimado cliente, Hola a todos | etiqueta a un amigo, dale like si | Más información, Haz clic aquí | ¡Claro! Aquí tienes... |
| Portuguese | Prezado cliente, Olá pessoal | marque aquele amigo | Saiba mais, Clique aqui | Claro! Aqui está uma legenda... |
| French | Chers clients, Bonjour à tous | Identifie un ami | En savoir plus, Cliquez ici | Bien sûr ! Voici... |
| German | Liebe Kundinnen und Kunden | Markiere einen Freund | Mehr erfahren, Hier klicken | Gerne! Hier sind drei Vorschläge |
| Indonesian | Halo Sobat, Pelanggan yang terhormat | tag temanmu, like dan share | Klik di sini | Berikut adalah beberapa caption |
| Malay | Pelanggan yang dihormati, Hai semua | tag kawan korang | Ketahui lebih lanjut | Berikut ialah beberapa kapsyen |
| Filipino | Mahal naming mga customer | i-tag ang barkada | Alamin pa | Narito ang ilang caption |
| Chinese | 尊敬的客户, 亲爱的用户, 大家好 | @你的好友, 评论区扣1 | 了解更多 | 以下是为你生成的文案 |
| Japanese | 皆様こんにちは, お客様各位 | 友達をタグ付け | 詳しくはこちら (often fine) | 以下は投稿文の案です |
| Korean | 존경하는 고객님, 안녕하세요 | 친구 태그, 좋아요와 팔로우 | 자세히 보기 (often fine) | 다음은 캡션입니다, 물론입니다 |
| Thai | เรียนลูกค้าผู้มีอุปการคุณ | แท็กเพื่อน, กดไลก์ กดแชร์ | คลิกที่นี่ | นี่คือแคปชัน... |
| Vietnamese | Kính gửi Quý khách | tag bạn bè, like và share | Tìm hiểu thêm | Dưới đây là một số gợi ý caption |
| Tamil | அன்புள்ள வாடிக்கையாளர்களே | நண்பர்களை டேக் பண்ணுங்க | மேலும் அறிய | |

## 6. Address and code-mixing

Pick the address form and the mixing rule before writing, and keep them the same in the post, the ad and the
replies. For the first twelve languages, `copy.md` §4 has the base row; this adds what goes beyond it.

| Language | Address | Mixing English in |
|:-|:-|:-|
| Hindi | आप with कीजिए or करें | one script per line: Roman lines stay Roman (order karo); Devanagari lines write loans in Devanagari (ऑर्डर, ऑफ़र), brand names in Latin |
| Urdu | آپ with کریں; کیجئے reads old-fashioned | loans in Urdu script (ری چارج، آرڈر), brand names in Latin; Roman Urdu with English is the app voice (scan karo) |
| Nepali | तपाईं with the polite imperative; हजुर in service replies; तिमी for youth; never तँ | loans in Devanagari (अफर, डेलिभरी) with गर्नु (अर्डर गर्नुस्); Roman Nepali is common on Facebook and TikTok |
| Arabic | a plural or no verb; dialect plurals اطلبوا، حيّاكم، الحقوا | English nouns in Arabic script take Arabic grammar (أوردرك، الديليفري); Latin for names only; Arabizi only if the brand already posts that way, never mixed with Arabic script in one line |
| Turkish | siz by default, -(y)In imperatives; -(y)InIz (tıklayınız) is letter style | English nouns take suffixes, with an apostrophe after names and numbers (23.59'a); English verb + etmek (confirm etmek) is mocked office talk |
| Spanish | per market | keep the loans the market uses (link en bio, look, outfit); never spell out a shortened loan (enlace en la biografía) |
| Portuguese | per market | BR delivery, cashback, link na bio; a European form in a BR post reads as the wrong variant |
| French | on for the brand voice; nous for notices | franglais nouns yes (live, story, drop, collab); English hype verbs no; Québec prefers courriel, magasiner, infolettre |
| German | du or Sie | loans joined or hyphenated (Sommer-Sale, Onlineshop); never split compounds (Kunden Service) |
| Indonesian | kamu; kak in marketplace captions and replies; never mix Anda with kamu | English commerce words are normal; English verbs take local affixes (di-cancel, nge-cancel) |
| Malay | anda in lowercase mid-sentence; korang or no pronoun when casual; awak one to one | bahasa rojak is normal for youth, food and commerce; never Indonesian words |
| Filipino | ka and mo; po and opo in service replies and for older readers; never kayo to one reader | English verbs and nouns take Tagalog affixes with a hyphen (mag-order, i-download, na-deliver) |
| Tamil | நீங்க with -ங்க | English nouns take Tamil case endings (ஆர்டருக்கு, store-la); English verbs take பண்ணு (ஆர்டர் பண்ணுங்க); one script per line |
| Chinese | no vocative by default; 姐妹们 and 宝子们 only on female-skewed 小红书 accounts; 家人们 reads as livestream selling; 亲 as Taobao service | a few lowercase Latin words are native (city, citywalk, vlog, OOTD, emo, MBTI); no English sentences; HK mixes more (book位) |
| Japanese | 〜の方 or 皆さん; お客様 in service notices; never あなた | everyday katakana loans are fine (セール, コスパ, タイパ); business katakana (ソリューション, シナジー) reads like a slide deck |
| Korean | drop "you"; 여러분, 고객님, ~님 or a community nickname; never 당신 in ads; 해요체 by default, 합쇼체 for formal notices | loans in Hangul (세일, 쿠폰, 굿즈, 팝업); Latin only for names, short sticker words (NEW, SALE, D-3) and codes |
| Thai | omit คุณ, address groups (ลูกค้าทุกคน, ใครที่...); one admin persona with one particle set; ท่าน only in formal notices | loans in Thai script (โปร, รีวิว, ไลฟ์); Latin for names, sizes, codes and 11.11; one form per word |
| Vietnamese | bạn, mọi người, cả nhà; the brand as mình or nhà mình; quý khách for banks and airlines | English words slot in unchanged (order, ship, freeship, sale, deal, combo, size, ib) |

## 7. Numbers, money and dates (the six not in `copy.md` §4)

| Language | Money | Dates and time | Other |
|:-|:-|:-|:-|
| Korean | 9,900원 (attached), 1만 원; no ₩ or KRW in consumer copy | 9월 24일(목) or 9.24(목); ranges with ~ (9/24~9/30); 오후 2시 or 14:00 | no comma after connective endings |
| Thai | 1,290 บาท, ฿99 with no space, or the tag form 99.- | Buddhist Era: 2026 is พ.ศ. 2569; 24 ก.ย. 69; 10:00 น. | no spaces between words; a space ends a phrase; no full stop |
| Vietnamese | 99.000đ (a full stop for thousands); 99k on social; never 99,000đ | day first (30/9/2026); 20h or 20:00; no AM or PM | k means thousand, so never write k for không near a price |
| Filipino | ₱499; "₱99 lang" is the everyday price line | 10AM, 8PM in everyday posts | |
| Nepali | रु. with Devanagari digits in Nepali script (रु. ९९९); Rs with Western digits in Roman posts; lakh grouping (रु. १,००,०००) | । ends a statement | |
| Indonesian, Malay | Rp49.000, 49rb, 99K (id); RM12.90, RM1,299 (ms) | ms months Mac, Ogos, Disember | an English separator in either is a wrong-format tell |

## 8. Language by language

Each entry: the register people use, then everyday swaps (stiff → plain), then the tells to cut, then one natural
line to calibrate your ear. The lint checks most of the tells (`--lang` code in brackets).

### Hindi (hi)
- **Register.** Everyday speech, not official Hindi. Casual Hindi online is mostly Roman (Hinglish); Devanagari still
  reaches Tier 2 and 3 audiences better. One script per line; English words take a Hindi light verb (order karo, ऑर्डर
  कीजिए) and Hindi postpositions (offers pe, ऐप पर). Shape: a question hook plus a hard fact (Bhook lagi? ₹99 mein
  thali). Peer words (yaar, bhai) only in youth and food voices.
- **Swaps.** चयन करें → चुनें; इसके अतिरिक्त → साथ ही; अतः → इसलिए; परिवर्तित करें → बदलें; पुनः प्रयास करें → दोबारा कोशिश
  करें; प्रदान करते हैं → देते हैं; सुनिश्चित करें → पक्का कर लें; क्रय करें → ख़रीदें; निःशुल्क → फ़्री; संगणक, कुंजीपटल →
  कंप्यूटर, कीबोर्ड.
- **Tells.** "सिर्फ़ X नहीं, बल्कि Y"; rule of three (स्वाद, सेहत और सुकून); "का आनंद लें" and "खोजें" CTAs; नई ऊँचाइयों पर;
  स्वाद की यात्रा; द्वारा passives; Devanagari words dropped into a Roman line (Monsoon sale में 30% off); a
  five-sentence apology for a late order.
- **Natural.** Chai ke saath samosa? Sirf ₹49 mein, aaj raat 10 baje tak.

### Urdu (ur)
- **Register.** The spoken Urdu of Pakistan, close to everyday Hindustani, not the Persian and Arabic literary layer.
  Microsoft's guide: short sentences, no passive, no corporate "we", کریں not کیجئے. Roman Urdu with English is the
  app voice; Urdu script with English loans in Urdu letters (ری چارج، آرڈر) reaches mass audiences. Hooks are short
  questions (بیلنس کم ہے؟). Type Urdu ک, ی, ہ, never the Arabic look-alikes ك, ي, ه (they break search).
- **Swaps.** کیجئے → کریں; ملاحظہ فرمائیں → دیکھیں; تشریف لے جائیے → جائیں; لطف اندوز ہوں → مزے کریں; مستفید ہوں →
  فائدہ اٹھائیں; علاوہ ازیں → اور، ساتھ ہی; لہٰذا → اس لیے; بدرجہ اتم → بہت زیادہ; گراں قدر → اہم.
- **Tells.** صرف X نہیں بلکہ Y; تجربہ کریں and دریافت کریں; ذائقے کا سفر; نئی بلندیوں تک; یقینی بنائیں; ہم بہترین سروس فراہم
  کرتے ہیں; کی جانب سے passives; honorific verbs in a caption (ملاحظہ فرمائیں).
- **Natural.** Bijli ka bill due hai? App se 2 minute mein pay karo, 50 rupay cashback bhi.

### Nepali (ne)
- **Register.** तपाईं with the polite imperative; the spoken गर्नुस् in captions, गर्नुहोस् in UI and notices, one form a
  post. Sanskrit tatsam words and the written present in दछ (गर्दछ, पर्दछ) mark notices; posts say गर्छ, पर्छ. English
  words take गर्नु (अर्डर गर्नुस्, recharge garnus). Warm markers: ल, नि, त, है as a tag; दाइ and दिदी in service copy.
- **Swaps.** रूपान्तर गर्नुहोस् → बदल्नुस्; उपयोग गर्नुहोस् → चलाउनुस्; हासिल गर्नुहोस् → पाउनुस्; गर्दछ → गर्छ; प्रदान गर्दछौं →
  दिन्छौं; सुनिश्चित गर्नुहोस् → पक्का गर्नुस्; यथाशीघ्र → चाँडै; अत्यन्त → एकदम; निःशुल्क → फ्री; हेतु → लागि.
- **Tells.** केवल X होइन, यो Y हो (while "X मात्र होइन, Y पनि" is native); स्वादको यात्रा; नयाँ उचाइमा; Hindi words in Nepali
  (और, आपका, हैं); notice formulas as a post (ग्राहक महानुभावहरूमा जानकारी गराइन्छ); तपाईंको in every phrase.
- **Natural.** ल, आजै अर्डर गर्नुस्! साँझ ६ बजेसम्मको अर्डर भोलि बिहानै घरमा।

### Arabic (ar)
- **Register.** The market's own dialect on social; standard Arabic reads correct but cold, "like an old radio news
  bulletin" in one copywriter's words. One dialect a post (Gulf, Egyptian, Levantine or Moroccan). Shape: a dialect
  question, then price, time and place in one short clause; verbless lines are fine (القهوة الثانية علينا). Plural
  verbs or no verb, since singular verbs are gendered.
- **Swaps.** الآن → الحين / دلوقتي / هلق / دابا; جيد جداً → زين / كويس أوي / منيح كتير; تم افتتاح فرعنا → فتحنا فرعنا; نقوم
  بتوصيل طلبك → نوصّلك طلبك; مُعدّ من قبل طهاتنا → طهاتنا يحضّرونه كل صبح; التوصيل مجاني → التوصيل علينا / ببلاش; احصل على →
  خذ / خد; لفترة محدودة → لين الخميس / لحد الخميس بس; لا تفوت الفرصة → لا يفوتكم / الحقوا.
- **Tells.** ليس مجرد X بل Y; في عالم اليوم المتسارع; علاوة على ذلك; تم and قام بـ helper verbs; بواسطة and من قبل; the English
  list comma (برجر، بيتزا، وحلا → برجر وبيتزا وحلا); a fronted phrase and a comma (في رمضان، نقدم...); انغمس، أطلق العنان،
  ارتقِ; تجربة فريدة من نوعها.
- **Natural (Gulf).** القهوة الثانية علينا لين الخميس، حيّاكم في فرع العليا.

### Turkish (tr)
- **Register.** Spoken Turkish: drop the written -mAktAdIr tense and the extra -DIr (Mağazamız Kadıköy'dedir →
  Mağaza Kadıköy'de), and drop pronouns the verb ending already carries. siz by default with -(y)In imperatives
  (deneyin); sen once the audience expects it. Verbless lines are normal (Kargo bedava. Sepette %30.). Use -Ip or
  -ArAk instead of chains of ve; never start a sentence with Ve.
- **Swaps.** sizlerle buluşmaktadır → geldi; hizmet vermektedir → açığız; ...'e sahip olun → (the result: Saçın ilk
  yıkamada yumuşasın); tarafından hazırlanan → şeflerimizin hazırladığı; deneyimleyin → deneyin, tadına bakın; Daha fazla
  bilgi için tıklayınız → Detaylar linkte; Doğal olarak → Haliyle.
- **Tells.** önemli bir rol oynamaktadır; Günümüzde openers; sadece X değil, aynı zamanda Y; bir X'ten fazlası;
  deneyimleyin; sahip olun; Sizin için ... size; a spare bir (harika bir fiyata bir kalite); English verb + etmek.
- **Natural.** Kargo bedava, sepette %30. Pazar 23.59'a kadar.

### Spanish (es)
- **Register.** Fact first, one idea a line. Machine Spanish reads ceremonious, relentlessly positive and generic,
  with rounded endings (Maldita.es). Write for the market: ES finde, pásate, vale; MX quincena, se te antoja, meses sin
  intereses; AR voseo (pedí, probá) and cuotas sin interés; CO usted in commerce. Concrete question hooks (¿Plan para el
  sábado?), never the bare one-word reveal (¿El secreto?). Sentence case headlines.
- **Swaps.** adquirir → comprar; realizar su pedido → pide / pedí / pida; efectuar el pago → pagar; contamos con →
  tenemos; con el objetivo de → para; le informamos que → (give the news); no dude en contactarnos → escríbenos /
  escribinos; le invitamos a visitarnos → pásate / date una vuelta / vení; obsequio → regalo; establecimiento → tienda.
- **Tells.** sumérgete, embárcate; al siguiente nivel, eleva tu; No es solo X, es Y; ¿El secreto?; cabe destacar, en
  resumen, juega un papel crucial; Title Case; estaremos enviando; a trailing gerund (haciendo que tu piel brille);
  Estamos emocionados de anunciar; Siéntete libre de.
- **Natural (es-ES).** Este finde, 2x1 en todas las pizzas medianas. Pídelas en la app hasta el domingo a las 23:59.

### Portuguese (pt)
- **Register.** BR casual is written the way people talk (tá, pra, a gente, bora, corre, chegou, sextou); PT-PT is
  more reserved and has its own words (fixe, bué, malta, telemóvel) and estar a + infinitive where BR uses the gerund.
  Mixing the two is a wrong-variant tell, and models default to PT-PT. Plain é and tem, not possui or conta com.
  Chat forms (vc, blz, kkkk) in replies and playful captions only, never on banners. Sentence case.
- **Swaps.** adquirir → comprar; efetuar o pagamento → pagar; possui, conta com → tem; utilizar → usar; com o objetivo
  de → pra (BR), para; gratuito → grátis; solicitar → pedir; no momento → agora; informamos que → (give the news);
  aguardamos a sua visita → passa aqui (BR), aparece (PT); estabelecimento → loja.
- **Tells.** no cenário atual; mergulhe, embarque nessa jornada; ao próximo nível, eleve, potencialize; não é apenas X,
  é Y, and a punchline closer (E isso muda tudo.); vale ressaltar, em suma; desempenha um papel fundamental; tapeçaria,
  testemunho; Title Case (Dia Das Mães); gerundismo (vamos estar enviando).
- **Natural (pt-BR).** Tá chovendo em SP? A gente entrega em até 40 minutos na zona sul, é só pedir pelo app.

### French (fr)
- **Register.** Familier on consumer social: short or verbless lines (Nouveau : ..., Petite faim ?), questions by
  intonation (Vous venez samedi ?), on for the brand (On vous attend samedi), a dropped ne only in playful posts.
  vous by default; tu for youth, sport and fashion; one form everywhere. Clipped words (promo, dispo, resto, appli)
  fine outside banking, health and B2B. French brands are known for short witty replies to the actual comment.
- **Swaps.** afin de → pour; au sein de → chez, dans; dans le cadre de → pour, pendant; mettre en place → lancer,
  faire; il convient de → il faut; effectuer un achat → acheter; N'hésitez pas à nous contacter → Une question ?
  Écrivez-nous en MP; Nous avons le plaisir de vous annoncer → C'est officiel : ...; impacter → toucher; adresser un
  problème → régler un problème; faire du sens → c'est logique.
- **Tells.** plongez dans l'univers de; dans un monde où; il est important de noter, en somme; révolutionnaire et
  captivante in clusters; plus qu'un X, un Y; que vous soyez X ou Y; élevez votre, libérez votre potentiel; voyage
  culinaire; poetic filler (un instant suspendu, une promesse murmurée).
- **Natural.** Pause café ? Le latte est à 3,50 € jusqu'à 11 h.

### German (de)
- **Register.** du, short main clauses and modal particles on consumer social (Schau mal vorbei, Probier's doch aus,
  Ist halt Herbst); a higher rate of "auch" is the strongest single sign German was not translated. Sie for finance,
  health and B2B is still plain with short sentences and one fact. Nominalstil and Amtsdeutsch read like a letter
  from the authorities: put an actor and a verb first. Regional voice only when it is real (Moin, Servus).
- **Swaps.** zwecks → für; bezüglich → zu, wegen; Die Lieferung erfolgt am Montag → Wir liefern am Montag; zur Anzeige
  bringen → anzeigen; im Rahmen der Aktion → bei der Aktion; zeitnah → bis Freitag; umgehend → sofort; die
  Inanspruchnahme → nutzen; bzw. → oder; ein Problem adressieren → angehen; eruieren → klären.
- **Tells.** Tauchen Sie ein in die Welt; in der heutigen schnelllebigen Welt; es ist wichtig zu beachten, Fazit:;
  auf das nächste Level, entfessle dein Potenzial; nahtlos, ganzheitlich, maßgeschneidert, Mehrwert; Das ist nicht nur
  X. Das ist Y.; zeugt von, unterstreichend; im Herzen von, eingebettet in; Gerne! Hier sind drei Vorschläge; Wir
  freuen uns, Ihnen mitteilen zu dürfen; split compounds (Kunden Service).
- **Natural.** Mittagstisch in 10 Minuten, werktags ab 11:30 Uhr. Schau mal vorbei!

### Indonesian (id)
- **Register.** The way people talk: short clauses ending in particles (nih, dong, deh, sih, yuk), short forms (butuh,
  pakai, udah, aja, banget, nggak). kamu by default, kak in marketplace captions and replies, gue and lo only for a
  Jakarta youth persona; never mix Anda with kamu. English commerce words are normal (checkout, flash sale, restock);
  one trend word a post (mager, gercep, racun). Shape: a question hook, one fact, one action with yuk or buruan.
- **Swaps.** membutuhkan → butuh; disarankan → sebaiknya; tolong, mohon, silakan → (drop in product copy); namun
  demikian → tapi; menggunakan → pakai; merupakan → adalah, or drop; oleh karena itu → jadi, makanya; selain itu →
  juga; tidak → nggak; sangat murah → murah banget; hanya → cuma, aja.
- **Tells.** di era digital saat ini; tak dapat dipungkiri; tidak hanya ... tetapi juga, bukan sekadar ... melainkan;
  merupakan salah satu; di mana as a relative pronoun; no particles anywhere (Segera lakukan pembelian); pelaksanaan
  ... dilakukan; formal passives; rasakan pengalaman; Anda with kak.
- **Natural.** Stoknya tinggal dikit nih, buruan ya! Diskon 20% sampai jam 12 malam.

### Malay, Malaysia (ms)
- **Register.** Everyday Malaysian Malay: tak, nak, je, dah, kat, lah; korang, kitorang. Bahasa rojak (weekend, sale,
  order, best gila, jom, syok, tapau) is normal for youth, food and commerce; banks, telcos and government-linked
  brands stay close to standard Malay and often post bilingual captions. anda in lowercase mid-sentence; saya or kami
  for the brand, never aku or gua. Never write Indonesian (bisa, gratis, ongkir, diskon, karena, banget, yuk).
- **Swaps.** tidak → tak; hendak → nak; sahaja → je; sudah → dah; di sana → kat sana; kalian → korang; walau
  bagaimanapun → tapi; rujuk → tengok; cantik → cun; gratis ongkir → penghantaran percuma; diskon → diskaun; unduh →
  muat turun; kata sandi → kata laluan; Idulfitri → Hari Raya Aidilfitri, maaf zahir dan batin.
- **Tells.** Indonesian words and particles; capital Anda mid-sentence; Indonesian number format (RM1.299 → RM1,299);
  dalam dunia yang pantas berubah; bukan sekadar X, tetapi Y; rasai pengalaman; Kami bangga memperkenalkan.
- **Natural.** Menu baru dah sampai! Ayam madu pedas RM13.90, jom try.

### Filipino and Taglish (tl)
- **Register.** Taglish is the normal written register online; all-Tagalog copy reads like a school text or a
  translation. English verbs and nouns take Tagalog affixes with a hyphen (mag-order, i-download, na-deliver).
  Particles carry the tone (na, pa, lang, naman, talaga); hooks like Order na!, Tara na!, Sulit!; prices as "₱99 lang".
  ka and mo in ads, po and opo in service replies. Predicate first (Bukas na ang store namin!), not the formal ay order.
- **Swaps.** ngunit, subalit → pero; upang → para; sapagkat → dahil, kasi; alinsunod sa → ayon sa; makipag-ugnayan →
  i-message; nakararanas ng mga problema → nagkakaproblema; mangyaring bisitahin → i-check; sa pamamagitan ng
  paggamit ng → gamit ang; lamang → lang; kayo, inyo (to one reader) → ka, mo.
- **Tells.** tuklasin, galugarin; maranasan ang; paglalakbay tungo sa; hindi lamang ... kundi pati na rin; sa mabilis na
  mundo ngayon; mangyaring; ay inversion (Ang aming tindahan ay bukas na); all-Tagalog where people use English
  (magmamaneho → magda-drive). Dated slang: lodi, petmalu, werpa.
- **Natural.** Crispy pa rin kahit i-deliver, ₱99 lang. Order na!

### Chinese (zh)
- **Register.** Short clauses, the concrete fact first, then a personal reaction; sentence-final particles; hooks like
  救命, 谁懂, 咱就是说. 活人感 (sounding like a living person: a visible founder, self-deprecating replies) is the 2025
  answer to AI flavour. zh-CN, zh-TW and zh-HK are separate versions: TW uses 影片, 品質, 資訊, 小編, 粉專, never
  auto-convert. Slang ages in months (绝绝子 and yyds are gone); one trend word a post at most.
- **Swaps.** 进行购买 → 买; 使用 → 用; 非常 → 很, 超; 例如 → 比如; 值得注意的是 → 还有一点; 旨在 → 就是为了; 因而 → 所以;
  此外 → 还有, 而且; 通过线上的方式购买 → 网上就能买; 于9月24日开售 → 24号开卖; 这是一个非常实用的礼物 → 这个礼物很实用.
- **Tells.** 在当今快节奏的时代; 不仅仅是X，更是Y; 值得注意的是, 总而言之, 综上所述; 首先…其次…最后…; 赋能, 全链路, 闭环;
  进行 + verb; 至关重要, 不可或缺; the 2026 chatbot tic 稳稳接住你的; stacked emoji bullets (✅💡🚀); untranslated English
  where Chinese has an everyday word.
- **Natural (zh-CN).** 救命，这个杯子也太能装了吧，750ml塞进包里刚好，现在39.9包邮。

### Japanese (ja)
- **Register.** Soft です・ます with ね and よ, mixed with 体言止め and short plain asides (正直, やっぱり); machine
  Japanese ends every sentence in 〜ます。 and reads like a manual. Catch lines without keigo. Brand accounts often post
  as a named operator (中の人). Everyday katakana loans are fine (セール, コスパ); business katakana is not. Address a
  segment (初めての方, お近くの方) or 皆さん; never あなた.
- **Swaps.** 休業させていただきます → 休業いたします, お休みです; 〜することができます → 〜できます; 〜と言えるでしょう →
  〜です, or cut; 以上のことから → cut; 〜という点において → 〜なら; お越しになられる → いらっしゃる; こちらが新作になります →
  こちらが新作です; ソリューション → what it fixes; 本日 → 今日.
- **Tells.** 今日の急速に変化する世界において; 単なるXではなく; 探っていきましょう; と言えるでしょう; 第一に…第二に…;
  可能性を解き放つ, 魔法のように, ゲームチェンジャー; アプリからご利用することができます; a colon lead-in (ご紹介します：);
  monotone 〜ます。endings; emoji bullets (✅軽い ✅安い); double keigo; おじさん構文 (heavy emoji plus 、、、).
- **Natural.** 9月26日(土)は渋谷店で試食会やります。13時からなので、お近くの方はぜひ。

### Korean (ko)
- **Register.** 해요체 by default (Toss writes all product copy in it); 합쇼체 only for formal notices (delays, recalls,
  price changes). Endings ~요!, ~죠, ~네요; ㅎㅎ is the brand-safe laugh; noun fragments land (신메뉴 출시!, 선착순
  100명!). Drop subjects and objects and vary sentence length. Drop "you": 여러분, 고객님, a community nickname, never
  당신. Loans in Hangul. Trend slang backfires when the brand misses its origin; stable words are safe (신상, 무배, 핫딜,
  재입고, 가성비).
- **Swaps.** 구매하실 수 있습니다 → 살 수 있어요; 보습력을 가지고 있습니다 → 보습력이 좋아요; 전문가에 의해 제작된 →
  전문가가 만든; ~에 있어서 → ~는; 엄선되어진 → 직접 고른; 다음과 같습니다 → (list directly); 혜택을 제공합니다 → 혜택
  드려요; 이벤트가 진행됩니다 → 이벤트 해요; 이용해 주시기 바랍니다 → 이용해 주세요; 금일, 익일 → 오늘, 내일; 해당 제품 → 이
  제품.
- **Tells.** 단순한 X가 아니라 Y and X를 넘어 Y로 (measured 9.2 times more often in AI text); ~를 가지고 있다; 에 의해 and
  되어지다; 당신의 in every line; ~들 on every plural; 중요합니다 hedges; 또한, 결론적으로 opening sentences; a comma after
  connective endings; every subject spelled out in equal-length sentences; dashes (줄표) in place of commas.
- **Natural.** 보온 12시간, 차 컵홀더에 쏙 들어가요. 오늘 주문하면 내일 도착!

### Thai (th)
- **Register.** Brand pages talk like a person, often as แอด, with one fixed particle set (ค่ะ, นะคะ for a female
  persona, ครับ, นะครับ for a male one); นะ, จ้า, เลย on neutral pages. Mostly omit คุณ and address groups (ลูกค้าทุกคน,
  ใครที่..., สายคาเฟ่). Loans in Thai script, one form a word. No spaces between words; a space ends a phrase; no full
  stop. Stable commerce words: โปร, ส่งฟรี, ของมันต้องมี, ป้ายยา, ทักแชท, กดสั่ง; dated slang only in a meme voice.
- **Swaps.** รับประทาน → กิน, ทาน; ถูกออกแบบมาเพื่อ → ทำมาเพื่อ; มีความสามารถในการกันน้ำ → กันน้ำได้; ณ ขณะนี้ → ตอนนี้;
  เนื่องจาก → เพราะ; ในกรณีที่ → ถ้า; เป็นจำนวนมาก → เยอะ; ประสบการณ์ที่ราบรื่น → ใช้ง่าย ลื่น ไม่สะดุด; ลูกค้าผู้มีอุปการคุณ →
  ลูกค้าทุกคน; ทางร้านขอแจ้งให้ทราบว่า → แจ้งนะคะ; ดำเนินการสั่งซื้อ → กดสั่งได้เลย.
- **Tells.** ถูก passives for good news (ถูกคัดสรรมาอย่างพิถีพิถัน); ไม่ใช่แค่ X แต่ยัง Y; นอกจากนี้, อีกทั้ง, ยิ่งไปกว่านั้น;
  ในยุคปัจจุบัน; คุณ and ของคุณ in every clause; มันคือ ... ที่ clefts; การ and ความ noun chains; คุณเคยสงสัยไหมว่า openers;
  ยกระดับ, ปลดล็อกศักยภาพ; puffery (ไร้ที่ติ, เหนือระดับ).
- **Natural.** หวานน้อย เข้มกำลังดี แก้วละ 45 บาท สั่งเลยค่ะ

### Vietnamese (vi)
- **Register.** One particle a sentence carries the warmth (nha in the South and Centre, nhé in the North and in
  writing, nè), ạ when answering a customer. bạn, mọi người or cả nhà for the reader; the brand as mình, tụi mình or
  nhà mình; quý khách only for banks and airlines. English words slot in unchanged (order, freeship, sale, combo, ib).
  Short clauses joined by commas, price and deadline early, a question tag (chưa?, nè?) instead of a formal CTA.
  Teencode (ko, đc) in comments and DMs only.
- **Swaps.** Kính gửi Quý khách → (drop it, open with the news); Quý khách → bạn, cả nhà; chúng tôi → mình, nhà mình;
  Vui lòng liên hệ → Nhắn shop nha; Vui lòng đợi → chờ xíu nha; Tải về không thành công → Không tải được; sử dụng →
  dùng; thực hiện, tiến hành → làm; miễn phí vận chuyển → freeship; đặt hàng → chốt đơn.
- **Tells.** Trong bối cảnh ... phát triển không ngừng; không chỉ là X mà còn là Y (narrow form); Hơn nữa, Thêm vào đó,
  Tóm lại; Dưới đây là một số gợi ý caption; được ... bởi passives; điều này, việc này fillers; relative clauses with
  nơi; một cách + adjective; của bạn in every clause; 99,000đ.
- **Natural.** Cà phê muối về lại menu rồi nè, 29k tới 14h thôi nha.

### Tamil (ta)
- **Register.** Spoken Tamil or Tanglish on social; written (literary) Tamil reads like a notice and is never used in
  informal talk. Spoken forms: இருக்கு, வந்தாச்சு, கிடைக்கும், பண்ணுங்க, வாங்க; -ங்க plurals and pronouns. English nouns
  take Tamil case endings (ஆர்டருக்கு), English verbs take பண்ணு (ஆர்டர் பண்ணுங்க). Spoken Tamil keeps many Sanskrit-origin
  words (சந்தோஷம், சுலபம்) where pure-Tamil coinages sound official. Sri Lanka: skip Chennai slang, get a local check.
- **Swaps.** இருக்கிறது → இருக்கு; கிடைக்கிறது → கிடைக்கும்; உள்ளது → இருக்கு; வேண்டும் → வேணும்; செய்யுங்கள் → பண்ணுங்க;
  வாருங்கள் → வாங்க; காத்திருங்கள் → வெயிட் பண்ணுங்க; கொடுங்கள் → குடுங்க; தவறவிடாதீர்கள் → மிஸ் பண்ணிடாதீங்க; நீங்கள் →
  நீங்க; உங்களுடைய → உங்களோட; என்று → -ன்னு.
- **Tells.** written verb forms in a caption (இப்போது கிடைக்கிறது); ஆர்டர் செய்யுங்கள்; செய்யக்கூடியதாக இருக்கும்;
  கண்டறியுங்கள், அனுபவியுங்கள்; பயணம் metaphors; வெறும் X அல்ல; புதிய உயரங்களுக்கு; உங்கள் in every line; literal idioms
  (கேக் துண்டு போல எளிது → ரொம்ப ஈஸி).
- **Natural.** புது ஃப்ளேவர் வந்தாச்சு! இப்பவே ஆர்டர் பண்ணுங்க.

## 9. Before you ship a line in any of these languages

1. Written from the brief in the target market's social register, not translated from English (`copy.md` §4).
2. Address form, dialect or variant, script and mixing rule fixed and kept (§6).
3. None of the calques (§2) or translated structures (§3); a doer and a verb in every sentence.
4. The spoken layer present in casual captions, absent from headlines, prices and legal lines (§4).
5. Numbers, money, dates and punctuation in the local form (§7, `copy.md` §4).
6. `copylint --lang <code>` clean of errors and warnings; `copyjudge --locale <market>` PASS or better.
7. A native reader has read it on the render.
