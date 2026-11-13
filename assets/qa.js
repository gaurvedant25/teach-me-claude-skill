// QA probe: run in the page. Visits each view and reports overflow, text size and small targets.
window.__qa = async function () {
  const T = window.__teachme, out = { width: innerWidth, views: {} };
  const wait = (ms) => new Promise(r => setTimeout(r, ms));
  const views = [["learn"], ["lesson", "t2-3"], ["lesson", "t9-2"], ["prereq"], ["practice"], ["revise"], ["test"], ["reference"]];
  const subs = { reference: ["formulas", "coverage", "checks", "progress"], practice: ["next", "pyq", "mixed"], revise: ["cards", "summary"] };
  for (const [v, arg] of views) {
    const list = subs[v] || [null];
    for (const s of list) {
      if (s) T.state().sub[v] = s;
      T.go(v, arg); await wait(250);
      const key = v + (arg ? ":" + arg : "") + (s ? ":" + s : "");
      const docOver = document.documentElement.scrollWidth - document.documentElement.clientWidth;
      const wide = [];
      document.querySelectorAll("main *").forEach(e => {
        const r = e.getBoundingClientRect();
        if (r.width && r.right > innerWidth + 1) {
          let p = e.parentElement, scrolls = false;
          while (p && p !== document.body) { const cs = getComputedStyle(p); if (/(auto|scroll)/.test(cs.overflowX)) { scrolls = true; break; } p = p.parentElement; }
          if (!scrolls) wide.push((e.className || e.tagName).toString().slice(0, 30));
        }
      });
      const small = [];
      document.querySelectorAll("main button, main select, main input:not([type=checkbox]):not([type=range]), header button").forEach(b => {
        const r = b.getBoundingClientRect(); if (r.width && r.height < 40) small.push((b.textContent || b.className).trim().slice(0, 20) + ":" + Math.round(r.height));
      });
      const rd = document.querySelector(".reader");
      out.views[key] = { docOver, wide: [...new Set(wide)].slice(0, 6), small: [...new Set(small)].slice(0, 6),
        readerFont: rd ? getComputedStyle(rd).fontSize : null, readerWidth: rd ? Math.round(rd.getBoundingClientRect().width) : null };
    }
  }
  return out;
};
