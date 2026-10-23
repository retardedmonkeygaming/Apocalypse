const SEG = {
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
  E: "afged",
  P: "abfeg",
  H: "fegbc",
  "-": "g",
  " ": "",
};

const ITEM_NAMES = {
  pipe: "Pipe Club",
  crowbar: "Crowbar",
  pistol: "Pistol",
  mask: "Filter Mask",
  radio_parts: "Radio Parts",
  lena_notes: "Voss Notes",
  holy_charm: "Wooden Charm",
  tunnel_key: "Tunnel Key",
  molotov: "Molotov",
  antibiotics: "Antibiotics",
  photo: "School Photo",
  halcyon_map: "Halcyon Leaflet",
};

function setBar(id, value, max) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.width = Math.max(0, Math.min(100, (value / max) * 100)) + "%";
}

function showSeg(health, gameOver, victory) {
  let ch = String(Math.min(9, Math.max(0, Math.floor((health || 0) / 10))));
  if (gameOver) ch = victory ? "P" : "E";
  const on = SEG[ch] || "";
  document.querySelectorAll(".seg-d").forEach((d) => {
    const name = [...d.classList].find((c) => "abcdefg".includes(c));
    d.classList.toggle("on", on.includes(name));
  });
}

function updateUI(state) {
  if (!state || !state.player) return;
  const p = state.player;
  const w = state.world;
  document.getElementById("day").textContent = w.day;
  document.getElementById("clock").textContent = w.is_night ? "NIGHT" : "DAY";
  document.getElementById("weather").textContent = (w.weather || "clear").toUpperCase();
  document.getElementById("location").textContent = w.location;
  document.getElementById("health").textContent = p.health;
  document.getElementById("infection").textContent = p.infection;
  document.getElementById("morale").textContent = p.morale;
  document.getElementById("humanity").textContent = p.humanity;
  document.getElementById("fort").textContent = w.fortification;
  document.getElementById("food").textContent = p.food;
  document.getElementById("water").textContent = p.water;
  document.getElementById("ammo").textContent = p.ammo;
  document.getElementById("scrap").textContent = p.scrap;
  document.getElementById("medkits").textContent = p.medkits;
  document.getElementById("weapon").textContent = (p.weapon || "fists").toUpperCase();
  document.getElementById("stage").textContent = (state.infection_stage || "clean").toUpperCase();

  setBar("bar-hp", p.health, 100);
  setBar("bar-inf", p.infection, 100);
  setBar("bar-mor", p.morale, 100);
  setBar("bar-hum", p.humanity, 100);
  setBar("bar-fort", w.fortification, 10);
  showSeg(p.health, state.game_over, state.victory);

  const ev = state.current_event;
  if (ev) {
    document.getElementById("event-title").textContent = ev.title || "";
    document.getElementById("event-text").textContent = ev.text || "";
    const map = {
      red: "btn-red",
      blue: "btn-blue",
      green: "btn-green",
      yellow: "btn-yellow",
    };
    Object.keys(map).forEach((k) => {
      const btn = document.getElementById(map[k]);
      const c = (ev.choices || []).find((x) => x.key === k);
      btn.querySelector("span").textContent = c ? c.label : "—";
      btn.disabled = !c || (!!state.game_over && !(c.effect && c.effect.restart));
    });
  }
  const conf = document.getElementById("btn-confirm");
  conf.querySelector("span").textContent = state.confirm_label || "OK";
  conf.disabled = state.confirm_label === "—";

  const partyList = document.getElementById("party-list");
  const pals = state.party || [];
  partyList.innerHTML = pals.length
    ? pals
        .map(
          (n) =>
            `<span class="chip" style="border-color:${
              n.color || "#888"
            };color:${n.color || "#ccc"}">${n.short}</span>`
        )
        .join("")
    : `<span class="chip" style="border-color:#444;color:#666">alone</span>`;

  const inv = p.inventory || [];
  document.getElementById("inv-count").textContent = `${inv.length}/${
    state.inv_slots || 8
  }`;
  document.getElementById("inv-list").innerHTML = inv.length
    ? inv.map((id) => `<div class="inv-item">· ${ITEM_NAMES[id] || id}</div>`).join("")
    : `<div class="inv-item" style="color:#555">empty pockets</div>`;

  const logEl = document.getElementById("log");
  logEl.innerHTML = (state.log || [])
    .map((l) => `<div>${escapeHtml(l)}</div>`)
    .join("");
  logEl.scrollTop = logEl.scrollHeight;

  const clog = document.getElementById("combat-log");
  if (state.combat && state.combat.active) {
    clog.textContent = (state.combat.log || []).slice(-2).join(" / ");
  } else {
    clog.textContent = "";
  }

  document.body.classList.toggle("night", !!w.is_night);
  document.body.classList.toggle("ending", !!state.game_over);
  const shakeFx = ["shake", "danger", "hit", "gun"];
  if (shakeFx.includes(state.fx)) {
    document.body.classList.remove("shake");
    void document.body.offsetWidth;
    document.body.classList.add("shake");
    setTimeout(() => document.body.classList.remove("shake"), 400);
  }
  if (window.SFX) SFX.play(state.fx);
  if (window.Scene) Scene.render(state);

  if (state.game_over) {
    document.getElementById("event-title").textContent =
      state.ending_title || (state.victory ? "EXTRACTION" : "YOU DIED");
    document.getElementById("event-text").textContent =
      state.ending_text || "";
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>]/g, (c) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
  }[c]));
}
