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
  const btnNext = $("btn-next");
  const chkAuto = $("chk-auto");
  const dicePanel = $("dice-panel");
  const diceFaces = $("dice-panel-faces");
  const invPanel = $("inv-panel");
  const invBag = $("inv-bag");
  const invParty = $("inv-party");
  const facePickPanel = $("face-pick-panel");
  const facePickFaces = $("face-pick-faces");
  const menuPanel = $("menu-panel");
  const menuStatus = $("menu-status");
  const btnContinue = $("btn-continue");
  const menuSave = $("menu-save");
  const menuSaveQuit = $("menu-save-quit");
  const itemDetailPanel = $("item-detail-panel");
  const itemDetailWhere = $("item-detail-where");
  const itemDetailTitle = $("item-detail-title");
  const itemDetailBody = $("item-detail-body");
  const fxLayer = $("fx-layer");

  let pollTimer = null;
  let lastLogLen = 0;
  let busy = false;
  let lastState = null;
  let autoTimer = null;
  let autoArmed = false;
  let lastChoiceKey = "";
  let pendingFaceEquip = null;
  let lastPartyKey = "";
  let lastEnemyKey = "";
  let lastInvKey = "";
  let lastHeaderKey = "";
  let pollInFlight = false;
  let lastFxId = 0;
  let fxClearTimer = null;
  const shownDieFaces = {};

  function stableKey(value) {
    try {
      return JSON.stringify(value);
    } catch (_) {
      return String(value);
    }
  }

  async function api(path, opts) {
    const res = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...opts,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

  function clearAutoTimer() {
    if (autoTimer) clearTimeout(autoTimer);
    autoTimer = null;
    autoArmed = false;
  }

  function scheduleAutoAdvance(state) {
    if (!state || !state.awaiting_turn || !chkAuto.checked) {
      clearAutoTimer();
      return;
    }
    if (autoArmed) return;
    autoArmed = true;
    const ms = Math.max(200, Math.round((state.turn_seconds || 1) * 1000));
    autoTimer = setTimeout(async () => {
      autoTimer = null;
      autoArmed = false;
      if (!chkAuto.checked) return;
      try {
        const next = await api("/api/advance", { method: "POST", body: "{}" });
        renderState(next);
      } catch (_) {
        /* server restarting */
      }
    }, ms);
  }

  function showPlay() {
    titleScreen.classList.add("hidden");
    playScreen.classList.remove("hidden");
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function normalizeFaces(faces) {
    if (!faces || !faces.length) return [];
    return faces.map((f, i) => {
      if (typeof f === "string") {
        return { slot: i + 1, name: f, detail: f };
      }
      return {
        slot: f.slot || i + 1,
        name: f.name || "",
        detail: f.detail || f.name || "",
      };
    });
  }

  function renderFaceList(faces) {
    const list = normalizeFaces(faces);
    if (!list.length) return "";
    return `
      <ol class="face-list compact">
        ${list
          .map(
            (f) => `
          <li>
            <span class="face-slot">${f.slot}</span>
            <span class="face-detail">${escapeHtml(f.detail)}</span>
          </li>`
          )
          .join("")}
      </ol>
    `;
  }

  function choiceKey(state) {
    const c = state && state.choice;
    if (!c) return "";
    return `${state.title}|${c.title}|${(c.options || []).map((o) => o.label).join(";")}`;
  }

  function showDiceInspector(fighter) {
    if (!fighter) return;
    const faces = normalizeFaces(fighter.faces);
    const bits = [];
    if (fighter.color) bits.push(fighter.color);
    if (fighter.tier !== "" && fighter.tier != null) bits.push(`Tier ${fighter.tier}`);
    $("dice-panel-eyebrow").textContent = bits.length ? bits.join(" · ") : "Dice sides";
    $("dice-panel-title").textContent = fighter.name || fighter.class_name || "Fighter";
    diceFaces.innerHTML = faces.length
      ? faces
          .map(
            (f) => `
        <li>
          <span class="face-slot">${f.slot}</span>
          <span class="face-detail">${escapeHtml(f.detail)}</span>
        </li>`
          )
          .join("")
      : `<li class="face-empty">No dice data</li>`;
    dicePanel.classList.remove("hidden");
  }

  function hideDiceInspector() {
    dicePanel.classList.add("hidden");
  }

  function itemLabel(item) {
    if (!item) return "";
    if (item.title) return item.title;
    if (item.tier != null && item.tier !== "") return `[T${item.tier}] ${item.name || ""}`;
    return item.name || "";
  }

  function findItemById(itemId) {
    if (!lastState || itemId == null || Number.isNaN(itemId)) return null;
    const bag = (lastState.inventory && lastState.inventory.bag) || [];
    const inBag = bag.find((item) => Number(item.id) === itemId);
    if (inBag) return { item: inBag, where: "In bag" };
    for (const hero of lastState.party || []) {
      for (const item of hero.item_slots || []) {
        if (item && Number(item.id) === itemId) {
          return { item, where: `Equipped on ${hero.name}` };
        }
      }
    }
    return null;
  }

  function hideItemDetail() {
    itemDetailPanel.classList.add("hidden");
  }

  function showItemDetail(item) {
    if (!item) return;
    const found = findItemById(Number(item.id));
    const where = item.holder
      ? `Equipped on ${item.holder}`
      : (found && found.where) || "In bag";
    itemDetailWhere.textContent = where;
    itemDetailTitle.textContent = itemLabel(item) || "Item";
    itemDetailBody.textContent = item.detail || "No description.";
    itemDetailPanel.classList.remove("hidden");
  }

  function itemFromTarget(el) {
    const bagItem = el.closest(".bag-item");
    const filled = el.closest(".item-slot.filled");
    const node = bagItem || filled;
    if (!node) return null;
    const itemId = Number(node.dataset.itemId);
    const found = findItemById(itemId);
    if (found) return found.item;
    // Fallback if state is briefly out of sync with the DOM.
    return {
      id: itemId,
      title: node.dataset.itemTitle || "",
      detail: node.dataset.itemDetail || "",
      holder: node.dataset.itemHolder || null,
    };
  }

  function renderItemSlots(f, heroIndex) {
    const slots = f.item_slots || [];
    const maxSlots = f.max_item_slots || slots.length || 0;
    if (!maxSlots) return "";
    const cells = [];
    for (let i = 0; i < maxSlots; i++) {
      const item = slots[i];
      if (item) {
        const label = itemLabel(item);
        cells.push(`
          <div class="item-slot filled"
               data-hero="${heroIndex}"
               data-slot="${i}"
               data-item-id="${item.id}"
               data-item-title="${escapeHtml(label)}"
               data-item-detail="${escapeHtml(item.detail || "")}"
               data-item-holder="${escapeHtml(item.holder || "")}"
               draggable="true"
               title="Right-click for description">
            <span class="item-slot-name">${escapeHtml(label)}</span>
          </div>`);
      } else {
        cells.push(`
          <div class="item-slot empty"
               data-hero="${heroIndex}"
               data-slot="${i}"
               title="Empty item slot">
            <span class="item-slot-name">Slot ${i + 1}</span>
          </div>`);
      }
    }
    return `<div class="item-slots" data-hero="${heroIndex}">${cells.join("")}</div>`;
  }

  function dieKey(side, index) {
    return `${side}-${index}`;
  }

  function shortFaceLabel(text) {
    const raw = String(text || "?").trim();
    if (!raw || raw === "?") return "?";
    // Keep labels readable on a small die face.
    return raw.length > 14 ? `${raw.slice(0, 13)}…` : raw;
  }

  function clearAttackLine() {
    if (fxClearTimer) {
      clearTimeout(fxClearTimer);
      fxClearTimer = null;
    }
    if (fxLayer) fxLayer.innerHTML = "";
    document.querySelectorAll(".battle-die.rolling, .battle-die.landed, .fighter.hit-flash").forEach((el) => {
      el.classList.remove("rolling", "landed", "hit-flash");
    });
  }

  function fighterEl(side, index) {
    return document.querySelector(`.fighter[data-side="${side}"][data-index="${index}"]`);
  }

  function dieEl(side, index) {
    return document.querySelector(`.battle-die[data-side="${side}"][data-index="${index}"]`);
  }

  function centerInBattlefield(el) {
    if (!el || !battlefield) return null;
    const a = el.getBoundingClientRect();
    const b = battlefield.getBoundingClientRect();
    return {
      x: a.left + a.width / 2 - b.left,
      y: a.top + a.height / 2 - b.top,
    };
  }

  function drawAttackLine(fromEl, toEl) {
    if (!fxLayer || !fromEl || !toEl) return;
    const from = centerInBattlefield(fromEl);
    const to = centerInBattlefield(toEl);
    if (!from || !to) return;
    const b = battlefield.getBoundingClientRect();
    fxLayer.setAttribute("viewBox", `0 0 ${b.width} ${b.height}`);
    fxLayer.innerHTML = `
      <line class="fx-line" x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}" />
      <circle class="fx-spark" cx="${to.x}" cy="${to.y}" r="5" />
    `;
  }

  function playCombatFx(fx, state) {
    if (!fx || !fx.id || fx.id === lastFxId) return;
    lastFxId = fx.id;
    clearAttackLine();

    const actor = fx.actor || {};
    const target = fx.target || {};
    const actorDie = dieEl(actor.side, actor.index);
    const actorCard = fighterEl(actor.side, actor.index);
    const targetCard = target.side != null ? fighterEl(target.side, target.index) : null;
    if (!actorDie) return;

    const faceLabel = shortFaceLabel(fx.face || "?");
    const key = dieKey(actor.side, actor.index);
    const faceLabelEl = actorDie.querySelector(".battle-die-face");
    const pool = ((state[actor.side === "enemy" ? "enemies" : "party"] || [])[actor.index] || {}).faces || [];
    const scramble = pool.map((f) => shortFaceLabel(f.name || f.detail || "?")).filter(Boolean);
    if (!scramble.length) scramble.push("?", "•", "◆");

    if (fx.kind === "stun") {
      actorDie.classList.add("landed");
      if (faceLabelEl) faceLabelEl.textContent = "Stun";
      shownDieFaces[key] = "Stun";
      return;
    }

    actorDie.classList.add("rolling");
    let tick = 0;
    const scrambleTimer = setInterval(() => {
      if (faceLabelEl) faceLabelEl.textContent = scramble[tick % scramble.length];
      tick += 1;
    }, 55);

    setTimeout(() => {
      clearInterval(scrambleTimer);
      actorDie.classList.remove("rolling");
      actorDie.classList.add("landed");
      if (faceLabelEl) faceLabelEl.textContent = faceLabel;
      shownDieFaces[key] = faceLabel;
      if (targetCard && targetCard !== actorCard) {
        drawAttackLine(actorDie, targetCard);
        targetCard.classList.add("hit-flash");
      }
      const holdMs = Math.max(400, Math.round(((state.turn_seconds || 1) * 1000) * 0.75));
      fxClearTimer = setTimeout(() => {
        if (fxLayer) fxLayer.innerHTML = "";
        actorDie.classList.remove("landed");
        if (targetCard) targetCard.classList.remove("hit-flash");
        fxClearTimer = null;
      }, holdMs);
    }, 320);
  }

  function renderFighter(f, enemy, index) {
    const pct = f.max_hp > 0 ? Math.max(0, Math.min(100, (100 * f.hp) / f.max_hp)) : 0;
    const tags = [];
    if (f.shield) tags.push(`shield ${f.shield}`);
    if (f.poison) tags.push(`poison ${f.poison}`);
    if (f.burn) tags.push(`burn ${f.burn}`);
    if (f.weaken) tags.push(`weaken ${f.weaken}`);
    if (f.stunned) tags.push("stunned");
    if (f.thorns) tags.push("thorns");

    const color = f.color ? `<span class="color-dot color-${f.color}"></span>` : "";
    const kind = enemy ? "foe" : "party-hero";
    const side = enemy ? "enemy" : "party";
    const faceShown = shownDieFaces[dieKey(side, index)] || "?";
    const dieHtml = `
      <div class="battle-die" data-side="${side}" data-index="${index}" aria-hidden="true">
        <span class="battle-die-face">${escapeHtml(shortFaceLabel(faceShown))}</span>
      </div>`;
    return `
      <div class="fighter-row ${enemy ? "foe-row" : "party-row"}">
        ${enemy ? dieHtml : ""}
        <article class="fighter ${kind} ${f.alive ? "" : "dead"}" data-index="${index}" data-side="${side}" title="Right-click to view dice">
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
          ${enemy ? "" : renderItemSlots(f, index)}
        </article>
        ${enemy ? "" : dieHtml}
      </div>
    `;
  }

  function renderBagItem(item) {
    const label = itemLabel(item);
    return `
      <div class="bag-item" draggable="true" data-item-id="${item.id}"
           data-item-title="${escapeHtml(label)}"
           data-item-detail="${escapeHtml(item.detail || "")}"
           title="Right-click for description · drag to equip">
        <strong>${escapeHtml(label)}</strong>
        <span>${item.needs_face ? "needs die face" : "drag onto a hero slot"}</span>
      </div>`;
  }

  function renderInventory(state) {
    const bag = (state.inventory && state.inventory.bag) || [];
    invBag.innerHTML = bag.length
      ? bag.map(renderBagItem).join("")
      : `<p class="inv-empty">Bag is empty</p>`;

    invParty.innerHTML = (state.party || [])
      .map((hero, i) => {
        return `
          <div class="inv-hero" data-hero="${i}">
            <div class="inv-hero-name">${escapeHtml(hero.name)}
              <span>${hero.slots || ""}</span>
            </div>
            ${renderItemSlots(hero, i)}
          </div>`;
      })
      .join("");
  }

  function inventoryAllowed(state) {
    return !!(state && state.phase && state.phase !== "boot" && state.phase !== "fight");
  }

  function openInventory() {
    if (!inventoryAllowed(lastState)) return;
    lastInvKey = "";
    renderInventory(lastState);
    invPanel.classList.remove("hidden");
  }

  function closeInventory() {
    hideItemDetail();
    invPanel.classList.add("hidden");
  }

  function closeTopOverlay() {
    if (!itemDetailPanel.classList.contains("hidden")) {
      hideItemDetail();
      return true;
    }
    if (!facePickPanel.classList.contains("hidden")) {
      hideFacePick();
      return true;
    }
    if (!dicePanel.classList.contains("hidden")) {
      hideDiceInspector();
      return true;
    }
    if (!invPanel.classList.contains("hidden")) {
      closeInventory();
      return true;
    }
    if (!menuPanel.classList.contains("hidden")) {
      closeMenu();
      return true;
    }
    return false;
  }

  function openMenu() {
    if (!lastState || lastState.phase === "boot") return;
    const canSave = !!lastState.can_save;
    menuSave.disabled = !canSave;
    menuSaveQuit.disabled = !canSave;
    menuStatus.textContent = canSave
      ? "Save stores your party and fight. Mid-fight saves restart that fight."
      : "Finish party select before saving. You can still quit.";
    menuPanel.classList.remove("hidden");
  }

  function closeMenu() {
    menuPanel.classList.add("hidden");
  }

  async function quitToTitle(save) {
    closeMenu();
    clearAutoTimer();
    const state = await api("/api/quit", {
      method: "POST",
      body: JSON.stringify({ save: !!save }),
    });
    lastLogLen = 0;
    lastChoiceKey = "";
    lastPartyKey = lastEnemyKey = lastInvKey = lastHeaderKey = "";
    renderState(state);
  }

  function openFacePick(itemName, faces, onPick) {
    $("face-pick-title").textContent = itemName || "Choose face";
    const list = normalizeFaces(faces);
    facePickFaces.innerHTML = list
      .map((f) => {
        const slotIndex = Math.max(0, (Number(f.slot) || 1) - 1);
        return `
      <li>
        <button type="button" class="face-pick-btn" data-slot="${slotIndex}">
          <span class="face-slot">${escapeHtml(String(f.slot))}</span>
          <span class="face-detail">${escapeHtml(f.detail || f.name || "")}</span>
        </button>
      </li>`;
      })
      .join("");
    facePickFaces.onclick = (ev) => {
      const btn = ev.target.closest(".face-pick-btn");
      if (!btn) return;
      facePickPanel.classList.add("hidden");
      facePickFaces.onclick = null;
      onPick(Number(btn.dataset.slot));
    };
    facePickPanel.classList.remove("hidden");
  }

  function hideFacePick() {
    facePickPanel.classList.add("hidden");
    facePickFaces.onclick = null;
    pendingFaceEquip = null;
  }

  async function tryEquip(itemId, heroIndex, faceSlot) {
    const body = { item_id: itemId, hero_index: heroIndex };
    if (faceSlot != null) body.face_slot = faceSlot;
    const state = await api("/api/inventory/equip", {
      method: "POST",
      body: JSON.stringify(body),
    });
    if (state.needs_face) {
      pendingFaceEquip = { itemId, heroIndex };
      const bagItem =
        state.inventory &&
        state.inventory.bag &&
        state.inventory.bag.find((i) => i.id === itemId);
      openFacePick(
        itemLabel(bagItem) || "Item",
        state.faces || [],
        async (slot) => {
          pendingFaceEquip = null;
          const next = await tryEquip(itemId, heroIndex, slot);
          renderState(next);
          if (!invPanel.classList.contains("hidden")) renderInventory(next);
        }
      );
      return state;
    }
    if (state.error && state.needs_face !== true) {
      $("inv-hint").textContent = state.error;
    }
    return state;
  }

  async function tryUnequip(itemId) {
    return api("/api/inventory/unequip", {
      method: "POST",
      body: JSON.stringify({ item_id: itemId }),
    });
  }

  function bindDragHandlers(root) {
    root.addEventListener("dragstart", (ev) => {
      const bagItem = ev.target.closest(".bag-item");
      const filled = ev.target.closest(".item-slot.filled");
      if (bagItem) {
        ev.dataTransfer.setData(
          "application/x-dice-item",
          JSON.stringify({ from: "bag", itemId: Number(bagItem.dataset.itemId) })
        );
        ev.dataTransfer.effectAllowed = "move";
      } else if (filled) {
        ev.dataTransfer.setData(
          "application/x-dice-item",
          JSON.stringify({
            from: "hero",
            itemId: Number(filled.dataset.itemId),
            heroIndex: Number(filled.dataset.hero),
          })
        );
        ev.dataTransfer.effectAllowed = "move";
      } else {
        return;
      }
    });

    root.addEventListener("dragover", (ev) => {
      const slot = ev.target.closest(".item-slot.empty");
      const bag = ev.target.closest(".inv-bag");
      if (slot || bag) {
        ev.preventDefault();
        ev.dataTransfer.dropEffect = "move";
        if (slot) slot.classList.add("drop-hover");
        if (bag) bag.classList.add("drop-hover");
      }
    });

    root.addEventListener("dragleave", (ev) => {
      const slot = ev.target.closest(".item-slot");
      const bag = ev.target.closest(".inv-bag");
      if (slot) slot.classList.remove("drop-hover");
      if (bag) bag.classList.remove("drop-hover");
    });

    root.addEventListener("drop", async (ev) => {
      const slot = ev.target.closest(".item-slot.empty");
      const bag = ev.target.closest(".inv-bag");
      document.querySelectorAll(".drop-hover").forEach((el) => el.classList.remove("drop-hover"));
      let payload;
      try {
        payload = JSON.parse(ev.dataTransfer.getData("application/x-dice-item") || "{}");
      } catch (_) {
        return;
      }
      if (!payload.itemId) return;
      ev.preventDefault();
      if (busy) return;
      busy = true;
      try {
        let state;
        if (slot && payload.from === "bag") {
          state = await tryEquip(payload.itemId, Number(slot.dataset.hero));
        } else if (bag && payload.from === "hero") {
          state = await tryUnequip(payload.itemId);
        } else {
          return;
        }
        renderState(state);
        if (!invPanel.classList.contains("hidden")) renderInventory(state);
      } finally {
        busy = false;
      }
    });
  }

  function renderState(state) {
    if (!state) return;
    lastState = state;

    if (state.phase === "boot") {
      titleScreen.classList.remove("hidden");
      playScreen.classList.add("hidden");
      hideDiceInspector();
      closeInventory();
      hideFacePick();
      hideItemDetail();
      closeMenu();
      clearAutoTimer();
      lastPartyKey = lastEnemyKey = lastInvKey = lastHeaderKey = "";
      lastFxId = 0;
      Object.keys(shownDieFaces).forEach((k) => delete shownDieFaces[k]);
      clearAttackLine();
      btnContinue.classList.toggle("hidden", !state.has_save);
      return;
    }

    showPlay();
    btnContinue.classList.add("hidden");
    startPolling();

    const canUseInventory = inventoryAllowed(state);
    if (!canUseInventory) closeInventory();
    const btnInv = $("btn-inventory");
    btnInv.disabled = !canUseInventory;
    btnInv.title = canUseInventory
      ? "Manage bag and hero item slots"
      : "Inventory is closed during fights";

    const headerKey = [
      state.phase,
      state.title,
      state.subtitle,
      state.fight,
      state.mana,
      !!state.awaiting_turn,
      state.auto_play,
      !!(state.enemies || []).length,
      canUseInventory,
    ].join("|");
    if (headerKey !== lastHeaderKey) {
      lastHeaderKey = headerKey;
      $("phase-title").textContent = state.title || "";
      $("phase-sub").textContent = state.subtitle || "";
      $("fight-label").textContent = state.fight ? `Fight ${state.fight}` : "Run";

      const inFight = state.phase === "fight";
      battlefield.classList.toggle("dimmed", !inFight && state.phase === "choice");
      logPanel.classList.toggle("dimmed", !inFight && state.phase === "choice");
      logPanel.classList.toggle(
        "hidden",
        state.phase === "choice" && !(state.enemies || []).length
      );

      if ((state.mana || 0) > 0 || inFight) {
        manaChip.classList.remove("hidden");
        $("mana-val").textContent = String(state.mana || 0);
      } else {
        manaChip.classList.add("hidden");
      }

      btnNext.disabled = !state.awaiting_turn;
      if (typeof state.auto_play === "boolean" && chkAuto.checked !== state.auto_play) {
        chkAuto.checked = state.auto_play;
      }
    }

    const partyKey = stableKey(state.party || []);
    if (partyKey !== lastPartyKey) {
      lastPartyKey = partyKey;
      partyEl.innerHTML = (state.party || [])
        .map((f, i) => renderFighter(f, false, i))
        .join("");
    }

    const enemyKey = stableKey(state.enemies || []);
    if (enemyKey !== lastEnemyKey) {
      lastEnemyKey = enemyKey;
      enemyEl.innerHTML = (state.enemies || [])
        .map((f, i) => renderFighter(f, true, i))
        .join("");
    }

    if (state.phase === "fight" && state.fx) {
      playCombatFx(state.fx, state);
    } else if (state.phase !== "fight") {
      clearAttackLine();
    }

    if (!invPanel.classList.contains("hidden")) {
      const invKey = stableKey({
        bag: (state.inventory && state.inventory.bag) || [],
        party: state.party || [],
      });
      if (invKey !== lastInvKey) {
        lastInvKey = invKey;
        renderInventory(state);
      }
    }

    const log = state.log || [];
    if (log.length !== lastLogLen) {
      logEl.innerHTML = log
        .map((e) => `<div class="entry ${e.kind || ""}">${escapeHtml(e.text)}</div>`)
        .join("");
      logEl.scrollTop = logEl.scrollHeight;
      lastLogLen = log.length;
    }

    const choice = state.choice;
    const key = choiceKey(state);
    if (choice && choice.options && choice.options.length) {
      choicePanel.classList.remove("hidden");
      if (key !== lastChoiceKey) {
        choiceGrid.innerHTML = choice.options
          .map((opt, i) => {
            const heroes = (opt.heroes || [])
              .map((h) => {
                const facesHtml = renderFaceList(h.faces);
                const slotsHint = h.slots ? ` · ${h.slots}` : "";
                return `
                <div class="hero-preview">
                  <span class="hero-chip">${escapeHtml(h.name)} · ${h.hp}${
                  h.max_hp ? `/${h.max_hp}` : ""
                } HP${slotsHint}${h.tier != null && h.tier !== "" ? ` · T${h.tier}` : ""}</span>
                  ${facesHtml}
                </div>`;
              })
              .join("");
            const optionFaces =
              !opt.heroes || !opt.heroes.length ? renderFaceList(opt.faces) : "";
            return `
            <button type="button" class="choice-card" data-index="${i}">
              <span class="label">${escapeHtml(opt.label)}</span>
              <span class="detail">${escapeHtml(opt.detail || "")}</span>
              ${heroes ? `<div class="hero-preview-row">${heroes}</div>` : ""}
              ${optionFaces}
            </button>
          `;
          })
          .join("");
        lastChoiceKey = key;
        choicePanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    } else {
      // Always clear — don't gate on lastChoiceKey (choose handler resets it early).
      choicePanel.classList.add("hidden");
      choiceGrid.innerHTML = "";
      lastChoiceKey = "";
    }

    scheduleAutoAdvance(state);
  }

  async function poll() {
    if (pollInFlight) return;
    pollInFlight = true;
    try {
      const state = await api("/api/state");
      renderState(state);
    } catch (_) {
      /* server restarting */
    } finally {
      pollInFlight = false;
    }
  }

  function startPolling() {
    if (pollTimer) return;
    pollTimer = setInterval(poll, 400);
  }

  $("btn-start").addEventListener("click", async () => {
    if (busy) return;
    busy = true;
    try {
      lastLogLen = 0;
      lastChoiceKey = "";
      lastPartyKey = lastEnemyKey = lastInvKey = lastHeaderKey = "";
      const state = await api("/api/new", { method: "POST", body: "{}" });
      renderState(state);
      startPolling();
    } finally {
      busy = false;
    }
  });

  btnContinue.addEventListener("click", async () => {
    if (busy) return;
    busy = true;
    try {
      lastLogLen = 0;
      lastChoiceKey = "";
      lastPartyKey = lastEnemyKey = lastInvKey = lastHeaderKey = "";
      const state = await api("/api/continue", { method: "POST", body: "{}" });
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
      // Hide immediately so stale options can't linger under the combat log.
      choicePanel.classList.add("hidden");
      choiceGrid.innerHTML = "";
      lastChoiceKey = "";
      const state = await api("/api/choose", {
        method: "POST",
        body: JSON.stringify({ index }),
      });
      renderState(state);
      if (state.choice) {
        choicePanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    } finally {
      busy = false;
    }
  });

  btnNext.addEventListener("click", async () => {
    if (btnNext.disabled || busy) return;
    busy = true;
    try {
      const state = await api("/api/advance", { method: "POST", body: "{}" });
      renderState(state);
    } finally {
      busy = false;
    }
  });

  chkAuto.addEventListener("change", async () => {
    clearAutoTimer();
    try {
      const state = await api("/api/settings", {
        method: "POST",
        body: JSON.stringify({ auto_play: chkAuto.checked }),
      });
      renderState(state);
    } catch (_) {
      if (lastState) scheduleAutoAdvance({ ...lastState, auto_play: chkAuto.checked });
    }
  });

  $("btn-inventory").addEventListener("click", () => {
    if (!inventoryAllowed(lastState)) return;
    if (invPanel.classList.contains("hidden")) openInventory();
    else closeInventory();
  });
  $("inv-panel-close").addEventListener("click", closeInventory);
  invPanel.addEventListener("click", (ev) => {
    if (ev.target === invPanel) closeInventory();
  });

  function onItemContextMenu(ev) {
    const item = itemFromTarget(ev.target);
    if (!item) return;
    ev.preventDefault();
    ev.stopPropagation();
    showItemDetail(item);
  }

  invPanel.addEventListener("contextmenu", onItemContextMenu);
  // Delegate from the battlefield so party and foes share one path (and survive re-renders).
  battlefield.addEventListener("contextmenu", (ev) => {
    if (itemFromTarget(ev.target)) {
      onItemContextMenu(ev);
      return;
    }
    const card = ev.target.closest(".fighter[data-side]");
    if (!card || !lastState) return;
    ev.preventDefault();
    const idx = Number(card.dataset.index);
    const side = card.dataset.side;
    const fighter =
      side === "enemy"
        ? (lastState.enemies || [])[idx]
        : (lastState.party || [])[idx];
    showDiceInspector(fighter);
  });

  $("item-detail-close").addEventListener("click", hideItemDetail);
  itemDetailPanel.addEventListener("click", (ev) => {
    if (ev.target === itemDetailPanel) hideItemDetail();
  });
  $("dice-panel-close").addEventListener("click", hideDiceInspector);
  dicePanel.addEventListener("click", (ev) => {
    if (ev.target === dicePanel) hideDiceInspector();
  });
  $("face-pick-close").addEventListener("click", hideFacePick);
  facePickPanel.addEventListener("click", (ev) => {
    if (ev.target === facePickPanel) hideFacePick();
  });
  document.addEventListener("keydown", (ev) => {
    if (ev.key !== "Escape") return;
    if (closeTopOverlay()) return;
    if (lastState && lastState.phase !== "boot") openMenu();
  });

  $("menu-resume").addEventListener("click", closeMenu);
  menuPanel.addEventListener("click", (ev) => {
    if (ev.target === menuPanel) closeMenu();
  });
  menuSave.addEventListener("click", async () => {
    if (busy || menuSave.disabled) return;
    busy = true;
    try {
      const state = await api("/api/save", { method: "POST", body: "{}" });
      renderState(state);
      menuStatus.textContent = state.error
        ? state.error
        : state.saved
          ? "Saved."
          : "Save finished.";
      menuSave.disabled = !state.can_save;
      menuSaveQuit.disabled = !state.can_save;
    } finally {
      busy = false;
    }
  });
  menuSaveQuit.addEventListener("click", async () => {
    if (busy || menuSaveQuit.disabled) return;
    busy = true;
    try {
      await quitToTitle(true);
    } finally {
      busy = false;
    }
  });
  $("menu-quit").addEventListener("click", async () => {
    if (busy) return;
    busy = true;
    try {
      await quitToTitle(false);
    } finally {
      busy = false;
    }
  });

  bindDragHandlers(document);

  // Resume polling if a run is already in progress (e.g. after refresh).
  poll();
})();
