/* ==========================================================================
   APOCALYPSE TERMINAL — UI Controller
   Synchronizes real-time state with HUD, CRT meters, 7-segment LED, and inventory
   ========================================================================== */

const SEG_MAP = {
  0: "abcdef",
  1: "bc",
  2: "abged",
  3: "abgcd",
  4: "fgbc",
  5: "afgcd",
  6: "afgecd",
  7: "abc",
  8: "abcdefg",
  9: "abfgcd",
  A: "abcefg",
  b: "cdefg",
  C: "afed",
  c: "edg",
  d: "bcdeg",
  E: "afged",
  F: "afge",
  H: "bcefg",
  h: "cefg",
  L: "fed",
  n: "ceg",
  o: "cdeg",
  P: "abfeg",
  r: "eg",
  t: "defg",
  S: "afgcd",
  G: "afgedc",
  U: "bcdef",
  y: "bcdeg",
  g: "bcdfg",
  R: "abfeg",
  W: "bdf",
  j: "bc",
  u: "bcde",
  "-": "g",
  "_": "d",
  " ": "",
};

const SEG_LABELS = {
  " ": "IDLE",
  C: "COMBAT",
  H: "HUB · DAY",
  n: "HUB · NIGHT",
  F: "FORESTOS",
  b: "CALIBRATING",
  L: "LOG ENGINE",
  R: "SHORTWAVE",
  M: "OVERWORLD",
  S: "⚠ SANITY CRIT",
  d: "⚠ DANGER",
  L2: "LOG",
  P: "SHIFT PASSED",
  E: "SHIFT FAILED",
};

const ITEM_NAMES = {
  pipe: "Pipe Club",
  crowbar: "Heavy Crowbar",
  spiked_bat: "Spiked Bat",
  machete: "Rusted Machete",
  pistol: "Police 9mm",
  shotgun: "Remington 12G",
  rifle: "Hunting Rifle",
  mask: "Filter Mask",
  gas_mask: "Military Gas Mask",
  radio_parts: "Radio Parts",
  lena_notes: "Voss Notes",
  voss_cure: "Voss Serum",
  holy_charm: "Wooden Charm",
  tunnel_key: "Transit Key",
  molotov: "Molotov",
  antibiotics: "Antibiotics",
  herbal_poultice: "Herbal Poultice",
  clean_gauze: "Field Bandage",
  photo: "Class Photo",
  dog_treat: "Jerky Tin",
  halcyon_leaflet: "Halcyon Leaflet",
  wire_cutters: "Wire Cutters",
  spear: "Rebar Spear",
};

// ── Typewriter Effect ─────────────────────────────────────────────────────────
// Animates text appearing character-by-character for cinematic effect.
// Only re-runs when the text actually changes (efficient on re-renders).
const _tw = { timer: null, lastId: "", lastText: "" };

function typewriterText(el, text, eventId, speedMs) {
  if (!el) return;
  // Use eventId as cache key — avoids re-typing identical text on every state push
  const cacheKey = (eventId || "") + "|" + (text || "");
  if (cacheKey === _tw.lastText) return;
  _tw.lastText = cacheKey;

  if (_tw.timer) { clearInterval(_tw.timer); _tw.timer = null; }
  el.textContent = "";
  let i = 0;
  // Cap the full reveal at ~1.5s so long events never feel like a loading gate.
  const speed = Math.max(3, Math.min(speedMs || 16, Math.ceil(1500 / Math.max(1, text.length))));
  _tw.timer = setInterval(() => {
    if (i >= text.length) { clearInterval(_tw.timer); _tw.timer = null; return; }
    el.textContent += text[i];
    i++;
  }, speed);
}
// ─────────────────────────────────────────────────────────────────────────────

function setBar(id, value, max) {
  const el = document.getElementById(id);
  if (!el) return;
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  el.style.width = pct + "%";
}

function showSeg(state) {
  // Engine is now the single source of truth (state.seg / state.seg_danger),
  // so the on-screen mirror can never drift from the physical 7-segment.
  let ch = " ";
  let danger = false;
  if (state && typeof state === "object" && "seg" in state) {
    ch = String(state.seg || " ").trim() || " ";
    danger = !!state.seg_danger;
  } else {
    // Back-compat fallback (old save / raw health arg)
    const health = typeof state === "number" ? state : (state && state.player && state.player.health) || 0;
    ch = String(Math.min(9, Math.max(0, Math.floor(health / 10))));
  }

  const on = SEG_MAP[ch] || SEG_MAP[ch.toUpperCase()] || "";
  document.querySelectorAll(".seg-d").forEach((d) => {
    const segName = [...d.classList].find((c) => "abcdefg".includes(c));
    d.classList.toggle("on", on.includes(segName));
  });

  const segEl = document.getElementById("seg");
  if (segEl) segEl.classList.toggle("danger", danger);
  const lbl = document.getElementById("seg-label");
  if (lbl) lbl.textContent = danger ? `⚠ ${SEG_LABELS[ch] || "ALERT"}` : (SEG_LABELS[ch] || "HEALTH DIGIT");
}

function escapeHtml(s) {
  return String(s || "").replace(/[&<>]/g, (c) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
  }[c]));
}

function updateUI(state) {
  if (!state || !state.player) return;
  const p = state.player;
  const w = state.world;

  // 1. HUD & CLOCK
  document.getElementById("day").textContent = w.day;
  const clockEl = document.getElementById("clock");
  clockEl.textContent = w.is_night ? "NIGHT" : "DAY";
  document.getElementById("weather").textContent = (w.weather || "clear").toUpperCase();
  document.getElementById("location").textContent = w.location || "Home Base";

  // 2. METERS
  document.getElementById("health").textContent = p.health;
  document.getElementById("infection").textContent = p.infection;
  document.getElementById("morale").textContent = p.morale;
  document.getElementById("humanity").textContent = p.humanity;
  document.getElementById("fort").textContent = w.fortification;

  setBar("bar-hp", p.health, 100);
  setBar("bar-inf", p.infection, 100);
  setBar("bar-mor", p.morale, 100);
  setBar("bar-hum", p.humanity, 100);
  setBar("bar-fort", w.fortification, 10);

  // 3. 7-SEGMENT DISPLAY (synced from engine)
  showSeg(state);

  // 4. RESOURCES
  document.getElementById("food").textContent = p.food;
  document.getElementById("water").textContent = p.water;
  document.getElementById("ammo").textContent = p.ammo;
  document.getElementById("scrap").textContent = p.scrap;
  document.getElementById("medkits").textContent = p.medkits;
  document.getElementById("weapon").textContent = (p.weapon || "fists").toUpperCase().replace("_", " ");

  const stageEl = document.getElementById("stage");
  const stage = state.infection_stage || "clean";
  stageEl.textContent = stage.toUpperCase();
  stageEl.className = `stage-${stage}`;

  // 5. STORY EVENT & BUTTONS
  const ev = state.current_event;
  if (ev) {
    document.getElementById("event-title").textContent = ev.title || "";
    // Cinematic typewriter reveal — only re-runs if text or event id changes
    typewriterText(
      document.getElementById("event-text"),
      ev.text || "",
      ev.id || state.mode,
      14
    );

    const btnMap = {
      red: "btn-red",
      blue: "btn-blue",
      green: "btn-green",
      yellow: "btn-yellow",
    };

    Object.keys(btnMap).forEach((k) => {
      const btn = document.getElementById(btnMap[k]);
      const c = (ev.choices || []).find((x) => x.key === k);
      const textSpan = btn.querySelector(".btn-text");
      if (c) {
        textSpan.textContent = c.label;
        btn.disabled = !!state.game_over && !(c.effect && c.effect.restart);
      } else {
        textSpan.textContent = "—";
        btn.disabled = true;
      }
    });
  }

  // 6. CONFIRM UTILITY BUTTON
  const confBtn = document.getElementById("btn-confirm");
  const confText = document.getElementById("confirm-text");
  const label = state.confirm_label || "OK";
  confText.textContent = label;
  confBtn.disabled = label === "—";

  // 7. COMBAT TACTICAL BANNER
  const combatBanner = document.getElementById("combat-banner");
  if (state.combat && state.combat.active) {
    combatBanner.classList.remove("hidden");
    document.getElementById("combat-target").textContent =
      `${(state.combat.enemy_name || "ENEMY").toUpperCase()} (HP ${Math.max(0, state.combat.enemy_hp)}/${state.combat.enemy_max})`;
    document.getElementById("combat-intent").textContent = state.combat.enemy_intent || "Closing in";
  } else {
    combatBanner.classList.add("hidden");
  }

  // 8. COMPANIONS ROSTER
  const partyList = document.getElementById("party-list");
  const party = state.party || [];
  document.getElementById("party-count").textContent = party.length + (w.flags && w.flags.has_dog ? 1 : 0);

  let partyHtml = "";
  if (w.flags && w.flags.has_dog) {
    partyHtml += `<span class="chip-npc" style="border-color:#d4a373;color:#d4a373">🐕 Scraps</span>`;
  }
  if (party.length > 0) {
    partyHtml += party
      .map(
        (n) =>
          `<span class="chip-npc" style="border-color:${n.color || "#888"};color:${n.color || "#ccc"}">${escapeHtml(n.short)} (${n.role || "Survivor"})</span>`
      )
      .join("");
  }
  if (!partyHtml) {
    partyHtml = `<span style="color:#555;font-size:11px;">Alone with the radio</span>`;
  }
  partyList.innerHTML = partyHtml;

  // 9. BASE UPGRADES BADGES
  const flags = w.flags || {};
  document.getElementById("upg-rain").classList.toggle("active", !!flags.rain_catcher);
  document.getElementById("upg-garden").classList.toggle("active", !!flags.garden);
  document.getElementById("upg-alarm").classList.toggle("active", !!flags.alarm);
  document.getElementById("upg-medbay").classList.toggle("active", !!flags.medbay);
  document.getElementById("upg-radio").classList.toggle("active", !!flags.radio_repaired);

  // 10. INVENTORY PACK (8 SLOTS)
  const inv = p.inventory || [];
  document.getElementById("inv-count").textContent = `${inv.length}/8`;
  const invGrid = document.getElementById("inv-grid");
  let gridHtml = "";
  for (let i = 0; i < 8; i++) {
    if (i < inv.length) {
      const itemId = inv[i];
      const name = ITEM_NAMES[itemId] || itemId;
      const isConsumable = ["antibiotics", "herbal_poultice", "clean_gauze", "molotov"].includes(itemId);
      gridHtml += `
        <div class="inv-slot" data-item="${itemId}" onclick="handleItemClick('${itemId}')" title="${isConsumable ? 'Click to Use' : 'Equipped/Carried'}">
          <span>·</span>
          <span>${escapeHtml(name)}</span>
        </div>
      `;
    } else {
      gridHtml += `<div class="inv-slot empty"><span>—</span><span>[Empty]</span></div>`;
    }
  }
  invGrid.innerHTML = gridHtml;

  // 11. SURVIVOR LOG
  const logEl = document.getElementById("log-window");
  logEl.innerHTML = (state.log || [])
    .map((line) => {
      const isAction = line.startsWith(">");
      const isHeader = line.startsWith("──");
      return `<div class="${isAction ? "player-action" : ""}" style="${isHeader ? "color:#e58e3c;font-weight:700;" : ""}">${escapeHtml(line)}</div>`;
    })
    .join("");
  logEl.scrollTop = logEl.scrollHeight;

  // 11b. RIDGE MODE — relabel meters for the fire-watch story
  const isRidge = state.scenario === "dead_ridge";
  document.body.classList.toggle("ridge-mode", isRidge);
  const barLabels = isRidge
    ? ["VITALITY", "NOISE SIG", "SANITY", "AWARENESS", "TOWER SEAL"]
    : null;
  if (barLabels) {
    const ids = [".hp-box .bar-meta span:first-child", ".inf-box .bar-meta span:first-child",
                 ".mor-box .bar-meta span:first-child", ".hum-box .bar-meta span:first-child",
                 ".fort-box .bar-meta span:first-child"];
    ids.forEach((sel, i) => {
      const el = document.querySelector(sel);
      if (el) el.textContent = barLabels[i];
    });
    const stageChip = document.getElementById("stage");
    if (stageChip) {
      stageChip.textContent = state.player.morale <= 30 ? "⚠ BREAKING" : "HOLDING";
      stageChip.className = state.player.morale <= 30 ? "stage-turning" : "stage-clean";
    }
  }

  // 12. SCREEN SHAKE & AUDIO FX
  document.body.classList.toggle("night", !!w.is_night);
  const shakeFx = ["shake", "danger", "hit", "gun"];
  if (shakeFx.includes(state.fx)) {
    const frame = document.getElementById("crt-screen");
    frame.classList.remove("shake");
    void frame.offsetWidth;
    frame.classList.add("shake");
    setTimeout(() => frame.classList.remove("shake"), 350);
  }

  if (window.SFX) {
    SFX.play(state.fx);
    if (isRidge && window.SFX.ridgeAmbience) {
      SFX.ridgeAmbience(p.morale, !!w.is_night);
    }
  }

  // 12b. EMAIL TOAST + NOTIFICATION CHIME
  if (isRidge && state.fx === "email") {
    const inbox = (w.flags && w.flags.rd_inbox) || [];
    const latest = inbox[inbox.length - 1];
    if (latest && latest.id !== _toastLastId) {
      _toastLastId = latest.id;
      showToast(`FORESTOS: '${latest.subject}' — ${latest.frm}`);
    }
  }

  // 13. RENDER PIXEL CANVAS
  if (window.Scene) {
    Scene.render(state);
  }

  // 14. UPDATE CITY MAP
  if (window.CityMap) {
    CityMap.update(state);
  }

  // 14b. FORESTOS LAPTOP OVERLAY & WEATHER STATION (Dead Ridge)
  if (window.LaptopOS) LaptopOS.update(state);
  if (window.WeatherStation) WeatherStation.update(state);

  // 15. GAME OVER / ENDING DISPLAY
  if (state.game_over) {
    document.getElementById("event-title").textContent =
      state.ending_title || (state.victory ? "EXTRACTION REACHED" : "COLD FLOOR");
    typewriterText(
      document.getElementById("event-text"),
      state.ending_text || "",
      "ending",
      22
    );
  }
}

let _toastLastId = "";
let _toastTimer = null;

function showToast(msg) {
  const toast = document.getElementById("toast");
  const body = document.getElementById("toast-body");
  if (!toast || !body) return;
  body.textContent = msg;
  toast.classList.remove("hidden");
  toast.classList.add("visible");
  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => {
    toast.classList.remove("visible");
    toast.classList.add("hidden");
  }, 4200);
  if (window.SFX && SFX.emailChime) SFX.emailChime();
}

function handleItemClick(itemId) {
  if (["antibiotics", "herbal_poultice", "clean_gauze"].includes(itemId)) {
    if (window.socket) {
      window.socket.send({ action: "use_item", item_id: itemId });
    }
  }
}
