/* ==========================================================================
   APOCALYPSE TERMINAL — Interactive City Map
   Pixel-art city overview with discovered/undiscovered zones, roads, and
   current position indicator. Overlays the main CRT screen as a toggleable
   panel — the original UI is never moved or replaced.
   ========================================================================== */

const CityMap = (() => {
  // ── Node layout (city grid — all coordinates in 0-1 normalized space) ──
  // Each entry: [id, label, nx, ny]   (nx/ny = 0..1 fraction of map canvas)
  const NODES = [
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
  ];

  // Roads as pairs of node IDs
  const ROADS = [
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

  function _nodePos(node, W, H) {
    return { x: node.x * W, y: node.y * H };
  }

  function _isKnown(id, knownList) {
    return (knownList || []).includes(id);
  }

  function _draw(state) {
    if (!_ctx || !_canvas) return;
    const W = _canvas.width;
    const H = _canvas.height;
    const known = (state && state.world && state.world.known_locations) || [];
    const current = (state && state.world && state.world.location) || "Home Base";
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
    _ctx.fillText("⚠  CITY RECONNAISSANCE MAP  ⚠", W / 2, 12);
    _ctx.fillStyle = C.text;
    _ctx.font = "7px monospace";
    _ctx.textAlign = "right";
    _ctx.fillText(`LOCATIONS: ${known.length}/${NODES.length}`, W - 6, 12);

    // Roads
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

      if (isCurrent) {
        // Pulsing glow halo
        const pulse = 0.5 + 0.5 * Math.sin(_t * 0.18);
        const gRadius = 10 + pulse * 4;
        const grad = _ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, gRadius);
        grad.addColorStop(0, `rgba(229,142,60,${0.3 + pulse * 0.15})`);
        grad.addColorStop(1, "rgba(229,142,60,0)");
        _ctx.fillStyle = grad;
        _ctx.beginPath();
        _ctx.arc(pos.x, pos.y, gRadius, 0, Math.PI * 2);
        _ctx.fill();
      }

      // Node box
      const bw = 28, bh = 14;
      const bx = pos.x - bw / 2;
      const by = pos.y - bh / 2;

      _ctx.fillStyle = isCurrent ? C.current : isKnown ? C.known : C.unknown;
      _ctx.fillRect(bx, by, bw, bh);
      _ctx.strokeStyle = isCurrent ? C.currentBdr : isKnown ? C.knownBdr : C.unknownBdr;
      _ctx.lineWidth = isCurrent ? 1.5 : 1;
      _ctx.strokeRect(bx, by, bw, bh);

      // Label
      if (isKnown || isCurrent) {
        // Short label (first word or abbreviation)
        const label = _shortLabel(node.id);
        _ctx.fillStyle = isCurrent ? "#fff" : C.textBright;
        _ctx.font = isCurrent ? "bold 6px monospace" : "6px monospace";
        _ctx.textAlign = "center";
        _ctx.fillText(label, pos.x, pos.y + 2.5);
      } else {
        // Unknown: show ???
        _ctx.fillStyle = C.textUnk;
        _ctx.font = "6px monospace";
        _ctx.textAlign = "center";
        _ctx.fillText("???", pos.x, pos.y + 2.5);
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
