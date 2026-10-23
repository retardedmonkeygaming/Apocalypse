/* ==========================================================================
   APOCALYPSE TERMINAL — Cinematic Pixel Engine & Tactical City Map (320x180)
   Features:
   - 12th Floor Apartment & EAS Emergency Alert Vignettes
   - Corridor & Stairwell perspective animations
   - Tactical Pixel City Map with radar sweep & pulsing player beacon
   - Multi-character idle breathing, weapon lunges, and enemy sprites
   - Particle systems: Rain splashes, lightning flashes, fog, and fire
   ========================================================================== */

const PAL = {
  apt12: { sky: ["#14080a", "#050204"], ground: "#2b1c14", accent: "#593325", lit: "#ff334b" },
  hallway: { sky: ["#1c1a16", "#0c0a08"], ground: "#29241b", accent: "#4d4231", lit: "#ffd24d" },
  stairwell: { sky: ["#0a0c10", "#020306"], ground: "#1a1e24", accent: "#303947", lit: "#85b8ff" },
  eas: { sky: ["#260408", "#0d0102"], ground: "#1a080a", accent: "#4d1218", lit: "#ff2233" },
  base: { sky: ["#1e2a38", "#0f141a"], ground: "#231b14", accent: "#593d25", lit: "#e58e3c" },
  streets: { sky: ["#2c3545", "#141720"], ground: "#2b2b2b", accent: "#444e59", lit: "#6ec8ff" },
  mall: { sky: ["#2d1c2d", "#120a14"], ground: "#27212d", accent: "#6e3b56", lit: "#ff79b0" },
  hospital: { sky: ["#1c2923", "#0b120f"], ground: "#1f2922", accent: "#58735d", lit: "#9dffb0" },
  radio: { sky: ["#122438", "#060914"], ground: "#19212d", accent: "#364e66", lit: "#6ec8ff" },
  warehouse: { sky: ["#291a14", "#0f0907"], ground: "#302216", accent: "#733b1e", lit: "#e07a3a" },
  church: { sky: ["#201730", "#090612"], ground: "#261e2b", accent: "#533961", lit: "#d4b5ff" },
  subway: { sky: ["#0a0d14", "#030408"], ground: "#15181f", accent: "#2d384a", lit: "#a0b4c8" },
  checkpoint: { sky: ["#22331c", "#0c140a"], ground: "#2e3325", accent: "#525e3c", lit: "#c8d48a" },
  school: { sky: ["#2d3545", "#11141c"], ground: "#302b21", accent: "#8a7e58", lit: "#ffe08a" },
  docks: { sky: ["#14242e", "#071118"], ground: "#16232b", accent: "#294b59", lit: "#6ad0c8" },
  gas: { sky: ["#261c14", "#0e0906"], ground: "#262015", accent: "#8c4420", lit: "#ffb030" },
  park: { sky: ["#1b2d1c", "#0a140a"], ground: "#202e1c", accent: "#416335", lit: "#a4e67a" },
  pharmacy: { sky: ["#182a2e", "#0a1314"], ground: "#1b2829", accent: "#3b5f63", lit: "#7ae0e6" },
  ending: { sky: ["#120606", "#000000"], ground: "#140c0c", accent: "#3b1616", lit: "#ff334b" },
};

function px(ctx, x, y, w, h, c) {
  ctx.fillStyle = c;
  ctx.fillRect(Math.floor(x), Math.floor(y), Math.floor(w), Math.floor(h));
}

function palFor(scene, loc) {
  const s = (scene || "").toLowerCase();
  const l = (loc || "").toLowerCase();
  if (PAL[s]) return PAL[s];
  if (l.includes("12th floor apartment") || l.includes("apt12")) return PAL.apt12;
  if (l.includes("corridor") || l.includes("hallway")) return PAL.hallway;
  if (l.includes("stairwell")) return PAL.stairwell;
  if (l.includes("base")) return PAL.base;
  if (l.includes("mall")) return PAL.mall;
  if (l.includes("hospital")) return PAL.hospital;
  if (l.includes("radio")) return PAL.radio;
  if (l.includes("warehouse")) return PAL.warehouse;
  if (l.includes("church")) return PAL.church;
  if (l.includes("subway")) return PAL.subway;
  if (l.includes("checkpoint")) return PAL.checkpoint;
  if (l.includes("school")) return PAL.school;
  if (l.includes("dock")) return PAL.docks;
  if (l.includes("gas")) return PAL.gas;
  if (l.includes("park")) return PAL.park;
  if (l.includes("pharmacy")) return PAL.pharmacy;
  return PAL.streets;
}

const Scene = {
  t: 0,
  lastState: null,
  viewMode: "scene", // "scene" or "map"

  init() {
    this.canvas = document.getElementById("view");
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext("2d");
    this.ctx.imageSmoothingEnabled = false;
  },

  toggleViewMode() {
    this.viewMode = this.viewMode === "scene" ? "map" : "scene";
    const btnScene = document.getElementById("toggle-scene");
    const btnMap = document.getElementById("toggle-map");
    if (btnScene && btnMap) {
      btnScene.classList.toggle("active", this.viewMode === "scene");
      btnMap.classList.toggle("active", this.viewMode === "map");
    }
    if (this.lastState) {
      this.render(this.lastState);
    }
  },

  render(state) {
    if (!this.ctx) this.init();
    if (!this.ctx || !state) return;

    this.lastState = state;
    this.t += 1;
    const ctx = this.ctx;
    const t = this.t;

    // Check if player selected "Scavenge" menu — auto-flip to map for tactical selection
    const isMapMenu = state.menu === "locations";

    if (this.viewMode === "map" || isMapMenu) {
      this.drawCityMap(ctx, state, t);
      return;
    }

    const w = state.world || {};
    const p = state.player || {};
    const night = !!w.is_night;
    const weather = (w.weather || "clear").toLowerCase();
    const loc = w.location || "12th Floor Apartment";
    const scene = (state.scene || "apt12").toLowerCase();
    const pal = palFor(scene, loc);

    // 1. SKY GRADIENT & CELESTIALS
    this.drawSky(ctx, pal, night, t);

    // 2. PARALLAX SKYLINE / WINDOW
    this.drawParallaxCity(ctx, pal, night, loc, t);

    // 3. ARCHITECTURE BACKDROP
    if (scene === "eas" || scene === "apt12" || loc.includes("12th Floor Apartment")) {
      this.drawApt1204(ctx, pal, w, t);
    } else if (scene === "hallway" || loc.includes("Corridor")) {
      this.drawCorridor(ctx, pal, t);
    } else if (scene === "stairwell" || loc.includes("Stairwell")) {
      this.drawStairwell(ctx, pal, t);
    } else if (loc.includes("Home Base") || scene === "base" || scene === "craft" || scene === "talk" || scene === "quiet") {
      this.drawBaseInterior(ctx, pal, w, p, t);
    } else {
      this.drawLocationBackdrop(ctx, pal, loc, scene, night, t);
    }

    // 4. ENTITIES: SURVIVOR & COMPANION & FOES
    this.drawEntities(ctx, state, t);

    // 5. WEATHER PARTICLES
    this.drawWeather(ctx, weather, t);

    // 6. INFECTION SCREEN TINT & CRT FLICKER
    const infStage = state.infection_stage || "clean";
    if (infStage === "fever") {
      ctx.fillStyle = "rgba(255, 184, 48, 0.06)";
      ctx.fillRect(0, 0, 320, 180);
    } else if (infStage === "lucid") {
      ctx.fillStyle = "rgba(120, 255, 60, 0.08)";
      ctx.fillRect(0, 0, 320, 180);
    } else if (infStage === "turning") {
      const alpha = 0.08 + Math.sin(t * 0.15) * 0.05;
      ctx.fillStyle = `rgba(255, 30, 30, ${alpha})`;
      ctx.fillRect(0, 0, 320, 180);
    }
  },

  // ─────────────────────────────────────────────────────────────
  // PIXEL CITY MAP (TACTICAL GRID)
  // ─────────────────────────────────────────────────────────────

  drawCityMap(ctx, state, t) {
    const mapData = state.map_data || {};
    const curLoc = (state.world && state.world.location) || "12th Floor Apartment";

    // 1. Dark Blueprint Grid
    ctx.fillStyle = "#060a0f";
    ctx.fillRect(0, 0, 320, 180);

    ctx.strokeStyle = "rgba(40, 80, 110, 0.18)";
    ctx.lineWidth = 1;
    for (let x = 0; x < 320; x += 16) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, 180);
      ctx.stroke();
    }
    for (let y = 0; y < 180; y += 16) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(320, y);
      ctx.stroke();
    }

    // 2. Compass & Map Title
    ctx.fillStyle = "#ffb830";
    ctx.font = "bold 9px monospace";
    ctx.fillText("TACTICAL DISTRICT GRID — CHANNEL 7", 8, 12);
    ctx.fillStyle = "#6ec8ff";
    ctx.font = "8px monospace";
    ctx.fillText("SECTOR 12 HIGH-RISE TO MILE 18 CHECKPOINT", 8, 22);

    // 3. Radar Sweep Circle
    const sweepAngle = (t * 0.03) % (Math.PI * 2);
    ctx.save();
    ctx.translate(160, 95);
    ctx.strokeStyle = "rgba(110, 200, 255, 0.15)";
    ctx.beginPath();
    ctx.arc(0, 0, 80, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(0, 0, 45, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(sweepAngle) * 80, Math.sin(sweepAngle) * 80);
    ctx.strokeStyle = "rgba(110, 200, 255, 0.35)";
    ctx.stroke();
    ctx.restore();

    // 4. Draw Connection Roads
    ctx.strokeStyle = "rgba(90, 130, 160, 0.35)";
    ctx.setLineDash([3, 3]);
    Object.values(mapData).forEach((node) => {
      const conns = node.connections || [];
      conns.forEach((targetName) => {
        const target = mapData[targetName];
        if (target) {
          ctx.beginPath();
          ctx.moveTo(node.x, node.y);
          ctx.lineTo(target.x, target.y);
          ctx.stroke();
        }
      });
    });
    ctx.setLineDash([]);

    // 5. Draw Location Nodes
    Object.values(mapData).forEach((node) => {
      const isCurrent = node.name.toLowerCase() === curLoc.toLowerCase();
      const threat = node.threat || "MED";
      const threatCols = {
        SAFE: "#52ff83",
        LOW: "#6ec8ff",
        MED: "#ffb830",
        HIGH: "#ff79b0",
        SEVERE: "#ff334b",
      };
      const col = threatCols[threat] || "#ffb830";

      // Node base icon box
      px(ctx, node.x - 7, node.y - 7, 14, 14, "#0d1620");
      px(ctx, node.x - 6, node.y - 6, 12, 12, isCurrent ? "#243c50" : "#131f2b");

      // Outer border
      ctx.strokeStyle = col;
      ctx.lineWidth = 1;
      ctx.strokeRect(node.x - 7, node.y - 7, 14, 14);

      // Icon text
      ctx.font = "9px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(node.icon || "📍", node.x, node.y + 3);

      // Label below
      ctx.fillStyle = isCurrent ? "#ffffff" : "#a2b9cc";
      ctx.font = isCurrent ? "bold 7px monospace" : "7px monospace";
      const shortName = node.name.replace("Apartment", "Apt").replace("Corridor", "Corr").replace("Military", "Mil");
      ctx.fillText(shortName.slice(0, 14), node.x, node.y + 14);

      // 6. Current Player Pulsing Beacon
      if (isCurrent) {
        const pulse = 10 + Math.sin(t * 0.2) * 4;
        ctx.strokeStyle = "#ff334b";
        ctx.beginPath();
        ctx.arc(node.x, node.y, pulse, 0, Math.PI * 2);
        ctx.stroke();

        // "YOU" marker badge
        px(ctx, node.x - 12, node.y - 18, 24, 8, "#ff334b");
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 6px monospace";
        ctx.fillText("YOU", node.x, node.y - 12);
      }
    });

    ctx.textAlign = "left";
  },

  // ─────────────────────────────────────────────────────────────
  // SCENE BACKGROUNDS
  // ─────────────────────────────────────────────────────────────

  drawSky(ctx, pal, night, t) {
    const grad = ctx.createLinearGradient(0, 0, 0, 115);
    if (night) {
      grad.addColorStop(0, "#030408");
      grad.addColorStop(1, "#0d131c");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 320, 180);

      // Stars
      for (let i = 0; i < 30; i++) {
        const sx = (i * 71 + 14) % 320;
        const sy = (i * 39 + 7) % 80;
        const blink = Math.sin(t * 0.05 + i) > 0.3;
        px(ctx, sx, sy, 1, 1, blink ? "#d4e2f5" : "rgba(120, 140, 170, 0.4)");
      }
      // Crescent Moon
      px(ctx, 275, 16, 7, 7, "#d9e2ec");
      px(ctx, 273, 14, 5, 5, "#030408");
    } else {
      grad.addColorStop(0, pal.sky[0]);
      grad.addColorStop(1, pal.sky[1]);
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 320, 180);

      // Pale Sun
      px(ctx, 42, 18, 10, 10, "#ffe8a3");
      px(ctx, 40, 16, 14, 14, "rgba(255, 232, 163, 0.2)");
    }
  },

  drawParallaxCity(ctx, pal, night, loc, t) {
    const baseY = 114;

    // Distant burning skyline
    ctx.fillStyle = night ? "#080d14" : "#111820";
    for (let x = 0; x < 320; x += 28) {
      const h = 25 + ((x * 19) % 30);
      ctx.fillRect(x, baseY - h - 10, 26, h + 10);
    }

    // Window buildings
    const heights = [45, 30, 60, 25, 52, 38, 65, 30, 48, 35];
    let bx = 0;
    heights.forEach((h, i) => {
      const bw = 34;
      px(ctx, bx, baseY - h, bw - 2, h, i % 2 ? pal.accent : "#18201a");

      for (let wy = baseY - h + 6; wy < baseY - 6; wy += 8) {
        for (let wx = bx + 4; wx < bx + bw - 6; wx += 7) {
          const isLit = (wx * 11 + wy * 13) % 7 === 0;
          const flicker = isLit && Math.sin(t * 0.1 + wx) > -0.2;
          px(ctx, wx, wy, 2, 2, flicker ? pal.lit : "#070a08");
        }
      }

      if (i === 4) {
        px(ctx, bx + 12, baseY - h - 14, 1, 14, "#444");
        const beaconOn = (t % 40) < 20;
        px(ctx, bx + 11, baseY - h - 15, 3, 2, beaconOn ? "#ff334b" : "#441111");
      }

      bx += bw - 2;
    });

    px(ctx, 0, baseY, 320, 66, pal.ground);
    px(ctx, 0, baseY, 320, 3, "#111613");
  },

  // ── APARTMENT 1204 (12TH FLOOR EAS OUTBREAK) ──
  drawApt1204(ctx, pal, world, t) {
    const baseY = 114;

    // Apartment interior walls & wood floor
    px(ctx, 35, 45, 250, 100, "#1a120e");
    px(ctx, 35, 108, 250, 37, "#281c15");

    // 12th-floor high window looking down
    px(ctx, 50, 52, 55, 45, "#0b0d14");
    // Window frame
    px(ctx, 48, 50, 59, 2, "#4a3322");
    px(ctx, 48, 97, 59, 2, "#4a3322");
    px(ctx, 76, 52, 2, 45, "#4a3322");

    // Distant searchlight beam cutting through window
    const beamAngle = Math.sin(t * 0.05) * 15;
    ctx.save();
    ctx.translate(76, 75);
    ctx.rotate((beamAngle * Math.PI) / 180);
    ctx.fillStyle = "rgba(255, 255, 255, 0.08)";
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(-20, -50);
    ctx.lineTo(20, -50);
    ctx.closePath();
    ctx.fill();
    ctx.restore();

    // TV / EAS MONITOR ON TABLE
    px(ctx, 215, 78, 48, 30, "#121417"); // TV set
    px(ctx, 220, 108, 38, 4, "#2a221b"); // Table
    px(ctx, 223, 112, 4, 25, "#2a221b"); // leg
    px(ctx, 251, 112, 4, 25, "#2a221b"); // leg

    // Flashing red EAS Emergency Screen
    const flashRed = (t % 24) < 12;
    px(ctx, 219, 82, 40, 22, flashRed ? "#990011" : "#1a0005");
    px(ctx, 223, 86, 32, 2, "#ffddaa"); // Emergency bar
    px(ctx, 223, 91, 24, 2, "#ffffff"); // text line
    px(ctx, 223, 96, 28, 2, "#ffffff"); // text line

    // Heavy Dresser Barricade against Door on right
    px(ctx, 268, 60, 16, 55, "#3b281b");
    px(ctx, 269, 75, 14, 2, "#523725");
    px(ctx, 269, 90, 14, 2, "#523725");
  },

  // ── 12TH FLOOR CORRIDOR ──
  drawCorridor(ctx, pal, t) {
    const baseY = 114;
    // Perspective hallway
    px(ctx, 0, 40, 320, 105, "#1f1d18");
    px(ctx, 0, 110, 320, 35, "#2d2a23");

    // Doors 1201, 1202, 1204, 1206
    const doors = [40, 95, 175, 235];
    doors.forEach((dx, idx) => {
      px(ctx, dx, 55, 30, 55, "#3d3023");
      px(ctx, dx + 2, 57, 26, 51, "#2b2117");
      px(ctx, dx + 24, 82, 2, 4, "#c49a45"); // brass knob
      // Door number plaque
      px(ctx, dx + 10, 64, 10, 4, "#d1b46a");
    });

    // Overhead fluorescent tube light with flicker
    px(ctx, 130, 42, 60, 3, "#444");
    const tubeLit = Math.sin(t * 0.4) > -0.7;
    px(ctx, 132, 43, 56, 2, tubeLit ? "#fff8d6" : "#443f2d");

    // Light pool on carpet
    if (tubeLit) {
      ctx.fillStyle = "rgba(255, 248, 214, 0.08)";
      ctx.beginPath();
      ctx.moveTo(130, 45);
      ctx.lineTo(90, 140);
      ctx.lineTo(230, 140);
      ctx.lineTo(190, 45);
      ctx.closePath();
      ctx.fill();
    }

    // Blood smear on wall
    px(ctx, 148, 85, 12, 3, "#6b1414");
    px(ctx, 152, 88, 2, 8, "#6b1414");
  },

  // ── STAIRWELL ──
  drawStairwell(ctx, pal, t) {
    const baseY = 114;
    // Concrete shaft
    px(ctx, 40, 30, 240, 120, "#13171c");
    // Concrete steps winding
    for (let i = 0; i < 8; i++) {
      const sy = 40 + i * 13;
      px(ctx, 60, sy, 200, 4, "#272e38");
      px(ctx, 60, sy + 4, 200, 9, "#1c2129");
      // Metal handrail
      px(ctx, 60, sy - 8, 200, 2, "#4a5563");
    }

    // Flashlight beam scanning
    const sweep = Math.sin(t * 0.08) * 20;
    ctx.save();
    ctx.translate(95, 110);
    ctx.rotate(((-30 + sweep) * Math.PI) / 180);
    ctx.fillStyle = "rgba(180, 220, 255, 0.15)";
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(120, -35);
    ctx.lineTo(120, 35);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  },

  // ── HOME BASE (FORTIFIED SAFEHOUSE) ──
  drawBaseInterior(ctx, pal, world, player, t) {
    const fort = world.fortification || 0;
    const flags = world.flags || {};
    const baseY = 114;

    px(ctx, 40, 50, 240, 95, "#221a14");
    px(ctx, 40, 110, 240, 35, "#30241b");

    // Boarded window
    px(ctx, 55, 60, 48, 38, "#0a0e14");
    const boardCount = Math.min(10, Math.max(1, fort));
    for (let i = 0; i < boardCount; i++) {
      const by = 62 + i * 3.5;
      px(ctx, 53, by, 52, 3, "#543823");
      px(ctx, 55, by + 1, 2, 1, "#777");
      px(ctx, 102, by + 1, 2, 1, "#777");
    }

    // Workbench
    px(ctx, 220, 85, 55, 30, "#3e2b1d");
    px(ctx, 224, 115, 6, 25, "#261a12");
    px(ctx, 264, 115, 6, 25, "#261a12");

    if (flags.radio_repaired) {
      px(ctx, 230, 75, 18, 10, "#192429");
      const glow = (t % 30) < 15 ? "#ffaa33" : "#ff7711";
      px(ctx, 236, 71, 3, 4, glow);
      px(ctx, 242, 68, 1, 7, "#777");
    }

    if (flags.rain_catcher) {
      px(ctx, 44, 98, 14, 22, "#2b4a5e");
      px(ctx, 44, 97, 14, 2, "#182c38");
    }

    if (flags.garden) {
      px(ctx, 60, 100, 38, 10, "#3d2a1b");
      for (let gx = 64; gx < 94; gx += 6) {
        px(ctx, gx, 96, 3, 4, "#5cb85c");
      }
    }

    if (flags.alarm) {
      px(ctx, 110, 68, 80, 1, "#555");
      px(ctx, 130, 69, 3, 5, "#a8a8a8");
      px(ctx, 160, 69, 3, 5, "#a8a8a8");
    }

    // Candle flame
    px(ctx, 255, 80, 4, 5, "#e58e3c");
    px(ctx, 256, 77, 2, 3, (t % 10 < 5) ? "#ffe680" : "#ffaa33");
  },

  drawLocationBackdrop(ctx, pal, loc, scene, night, t) {
    const baseY = 114;
    const l = loc.toLowerCase();

    if (l.includes("mall")) {
      px(ctx, 50, 40, 110, 74, "#1b1420");
      px(ctx, 56, 46, 34, 10, (t % 50 < 40) ? "#ff79b0" : "#552038");
      px(ctx, 180, 60, 80, 54, "#2d2433");
    } else if (l.includes("hospital")) {
      px(ctx, 80, 65, 80, 49, "#1c2621");
      px(ctx, 115, 75, 10, 20, "#ff334b");
      px(ctx, 110, 80, 20, 10, "#ff334b");
    } else if (l.includes("radio")) {
      for (let ty = 10; ty < baseY; ty += 12) {
        const w = 10 + (baseY - ty) * 0.25;
        px(ctx, 160 - w / 2, ty, w, 2, "#4a627a");
      }
      px(ctx, 159, 6, 3, 5, (t % 30 < 15) ? "#ff334b" : "#441111");
    } else if (l.includes("church")) {
      px(ctx, 135, 45, 50, 69, "#211a29");
      px(ctx, 150, 55, 20, 20, pal.lit);
      px(ctx, 158, 48, 4, 16, "#554466");
      px(ctx, 152, 53, 16, 4, "#554466");
    } else if (l.includes("subway")) {
      px(ctx, 40, 45, 240, 69, "#12141a");
      px(ctx, 0, baseY + 12, 320, 2, "#555");
      px(ctx, 0, baseY + 20, 320, 2, "#555");
    } else if (l.includes("checkpoint")) {
      for (let sby = baseY - 16; sby < baseY; sby += 5) {
        for (let sbx = 40; sbx < 160; sbx += 14) {
          px(ctx, sbx, sby, 12, 4, "#6b6f4e");
        }
      }
    } else if (l.includes("docks")) {
      for (let wy = baseY + 6; wy < 180; wy += 8) {
        const off = Math.sin(t * 0.08 + wy) * 6;
        px(ctx, 20 + off, wy, 280, 2, "#366b7a");
      }
      px(ctx, 180, baseY - 18, 90, 20, "#192329");
      px(ctx, 210, baseY - 32, 30, 14, "#2a3942");
    }
  },

  // ─────────────────────────────────────────────────────────────
  // ENTITY SPRITES: SURVIVOR, COMPANIONS & ZOMBIES
  // ─────────────────────────────────────────────────────────────

  drawEntities(ctx, state, t) {
    const baseY = 114;
    const scene = (state.scene || "").toLowerCase();
    const mode = state.mode;
    const party = state.party || [];
    const loc = (state.world && state.world.location) || "";
    const isBase = loc.includes("Home Base") || loc.includes("12th Floor Apartment");

    // 1. Player Character
    const playerColors = {
      head: "#f0c8a0",
      body: "#385642",
      leg: "#202e24",
      arm: "#d0aa80",
    };
    const playerX = isBase ? 115 : 75;
    const playerY = baseY - 2;
    this.drawPerson(ctx, playerX, playerY, playerColors, 2, t);

    // 2. Companions (Maya, Sean, Marcus, Lena, Kid, etc.)
    const npcCols = {
      maya: { head: "#f2c6a0", body: "#d14b8a", leg: "#261a29", arm: "#f2c6a0" },
      sean: { head: "#c89462", body: "#2a425e", leg: "#192430", arm: "#c89462" },
      marcus: { head: "#c89462", body: "#2a425e", leg: "#192430", arm: "#c89462" },
      lena: { head: "#e0e8db", body: "#84a689", leg: "#333e36", arm: "#e0e8db" },
      kid: { head: "#f5d787", body: "#5e4b2a", leg: "#3a2d18", arm: "#f5d787" },
      miriam: { head: "#eeddcc", body: "#3f2d57", leg: "#231830", arm: "#eeddcc" },
      ghost: { head: "#9fb5c7", body: "#2b343d", leg: "#1a2026", arm: "#9fb5c7" },
      butcher: { head: "#e5b394", body: "#6e2121", leg: "#381010", arm: "#e5b394" },
    };

    if (isBase) {
      party.slice(0, 4).forEach((n, idx) => {
        const cols = npcCols[n.id] || npcCols.sean;
        const nx = 145 + idx * 24;
        const scale = n.id === "kid" ? 1.5 : 2;
        this.drawPerson(ctx, nx, baseY - 2, cols, scale, t + idx * 3);
      });

      if (state.world && state.world.flags && state.world.flags.has_dog) {
        this.drawDog(ctx, 92, baseY + 6, t);
      }
    } else {
      // If companion recruited, companion stands near player on field expeditions!
      if (party.length > 0) {
        const mainComp = party[0];
        const cols = npcCols[mainComp.id] || npcCols.maya;
        this.drawPerson(ctx, 50, baseY - 2, cols, 2, t + 2);
      }

      // Foes & NPCs in Field
      if (mode === "combat" || ["shambler", "runner", "bloater", "armored", "stalker"].includes(scene)) {
        const enemyKind = state.combat && state.combat.enemy_id ? state.combat.enemy_id : scene;
        this.drawEnemy(ctx, 210, baseY - 2, enemyKind, t);
      } else if (["lena", "marcus", "kid", "miriam", "ghost", "butcher", "maya", "sean"].includes(scene)) {
        const cols = npcCols[scene] || npcCols.marcus;
        this.drawPerson(ctx, 210, baseY - 2, cols, scene === "kid" ? 1.5 : 2, t);
      }
    }
  },

  drawPerson(ctx, x, y, cols, scale, t) {
    const s = scale || 2;
    const bob = Math.sin(t * 0.1) > 0 ? 1 : 0;
    const py = y - s * 8 + bob;

    // Head
    px(ctx, x + s, py, s * 2, s * 2, cols.head);
    // Torso
    px(ctx, x, py + s * 2, s * 4, s * 3, cols.body);
    // Arms
    px(ctx, x - s, py + s * 2.5, s, s * 2.5, cols.arm);
    px(ctx, x + s * 4, py + s * 2.5, s, s * 2.5, cols.arm);
    // Legs
    px(ctx, x + s * 0.5, py + s * 5, s * 1.2, s * 3, cols.leg);
    px(ctx, x + s * 2.3, py + s * 5, s * 1.2, s * 3, cols.leg);
  },

  drawDog(ctx, x, y, t) {
    px(ctx, x, y - 6, 12, 6, "#9e774d");
    px(ctx, x + 9, y - 10, 5, 5, "#9e774d");
    px(ctx, x + 13, y - 8, 3, 3, "#422e1b");
    px(ctx, x + 8, y - 12, 2, 3, "#543b23");
    px(ctx, x + 2, y, 2, 4, "#543b23");
    px(ctx, x + 8, y, 2, 4, "#543b23");
    const wag = Math.sin(t * 0.3) > 0 ? -2 : 0;
    px(ctx, x - 3, y - 8 + wag, 3, 2, "#9e774d");
  },

  drawEnemy(ctx, x, y, kind, t) {
    const tints = {
      shambler: { head: "#7a9c68", body: "#3f4f36", leg: "#263021", arm: "#5e7850" },
      runner: { head: "#b5c478", body: "#592b25", leg: "#331814", arm: "#7a3b33" },
      bloater: { head: "#5e7545", body: "#395e24", leg: "#213615", arm: "#47732e" },
      armored: { head: "#889488", body: "#313831", leg: "#1e241e", arm: "#555e55" },
      stalker: { head: "#3d474d", body: "#1b2126", leg: "#101417", arm: "#2b343b" },
      butcher_fight: { head: "#d99f7e", body: "#691f1f", leg: "#360f0f", arm: "#d99f7e" },
    };

    const c = tints[kind] || tints.shambler;
    const isBloater = kind === "bloater";
    const sc = isBloater ? 3 : 2;
    const lunging = Math.sin(t * 0.18) > 0 ? 1 : -1;

    this.drawPerson(ctx, x + lunging, y, c, sc, t);

    if (kind === "armored") {
      px(ctx, x - 4, y - 14, 4, 16, "#666e66");
      px(ctx, x - 3, y - 12, 2, 4, "#8df");
    } else if (kind === "butcher_fight") {
      px(ctx, x - 5, y - 18, 5, 8, "#d1d5db");
      px(ctx, x - 3, y - 10, 2, 5, "#522");
    }
  },

  drawWeather(ctx, weather, t) {
    if (weather === "rain" || weather === "storm") {
      ctx.fillStyle = "rgba(180, 210, 255, 0.45)";
      const count = weather === "storm" ? 85 : 45;
      for (let i = 0; i < count; i++) {
        const rx = (i * 43 + t * 9) % 320;
        const ry = (i * 29 + t * 15) % 180;
        ctx.fillRect(rx, ry, 1, 6);
        if (ry > 114) {
          ctx.fillRect(rx - 1, ry + 6, 3, 1);
        }
      }
    }

    if (weather === "fog") {
      for (let i = 0; i < 3; i++) {
        const fy = 80 + i * 25;
        ctx.fillStyle = "rgba(190, 205, 200, 0.14)";
        ctx.fillRect(0, fy, 320, 30);
      }
    }

    if (weather === "storm") {
      if ((t % 95) < 3) {
        ctx.fillStyle = "rgba(230, 240, 255, 0.45)";
        ctx.fillRect(0, 0, 320, 180);
      }
    }
  },
};
