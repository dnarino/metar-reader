/* METAR Reader: small client-side features (no framework). */
(function () {
  "use strict";

  const RECENT_KEY = "metar.recent";
  const FAVORITES_KEY = "metar.favorites";
  const MAX_RECENT = 12;

  // ---- Storage (localStorage can be unavailable, e.g. in private mode) ----

  function load(key) {
    try {
      const value = JSON.parse(localStorage.getItem(key) || "[]");
      return Array.isArray(value) ? value : [];
    } catch (e) {
      return [];
    }
  }

  function save(key, list) {
    try {
      localStorage.setItem(key, JSON.stringify(list));
    } catch (e) {
      /* storage disabled: features just won't persist */
    }
  }

  // ---- Zulu clock ----

  function startClock() {
    const el = document.getElementById("zulu-clock");
    if (!el) return;
    const tick = () => {
      const now = new Date();
      const hh = String(now.getUTCHours()).padStart(2, "0");
      const mm = String(now.getUTCMinutes()).padStart(2, "0");
      el.textContent = `${hh}:${mm} ZULU`;
    };
    tick();
    setInterval(tick, 1000);
  }

  // ---- Search input ----

  function setupSearch() {
    const input = document.getElementById("code-input");
    const clear = document.getElementById("clear-input");
    if (!input) return;
    input.addEventListener("input", () => {
      const pos = input.selectionStart;
      input.value = input.value.toUpperCase();
      input.setSelectionRange(pos, pos);
      if (clear) clear.hidden = input.value === "";
    });
    if (clear) {
      clear.addEventListener("click", () => {
        input.value = "";
        clear.hidden = true;
        input.focus();
      });
    }
  }

  // ---- Copy raw METAR ----

  function setupCopy() {
    const btn = document.getElementById("copy-raw");
    const raw = document.getElementById("raw-metar");
    if (!btn || !raw) return;
    const label = btn.querySelector(".copy-label");
    btn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(raw.textContent.trim());
        label.textContent = "Copied!";
      } catch (e) {
        label.textContent = "Press Ctrl+C";
        window.getSelection().selectAllChildren(raw);
      }
      setTimeout(() => { label.textContent = "Copy"; }, 2000);
    });
  }

  // ---- Current station: record lookup + favorite toggle ----

  function stationFromPage() {
    const el = document.getElementById("station");
    if (!el) return null;
    const d = el.dataset;
    return {
      code: d.code,
      name: d.name,
      location: d.location || null,
      category: d.category,
      temp_f: d.tempF === "" ? null : Number(d.tempF),
    };
  }

  function recordLookup(station) {
    const recent = load(RECENT_KEY).filter((s) => s.code !== station.code);
    recent.unshift({ ...station, ts: Date.now() });
    save(RECENT_KEY, recent.slice(0, MAX_RECENT));
  }

  function setupFavoriteToggle(station) {
    const btn = document.getElementById("fav-toggle");
    if (!btn) return;
    const label = btn.querySelector(".fav-label");
    const isFav = () => load(FAVORITES_KEY).some((s) => s.code === station.code);
    const render = () => {
      const fav = isFav();
      btn.setAttribute("aria-pressed", String(fav));
      label.textContent = fav ? "Favorite" : "Add to favorites";
    };
    btn.addEventListener("click", () => {
      let favs = load(FAVORITES_KEY);
      if (isFav()) {
        favs = favs.filter((s) => s.code !== station.code);
      } else {
        favs.push({ code: station.code, name: station.name, location: station.location });
      }
      save(FAVORITES_KEY, favs);
      render();
      renderAllLists();
    });
    render();
  }

  // ---- Station lists (favorites / recent) ----

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function categoryBadge(item) {
    if (!item.category) return null;
    const temp = item.temp_f != null ? ` ${item.temp_f}°` : "";
    return el("span", `cat cat-${item.category}`, `${item.category}${temp}`);
  }

  function renderList(listEl, items, opts) {
    listEl.replaceChildren();
    if (!items.length) {
      const msg = opts.kind === "favorites"
        ? "No favorites yet. Open an airport and press “Add to favorites”."
        : "No lookups yet. Search for an airport to get started.";
      listEl.append(el("li", "empty", msg));
      return;
    }
    for (const item of items) {
      const li = el("li");
      const link = el("a", "station-row");
      link.href = `/station/${encodeURIComponent(item.code)}`;

      const left = el("div");
      left.style.minWidth = "0";
      left.append(el("span", "code", item.code));
      const where = item.name || item.location;
      if (where) left.append(el("span", "where", where));
      if (opts.detailed && item.summary) left.append(el("span", "summary", item.summary));
      if (opts.detailed && item.unavailable) left.append(el("span", "summary", "No current report"));

      const right = el("div", "right");
      const badge = categoryBadge(item);
      if (badge) right.append(badge);
      if (opts.detailed && item.obs) right.append(el("span", "caption muted mono", item.obs));

      link.append(left, right);
      li.append(link);

      if (opts.removable) {
        const remove = el("button", "icon-btn");
        remove.type = "button";
        remove.title = `Remove ${item.code}`;
        remove.append(el("span", "material-symbols-outlined icon-sm", "close"));
        remove.addEventListener("click", () => {
          const key = opts.kind === "favorites" ? FAVORITES_KEY : RECENT_KEY;
          save(key, load(key).filter((s) => s.code !== item.code));
          renderAllLists();
        });
        li.append(remove);
      }
      listEl.append(li);
    }
  }

  const liveCache = {};

  async function fetchLive(codes) {
    const missing = codes.filter((c) => !(c in liveCache));
    if (missing.length) {
      try {
        const res = await fetch(`/api/stations?ids=${encodeURIComponent(missing.join(","))}`);
        if (!res.ok) throw new Error(res.status);
        const data = await res.json();
        for (const c of missing) liveCache[c] = null;
        for (const s of data.stations) liveCache[s.code] = s;
      } catch (e) {
        return {}; // keep showing the stored data
      }
    }
    return liveCache;
  }

  function renderAllLists() {
    document.querySelectorAll("[data-station-list]").forEach(async (listEl) => {
      const kind = listEl.dataset.stationList;
      const opts = {
        kind,
        detailed: "detailed" in listEl.dataset,
        removable: "removable" in listEl.dataset,
      };
      const limit = Number(listEl.dataset.limit) || Infinity;
      const stored = load(kind === "favorites" ? FAVORITES_KEY : RECENT_KEY).slice(0, limit);

      renderList(listEl, stored, opts); // instant, from storage
      if (!stored.length) return;

      const live = await fetchLive(stored.map((s) => s.code));
      if (!Object.keys(live).length) return;
      const merged = stored.map((s) => {
        if (live[s.code]) return { ...s, ...live[s.code] };
        if (live[s.code] === null) return { ...s, category: null, temp_f: null, unavailable: true };
        return s;
      });
      renderList(listEl, merged, opts);
    });
  }

  // ---- Start ----

  startClock();
  setupSearch();
  setupCopy();
  const station = stationFromPage();
  if (station) {
    recordLookup(station);
    setupFavoriteToggle(station);
  }
  renderAllLists();
})();
