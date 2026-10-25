/* ==========================================================================
   APOCALYPSE TERMINAL — Game Controller & Input Dispatcher
   Maps keyboard, mouse, touch, and audio events to GameSocket actions
   ========================================================================== */

const socket = new GameSocket(
  (location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws"
);
window.socket = socket;

socket.on("state", (state) => {
  window.__rdState = state; // shared with pixel.js (party/seal lookups)
  updateUI(state);
});

socket.connect();

// Instant first paint: render from HTTP immediately instead of showing
// "WAITING FOR BROADCAST..." until the WebSocket handshake completes.
fetch("/api/state")
  .then((r) => (r.ok ? r.json() : null))
  .then((s) => {
    if (s && s.player) updateUI(s);
  })
  .catch(() => {});

function press(key) {
  const btnId = {
    red: "btn-red",
    blue: "btn-blue",
    green: "btn-green",
    yellow: "btn-yellow",
    confirm: "btn-confirm",
  }[key];

  const btn = document.getElementById(btnId);
  if (btn && !btn.disabled) {
    btn.classList.add("pressed");
    setTimeout(() => btn.classList.remove("pressed"), 120);
  }

  // Audio blip on press
  if (window.SFX) {
    SFX.ensure();
    const toneFreq = key === "confirm" ? 520 : 380;
    SFX.beep(toneFreq, 0.04, "square", 0.03);
  }

  if (key === "confirm") {
    socket.send({ action: "confirm" });
  } else {
    socket.send({ action: "choice", key });
  }
}

// ── BUTTON COMBINATIONS ─────────────────────────────────────────────
// Two arcade keys pressed together trigger cabinet-level commands.
const COMBOS = {
  "1+2": () => { if (window.CityMap) CityMap.toggle(); comboFlash("🗺 TACTICAL MAP"); },
  "3+4": () => { toggleGuide(); comboFlash("📟 FIELD MANUAL"); },
  "1+4": () => { socket.send({ action: "page" }); comboFlash("📄 MORE STORIES"); },
  "2+3": () => {
    if (window.SFX) {
      SFX.ensure();
      const muted = SFX.toggleMute();
      const btn = document.getElementById("btn-mute");
      if (btn) btn.textContent = muted ? "SOUND: OFF" : "SOUND: ON";
    }
    comboFlash("🔇 AUDIO TOGGLE");
  },
  "2+4": () => {
    if (window.WeatherStation) {
      WeatherStation.toggle();
      comboFlash(WeatherStation.isVisible() ? "🛰 WEATHER STATION ONLINE" : "🛰 WEATHER STATION OFFLINE");
    }
  },
};

const _held = new Set();

function comboFlash(msg) {
  if (window.SFX) { SFX.ensure(); SFX.beep(740, 0.05, "square", 0.04); setTimeout(() => SFX.beep(1108, 0.08, "square", 0.04), 60); }
  const el = document.getElementById("toast");
  const body = document.getElementById("toast-body");
  if (el && body) {
    body.textContent = msg;
    el.classList.remove("hidden");
    el.classList.add("visible", "combo");
    setTimeout(() => { el.classList.remove("visible", "combo"); el.classList.add("hidden"); }, 1400);
  }
}

function toggleGuide(force) {
  const g = document.getElementById("guide-overlay");
  if (!g) return;
  const show = force != null ? force : g.classList.contains("hidden");
  g.classList.toggle("hidden", !show);
  g.classList.toggle("visible", show);
}

document.addEventListener("keyup", (e) => {
  if ("1234".includes(e.key)) _held.delete(e.key);
});

// 1. ARCADE BUTTON CLICKS — delegated at document level so a button that is
// re-rendered, re-enabled or moved can never end up without a handler.
document.addEventListener("click", (ev) => {
  const btn = ev.target && ev.target.closest ? ev.target.closest(".arcade-btn") : null;
  if (!btn) return;
  const span = btn.querySelector(".btn-text");
  const label = span ? span.textContent.trim() : "";
  // "—" means this key genuinely carries no option right now.
  if (label === "—" || label === "") return;
  press(btn.dataset.key);
}, true);

// 2. FOOTER UTILITIES: NEW RUN, MUTE, SCANLINES & MAP
document.getElementById("btn-new-game").addEventListener("click", () => {
  if (confirm("Abandon this run and wake up behind the boarded door again?")) {
    if (window.SFX) SFX.ensure();
    socket.send({ action: "new_game" });
  }
});

document.getElementById("btn-mute").addEventListener("click", () => {
  if (window.SFX) {
    SFX.ensure();
    const muted = SFX.toggleMute();
    document.getElementById("btn-mute").textContent = muted ? "SOUND: OFF" : "SOUND: ON";
  }
});

document.getElementById("btn-scanlines").addEventListener("click", () => {
  document.body.classList.toggle("no-scanlines");
  const isNoScan = document.body.classList.contains("no-scanlines");
  document.getElementById("btn-scanlines").textContent = `CRT: ${isNoScan ? "MODERN" : "VINTAGE"}`;
});

document.getElementById("btn-3d").addEventListener("click", () => {
  if (window.Scene3D) comboFlash(Scene3D.cycleQuality());
});

document.getElementById("btn-map").addEventListener("click", () => {
  if (window.CityMap) CityMap.toggle();
});

document.getElementById("btn-guide").addEventListener("click", () => toggleGuide());
document.getElementById("guide-close").addEventListener("click", () => toggleGuide(false));

// 3. KEYBOARD EVENT LISTENER
document.addEventListener("keydown", (e) => {
  if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA")) {
    return;
  }

  const keyMap = {
    "1": "red",
    "2": "blue",
    "3": "green",
    "4": "yellow",
    " ": "confirm",
    "Enter": "confirm",
  };

  // Combo detection: two of 1/2/3/4 held together
  if ("1234".includes(e.key)) {
    if (_held.size > 0) {
      const other = [..._held][0];
      const combo = [other, e.key].sort().join("+");
      _held.clear();
      if (COMBOS[combo]) {
        e.preventDefault();
        COMBOS[combo]();
        return;
      }
    }
    _held.add(e.key);
  }

  if (keyMap[e.key]) {
    e.preventDefault();
    press(keyMap[e.key]);
    return;
  }

  // Shortcut: 5 (or G on the scenario menu) flips story-select pages
  if (e.key === "5") {
    e.preventDefault();
    socket.send({ action: "page" });
    return;
  }

  // Shortcut: G / Esc toggles the beginner's guide
  if (e.key === "g" || e.key === "G" || e.key === "Escape") {
    e.preventDefault();
    toggleGuide();
    return;
  }

  // Shortcut: W toggles the ridge weather station
  if (e.key === "w" || e.key === "W") {
    if (window.WeatherStation && window.__rdState && window.__rdState.scenario === "dead_ridge") {
      e.preventDefault();
      WeatherStation.toggle();
    }
    return;
  }

  // Shortcut: Tab for city map (most intuitive key for a "map" toggle)
  if (e.key === "Tab") {
    e.preventDefault();
    if (window.CityMap) CityMap.toggle();
    return;
  }

  // Shortcut: N for new run
  if (e.key === "n" || e.key === "N") {
    if (confirm("Abandon this run and wake up behind the boarded door again?")) {
      socket.send({ action: "new_game" });
    }
  }

  // Shortcut: M for mute
  if (e.key === "m" || e.key === "M") {
    if (window.SFX) SFX.toggleMute();
  }
});

// 4. ANIMATION TICKER FOR PROCEDURAL PIXEL CANVAS
setInterval(() => {
  if (window.Scene && Scene.lastState) {
    Scene.render(Scene.lastState);
  }
}, 80);
