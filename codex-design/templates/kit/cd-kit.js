/* codex-design kit: fit text to its box.
   <h1 data-fit="56,140" data-fit-lines="2"> gets the largest size between 56 and 140 px that fits its box
   (and at most 2 lines). The box needs a width, and a height when it holds several lines. One value is the minimum
   and the CSS size the maximum; a value may be a share of the CSS size ("60%") or "floor", the canvas's text floor
   (--min-text), so one pattern fits canvases of any size.
   The renderer waits for window.__cdReady before it captures; a text that cannot fit gets data-fit-failed. */
(() => {
  // lines, not rect tops: a range also returns the boxes of child elements (a blockified span in a flex column is
  // shorter than its text's content area) and a smaller run on the same baseline starts lower, so a rect joins a line
  // whose middle is within a third of the smaller height of its own
  const lineCount = el => {
    const r = document.createRange();
    r.selectNodeContents(el);
    const lines = [];
    for (const q of r.getClientRects()) {
      if (q.width <= 1 || q.height <= 1) continue;
      const mid = (q.top + q.bottom) / 2;
      if (!lines.some(l => Math.abs(l.mid - mid) < 0.35 * Math.min(l.h, q.height))) lines.push({ mid, h: q.height });
    }
    return lines.length;
  };
  // tight display leading lets descenders poke below the line box: allow a fifth of the size vertically.
  // Every line must also sit inside the box: bottom-aligned (flex-end) text overflows upwards, which scrollHeight
  // does not count.
  const fits = (el, maxLines) => {
    const cs = getComputedStyle(el), fs = parseFloat(cs.fontSize);
    const lh = cs.lineHeight === 'normal' ? null : parseFloat(cs.lineHeight);
    const b = el.getBoundingClientRect(), r = document.createRange();
    r.selectNodeContents(el);
    const rects = [...r.getClientRects()].filter(q => q.width > 1);
    // a line's rect is the font's content area, taller than a tight line box (Young Serif: 1.42 em at line-height 1):
    // allow that part on top of a fifth of the size, above the first line and below the last
    const extra = lh && rects.length ? Math.max(0, (rects[0].height - lh) / 2) : 0;
    const allow = Math.max(1, fs * 0.2) + extra;
    if (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + allow) return false;
    for (const q of rects) {
      if (q.top < b.top - allow || q.bottom > b.bottom + allow || q.left < b.left - 1 || q.right > b.right + 1)
        return false;
    }
    return !maxLines || lineCount(el) <= maxLines;
  };

  async function fitAll() {
    await document.fonts.ready;
    for (const el of document.querySelectorAll('[data-fit]')) {
      const css = parseFloat(getComputedStyle(el).fontSize);
      const floor = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--min-text')) || 12;
      const val = (t, dflt) => {
        t = (t || '').trim();
        return !t ? dflt : t === 'floor' ? floor : t.endsWith('%') ? css * parseFloat(t) / 100 : Number(t);
      };
      const parts = el.dataset.fit.split(',');
      const maxLines = Number(el.dataset.fitLines) || 0;
      let lo = val(parts[0], 12), hi = val(parts[1], css);
      if (lo > hi) hi = lo;  // a CSS size under the floor is raised to it (and fails loudly if it cannot fit)
      el.style.fontSize = hi + 'px';
      if (fits(el, maxLines)) continue;
      for (let i = 0; i < 20 && hi - lo > 0.5; i++) {
        const mid = (lo + hi) / 2;
        el.style.fontSize = mid + 'px';
        if (fits(el, maxLines)) lo = mid; else hi = mid;
      }
      el.style.fontSize = Math.floor(lo) + 'px';
      if (!fits(el, maxLines)) el.dataset.fitFailed = '1';
    }
  }
  // pages that build their DOM in script (the brand book) call window.__cdFit() again when they are done
  window.__cdFit = fitAll;
  window.__cdReady = fitAll();
})();
