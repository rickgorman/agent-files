(function () {
  const DATA = window.HEATMAP_DATA;
  if (!DATA) {
    console.error("HEATMAP_DATA missing");
    return;
  }

  const {
    title,
    subtitle,
    tiers,
    categories: categoryDefs,
    parts,
    chunk_seconds,
    bar_seconds,
    notes,
    scored_count,
    total_count,
  } = DATA;

  const categoryKeys = categoryDefs.map((c) => c.key);
  const categoryLabel = {};
  categoryDefs.forEach((c) => {
    categoryLabel[c.key] = c.label || c.key;
  });

  const PALETTE = [
    "#3d4a8c",
    "#9c2840",
    "#1a6b62",
    "#a67c2e",
    "#5c4d7a",
    "#2d6a4f",
  ];

  function colorForCategory(index) {
    return PALETTE[index % PALETTE.length];
  }

  const GUTTER = 112;
  const LINE_GAP = 34;
  const LINE_COUNT = categoryKeys.length;
  const TOP_PAD = 18;
  const RIGHT_PAD = 26;
  const BOTTOM_PAD = 28;
  const SVG_HEIGHT = TOP_PAD + Math.max(0, LINE_COUNT - 1) * LINE_GAP + BOTTOM_PAD;
  const NOTES_PER_BAR = Math.max(1, Math.round(bar_seconds / chunk_seconds));
  const TICK_INTERVAL = Math.max(300, Math.min(1800, Math.floor(bar_seconds / 8)));

  const categoryVisible = {};
  categoryKeys.forEach((c) => {
    categoryVisible[c] = true;
  });
  let topTierOnly = false;

  const topTierIndex = tiers.length - 1;
  const highTierCutoff = Math.max(0, tiers.length - 2);

  function formatStreamTime(totalSeconds) {
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    return `${h}:${String(m).padStart(2, "0")}`;
  }

  function lineY(lineIndex) {
    return TOP_PAD + lineIndex * LINE_GAP;
  }

  function maxStartForPart(partNum) {
    let max = 0;
    for (const n of notes) {
      if (n.part === partNum) max = Math.max(max, n.start_s);
    }
    return max;
  }

  function barCountForPart(partNum) {
    const max = maxStartForPart(partNum);
    if (max <= 0) return 1;
    return Math.ceil((max + chunk_seconds) / bar_seconds);
  }

  function notesInBar(partNum, barIndex) {
    const barStart = barIndex * bar_seconds;
    const barEnd = barStart + bar_seconds;
    return notes.filter(
      (n) => n.part === partNum && n.start_s >= barStart && n.start_s < barEnd
    );
  }

  function radiusFromExpected(expected) {
    const scale = Math.max(1, tiers.length - 1);
    return 2.2 + (expected / scale) * (2.3 * scale);
  }

  function svgEl(tag, attrs) {
    const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
    if (attrs) {
      for (const [k, v] of Object.entries(attrs)) {
        el.setAttribute(k, String(v));
      }
    }
    return el;
  }

  function drawNote(parent, note, catKey, lineIndex, xCenter) {
    if (!categoryVisible[catKey]) return;

    const catData = note.categories[catKey];
    const y = lineY(lineIndex);
    const color = colorForCategory(categoryKeys.indexOf(catKey));

    const g = svgEl("g", { class: "note-group" });
    g.dataset.noteId = note.id;
    g.dataset.category = catKey;

    if (!note.scored || catData.expected == null) {
      const ring = svgEl("circle", {
        class: "note-dot unscored",
        cx: xCenter,
        cy: y,
        r: 3,
        fill: "none",
        stroke: "#b0a89c",
        "stroke-width": 2,
      });
      g.appendChild(ring);
      parent.appendChild(g);
      return;
    }

    const expected = catData.expected;
    const tierIndex = catData.tier_index;
    const isLow = expected < 0.35;
    const r = isLow ? 3 : radiusFromExpected(expected);
    const dimmed =
      topTierOnly &&
      note.scored &&
      tierIndex != null &&
      tierIndex < highTierCutoff;

    if (isLow) {
      const ring = svgEl("circle", {
        class: `note-dot${dimmed ? " dimmed-tier" : ""}`,
        cx: xCenter,
        cy: y,
        r: 3,
        fill: "none",
        stroke: color,
        "stroke-width": 2,
        opacity: dimmed ? 0.12 : 0.82,
      });
      g.appendChild(ring);
      if (tierIndex === topTierIndex) {
        g.appendChild(
          svgEl("circle", {
            cx: xCenter,
            cy: y,
            r: 5,
            fill: "none",
            stroke: "#1a1814",
            "stroke-width": 1,
            opacity: dimmed ? 0.12 : 0.9,
          })
        );
      }
    } else {
      const dot = svgEl("circle", {
        class: `note-dot${dimmed ? " dimmed-tier" : ""}`,
        cx: xCenter,
        cy: y,
        r,
        fill: color,
        opacity: dimmed ? 0.12 : 0.82,
      });
      g.appendChild(dot);
      if (tierIndex === topTierIndex) {
        g.appendChild(
          svgEl("circle", {
            cx: xCenter,
            cy: y,
            r: r + 2,
            fill: "none",
            stroke: "#1a1814",
            "stroke-width": 1,
            opacity: dimmed ? 0.12 : 0.9,
            class: "top-tier-ring",
          })
        );
      }
    }

    parent.appendChild(g);
  }

  function buildBar(partNum, partLabel, barIndex, plotWidth) {
    const barStart = barIndex * bar_seconds;
    const svgWidth = GUTTER + plotWidth + RIGHT_PAD;
    const barNotes = notesInBar(partNum, barIndex);

    const svg = svgEl("svg", {
      class: "bar-svg",
      viewBox: `0 0 ${svgWidth} ${SVG_HEIGHT}`,
      width: svgWidth,
      height: SVG_HEIGHT,
      role: "img",
      "aria-label": `${partLabel} bar ${barIndex + 1}`,
    });

    const plotLeft = GUTTER;
    const plotRight = GUTTER + plotWidth;

    categoryKeys.forEach((catKey, i) => {
      if (!categoryVisible[catKey]) return;
      const y = lineY(i);
      svg.appendChild(
        svgEl("line", {
          class: "staff-line",
          x1: plotLeft,
          y1: y,
          x2: plotRight,
          y2: y,
        })
      );
      const label = categoryLabel[catKey] || catKey;
      const short =
        label.length > 14 ? label.slice(0, 12).trim() + "…" : label;
      svg.appendChild(
        svgEl("text", {
          class: "cat-label",
          x: 8,
          y: y + 4,
          "text-anchor": "start",
        })
      ).textContent = short;
    });

    svg.appendChild(
      svgEl("line", {
        class: "barline",
        x1: plotLeft,
        y1: TOP_PAD - 6,
        x2: plotLeft,
        y2: lineY(LINE_COUNT - 1) + 6,
      })
    );
    svg.appendChild(
      svgEl("line", {
        class: "barline",
        x1: plotRight,
        y1: TOP_PAD - 6,
        x2: plotRight,
        y2: lineY(LINE_COUNT - 1) + 6,
      })
    );

    for (let t = 0; t <= bar_seconds; t += TICK_INTERVAL) {
      const x = plotLeft + (t / bar_seconds) * plotWidth;
      const streamSec = barStart + t;
      svg.appendChild(
        svgEl("line", {
          class: "tick",
          x1: x,
          y1: TOP_PAD - 4,
          x2: x,
          y2: lineY(LINE_COUNT - 1) + 4,
        })
      );
      const timeLabel = svgEl("text", {
        class: "time-label",
        x,
        y: SVG_HEIGHT - 6,
        "text-anchor": "middle",
      });
      timeLabel.textContent = formatStreamTime(streamSec);
      svg.appendChild(timeLabel);
    }

    const highlightsLayer = svgEl("g", { class: "highlights-layer" });
    const hitsLayer = svgEl("g", { class: "hits-layer" });
    const dotsLayer = svgEl("g", { class: "dots-layer" });

    const colWidth = plotWidth / NOTES_PER_BAR;

    for (const note of barNotes) {
      const offsetInBar = note.start_s - barStart;
      const slot = Math.floor(offsetInBar / chunk_seconds);
      const colLeft = plotLeft + slot * colWidth;
      const xCenter = colLeft + colWidth * 0.5;

      const highlight = svgEl("rect", {
        class: "column-highlight",
        x: colLeft,
        y: TOP_PAD - 8,
        width: colWidth,
        height: lineY(LINE_COUNT - 1) - TOP_PAD + 16,
        "data-note-id": note.id,
      });
      highlightsLayer.appendChild(highlight);

      const hit = svgEl("rect", {
        class: "hit-column",
        x: colLeft,
        y: TOP_PAD - 8,
        width: colWidth,
        height: lineY(LINE_COUNT - 1) - TOP_PAD + 16,
        "data-note-id": note.id,
      });
      hit.noteRef = note;
      hitsLayer.appendChild(hit);

      categoryKeys.forEach((catKey, lineIndex) => {
        drawNote(dotsLayer, note, catKey, lineIndex, xCenter);
      });
    }

    svg.appendChild(highlightsLayer);
    svg.appendChild(dotsLayer);
    svg.appendChild(hitsLayer);

    wireBarInteraction(svg);

    return svg;
  }

  function wireBarInteraction(svg) {
    const tooltip = document.getElementById("tooltip");
    const hits = svg.querySelectorAll(".hit-column");

    hits.forEach((hit) => {
      const note = hit.noteRef;
      const noteId = note.id;

      hit.addEventListener("mouseenter", (e) => {
        svg
          .querySelectorAll(`.column-highlight[data-note-id="${noteId}"]`)
          .forEach((el) => el.classList.add("visible"));
        showTooltip(e, note);
      });

      hit.addEventListener("mousemove", (e) => {
        positionTooltip(e);
      });

      hit.addEventListener("mouseleave", () => {
        svg
          .querySelectorAll(`.column-highlight[data-note-id="${noteId}"]`)
          .forEach((el) => el.classList.remove("visible"));
        hideTooltip();
      });

      hit.addEventListener("click", () => {
        openDrawer(note);
      });
    });
  }

  function partInfo(partNum) {
    return parts.find((p) => p.part === partNum) || { label: `Part ${partNum}` };
  }

  function showTooltip(event, note) {
    const tooltip = document.getElementById("tooltip");
    const info = partInfo(note.part);
    const time = formatStreamTime(note.start_s);

    let rows = "";
    for (const cat of categoryKeys) {
      const c = note.categories[cat];
      const short = categoryLabel[cat] || cat;
      if (!note.scored || c.expected == null) {
        rows += `<div class="tt-row"><span class="tt-cat">${escapeHtml(short)}</span><span>—</span></div>`;
      } else {
        const tierName = c.tier || tiers[c.tier_index] || "—";
        rows += `<div class="tt-row"><span class="tt-cat">${escapeHtml(short)}</span><span>${escapeHtml(tierName)} (${c.expected.toFixed(2)})</span></div>`;
      }
    }

    const excerpt = (note.excerpt || "").slice(0, 240);
    tooltip.innerHTML = `
      <div class="tt-time">${escapeHtml(info.label)} · ${time}</div>
      ${rows}
      <div class="tt-excerpt">${escapeHtml(excerpt)}${note.excerpt && note.excerpt.length > 240 ? "…" : ""}</div>
    `;
    tooltip.classList.add("visible");
    positionTooltip(event);
  }

  function positionTooltip(event) {
    const tooltip = document.getElementById("tooltip");
    const pad = 14;
    let left = event.clientX + pad;
    let top = event.clientY + pad;
    const rect = tooltip.getBoundingClientRect();
    if (left + rect.width > window.innerWidth - 8) {
      left = event.clientX - rect.width - pad;
    }
    if (top + rect.height > window.innerHeight - 8) {
      top = event.clientY - rect.height - pad;
    }
    tooltip.style.left = `${Math.max(8, left)}px`;
    tooltip.style.top = `${Math.max(8, top)}px`;
  }

  function hideTooltip() {
    document.getElementById("tooltip").classList.remove("visible");
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  const CONTEXT_WORDS = 500;

  function notesForPart(partNum) {
    return notes
      .filter((n) => n.part === partNum)
      .sort((a, b) => a.chunk_index - b.chunk_index);
  }

  function splitWords(text) {
    if (!text || !String(text).trim()) return [];
    return String(text).trim().split(/\s+/);
  }

  function lastNWords(text, n) {
    const words = splitWords(text);
    if (words.length <= n) return words.join(" ");
    return words.slice(-n).join(" ");
  }

  function firstNWords(text, n) {
    const words = splitWords(text);
    if (words.length <= n) return words.join(" ");
    return words.slice(0, n).join(" ");
  }

  function noteFullText(note) {
    return note.text != null && note.text !== "" ? note.text : note.excerpt || "";
  }

  function precedingContext(note) {
    const partNotes = notesForPart(note.part);
    const idx = partNotes.findIndex((n) => n.id === note.id);
    if (idx <= 0) return "";
    const combined = partNotes
      .slice(0, idx)
      .map((n) => noteFullText(n))
      .join(" ");
    return lastNWords(combined, CONTEXT_WORDS);
  }

  function followingContext(note) {
    const partNotes = notesForPart(note.part);
    const idx = partNotes.findIndex((n) => n.id === note.id);
    if (idx < 0 || idx >= partNotes.length - 1) return "";
    const combined = partNotes
      .slice(idx + 1)
      .map((n) => noteFullText(n))
      .join(" ");
    return firstNWords(combined, CONTEXT_WORDS);
  }

  function partTranscriptText(partNum) {
    return notesForPart(partNum)
      .map((n) => noteFullText(n))
      .join("\n\n");
  }

  function entireTranscriptText() {
    const sortedParts = [...parts].sort((a, b) => a.part - b.part);
    return sortedParts
      .map((p) => {
        const header = `=== ${p.label} ===`;
        return `${header}\n\n${partTranscriptText(p.part)}`;
      })
      .join("\n\n");
  }

  function fallbackCopyText(text) {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    ta.style.top = "0";
    document.body.appendChild(ta);
    ta.select();
    ta.setSelectionRange(0, text.length);
    let ok = false;
    try {
      ok = document.execCommand("copy");
    } catch {
      ok = false;
    }
    document.body.removeChild(ta);
    return ok;
  }

  function copyTextToClipboard(text) {
    return new Promise((resolve, reject) => {
      if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
        navigator.clipboard
          .writeText(text)
          .then(() => resolve())
          .catch(() => {
            if (fallbackCopyText(text)) resolve();
            else reject(new Error("copy failed"));
          });
      } else if (fallbackCopyText(text)) {
        resolve();
      } else {
        reject(new Error("copy failed"));
      }
    });
  }

  function wireCopyButton(button, getText, defaultLabel) {
    button.addEventListener("click", () => {
      const label = defaultLabel || button.textContent;
      copyTextToClipboard(getText())
        .then(() => {
          button.textContent = "Copied";
          setTimeout(() => {
            button.textContent = label;
          }, 1500);
        })
        .catch(() => {
          button.textContent = "Copy failed";
          setTimeout(() => {
            button.textContent = label;
          }, 1500);
        });
    });
  }

  function openDrawer(note) {
    const backdrop = document.getElementById("drawer-backdrop");
    const drawer = document.getElementById("drawer");
    const info = partInfo(note.part);

    document.getElementById("drawer-title").textContent = `${info.label} · ${formatStreamTime(note.start_s)}`;
    document.getElementById("drawer-meta").textContent = `${note.words} words · ${note.id}`;

    const catsEl = document.getElementById("drawer-cats");
    catsEl.innerHTML = "";
    for (const cat of categoryKeys) {
      const c = note.categories[cat];
      const row = document.createElement("div");
      row.className = "drawer-cat-row";
      const name = document.createElement("div");
      name.className = "drawer-cat-name";
      name.textContent = categoryLabel[cat] || cat;
      const stats = document.createElement("div");
      stats.className = "drawer-cat-stats";
      if (!note.scored || c.expected == null) {
        stats.innerHTML = '<span class="unscored">Not scored yet</span>';
      } else {
        const tierName = c.tier || tiers[c.tier_index] || "—";
        const conf = c.confidence != null ? c.confidence.toFixed(2) : "—";
        stats.textContent = `${tierName} · expected ${c.expected.toFixed(2)} · confidence ${conf}`;
      }
      row.appendChild(name);
      row.appendChild(stats);
      catsEl.appendChild(row);
    }

    const pane = document.getElementById("drawer-transcript-pane");
    pane.innerHTML = "";

    const before = precedingContext(note);
    if (before) {
      const beforeEl = document.createElement("div");
      beforeEl.className = "drawer-transcript-block drawer-transcript-context";
      beforeEl.textContent = before;
      pane.appendChild(beforeEl);
    }

    const startDivider = document.createElement("div");
    startDivider.className = "drawer-chunk-divider";
    startDivider.id = "drawer-chunk-start";
    startDivider.textContent = "chunk start";
    pane.appendChild(startDivider);

    const chunkEl = document.createElement("div");
    chunkEl.className = "drawer-transcript-block drawer-transcript-chunk";
    chunkEl.textContent = noteFullText(note);
    pane.appendChild(chunkEl);

    const endDivider = document.createElement("div");
    endDivider.className = "drawer-chunk-divider";
    endDivider.textContent = "chunk end";
    pane.appendChild(endDivider);

    const after = followingContext(note);
    if (after) {
      const afterEl = document.createElement("div");
      afterEl.className = "drawer-transcript-block drawer-transcript-context";
      afterEl.textContent = after;
      pane.appendChild(afterEl);
    }

    backdrop.classList.add("open");
    drawer.classList.add("open");
    hideTooltip();

    const scrollToChunk = () => {
      const marker = document.getElementById("drawer-chunk-start");
      if (marker) {
        pane.scrollTop = marker.offsetTop;
      }
    };
    requestAnimationFrame(() => {
      requestAnimationFrame(scrollToChunk);
    });
  }

  function closeDrawer() {
    document.getElementById("drawer-backdrop").classList.remove("open");
    document.getElementById("drawer").classList.remove("open");
  }

  function renderLegend() {
    const tierLegend = document.getElementById("legend-tiers");
    tierLegend.innerHTML = "";
    tiers.forEach((name, i) => {
      const exp = i;
      const r = exp < 0.35 ? 3 : radiusFromExpected(exp);
      const item = document.createElement("div");
      item.className = "legend-tier";
      const svg = svgEl("svg", { width: 28, height: 28 });
      const circle = svgEl("circle", {
        cx: 14,
        cy: 14,
        r: Math.min(r, 11),
        fill: "#4a453d",
        opacity: 0.75,
      });
      svg.appendChild(circle);
      if (i === topTierIndex) {
        svg.appendChild(
          svgEl("circle", {
            cx: 14,
            cy: 14,
            r: Math.min(r, 11) + 2,
            fill: "none",
            stroke: "#1a1814",
            "stroke-width": 1,
          })
        );
      }
      item.appendChild(svg);
      const label = document.createElement("span");
      label.textContent = name;
      item.appendChild(label);
      tierLegend.appendChild(item);
    });

    const catLegend = document.getElementById("legend-cats");
    catLegend.innerHTML = "";
    categoryDefs.forEach((cat, i) => {
      const item = document.createElement("div");
      item.className = "legend-cat";
      const sw = document.createElement("span");
      sw.className = "legend-swatch";
      sw.style.background = colorForCategory(i);
      item.appendChild(sw);
      const label = document.createElement("span");
      label.textContent = cat.label || cat.key;
      item.appendChild(label);
      catLegend.appendChild(item);
    });
  }

  function renderControls() {
    const row = document.getElementById("category-pills");
    row.innerHTML = "";
    categoryKeys.forEach((cat) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "pill active";
      btn.dataset.category = cat;
      btn.textContent = categoryLabel[cat] || cat;
      btn.addEventListener("click", () => {
        categoryVisible[cat] = !categoryVisible[cat];
        btn.classList.toggle("active", categoryVisible[cat]);
        btn.classList.toggle("dimmed", !categoryVisible[cat]);
        rerender();
      });
      row.appendChild(btn);
    });

    const topBtn = document.getElementById("top-tier-toggle");
    topBtn.classList.toggle("active", topTierOnly);
    topBtn.addEventListener("click", () => {
      topTierOnly = !topTierOnly;
      topBtn.classList.toggle("active", topTierOnly);
      rerender();
    });
  }

  function renderParts() {
    const root = document.getElementById("parts-root");
    root.innerHTML = "";
    const plotWidth = Math.max(320, Math.min(1200, window.innerWidth - GUTTER - 48));

    const sortedParts = [...parts].sort((a, b) => a.part - b.part);

    for (const info of sortedParts) {
      const partNum = info.part;
      const section = document.createElement("section");
      section.className = "part-section";

      const headingRow = document.createElement("div");
      headingRow.className = "part-heading-row";

      const h2 = document.createElement("h2");
      h2.textContent = info.label || `Part ${partNum}`;
      headingRow.appendChild(h2);

      const copyPartBtn = document.createElement("button");
      copyPartBtn.type = "button";
      copyPartBtn.className = "pill copy-btn";
      copyPartBtn.textContent = "Copy transcript";
      wireCopyButton(copyPartBtn, () => partTranscriptText(partNum), "Copy transcript");
      headingRow.appendChild(copyPartBtn);

      section.appendChild(headingRow);

      const bars = barCountForPart(partNum);
      for (let b = 0; b < bars; b++) {
        const barStart = b * bar_seconds;
        const barEnd = barStart + bar_seconds;
        const wrap = document.createElement("div");
        wrap.className = "bar-wrap";

        const barLbl = document.createElement("div");
        barLbl.className = "bar-label";
        barLbl.textContent = `${formatStreamTime(barStart)} – ${formatStreamTime(barEnd)}`;
        wrap.appendChild(barLbl);

        wrap.appendChild(buildBar(partNum, info.label, b, plotWidth));
        section.appendChild(wrap);
      }

      root.appendChild(section);
    }
  }

  function rerender() {
    renderParts();
  }

  function initHeader() {
    document.getElementById("page-title").textContent = title || "Transcript heatmap";
    document.title = title || "Transcript heatmap";
    const subEl = document.getElementById("subtitle");
    if (subtitle) {
      subEl.textContent = subtitle;
    } else {
      const hours = (total_count * chunk_seconds) / 3600;
      const hoursStr = hours % 1 === 0 ? String(hours) : hours.toFixed(1);
      subEl.textContent = `${parts.length} parts · ${hoursStr} hours · ${total_count} chunks · ${scored_count} scored`;
    }
  }

  function init() {
    initHeader();
    renderLegend();
    renderControls();
    renderParts();

    document.getElementById("drawer-close").addEventListener("click", closeDrawer);
    document.getElementById("drawer-backdrop").addEventListener("click", closeDrawer);

    wireCopyButton(
      document.getElementById("copy-everything"),
      entireTranscriptText,
      "Copy everything"
    );
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeDrawer();
    });

    let resizeTimer;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(renderParts, 150);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
