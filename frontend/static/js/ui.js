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
  "-": "g",
  "_": "d",
  " ": "",
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
};

function setBar(id, value, max) {
  const el = document.getElementById(id);
  if (!el) return;
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  el.style.width = pct + "%";
}

function showSeg(health, gameOver, victory, mode) {
  let ch = " ";
  if (gameOver) {
    ch = victory ? "P" : "E";
  } else if (mode === "combat") {
    ch = "C";
  } else {
    ch = String(Math.min(9, Math.max(0, Math.floor((health || 0) / 10))));
  }

  const on = SEG_MAP[ch] || "";
  document.querySelectorAll(".seg-d").forEach((d) => {
    const segName = [...d.classList].find((c) => "abcdefg".includes(c));
    d.classList.toggle("on", on.includes(segName));
  });
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

  // 3. 7-SEGMENT DISPLAY
  showSeg(p.health, state.game_over, state.victory, state.mode);

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
    document.getElementById("event-text").textContent = ev.text || "";

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
    document.getElementById("combat-target").textContent = `${state.combat.enemy_name.upper()} (HP ${Math.max(0, state.combat.enemy_hp)}/${state.combat.enemy_max})`;
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
  }

  // 13. RENDER PIXEL CANVAS
  if (window.Scene) {
    Scene.render(state);
  }

  // 14. GAME OVER / ENDING DISPLAY
  if (state.game_over) {
    document.getElementById("event-title").textContent =
      state.ending_title || (state.victory ? "EXTRACTION REACHED" : "COLD FLOOR");
    document.getElementById("event-text").textContent = state.ending_text || "";
  }
}

function handleItemClick(itemId) {
  if (["antibiotics", "herbal_poultice", "clean_gauze"].includes(itemId)) {
    if (window.socket) {
      window.socket.send({ action: "use_item", item_id: itemId });
    }
  }
}
