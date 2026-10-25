/* ==========================================================================
   APOCALYPSE TERMINAL — Interactive City Map
   Pixel-art city overview with discovered/undiscovered zones, roads, and
   current position indicator. Overlays the main CRT screen as a toggleable
   panel — the original UI is never moved or replaced.
   ========================================================================== */

const CityMap = (() => {
  // ── Node layout (city grid — all coordinates in 0-1 normalized space) ──
  // Each entry: [id, label, nx, ny]   (nx/ny = 0..1 fraction of map canvas)
  const _CITY_NODES = [
    { id: "Home Base",           x: 0.50, y: 0.52, icon: "🏠" },
    { id: "Streets",             x: 0.50, y: 0.38, icon: "🛣" },
    { id: "Abandoned Mall",      x: 0.22, y: 0.26, icon: "🏪" },
    { id: "Hospital",            x: 0.76, y: 0.26, icon: "🏥" },
    { id: "Radio Tower",         x: 0.14, y: 0.54, icon: "📡" },
    { id: "Warehouse",           x: 0.82, y: 0.52, icon: "🏭" },
    { id: "Church",              x: 0.36, y: 0.68, icon: "⛪" },
    { id: "Subway Tunnels",      x: 0.62, y: 0.70, icon: "🚇" },
    { id: "Military Checkpoint", x: 0.50, y: 0.14, icon: "🔰" },
    { id: "School",              x: 0.28, y: 0.44, icon: "🏫" },
    { id: "Docks",               x: 0.84, y: 0.76, icon: "⚓" },
    { id: "Overgrown Park",      x: 0.18, y: 0.74, icon: "🌿" },
    { id: "Gas Station",         x: 0.66, y: 0.42, icon: "⛽" },
    { id: "Ruined Pharmacy",     x: 0.38, y: 0.18, icon: "💊" },
    // ── Expanded city zones ──
    { id: "Fire Station",        x: 0.74, y: 0.34, icon: "🚒" },
    { id: "City Prison",         x: 0.90, y: 0.44, icon: "🔒" },
    { id: "Bus Depot",           x: 0.52, y: 0.62, icon: "🚌" },
    { id: "Waterworks",          x: 0.72, y: 0.64, icon: "🚰" },
    { id: "Overpass Camp",       x: 0.12, y: 0.86, icon: "⛺" },
    { id: "Memorial Stadium",    x: 0.58, y: 0.84, icon: "🏟" },
  ];

  // Roads as pairs of node IDs
  const _CITY_ROADS = [
    ["Home Base", "Streets"],
    ["Home Base", "Church"],
    ["Home Base", "Subway Tunnels"],
    ["Streets", "Abandoned Mall"],
    ["Streets", "Hospital"],
    ["Streets", "Military Checkpoint"],
    ["Streets", "Ruined Pharmacy"],
    ["Streets", "School"],
    ["Streets", "Gas Station"],
    ["Abandoned Mall", "Radio Tower"],
    ["Abandoned Mall", "Church"],
    ["Hospital", "Warehouse"],
    ["Hospital", "Gas Station"],
    ["Warehouse", "Docks"],
    ["Church", "Overgrown Park"],
    ["Subway Tunnels", "Docks"],
    ["Military Checkpoint", "Radio Tower"],
    ["School", "Radio Tower"],
    ["Ruined Pharmacy", "Military Checkpoint"],
    // Expanded zones
    ["Hospital", "Fire Station"],
    ["Fire Station", "City Prison"],
    ["Fire Station", "Gas Station"],
    ["Warehouse", "City Prison"],
    ["City Prison", "Waterworks"],
    ["Home Base", "Bus Depot"],
    ["Bus Depot", "Waterworks"],
    ["Bus Depot", "Memorial Stadium"],
    ["Subway Tunnels", "Bus Depot"],
    ["Church", "Overpass Camp"],
    ["Overgrown Park", "Overpass Camp"],
    ["Overpass Camp", "Memorial Stadium"],
    ["Waterworks", "Docks"],
    ["Memorial Stadium", "Waterworks"],
  ];

  // ── Dead Ridge overworld (story mode) ────────────────────────
  const RIDGE_NODES = [
    { id: "Fire-Tower 1", x: 0.78, y: 0.16, icon: "🗼" },
    { id: "The Northern Ravine", x: 0.22, y: 0.20, icon: "⛰" },
    { id: "The Copperhead Bridge", x: 0.20, y: 0.46, icon: "🌉" },
    { id: "Fire-Tower 2", x: 0.76, y: 0.48, icon: "🗼" },
    { id: "The Compass Cabins", x: 0.34, y: 0.62, icon: "🛖" },
    { id: "Old Mining Shaft 4", x: 0.28, y: 0.86, icon: "⛏" },
    { id: "Ranger Station Ruins", x: 0.60, y: 0.24, icon: "🏚" },
    { id: "Overturned Railcar", x: 0.52, y: 0.36, icon: "🚆" },
    { id: "Limestone Sinkhole", x: 0.66, y: 0.82, icon: "🕳" },
  ];
  const RIDGE_ROADS = [
    ["Fire-Tower 1", "The Northern Ravine"],
    ["The Northern Ravine", "The Copperhead Bridge"],
    ["The Copperhead Bridge", "The Compass Cabins"],
    ["The Compass Cabins", "Old Mining Shaft 4"],
    ["The Compass Cabins", "Fire-Tower 2"],
    ["Fire-Tower 2", "Fire-Tower 1"],
    ["Fire-Tower 2", "Ranger Station Ruins"],
    ["Ranger Station Ruins", "Overturned Railcar"],
    ["Overturned Railcar", "The Northern Ravine"],
    ["Old Mining Shaft 4", "Limestone Sinkhole"],
    ["Limestone Sinkhole", "Fire-Tower 2"],
  ];

  // Colors
  const C = {
    bg:        "#0a0c0f",
    grid:      "#12181e",
    road:      "#1e2830",
    roadKnown: "#2e4050",
    unknown:   "#1a2230",
    unknownBdr:"#263040",
    known:     "#1e3a28",
    knownBdr:  "#3a7058",
    current:   "#e58e3c",
    currentBdr:"#ff6628",
    text:      "#8ab0b0",
    textBright:"#c8e0d8",
    textUnk:   "#304048",
    scanline:  "rgba(0,0,0,0.3)",
    glow:      "rgba(229, 142, 60, 0.15)",
  };

  let _canvas = null;
  let _ctx = null;
  let _overlay = null;
  let _visible = false;
  let _lastState = null;
  let _t = 0;
  let _statuses = null;   // live availability from the backend (state.map_nodes)
  let _hover = null;      // node id under the cursor

  // Status palette — every node colour means something
  const STY = {
    home:    { fill: "#e58e3c", bdr: "#ff6628", text: "#1a0e04" },
    open:    { fill: "#1e3a28", bdr: "#3a7058", text: "#c8e0d8" },
    danger:  { fill: "#3a1a18", bdr: "#e04a3a", text: "#ffb0a0" },
    locked:  { fill: "#141a22", bdr: "#2a3240", text: "#4a5560" },
    blocked: { fill: "#2a1216", bdr: "#7a2a2a", text: "#c07070" },
  };

  function _statusOf(id, knownList) {
    const s = _statuses ? _statuses.find((m) => m.id === id) : null;
    if (s) return s;
    return { id, status: knownList && knownList.includes(id) ? "open" : "locked", reason: "", risk: 40, beat: false };
  }

  function _hit(mx, my) {
    if (!_lastState) return null;
    const state = _lastState;
    const isRidge = state.scenario === "dead_ridge";
    const NODES = isRidge ? RIDGE_NODES : _CITY_NODES;
    const known = isRidge ? (state.world.flags.rd_visited || [])
                          : ((state.world || {}).known_locations || []);
    for (const n of NODES) {
      const p = _nodePos(n, _canvas.width, _canvas.height);
      if (Math.abs(mx - p.x) <= 16 && Math.abs(my - p.y) <= 10) return n.id;
    }
    return null;
  }

  function _onMove(ev) {
    if (!_canvas) return;
    const r = _canvas.getBoundingClientRect();
    const mx = (ev.clientX - r.left) * (_canvas.width / r.width);
    const my = (ev.clientY - r.top) * (_canvas.height / r.height);
    _hover = _hit(mx, my);
    _canvas.style.cursor = _hover ? "pointer" : "default";
    if (_visible && _lastState) _draw(_lastState);
  }

  function _onClick(ev) {
    if (!_canvas) return;
    const r = _canvas.getBoundingClientRect();
    const mx = (ev.clientX - r.left) * (_canvas.width / r.width);
    const my = (ev.clientY - r.top) * (_canvas.height / r.height);
    const id = _hit(mx, my);
    if (!id) return;
    const st = _statusOf(id, []);
    const isRidge = _lastState && _lastState.scenario === "dead_ridge";
    if (!isRidge) {
      // Classic runs: the map is intel — the scavenge menu is how you move.
      if (typeof comboFlash === "function") comboFlash(`📍 ${id.toUpperCase()} — pick it from SCAVENGE`);
      return;
    }
    if (st.status === "locked" || st.status === "blocked") {
      if (typeof comboFlash === "function") comboFlash(`⛔ ${id.toUpperCase()}: ${st.reason || "no route"}`);
      return;
    }
    if (window.socket) window.socket.send({ action: "goto", node: id });
    if (typeof comboFlash === "function") comboFlash(`🚶 TRAVELLING — ${id.toUpperCase()}`);
    CityMap.hide();
  }

  function _nodePos(node, W, H) {
    return { x: node.x * W, y: node.y * H };
  }

  function _isKnown(id, knownList) {
    return (knownList || []).includes(id);
  }

  function _draw(state) {
    if (!_ctx || !_canvas) return;
    const isRidge = !!(state && state.scenario === "dead_ridge");
    const NODES = isRidge ? RIDGE_NODES : _CITY_NODES;
    const ROADS = isRidge ? RIDGE_ROADS : _CITY_ROADS;
    const TITLE = isRidge ? "🌲  DEAD RIDGE OVERWORLD — CLICK A NODE TO TRAVEL  🌲" : "⚠  CITY RECONNAISSANCE MAP  ⚠";
    const known = isRidge
      ? (state.world.flags.rd_visited || [])
      : (state && state.world && state.world.known_locations) || [];
    const current = (state && state.world && state.world.location) || "Home Base";
    _statuses = isRidge ? (state.map_nodes || null) : null;
    // Canvas drawing space (this was the bug that kept the map blank:
    // W/H were referenced but never declared in this scope)
    const W = _canvas.width;
    const H = _canvas.height;
    _t++;

    // Background
    _ctx.fillStyle = C.bg;
    _ctx.fillRect(0, 0, W, H);

    // Subtle grid
    _ctx.strokeStyle = C.grid;
    _ctx.lineWidth = 0.5;
    for (let gx = 0; gx < W; gx += 20) {
      _ctx.beginPath(); _ctx.moveTo(gx, 0); _ctx.lineTo(gx, H); _ctx.stroke();
    }
    for (let gy = 0; gy < H; gy += 20) {
      _ctx.beginPath(); _ctx.moveTo(0, gy); _ctx.lineTo(W, gy); _ctx.stroke();
    }

    // Title header strip
    _ctx.fillStyle = "#0f1820";
    _ctx.fillRect(0, 0, W, 18);
    _ctx.fillStyle = C.current;
    _ctx.font = "bold 9px monospace";
    _ctx.textAlign = "center";
    _ctx.fillText(TITLE, W / 2, 12);
    _ctx.fillStyle = C.text;
    _ctx.font = "7px monospace";
    _ctx.textAlign = "right";
    // Day/weather live in the footer so the title can never collide with them
    if (!isRidge) {
      _ctx.fillText(`LOCATIONS: ${known.length}/${NODES.length}`, W - 6, 12);
    }
    _ctx.textAlign = "center";

    // Roads (resolved from the active map set)
    ROADS.forEach(([a, b]) => {
      const na = NODES.find(n => n.id === a);
      const nb = NODES.find(n => n.id === b);
      if (!na || !nb) return;
      const pa = _nodePos(na, W, H);
      const pb = _nodePos(nb, W, H);
      const bothKnown = _isKnown(a, known) && _isKnown(b, known);
      _ctx.strokeStyle = bothKnown ? C.roadKnown : C.road;
      _ctx.lineWidth = bothKnown ? 1.5 : 0.8;
      _ctx.setLineDash(bothKnown ? [] : [3, 4]);
      _ctx.beginPath();
      _ctx.moveTo(pa.x, pa.y);
      _ctx.lineTo(pb.x, pb.y);
      _ctx.stroke();
      _ctx.setLineDash([]);
    });

    // Nodes
    NODES.forEach((node) => {
      const pos = _nodePos(node, W, H);
      const isKnown = _isKnown(node.id, known);
      const isCurrent = node.id === current;
      const st = _statusOf(node.id, known);
      const sty = STY[st.status] || STY.locked;
      const visible = isKnown || isCurrent || st.status === "open" || st.status === "home";
      const isHover = _hover === node.id;

      if (isCurrent || st.status === "danger") {
        // Pulsing halo — amber for you, red for a place that is hot right now
        const pulse = 0.5 + 0.5 * Math.sin(_t * 0.18);
        const gRadius = 10 + pulse * 4;
        const base = isCurrent ? "229,142,60" : "224,74,58";
        const grad = _ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, gRadius);
        grad.addColorStop(0, `rgba(${base},${0.3 + pulse * 0.18})`);
        grad.addColorStop(1, `rgba(${base},0)`);
        _ctx.fillStyle = grad;
        _ctx.beginPath();
        _ctx.arc(pos.x, pos.y, gRadius, 0, Math.PI * 2);
        _ctx.fill();
      }

      // Node box
      const bw = 28, bh = 14;
      const bx = pos.x - bw / 2;
      const by = pos.y - bh / 2;

      _ctx.fillStyle = sty.fill;
      _ctx.fillRect(bx, by, bw, bh);
      _ctx.strokeStyle = isHover ? "#fff" : sty.bdr;
      _ctx.lineWidth = isCurrent || isHover ? 1.5 : 1;
      _ctx.strokeRect(bx, by, bw, bh);

      // Label
      if (visible) {
        const label = _shortLabel(node.id);
        _ctx.fillStyle = sty.text;
        _ctx.font = isCurrent ? "bold 6px monospace" : "6px monospace";
        _ctx.textAlign = "center";
        _ctx.fillText(label, pos.x, pos.y + 2.5);
      } else {
        _ctx.fillStyle = C.textUnk;
        _ctx.font = "6px monospace";
        _ctx.textAlign = "center";
        _ctx.fillText("???", pos.x, pos.y + 2.5);
      }

      // Story beat waiting here
      if (st.beat) {
        _ctx.fillStyle = "#ffd166";
        _ctx.font = "bold 8px monospace";
        _ctx.textAlign = "left";
        _ctx.fillText("!", bx + bw + 2, by + 4);
      }
      // No daylight / no route marker
      if (st.status === "locked" || st.status === "blocked") {
        _ctx.strokeStyle = "rgba(200,90,90,0.7)";
        _ctx.lineWidth = 1;
        _ctx.beginPath();
        _ctx.moveTo(bx + 4, by + 3); _ctx.lineTo(bx + bw - 4, by + bh - 3);
        _ctx.moveTo(bx + bw - 4, by + 3); _ctx.lineTo(bx + 4, by + bh - 3);
        _ctx.stroke();
      }
    });

    // Scanline overlay for CRT feel
    for (let sl = 18; sl < H; sl += 3) {
      _ctx.fillStyle = C.scanline;
      _ctx.fillRect(0, sl, W, 1);
    }

    // Current location legend at bottom
    _ctx.fillStyle = "#0f1820";
    _ctx.fillRect(0, H - 16, W, 16);
    _ctx.fillStyle = C.current;
    _ctx.font = "bold 8px monospace";
    _ctx.textAlign = "left";
    _ctx.fillText("▶ YOU ARE HERE:", 6, H - 5);
    _ctx.fillStyle = C.textBright;
    _ctx.font = "7px monospace";
    _ctx.fillText(current.toUpperCase(), 90, H - 5);

    // Bottom legend: status of the place under your cursor, else campaign clock
    let footer = "";
    if (_hover && isRidge) {
      const st = _statusOf(_hover, known);
      const tag = { open: "OPEN", danger: "⚠ DANGER", locked: "LOCKED", blocked: "BLOCKED", home: "BASE" }[st.status] || "";
      footer = `${_hover.toUpperCase()} · ${tag} · RISK ${st.risk || 0}% — ${st.reason || st.beat_note || st.blurb || "click to travel"}`;
    } else if (isRidge) {
      footer = `DAY ${state.world.day}/30 · ${(state.world.weather || "clear").toUpperCase()} · ` +
               `${state.world.is_night ? "NIGHT" : "DAY"} · ${known.length}/${NODES.length} KNOWN`;
    }
    if (footer) {
      // Left legend is drawn at fixed x=90 for the location name — measure it
      // the same way it was drawn so the two can never touch.
      _ctx.font = "bold 8px monospace";
      const labelW = _ctx.measureText("▶ YOU ARE HERE:").width;
      _ctx.font = "7px monospace";
      const locW = _ctx.measureText(current.toUpperCase()).width;
      const leftEnd = Math.max(6 + labelW + 6, 90 + locW) + 10;
      const budget = Math.max(40, W - 6 - leftEnd);
      let line = footer;
      while (line.length > 4 && _ctx.measureText(line).width > budget) line = line.slice(0, -2);
      if (line !== footer) line = line.slice(0, -1) + "…";
      _ctx.fillStyle = _hover ? "#ffd166" : C.text;
      _ctx.font = "7px monospace";
      _ctx.textAlign = "right";
      _ctx.fillText(line, W - 6, H - 5);
      _ctx.textAlign = "left";
    }
  }

  function _shortLabel(id) {
    const abbr = {
      "Home Base": "BASE",
      "Streets": "STREET",
      "Abandoned Mall": "MALL",
      "Hospital": "HOSP",
      "Radio Tower": "RADIO",
      "Warehouse": "W.HSE",
      "Church": "CHURCH",
      "Subway Tunnels": "SUBWAY",
      "Military Checkpoint": "MILIT",
      "School": "SCHOOL",
      "Docks": "DOCKS",
      "Overgrown Park": "PARK",
      "Gas Station": "GAS",
      "Ruined Pharmacy": "PHARM",
      "Fire Station": "FIRE",
      "City Prison": "PRISON",
      "Bus Depot": "BUS",
      "Waterworks": "WTRWRK",
      "Overpass Camp": "CAMPOVR",
      "Memorial Stadium": "STADIUM",
      "Fire-Tower 1": "TWR 1",
      "Fire-Tower 2": "TWR 2",
      "The Northern Ravine": "RAVINE",
      "The Copperhead Bridge": "BRIDGE",
      "The Compass Cabins": "CABINS",
      "Old Mining Shaft 4": "SHAFT 4",
      "Ranger Station Ruins": "RUINS",
      "Overturned Railcar": "RAILCAR",
      "Limestone Sinkhole": "SINKHOLE",
    };
    return abbr[id] || id.split(" ")[0].toUpperCase().slice(0, 6);
  }

  function _createOverlay() {
    // Overlay sits inside #crt-screen without touching existing layout.
    // It's an absolutely-positioned panel that fades in/out.
    const overlay = document.createElement("div");
    overlay.id = "city-map-overlay";
    overlay.style.cssText = `
      position: absolute;
      top: 4px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 900;
      display: none;
      flex-direction: column;
      align-items: center;
      pointer-events: auto;
      background: rgba(6,10,14,0.96);
      border: 1px solid #2a4a5e;
      box-shadow: 0 0 24px rgba(0,180,230,0.18), 0 0 2px #0af inset;
      padding: 2px;
    `;

    const canvas = document.createElement("canvas");
    canvas.id = "city-map-canvas";
    canvas.width = 320;
    canvas.height = 210;
    canvas.style.cssText = "display:block;image-rendering:pixelated;";
    canvas.addEventListener("mousemove", _onMove);
    canvas.addEventListener("mouseleave", () => { _hover = null; if (_visible && _lastState) _draw(_lastState); });
    canvas.addEventListener("click", _onClick);

    const closeBtn = document.createElement("button");
    closeBtn.textContent = "✕ CLOSE MAP  [Tab]";
    closeBtn.style.cssText = `
      width: 100%;
      background: #0a1820;
      border: none;
      border-top: 1px solid #1a3040;
      color: #4a8898;
      font: bold 9px monospace;
      padding: 4px 0;
      cursor: pointer;
      letter-spacing: 1px;
    `;
    closeBtn.addEventListener("click", () => CityMap.hide());
    closeBtn.addEventListener("mouseenter", () => closeBtn.style.color = "#e58e3c");
    closeBtn.addEventListener("mouseleave", () => closeBtn.style.color = "#4a8898");

    overlay.appendChild(canvas);
    overlay.appendChild(closeBtn);

    const screen = document.getElementById("crt-screen");
    if (screen) {
      screen.style.position = "relative";
      screen.appendChild(overlay);
    } else {
      document.body.appendChild(overlay);
    }

    return { overlay, canvas };
  }

  function _init() {
    if (_canvas) return;
    const { overlay, canvas } = _createOverlay();
    _overlay = overlay;
    _canvas = canvas;
    _ctx = canvas.getContext("2d");
    _ctx.imageSmoothingEnabled = false;
  }

  return {
    init() { _init(); },

    toggle() {
      _init();
      _visible ? this.hide() : this.show();
    },

    show() {
      _init();
      _visible = true;
      _overlay.style.display = "flex";
      if (_lastState) _draw(_lastState);
    },

    hide() {
      _visible = false;
      if (_overlay) _overlay.style.display = "none";
    },

    update(state) {
      _lastState = state;
      if (_visible) _draw(state);
    },
  };
})();

// Auto-initialize (non-blocking)
document.addEventListener("DOMContentLoaded", () => CityMap.init());

// Classic scripts declare `const` in the global lexical scope, NOT on window.
// game.js/ui.js check `window.CityMap` — without this the MAP button is dead.
window.CityMap = CityMap;
