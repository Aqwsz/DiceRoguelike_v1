(() => {
  const $ = (id) => document.getElementById(id);

  const titleScreen = $("screen-title");
  const playScreen = $("screen-play");
  const partyEl = $("party-fighters");
  const enemyEl = $("enemy-fighters");
  const logEl = $("combat-log");
  const choicePanel = $("choice-panel");
  const choiceGrid = $("choice-grid");
  const battlefield = $("battlefield");
  const logPanel = $("log-panel");
  const manaChip = $("mana-chip");

  let pollTimer = null;
  let lastLogLen = 0;
  let busy = false;

  async function api(path, opts) {
    const res = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...opts,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

  function showPlay() {
    titleScreen.classList.add("hidden");
    playScreen.classList.remove("hidden");
  }

  function renderFighter(f, enemy) {
    const pct = f.max_hp > 0 ? Math.max(0, Math.min(100, (100 * f.hp) / f.max_hp)) : 0;
    const tags = [];
    if (f.shield) tags.push(`shield ${f.shield}`);
    if (f.poison) tags.push(`poison ${f.poison}`);
    if (f.burn) tags.push(`burn ${f.burn}`);
    if (f.weaken) tags.push(`weaken ${f.weaken}`);
    if (f.stunned) tags.push("stunned");
    if (f.thorns) tags.push("thorns");
    if (f.items && f.items.length) tags.push(f.items.join(", "));

    const color = f.color ? `<span class="color-dot color-${f.color}"></span>` : "";
    return `
      <article class="fighter ${enemy ? "enemy" : ""} ${f.alive ? "" : "dead"}">
        <div class="fighter-head">
          <span class="fighter-name">${color}${escapeHtml(f.name)}</span>
          <span>${f.alive ? "" : "fallen"}</span>
        </div>
        <div class="hp-track"><div class="hp-fill" style="width:${pct}%"></div></div>
        <div class="hp-meta">
          <span>${f.hp}/${f.max_hp} HP</span>
          <span>${f.tier !== "" && f.tier != null ? `T${f.tier}` : ""}</span>
        </div>
        ${tags.length ? `<div class="status-tags">${escapeHtml(tags.join(" · "))}</div>` : ""}
      </article>
    `;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function renderState(state) {
    if (!state) return;

    if (state.phase === "boot") {
      titleScreen.classList.remove("hidden");
      playScreen.classList.add("hidden");
      return;
    }

    showPlay();
    $("phase-title").textContent = state.title || "";
    $("phase-sub").textContent = state.subtitle || "";
    $("fight-label").textContent = state.fight ? `Fight ${state.fight}` : "Run";

    const inFight = state.phase === "fight";
    battlefield.classList.toggle("dimmed", !inFight && state.phase === "choice");
    logPanel.classList.toggle("dimmed", !inFight && state.phase === "choice");
    logPanel.classList.toggle("hidden", state.phase === "choice" && !(state.enemies || []).length);

    if ((state.mana || 0) > 0 || inFight) {
      manaChip.classList.remove("hidden");
      $("mana-val").textContent = String(state.mana || 0);
    } else {
      manaChip.classList.add("hidden");
    }

    partyEl.innerHTML = (state.party || []).map((f) => renderFighter(f, false)).join("");
    enemyEl.innerHTML = (state.enemies || []).map((f) => renderFighter(f, true)).join("");

    const log = state.log || [];
    if (log.length !== lastLogLen) {
      logEl.innerHTML = log
        .map((e) => `<div class="entry ${e.kind || ""}">${escapeHtml(e.text)}</div>`)
        .join("");
      logEl.scrollTop = logEl.scrollHeight;
      lastLogLen = log.length;
    }

    const choice = state.choice;
    if (choice && choice.options && choice.options.length) {
      choicePanel.classList.remove("hidden");
      choiceGrid.innerHTML = choice.options
        .map((opt, i) => {
          const heroes = (opt.heroes || [])
            .map(
              (h) =>
                `<span class="hero-chip">${escapeHtml(h.name)} · ${h.hp} HP</span>`
            )
            .join("");
          return `
            <button type="button" class="choice-card" data-index="${i}">
              <span class="label">${escapeHtml(opt.label)}</span>
              <span class="detail">${escapeHtml(opt.detail || "")}</span>
              ${heroes ? `<div class="hero-chip-row">${heroes}</div>` : ""}
            </button>
          `;
        })
        .join("");
    } else {
      choicePanel.classList.add("hidden");
      choiceGrid.innerHTML = "";
    }
  }

  async function poll() {
    try {
      const state = await api("/api/state");
      renderState(state);
    } catch (_) {
      /* server restarting */
    }
  }

  function startPolling() {
    if (pollTimer) clearInterval(pollTimer);
    pollTimer = setInterval(poll, 280);
  }

  $("btn-start").addEventListener("click", async () => {
    if (busy) return;
    busy = true;
    try {
      lastLogLen = 0;
      const state = await api("/api/new", { method: "POST", body: "{}" });
      renderState(state);
      startPolling();
    } finally {
      busy = false;
    }
  });

  choiceGrid.addEventListener("click", async (ev) => {
    const card = ev.target.closest(".choice-card");
    if (!card || busy) return;
    busy = true;
    try {
      const index = Number(card.dataset.index);
      const state = await api("/api/choose", {
        method: "POST",
        body: JSON.stringify({ index }),
      });
      renderState(state);
    } finally {
      busy = false;
    }
  });

  // Idle title until Start.
  poll();
})();
