/* ==========================================================================
   APOCALYPSE TERMINAL — Game Controller & Input Dispatcher
   Maps keyboard, mouse, touch, and audio events to GameSocket actions
   ========================================================================== */

const socket = new GameSocket(
  (location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws"
);
window.socket = socket;

socket.on("state", (state) => {
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

// 1. ARCADE BUTTON CLICKS
document.querySelectorAll(".arcade-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    if (!btn.disabled) {
      press(btn.dataset.key);
    }
  });
});

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

document.getElementById("btn-map").addEventListener("click", () => {
  if (window.CityMap) CityMap.toggle();
});

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

  if (keyMap[e.key]) {
    e.preventDefault();
    press(keyMap[e.key]);
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
