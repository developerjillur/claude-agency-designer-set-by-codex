#!/usr/bin/env python3
"""nexa-research: the tools behind the research skill. Claude does the searching, reading and judging with its own
web search, web fetch, browser and subagents; this script adds what those tools do not: sources a search engine does
not show (YouTube numbers and comments, scholarly indexes, Hacker News, Wikipedia), exact quote checks against the
page itself, a claim ledger with source grades, and the gates a research pack must pass before a writer uses it.

Standard library only, Python 3.9 or newer.

  research.py doctor
  research.py new DIR --topic "..."                 a research folder: plan.md, sources.json, ledger.json, notes/
  research.py youtube search "query" [--n 20] [--details]
  research.py youtube comments VIDEO [--n 100] [--sort top|new]
  research.py youtube captions VIDEO [--lang en]
  research.py academic "query" [--n 8] [--source all|openalex|crossref|arxiv|semantic]
  research.py hn "query" [--n 10]
  research.py wiki "query" [--lang en] [--n 5]
  research.py fetch URL [--meta] [--out FILE]
  research.py wayback URL
  research.py source add DIR --url U --title T --publisher P [--date D] [--kind K] --grade A|B|C|D|E
  research.py claim add DIR --text "..." --source ID [--source ID2] --quote "..." [--where "..."] [--key]
  research.py claim set DIR c3 --status manual|conflicting|removed|unverified [--note "how, by whom"]
  research.py note add DIR --bank voice|story|competitors --text "..." [--source S] [--set key=value ...]
  research.py youtube comments VIDEO --bank DIR [--keep 60]     the audience's words straight into the voice bank
  research.py youtube search "query" --bank DIR                 the videos into the competitor list
  research.py audit FILE --dir DIR [--level final]   every factual sentence of a brief or article carries a claim id
  research.py budget DIR [--add N --by AGENT] [--cap 200]   the session's shared WebSearch count
  research.py verify DIR [--ids c1,c2] [--fresh]
  research.py check DIR [--level draft|standard|final] [--fresh-years N]
  research.py pack DIR

Every command prints JSON on stdout (logs go to stderr); `check` exits 1 when a gate fails.
"""
import argparse
import datetime
import hashlib
import html
import html.parser
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SKILL_VERSION = "2026.09.26.1"
UA = os.environ.get("NEXA_RESEARCH_UA",
                    "nexa-research/1.0 (+https://github.com/developerjillur/claude-agency-designer-set-by-codex)")
CACHE = Path(os.environ.get("NEXA_CACHE", str(Path.home() / ".cache" / "nexa-writing"))) / "pages"
GRADES = {
    "A": "primary: the original study, dataset, filing, law, official statistics, the person's own words on record",
    "B": "edited secondary: reputable news with corrections policy, peer-reviewed reviews, official documentation",
    "C": "credible trade or expert source that cites its evidence",
    "D": "blogs, forums, social posts, marketing pages: opinion and the audience's words, never a fact on its own",
    "E": "unverifiable: anonymous, content farms, AI-written pages, dead with no archive",
}
KINDS = ("study", "dataset", "official", "news", "book", "expert", "video", "podcast", "forum", "social", "company",
         "review", "other")
STATUSES = ("unverified", "verified", "unsupported", "conflicting", "manual", "removed")


def log(message):
    print(f"[nexa-research {time.strftime('%H:%M:%S')}] {message}", file=sys.stderr, flush=True)


def die(message, code=2):
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    sys.exit(code)


def emit(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------------------------------------------------ http

def http_get(url, timeout=30, accept="application/json", retries=2, headers=None):
    """GET with an honest user agent, backoff on 429 and 5xx. Returns (status, bytes, final_url)."""
    hdrs = {"User-Agent": UA, "Accept": accept, "Accept-Language": "en;q=0.9, *;q=0.5"}
    hdrs.update(headers or {})
    delay = 2.0
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers=hdrs)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read(), resp.geturl()
        except urllib.error.HTTPError as e:
            body = e.read() if hasattr(e, "read") else b""
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                wait = retry_after(e.headers.get("Retry-After"), delay) if e.headers else delay
                log(f"{urllib.parse.urlsplit(url).netloc}: HTTP {e.code}, waiting {min(wait, 30):.0f} s")
                time.sleep(min(wait, 30))
                delay *= 2
                continue
            return e.code, body, url
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt < retries:
                time.sleep(delay)
                delay *= 2
                continue
            return 0, str(e).encode(), url
    return 0, b"", url


def retry_after(value, default):
    """Retry-After is seconds or an HTTP date (RFC 7231); anything unreadable falls back to the default."""
    if not value:
        return default
    try:
        return max(0.0, min(120.0, float(value)))
    except ValueError:
        pass
    try:
        import email.utils
        when = email.utils.parsedate_to_datetime(value)
        return max(0.0, min(120.0, when.timestamp() - time.time()))
    except (TypeError, ValueError, IndexError, OverflowError):
        return default


def get_json(url, timeout=30):
    status, body, _ = http_get(url, timeout=timeout)
    if status != 200:
        return None, f"HTTP {status}: {body[:200].decode('utf-8', 'replace')}"
    try:
        return json.loads(body.decode("utf-8")), None
    except ValueError as e:
        return None, f"not JSON: {e}"


# ------------------------------------------------------------------------------------------------- page to text

class _TextParser(html.parser.HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "template", "iframe", "head"}
    BLOCK = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "section", "article", "blockquote",
             "header", "footer", "figcaption", "pre", "table", "ul", "ol"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip, self.title, self.meta, self._in_title = [], 0, "", {}, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            key = (a.get("property") or a.get("name") or a.get("itemprop") or "").lower()
            if key and a.get("content"):
                self.meta.setdefault(key, a["content"])
        if tag in self.SKIP and tag != "head":
            self.skip += 1
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in self.SKIP and tag != "head" and self.skip:
            self.skip -= 1
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self.skip:
            self.parts.append(data)


def html_to_text(raw):
    p = _TextParser()
    try:
        p.feed(raw)
    except Exception:  # noqa: BLE001 (broken markup still yields what was parsed)
        pass
    text = "".join(p.parts)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
    meta = p.meta
    info = {
        "title": (meta.get("og:title") or p.title or "").strip(),
        "site": meta.get("og:site_name", ""),
        "published": meta.get("article:published_time") or meta.get("datepublished") or meta.get("date")
        or meta.get("dc.date") or meta.get("citation_publication_date") or "",
        "author": meta.get("author") or meta.get("article:author") or meta.get("citation_author") or "",
        "description": meta.get("og:description") or meta.get("description") or "",
    }
    return text, info


def fetch_page(url, fresh=False):
    """Text and metadata of a page, cached by URL. Returns dict(ok, url, status, text, info, cached, error)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]
    cfile = CACHE / f"{key}.json"
    if not fresh and cfile.exists():
        try:
            data = json.loads(cfile.read_text(encoding="utf-8"))
            data["cached"] = True
            return data
        except ValueError:
            pass
    status, body, final = http_get(url, accept="text/html,application/xhtml+xml,*/*;q=0.8", retries=1)
    if status != 200:
        return {"ok": False, "url": url, "status": status, "cached": False,
                "error": f"HTTP {status}" + (" (blocked for scripts: read it with WebFetch or the browser)"
                                             if status in (401, 403) else "")}
    raw = body.decode("utf-8", "replace")
    if body[:5] == b"%PDF-":
        return {"ok": False, "url": url, "status": status, "cached": False,
                "error": "PDF: read it with WebFetch or a PDF reader; mark the claim 'manual' after checking"}
    text, info = html_to_text(raw)
    data = {"ok": True, "url": url, "final_url": final, "status": status, "text": text, "info": info,
            "fetched_at": now_iso(), "cached": False}
    cfile.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


# ---------------------------------------------------------------------------------------------- quote matching

QUOTE_MAP = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2013": "-",
                           "\u2014": "-", "\xa0": " ", "\u2026": "..."})


def normalize(text):
    text = html.unescape(text or "").translate(QUOTE_MAP).lower()
    text = re.sub(r"[^\w\s%.$€£৳-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def quote_in_text(quote, text):
    """(found, how): exact after normalizing, or 90 % of the quote's words in order inside a window of the page."""
    q, t = normalize(quote), normalize(text)
    if not q:
        return False, "empty quote"
    if q in t:
        return True, "exact"
    qw = q.split()
    if len(qw) < 4:
        return False, "not found (short quote needs an exact match)"
    tw = t.split()
    need = max(3, int(round(len(qw) * 0.9)))
    window = len(qw) + 6
    first = {w for w in qw[:3]}
    for i, w in enumerate(tw):
        if w not in first:
            continue
        seg = tw[i:i + window]
        j = hits = 0
        for word in seg:
            if j < len(qw) and word == qw[j]:
                hits += 1
                j += 1
            elif j + 1 < len(qw) and word == qw[j + 1]:
                hits += 1
                j += 2
        if hits >= need:
            return True, f"close ({hits} of {len(qw)} words in order)"
    return False, "not found"


# ------------------------------------------------------------------------------------------------------- youtube

def yt_id(value):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([A-Za-z0-9_-]{11})", value or "")
    if m:
        return m.group(1)
    return value if re.fullmatch(r"[A-Za-z0-9_-]{11}", value or "") else None


def ytdlp(args, timeout=300):
    cmd = ["yt-dlp", "--no-warnings", "--no-update"] + args
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        die("yt-dlp not found: brew install yt-dlp (or pip install yt-dlp)")
    except subprocess.TimeoutExpired:
        die(f"yt-dlp timed out after {timeout} s")
    return proc


def views_per_day(views, upload_date):
    if not views or not upload_date:
        return None
    try:
        d = datetime.datetime.strptime(str(upload_date), "%Y%m%d").date()
    except ValueError:
        return None
    days = max(1, (datetime.date.today() - d).days)
    return round(views / days, 1)


BANKS = {"voice": ("voice-bank.json", "v"), "story": ("story-bank.json", "st"), "competitors": ("competitors.json", "k")}
# What each bank's items hold (other keys may be added with --set):
#   voice:       text (the words as written), source, kind (comment, review, question, search, dm, interview), lang,
#                likes, segment
#   story:       text (the story in one or two lines), source, people, turn, claims (claim ids), mode
#   competitors: url, title, channel, hook (the opening line, from the captions), angle, result (views or another
#                known outcome), length_s, published, x_median_views, notes


def bank_add(d, bank, items):
    """Append items to a note bank with fresh ids; a voice item whose text is already there is skipped."""
    name, prefix = BANKS[bank]
    path = rdir(d) / "notes" / name
    if not path.parent.exists():
        die(f"no notes folder in {rdir(d)}: run `research.py new` first")
    data = load(path, {"schema": f"nexa.{bank}/1", "items": []})
    have = {(it.get("text") or "").strip().lower() for it in data["items"]} if bank == "voice" else set()
    have_urls = {it.get("url") for it in data["items"] if it.get("url")}
    added = []
    for it in items:
        key = (it.get("text") or "").strip().lower()
        if bank == "voice" and (not key or key in have):
            continue
        if bank == "competitors" and it.get("url") in have_urls:
            continue
        it = dict(it, id=_next_id(data["items"], prefix), added=now_iso())
        data["items"].append(it)
        added.append(it["id"])
        have.add(key)
        have_urls.add(it.get("url"))
    save(path, data)
    return {"bank": str(path), "added": len(added), "ids": added, "total": len(data["items"])}


def cmd_note(args):
    item = {"text": args.text}
    if args.source:
        item["source"] = args.source
    for kv in args.set or []:
        if "=" not in kv:
            die(f"--set takes key=value, got {kv!r}")
        k, v = kv.split("=", 1)
        item[k.strip()] = v.strip()
    if args.bank == "competitors" and not (item.get("url") or item.get("source")):
        die("a competitor needs --set url=... (or --source)")
    emit(dict({"ok": True}, **bank_add(args.dir, args.bank, [item])))


def cmd_youtube(args):
    if args.what == "search":
        n = max(1, min(args.n, 50))
        proc = ytdlp(["--flat-playlist", "--dump-json", f"ytsearch{n}:{args.query}"])
        rows = []
        for line in proc.stdout.splitlines():
            try:
                d = json.loads(line)
            except ValueError:
                continue
            rows.append({"id": d.get("id"), "title": d.get("title"), "channel": d.get("channel") or d.get("uploader"),
                         "views": d.get("view_count"), "duration_s": d.get("duration"),
                         "url": f"https://www.youtube.com/watch?v={d.get('id')}"})
        if args.details:
            for r in rows:
                p = ytdlp(["--skip-download", "--dump-json", r["url"]], timeout=120)
                try:
                    d = json.loads(p.stdout.splitlines()[-1])
                except (ValueError, IndexError):
                    continue
                r.update(upload_date=d.get("upload_date"), likes=d.get("like_count"),
                         comments=d.get("comment_count"), subscribers=d.get("channel_follower_count"),
                         tags=(d.get("tags") or [])[:12], description=(d.get("description") or "")[:600],
                         chapters=[c.get("title") for c in (d.get("chapters") or [])][:30],
                         language=d.get("language"))
                r["views_per_day"] = views_per_day(r.get("views"), r.get("upload_date"))
                subs = r.get("subscribers")
                r["views_per_subscriber"] = round(r["views"] / subs, 2) if subs and r.get("views") else None
        vals = sorted(v for v in (r.get("views") or 0 for r in rows) if v)
        median = vals[len(vals) // 2] if vals else None
        for r in rows:
            r["x_median_views"] = round(r["views"] / median, 2) if median and r.get("views") else None
        banked = None
        if args.bank:
            banked = bank_add(args.bank, "competitors", [
                {"url": r["url"], "title": r.get("title"), "channel": r.get("channel"), "result": r.get("views"),
                 "result_kind": "views", "x_median_views": r.get("x_median_views"), "length_s": r.get("duration_s"),
                 "published": r.get("upload_date"), "hook": "", "angle": "", "query": args.query} for r in rows])
        emit({"ok": True, "query": args.query, "count": len(rows), "median_views": median, "videos": rows,
              "banked": banked,
              "note": "x_median_views over 3 marks an outlier worth studying (title, hook, angle); fill each "
                      "competitor's hook from its captions (`youtube captions`)"})
        return
    vid = yt_id(args.video)
    if not vid:
        die("give a YouTube URL or an 11-character video id")
    url = f"https://www.youtube.com/watch?v={vid}"
    work = CACHE.parent / "yt" / vid
    work.mkdir(parents=True, exist_ok=True)
    if args.what == "comments":
        n = max(1, min(args.n, 1000))
        ytdlp(["--skip-download", "--write-comments", "--extractor-args",
               f"youtube:max_comments={n},all,20,0;comment_sort={args.sort}", "-o", str(work / "v.%(ext)s"), url],
              timeout=600)
        info = work / "v.info.json"
        if not info.exists():
            die("no comments: the video may have them turned off, or YouTube refused the request")
        d = json.loads(info.read_text(encoding="utf-8"))
        cs = [{"text": c.get("text"), "likes": c.get("like_count"), "is_reply": c.get("parent") not in (None, "root"),
               "author_is_uploader": c.get("author_is_uploader")} for c in (d.get("comments") or [])]
        banked = None
        if args.bank:
            keep = [c for c in cs if not c["is_reply"] and not c["author_is_uploader"] and c.get("text")
                    and len(c["text"].strip()) >= 20 and not re.search(r"https?://", c["text"])]
            keep.sort(key=lambda c: -(c.get("likes") or 0))
            banked = bank_add(args.bank, "voice", [
                {"text": c["text"].strip(), "source": url, "kind": "comment", "likes": c.get("likes"),
                 "video_title": d.get("title")} for c in keep[:args.keep]])
        emit({"ok": True, "video": url, "title": d.get("title"), "views": d.get("view_count"),
              "upload_date": d.get("upload_date"), "comment_count": d.get("comment_count"), "comments": cs,
              "banked": banked,
              "note": "the audience's own words: copy pains, desires, objections and phrases into notes/voice-bank.json "
                      "with the video as source (grade D: opinion, never a fact)"})
        return
    if args.what == "captions":
        for f in work.glob("cap*"):
            f.unlink()
        ytdlp(["--skip-download", "--write-subs", "--write-auto-subs", "--sub-langs", f"{args.lang}.*,{args.lang}",
               "--sub-format", "vtt", "-o", str(work / "cap.%(ext)s"), url], timeout=300)
        vtts = sorted(work.glob("cap*.vtt"))
        if not vtts:
            die(f"no {args.lang} captions: transcribe it with agy-watch-video (`transcribe`) instead")
        lines, last = [], None
        for line in vtts[0].read_text(encoding="utf-8", errors="replace").splitlines():
            if "-->" in line or not line.strip() or line.startswith(("WEBVTT", "Kind:", "Language:")):
                continue
            clean = re.sub(r"<[^>]+>", "", line).strip()
            if clean and clean != last:
                lines.append(clean)
                last = clean
        text = " ".join(lines)
        emit({"ok": True, "video": url, "file": str(vtts[0]), "auto": ".orig" not in vtts[0].name,
              "words": len(text.split()), "text": text})


# ----------------------------------------------------------------------------------------------------- academic

def _openalex(q, n):
    data, err = get_json("https://api.openalex.org/works?" + urllib.parse.urlencode(
        {"search": q, "per-page": n, "mailto": "research@example.invalid"}))
    if err:
        return [], f"openalex: {err}"
    out = []
    for w in data.get("results", []):
        loc = (w.get("primary_location") or {}).get("source") or {}
        out.append({"source": "openalex", "title": w.get("title"), "year": w.get("publication_year"),
                    "authors": [a["author"]["display_name"] for a in (w.get("authorships") or [])[:6]],
                    "venue": loc.get("display_name"), "cited_by": w.get("cited_by_count"),
                    "doi": w.get("doi"), "url": w.get("doi") or w.get("id"),
                    "open_access": (w.get("open_access") or {}).get("oa_url"), "type": w.get("type")})
    return out, None


def _crossref(q, n):
    data, err = get_json("https://api.crossref.org/works?" + urllib.parse.urlencode({"query": q, "rows": n}))
    if err:
        return [], f"crossref: {err}"
    out = []
    for w in data.get("message", {}).get("items", []):
        year = ((w.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        out.append({"source": "crossref", "title": (w.get("title") or [""])[0], "year": year,
                    "authors": [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in (w.get("author") or [])[:6]],
                    "venue": (w.get("container-title") or [""])[0], "cited_by": w.get("is-referenced-by-count"),
                    "doi": w.get("DOI"), "url": w.get("URL"), "type": w.get("type")})
    return out, None


def _arxiv(q, n):
    status, body, _ = http_get("https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": f"all:{q}", "max_results": n}), accept="application/atom+xml")
    if status != 200:
        return [], f"arxiv: HTTP {status}"
    import xml.etree.ElementTree as ET
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    try:
        root = ET.fromstring(body)
    except ET.ParseError as e:
        return [], f"arxiv: {e}"
    for e in root.findall("a:entry", ns):
        out.append({"source": "arxiv", "title": " ".join((e.findtext("a:title", "", ns) or "").split()),
                    "year": (e.findtext("a:published", "", ns) or "")[:4],
                    "authors": [a.findtext("a:name", "", ns) for a in e.findall("a:author", ns)][:6],
                    "venue": "arXiv (preprint, not peer reviewed)", "url": e.findtext("a:id", "", ns),
                    "summary": " ".join((e.findtext("a:summary", "", ns) or "").split())[:500]})
    return out, None


def _semantic(q, n):
    data, err = get_json("https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(
        {"query": q, "limit": n, "fields": "title,year,citationCount,url,venue,authors,externalIds,tldr"}))
    if err:
        return [], f"semantic scholar: {err} (no key: it limits requests; try again later or use openalex)"
    out = []
    for p in data.get("data", []):
        out.append({"source": "semantic", "title": p.get("title"), "year": p.get("year"),
                    "authors": [a.get("name") for a in (p.get("authors") or [])[:6]], "venue": p.get("venue"),
                    "cited_by": p.get("citationCount"), "url": p.get("url"),
                    "doi": (p.get("externalIds") or {}).get("DOI"),
                    "tldr": ((p.get("tldr") or {}).get("text") or "")[:300]})
    return out, None


def cmd_academic(args):
    fns = {"openalex": _openalex, "crossref": _crossref, "arxiv": _arxiv, "semantic": _semantic}
    names = list(fns) if args.source == "all" else [args.source]
    results, errors = [], []
    for name in names:
        rows, err = fns[name](args.query, args.n)
        results += rows
        if err:
            errors.append(err)
    emit({"ok": bool(results), "query": args.query, "count": len(results), "results": results, "errors": errors,
          "note": "a paper is grade A for what it measured; read the abstract and methods before citing a number"})


# ------------------------------------------------------------------------------------------- community, wiki, web

def cmd_hn(args):
    data, err = get_json("https://hn.algolia.com/api/v1/search?" + urllib.parse.urlencode(
        {"query": args.query, "tags": "story", "hitsPerPage": args.n}))
    if err:
        die(f"hacker news: {err}")
    hits = [{"title": h.get("title"), "points": h.get("points"), "comments": h.get("num_comments"),
             "url": h.get("url"), "discussion": f"https://news.ycombinator.com/item?id={h.get('objectID')}",
             "date": (h.get("created_at") or "")[:10]} for h in data.get("hits", [])]
    emit({"ok": True, "query": args.query, "hits": hits,
          "note": "discussion threads show what practitioners dispute; grade D unless a comment links evidence"})


def cmd_wiki(args):
    base = f"https://{args.lang}.wikipedia.org"
    data, err = get_json(f"{base}/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "list": "search", "srsearch": args.query, "format": "json", "srlimit": args.n}))
    if err:
        die(f"wikipedia: {err}")
    out = []
    for s in data.get("query", {}).get("search", []):
        title = s.get("title")
        summ, _ = get_json(f"{base}/api/rest_v1/page/summary/" + urllib.parse.quote(title.replace(" ", "_")))
        out.append({"title": title, "url": f"{base}/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
                    "summary": (summ or {}).get("extract", "")[:700]})
    emit({"ok": True, "query": args.query, "results": out,
          "note": "Wikipedia is a map to sources: follow its citations and cite those, not the article"})


def cmd_fetch(args):
    page = fetch_page(args.url, fresh=args.fresh)
    if not page.get("ok"):
        emit(page)
        sys.exit(1)
    if args.out:
        Path(args.out).write_text(page["text"], encoding="utf-8")
    out = {"ok": True, "url": page["url"], "final_url": page.get("final_url"), "info": page["info"],
           "chars": len(page["text"]), "cached": page.get("cached"), "fetched_at": page.get("fetched_at")}
    if not args.meta:
        out["text"] = page["text"][:args.max_chars]
    emit(out)


def cmd_wayback(args):
    data, err = get_json("https://archive.org/wayback/available?" + urllib.parse.urlencode({"url": args.url}))
    if err:
        die(f"wayback: {err}")
    snap = (data.get("archived_snapshots") or {}).get("closest") or {}
    emit({"ok": bool(snap), "url": args.url, "archived": snap.get("url"), "timestamp": snap.get("timestamp")})


# ------------------------------------------------------------------------------------------------ ledger files

def rdir(path):
    d = Path(path).expanduser()
    return d / "research" if (d / "research").is_dir() else d


def load(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def save(path, data):
    path = Path(path)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


PLAN = """# Research plan: {topic}

Created {created}. Level: {level}. Language: {lang}.

## The question
What exactly must be true, and for whom, before anyone writes? (one sentence)

## Sub-questions (the tree)
1.
2.
3.

## Where the answers live (per sub-question: source types, languages, sites)

## Budget and stopping rule
Draft: 5 to 10 sources. Standard: 20 to 40. Deep: 60 or more, two rounds. Stop when new sources stop changing the
findings, not when the budget runs out.

## Findings (filled at the end: what is solid, what is disputed, what is unknown)
"""


def cmd_new(args):
    d = Path(args.dir).expanduser() / "research"
    if (d / "ledger.json").exists():
        die(f"{d} already holds a ledger (never overwritten)")
    (d / "notes").mkdir(parents=True, exist_ok=True)
    (d / "plan.md").write_text(PLAN.format(topic=args.topic, created=now_iso()[:10], level=args.level, lang=args.lang),
                               encoding="utf-8")
    save(d / "sources.json", {"schema": "nexa.sources/1", "topic": args.topic, "sources": []})
    save(d / "ledger.json", {"schema": "nexa.ledger/1", "topic": args.topic, "level": args.level, "claims": []})
    for name, kind in (("story-bank.json", "story"), ("voice-bank.json", "voice"), ("competitors.json", "competitors")):
        save(d / "notes" / name, {"schema": f"nexa.{kind}/1", "items": []})
    emit({"ok": True, "dir": str(d), "files": ["plan.md", "sources.json", "ledger.json", "notes/story-bank.json",
                                                "notes/voice-bank.json", "notes/competitors.json"]})


def _next_id(items, prefix):
    nums = [int(i["id"][len(prefix):]) for i in items if str(i.get("id", "")).startswith(prefix)
            and str(i["id"][len(prefix):]).isdigit()]
    return f"{prefix}{max(nums, default=0) + 1}"


def cmd_source(args):
    d = rdir(args.dir)
    sp = d / "sources.json"
    data = load(sp, None)
    if data is None:
        die(f"no sources.json in {d}: run `research.py new` first")
    if args.grade.upper() not in GRADES:
        die("grade must be A, B, C, D or E")
    for s in data["sources"]:
        if s["url"] == args.url:
            emit({"ok": True, "id": s["id"], "existing": True})
            return
    sid = _next_id(data["sources"], "s")
    data["sources"].append({"id": sid, "url": args.url, "title": args.title, "publisher": args.publisher,
                            "date": args.date, "kind": args.kind, "grade": args.grade.upper(), "accessed": now_iso(),
                            "note": args.note})
    save(sp, data)
    emit({"ok": True, "id": sid, "grade_means": GRADES[args.grade.upper()]})


def cmd_claim(args):
    d = rdir(args.dir)
    lp, sp = d / "ledger.json", d / "sources.json"
    ledger, sources = load(lp, None), load(sp, None)
    if ledger is None or sources is None:
        die(f"no ledger in {d}: run `research.py new` first")
    known = {s["id"] for s in sources["sources"]}
    missing = [s for s in args.source if s not in known]
    if missing:
        die(f"unknown source ids {missing}: add them with `research.py source add` first")
    cid = _next_id(ledger["claims"], "c")
    ledger["claims"].append({"id": cid, "text": args.text, "source_ids": args.source, "quote": args.quote,
                             "where": args.where, "date": args.date, "key": bool(args.key), "status": "unverified",
                             "checked_at": None, "how": None})
    save(lp, ledger)
    emit({"ok": True, "id": cid})


def cmd_claim_set(args):
    """A person's decision on a claim: manual (checked by hand, e.g. a video quote against its transcript),
    conflicting (sources disagree), removed, or back to unverified. The note says how and by whom."""
    d = rdir(args.dir)
    lp = d / "ledger.json"
    ledger = load(lp, None)
    if ledger is None:
        die(f"no ledger in {d}")
    c = next((x for x in ledger["claims"] if x["id"] == args.id), None)
    if c is None:
        die(f"no claim {args.id}")
    if args.status == "manual" and not args.note:
        die("a manual check needs --note: what was checked, against what, by whom")
    c["status"], c["checked_at"] = args.status, now_iso()
    c["how"] = f"set by hand: {args.note}" if args.note else "set by hand"
    save(lp, ledger)
    emit({"ok": True, "id": c["id"], "status": c["status"]})


def cmd_verify(args):
    d = rdir(args.dir)
    lp = d / "ledger.json"
    ledger, sources = load(lp, None), load(d / "sources.json", None)
    if ledger is None or sources is None:
        die(f"no ledger in {d}")
    by_id = {s["id"]: s for s in sources["sources"]}
    wanted = set(args.ids.split(",")) if args.ids else None
    report = []
    for c in ledger["claims"]:
        if wanted and c["id"] not in wanted:
            continue
        if c.get("status") in ("removed", "manual") and not wanted:
            continue
        found_in, tried = [], []
        for sid in c["source_ids"]:
            s = by_id.get(sid)
            if not s:
                continue
            vid = yt_id(s["url"]) if "youtu" in s["url"] else None
            if vid:
                tried.append(f"{sid}: video, check the quote against its transcript by hand or with captions")
                continue
            page = fetch_page(s["url"], fresh=args.fresh)
            if not page.get("ok"):
                tried.append(f"{sid}: {page.get('error')}")
                continue
            ok, how = quote_in_text(c.get("quote") or "", page["text"])
            tried.append(f"{sid}: {how}")
            if ok:
                found_in.append(sid)
        c["status"] = "verified" if found_in else ("unsupported" if tried and all(
            t.split(": ", 1)[1].startswith("not found") for t in tried) else "unverified")
        c["checked_at"], c["how"] = now_iso(), "; ".join(tried)
        report.append({"id": c["id"], "status": c["status"], "how": c["how"]})
    save(lp, ledger)
    counts = {s: sum(1 for c in ledger["claims"] if c.get("status") == s) for s in STATUSES}
    emit({"ok": True, "checked": report, "counts": counts})


def _year(date):
    m = re.match(r"(\d{4})", str(date or ""))
    return int(m.group(1)) if m else None


def run_check(d, level="standard", fresh_years=None):
    ledger, sources = load(d / "ledger.json", None), load(d / "sources.json", None)
    if ledger is None or sources is None:
        return {"ok": False, "errors": [f"no ledger in {d}"], "warnings": [], "stats": {}}
    by_id = {s["id"]: s for s in sources["sources"]}
    errors, warnings = [], []
    live = [c for c in ledger["claims"] if c.get("status") != "removed"]
    for c in live:
        srcs = [by_id[s] for s in c["source_ids"] if s in by_id]
        if not srcs:
            errors.append(f"{c['id']}: no source")
            continue
        if not (c.get("quote") or "").strip():
            errors.append(f"{c['id']}: no quote (the exact words that support it)")
        grades = [s.get("grade") for s in srcs]
        if all(g in ("D", "E") for g in grades):
            errors.append(f"{c['id']}: only grade {'/'.join(grades)} sources; a fact needs A, B or C")
        if c.get("key"):
            publishers = {(s.get("publisher") or s["url"]).lower() for s in srcs}
            if "A" not in grades and len(publishers) < 2:
                errors.append(f"{c['id']}: key claim needs a grade A source or two independent publishers")
        if c.get("status") == "unsupported":
            errors.append(f"{c['id']}: the quote was not found in its source")
        if c.get("status") == "conflicting":
            warnings.append(f"{c['id']}: sources disagree: say so in the text or drop it")
        if fresh_years:
            years = [_year(s.get("date")) for s in srcs if _year(s.get("date"))]
            if years and max(years) < datetime.date.today().year - fresh_years:
                warnings.append(f"{c['id']}: newest source is {max(years)}: older than {fresh_years} years")
    verified = sum(1 for c in live if c.get("status") in ("verified", "manual"))
    share = verified / len(live) if live else 1.0
    need = {"draft": 0.0, "standard": 0.6, "final": 0.9}[level]
    if share < need:
        (errors if level == "final" else warnings).append(
            f"{verified} of {len(live)} claims verified ({share:.0%}); {level} needs {need:.0%}")
    undated = [s["id"] for s in sources["sources"] if not s.get("date")]
    if undated:
        warnings.append(f"sources without a date: {', '.join(undated[:12])}")
    stats = {"claims": len(live), "verified": verified, "verified_share": round(share, 2),
             "sources": len(sources["sources"]),
             "by_grade": {g: sum(1 for s in sources["sources"] if s.get("grade") == g) for g in GRADES}}
    return {"ok": not errors, "level": level, "errors": errors, "warnings": warnings, "stats": stats}


def cmd_check(args):
    res = run_check(rdir(args.dir), args.level, args.fresh_years)
    emit(res)
    sys.exit(0 if res["ok"] else 1)


# a sentence that states a fact: a number, money, a share, a study, an attribution (R8 10, V1 SC-10)
FACTUAL = re.compile(r"(\d[\d,.]*\s?(%|percent|million|billion|crore|lakh|taka|tk\b|rupees?|dollars?)|[$\u20ac\u00a3"
                     r"\u09f3\u20b9]\s?\d|\b(19|20)\d\d\b|\b\d{2,}\b|\b(study|studies|survey|research|report|according to|"
                     r"data|found|found that|scientists|experts)\b|[\u09e6-\u09ef]{2,}|গবেষণা|জরিপ|অনুযায়ী)", re.I)
CLAIM_TAG = re.compile(r"\[(c\d+(?:\s*,\s*c\d+)*)\]", re.I)


def cmd_audit(args):
    """R8's citation gate for prose: every sentence that states a fact carries [cN] tags of claims in the ledger, and at
    the final level those claims are verified. Headings, list markers and quoted audience words are skipped."""
    d = rdir(args.dir)
    ledger = load(d / "ledger.json", None)
    if ledger is None:
        die(f"no ledger in {d}: run `research.py new` first")
    claims = {c["id"]: c for c in ledger["claims"] if c.get("status") != "removed"}
    text = Path(args.file).read_text(encoding="utf-8")
    body = re.sub(r"^#+\s.*$", "", text, flags=re.M)
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    sentences = [x.strip() for x in re.split(r"(?<=[.!?\u0964])\s+", body) if x.strip()]
    missing, unknown, weak = [], [], []
    for sent in sentences:
        tags = [t.strip().lower() for m in CLAIM_TAG.findall(sent) for t in m.split(",")]
        bare = CLAIM_TAG.sub("", sent)
        if FACTUAL.search(bare) and not tags:
            missing.append(sent[:120])
        for t in tags:
            if t not in claims:
                unknown.append(f"{t} in '{sent[:60]}'")
            elif args.level == "final" and claims[t].get("status") not in ("verified", "manual"):
                weak.append(f"{t} is {claims[t].get('status')} in '{sent[:60]}'")
    errors = [f"unknown claim {u}" for u in unknown] + [f"not verified: {w}" for w in weak]
    if args.level == "final":
        errors += [f"a factual sentence with no claim id: '{m}'" for m in missing]
        warnings = []
    else:
        warnings = [f"a factual sentence with no claim id: '{m}'" for m in missing]
    emit({"ok": not errors, "level": args.level, "sentences": len(sentences), "errors": errors, "warnings": warnings,
          "note": "tag facts with [c3] or [c3, c7]; quoted audience words and opinions need no tag"})
    sys.exit(0 if not errors else 1)


def cmd_budget(args):
    """The WebSearch tool's cap (about 200 calls) is shared by every agent in a session (R8 F3): count centrally, keep
    a quarter for verification, warn at 75 %, then route to the APIs and direct fetches."""
    d = rdir(args.dir)
    path = d / "budget.json"
    if args.cap is not None and args.cap < 1:
        die("--cap is 1 or more")
    data = load(path, {"schema": "nexa.budget/1", "cap": args.cap or 200, "used": 0, "by": {}})
    if args.cap is not None:
        data["cap"] = args.cap
    if args.add:
        data["used"] += args.add
        who = args.by or "lead"
        data["by"][who] = data["by"].get(who, 0) + args.add
        save(path, data)
    share = data["used"] / data["cap"] if data["cap"] else 0
    left = max(0, data["cap"] - data["used"])
    advice = ("fine" if share < 0.5 else "keep a quarter for verification and the gap pass" if share < 0.75 else
              "75 % used: route remaining lookups to the APIs (academic, wiki, hn, youtube) and direct fetches")
    emit({"ok": data["used"] <= data["cap"], "used": data["used"], "cap": data["cap"], "left": left,
          "share": round(share, 2), "by": data["by"], "advice": advice})


def cmd_pack(args):
    d = rdir(args.dir)
    res = run_check(d, "draft")
    ledger, sources = load(d / "ledger.json", {}), load(d / "sources.json", {})
    notes = {name: load(d / "notes" / f"{name}.json", {"items": []}).get("items", [])
             for name in ("story-bank", "voice-bank", "competitors")}
    findings = (d / "findings.md").read_text(encoding="utf-8") if (d / "findings.md").exists() else ""
    pack = {"schema": "nexa.research-pack/1", "topic": ledger.get("topic"), "made_at": now_iso(),
            "findings_md": findings, "sources": sources.get("sources", []),
            "claims": [c for c in ledger.get("claims", []) if c.get("status") != "removed"],
            "story_bank": notes["story-bank"], "voice_bank": notes["voice-bank"],
            "competitors": notes["competitors"], "check": res}
    save(d / "pack.json", pack)
    emit({"ok": True, "pack": str(d / "pack.json"), "claims": len(pack["claims"]),
          "verified": res["stats"].get("verified"), "story_items": len(pack["story_bank"]),
          "voice_items": len(pack["voice_bank"]), "competitors": len(pack["competitors"]),
          "gate_errors": res["errors"], "gate_warnings": res["warnings"]})


def cmd_doctor(_args):
    checks = {"python": sys.version.split()[0], "skill_version": SKILL_VERSION}
    try:
        checks["yt-dlp"] = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True,
                                          timeout=30).stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        checks["yt-dlp"] = "missing: brew install yt-dlp (YouTube search, comments and captions need it)"
    for name, url in (("openalex", "https://api.openalex.org/works?search=test&per-page=1"),
                      ("wikipedia", "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=test&format=json&srlimit=1"),
                      ("hacker_news", "https://hn.algolia.com/api/v1/search?query=test&hitsPerPage=1")):
        status, _, _ = http_get(url, timeout=15, retries=0)
        checks[name] = "ok" if status == 200 else f"HTTP {status}"
    checks["cache"] = str(CACHE)
    emit({"ok": True, "checks": checks, "grades": GRADES})


def main(argv=None):
    ap = argparse.ArgumentParser(prog="research.py", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    p = sub.add_parser("new")
    p.add_argument("dir")
    p.add_argument("--topic", required=True)
    p.add_argument("--level", default="standard", choices=["draft", "standard", "deep"])
    p.add_argument("--lang", default="en")
    y = sub.add_parser("youtube")
    ysub = y.add_subparsers(dest="what", required=True)
    ys = ysub.add_parser("search")
    ys.add_argument("query")
    ys.add_argument("--n", type=int, default=20)
    ys.add_argument("--details", action="store_true", help="upload date, likes, subscribers, chapters (slower)")
    ys.add_argument("--bank", help="a research folder: add the videos to notes/competitors.json")
    yc = ysub.add_parser("comments")
    yc.add_argument("video")
    yc.add_argument("--n", type=int, default=100)
    yc.add_argument("--sort", default="top", choices=["top", "new"])
    yc.add_argument("--bank", help="a research folder: add the top comments to notes/voice-bank.json")
    yc.add_argument("--keep", type=int, default=60, help="how many comments (most liked first) go into the bank")
    yp = ysub.add_parser("captions")
    yp.add_argument("video")
    yp.add_argument("--lang", default="en")
    a = sub.add_parser("academic")
    a.add_argument("query")
    a.add_argument("--n", type=int, default=8)
    a.add_argument("--source", default="all", choices=["all", "openalex", "crossref", "arxiv", "semantic"])
    h = sub.add_parser("hn")
    h.add_argument("query")
    h.add_argument("--n", type=int, default=10)
    w = sub.add_parser("wiki")
    w.add_argument("query")
    w.add_argument("--lang", default="en")
    w.add_argument("--n", type=int, default=5)
    f = sub.add_parser("fetch")
    f.add_argument("url")
    f.add_argument("--meta", action="store_true", help="metadata only, no text")
    f.add_argument("--out")
    f.add_argument("--fresh", action="store_true")
    f.add_argument("--max-chars", type=int, default=20000)
    wb = sub.add_parser("wayback")
    wb.add_argument("url")
    s = sub.add_parser("source")
    ssub = s.add_subparsers(dest="what", required=True)
    sa = ssub.add_parser("add")
    sa.add_argument("dir")
    sa.add_argument("--url", required=True)
    sa.add_argument("--title", required=True)
    sa.add_argument("--publisher", required=True)
    sa.add_argument("--date", default=None)
    sa.add_argument("--kind", default="other", choices=KINDS)
    sa.add_argument("--grade", required=True)
    sa.add_argument("--note", default=None)
    c = sub.add_parser("claim")
    csub = c.add_subparsers(dest="what", required=True)
    ca = csub.add_parser("add")
    ca.add_argument("dir")
    ca.add_argument("--text", required=True)
    ca.add_argument("--source", action="append", required=True)
    ca.add_argument("--quote", required=True)
    ca.add_argument("--where", default=None)
    ca.add_argument("--date", default=None)
    ca.add_argument("--key", action="store_true", help="a claim the piece stands on: needs A or two publishers")
    cs = csub.add_parser("set")
    cs.add_argument("dir")
    cs.add_argument("id")
    cs.add_argument("--status", required=True, choices=["manual", "conflicting", "removed", "unverified"])
    cs.add_argument("--note", help="how it was checked and by whom (required for manual)")
    v = sub.add_parser("verify")
    v.add_argument("dir")
    v.add_argument("--ids")
    v.add_argument("--fresh", action="store_true")
    k = sub.add_parser("check")
    k.add_argument("dir")
    k.add_argument("--level", default="standard", choices=["draft", "standard", "final"])
    k.add_argument("--fresh-years", type=int, default=None)
    pk = sub.add_parser("pack")
    pk.add_argument("dir")
    au = sub.add_parser("audit")
    au.add_argument("file")
    au.add_argument("--dir", required=True, help="the research folder whose ledger the tags point to")
    au.add_argument("--level", default="standard", choices=["draft", "standard", "final"])
    bu = sub.add_parser("budget")
    bu.add_argument("dir")
    bu.add_argument("--add", type=int, default=0, help="searches just used")
    bu.add_argument("--by", help="which agent used them")
    bu.add_argument("--cap", type=int)
    nt = sub.add_parser("note")
    nsub = nt.add_subparsers(dest="what", required=True)
    na = nsub.add_parser("add")
    na.add_argument("dir")
    na.add_argument("--bank", required=True, choices=sorted(BANKS))
    na.add_argument("--text", default="")
    na.add_argument("--source")
    na.add_argument("--set", action="append", help="key=value, repeatable (kind=review, url=..., hook=...)")
    args = ap.parse_args(argv)
    if args.cmd == "claim" and args.what == "set":
        return cmd_claim_set(args)
    handlers = {"doctor": cmd_doctor, "new": cmd_new, "youtube": cmd_youtube, "academic": cmd_academic,
                "hn": cmd_hn, "wiki": cmd_wiki, "fetch": cmd_fetch, "wayback": cmd_wayback,
                "source": cmd_source, "claim": cmd_claim, "verify": cmd_verify, "check": cmd_check,
                "pack": cmd_pack, "note": cmd_note, "audit": cmd_audit, "budget": cmd_budget}
    handlers[args.cmd](args)


if __name__ == "__main__":
    main()
