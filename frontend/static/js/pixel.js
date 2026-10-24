/* ==========================================================================
   APOCALYPSE TERMINAL — Procedural Pixel Engine (320x180)
   Layered skies, dynamic architecture, weather systems, and pixel sprites
   ========================================================================== */

const PAL = {
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

  init() {
    this.canvas = document.getElementById("view");
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext("2d");
    this.ctx.imageSmoothingEnabled = false;
  },

  render(state) {
    if (!this.ctx) this.init();
    if (!this.ctx || !state) return;

    this.lastState = state;
    this.t += 1;
    const ctx = this.ctx;
    const t = this.t;

    const w = state.world || {};
    const p = state.player || {};
    const night = !!w.is_night;
    const weather = (w.weather || "clear").toLowerCase();
    const loc = w.location || "Home Base";
    const scene = (state.scene || "streets").toLowerCase();
    const pal = palFor(scene, loc);

    const isBase = scene === "base" || scene === "craft" || scene === "talk" || scene === "quiet" || (loc === "Home Base" && state.mode !== "combat");

    // 1. SKY GRADIENT & CELESTIAL BODIES
    this.drawSky(ctx, pal, night, t);

    // 2. PARALLAX SKYLINE
    this.drawParallaxCity(ctx, pal, night, t);

    // 3. ARCHITECTURE / SCENE BACKDROP
    if (isBase) {
      this.drawBaseInterior(ctx, pal, w, p, state.party || [], t);
    } else {
      this.drawLocationBackdrop(ctx, pal, loc, scene, night, t);
    }

    // 4. ENTITIES: PLAYER, COMPANIONS & FOES
    this.drawEntities(ctx, state, isBase, t);

    // 5. WEATHER SYSTEMS
    this.drawWeather(ctx, weather, t);

    // 6. INFECTION SCREEN TINT
    const infStage = state.infection_stage || "clean";
    if (infStage === "fever") {
      ctx.fillStyle = "rgba(255, 184, 48, 0.05)";
      ctx.fillRect(0, 0, 320, 180);
    } else if (infStage === "lucid") {
      ctx.fillStyle = "rgba(120, 255, 60, 0.07)";
      ctx.fillRect(0, 0, 320, 180);
    } else if (infStage === "turning") {
      const alpha = 0.08 + Math.sin(t * 0.15) * 0.04;
      ctx.fillStyle = `rgba(255, 30, 30, ${alpha})`;
      ctx.fillRect(0, 0, 320, 180);
    }
  },

  drawSky(ctx, pal, night, t) {
    const grad = ctx.createLinearGradient(0, 0, 0, 120);
    if (night) {
      grad.addColorStop(0, "#030408");
      grad.addColorStop(1, "#0d131c");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 320, 180);

      // Stars twinkling
      for (let i = 0; i < 35; i++) {
        const sx = (i * 73 + 12) % 320;
        const sy = (i * 41 + 5) % 85;
        const blink = Math.sin(t * 0.05 + i) > 0.3;
        px(ctx, sx, sy, 1, 1, blink ? "#c8d4e5" : "rgba(120, 140, 170, 0.4)");
      }

      // Crescent Moon
      px(ctx, 270, 16, 8, 8, "#d9e2ec");
      px(ctx, 268, 14, 6, 6, "#030408");
    } else {
      grad.addColorStop(0, pal.sky[0]);
      grad.addColorStop(1, pal.sky[1]);
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 320, 180);

      // Pale Sun
      px(ctx, 42, 18, 10, 10, "#ffe8a3");
      px(ctx, 41, 19, 12, 8, "rgba(255, 232, 163, 0.3)");
    }
  },

  drawParallaxCity(ctx, pal, night, t) {
    const baseY = 114;

    // Distant mountain / skyline layer
    ctx.fillStyle = night ? "#070b10" : "#111820";
    for (let x = 0; x < 320; x += 30) {
      const h = 20 + ((x * 17) % 25);
      ctx.fillRect(x, baseY - h - 15, 28, h + 15);
    }

    // Midground buildings
    const heights = [45, 30, 60, 25, 52, 38, 65, 30, 48, 35];
    let bx = 0;
    heights.forEach((h, i) => {
      const bw = 34;
      px(ctx, bx, baseY - h, bw - 2, h, i % 2 ? pal.accent : "#18201a");

      // Windows
      for (let wy = baseY - h + 6; wy < baseY - 6; wy += 8) {
        for (let wx = bx + 4; wx < bx + bw - 6; wx += 7) {
          const isLit = (wx * 11 + wy * 13) % 7 === 0;
          const flicker = isLit && Math.sin(t * 0.1 + wx) > -0.2;
          px(ctx, wx, wy, 2, 2, flicker ? pal.lit : "#070a08");
        }
      }

      // Antenna on top
      if (i === 4) {
        px(ctx, bx + 12, baseY - h - 14, 1, 14, "#444");
        const beaconOn = (t % 40) < 20;
        px(ctx, bx + 11, baseY - h - 15, 3, 2, beaconOn ? "#ff334b" : "#441111");
      }

      bx += bw - 2;
    });

    // Street Ground
    px(ctx, 0, baseY, 320, 66, pal.ground);
    px(ctx, 0, baseY, 320, 3, "#111613");
  },

  drawBaseInterior(ctx, pal, world, player, party, t) {
    const fort = world.fortification || 0;
    const flags = world.flags || {};
    const baseY = 114;

    // Room walls and floor
    px(ctx, 40, 50, 240, 95, "#221a14");
    px(ctx, 40, 110, 240, 35, "#30241b");

    // Boarded window
    px(ctx, 55, 60, 48, 38, "#0a0e14");
    // Fortification cross-boards
    const boardCount = Math.min(10, Math.max(1, fort));
    for (let i = 0; i < boardCount; i++) {
      const by = 62 + i * 3.5;
      px(ctx, 53, by, 52, 3, "#543823");
      px(ctx, 55, by + 1, 2, 1, "#777"); // nail
      px(ctx, 102, by + 1, 2, 1, "#777"); // nail
    }

    // Workbench on right
    px(ctx, 220, 85, 55, 30, "#3e2b1d");
    px(ctx, 224, 115, 6, 25, "#261a12");
    px(ctx, 264, 115, 6, 25, "#261a12");

    // Upgrades visual elements
    if (flags.radio_repaired) {
      // Radio on workbench with glowing tube
      px(ctx, 230, 75, 18, 10, "#192429");
      const glow = (t % 30) < 15 ? "#ffaa33" : "#ff7711";
      px(ctx, 236, 71, 3, 4, glow);
      px(ctx, 242, 68, 1, 7, "#777"); // wire antenna
    }

    if (flags.rain_catcher) {
      // Blue water barrel in corner
      px(ctx, 44, 98, 14, 22, "#2b4a5e");
      px(ctx, 44, 97, 14, 2, "#182c38");
    }

    if (flags.garden) {
      // Green planter box under window
      px(ctx, 60, 100, 38, 10, "#3d2a1b");
      for (let gx = 64; gx < 94; gx += 6) {
        px(ctx, gx, 96, 3, 4, "#5cb85c");
      }
    }

    if (flags.alarm) {
      // Tin cans hanging on tripwire
      px(ctx, 110, 68, 80, 1, "#555");
      px(ctx, 130, 69, 3, 5, "#a8a8a8");
      px(ctx, 160, 69, 3, 5, "#a8a8a8");
    }

    // Candle flame on workbench
    px(ctx, 255, 80, 4, 5, "#e58e3c");
    px(ctx, 256, 77, 2, 3, (t % 10 < 5) ? "#ffe680" : "#ffaa33");
  },

  drawLocationBackdrop(ctx, pal, loc, scene, night, t) {
    const baseY = 114;
    const l = loc.toLowerCase();

    if (l.includes("mall")) {
      // Broken storefront & neon
      px(ctx, 50, 40, 110, 74, "#1b1420");
      px(ctx, 56, 46, 34, 10, (t % 50 < 40) ? "#ff79b0" : "#552038"); // Neon sign
      px(ctx, 180, 60, 80, 54, "#2d2433"); // Escalator
    } else if (l.includes("hospital")) {
      // Emergency cross & triage
      px(ctx, 80, 65, 80, 49, "#1c2621");
      px(ctx, 115, 75, 10, 20, "#ff334b"); // Red cross
      px(ctx, 110, 80, 20, 10, "#ff334b");
    } else if (l.includes("radio")) {
      // Massive steel lattice tower
      for (let ty = 10; ty < baseY; ty += 12) {
        const w = 10 + (baseY - ty) * 0.25;
        px(ctx, 160 - w / 2, ty, w, 2, "#4a627a");
      }
      px(ctx, 159, 6, 3, 5, (t % 30 < 15) ? "#ff334b" : "#441111");
    } else if (l.includes("church")) {
      // Rose stained glass window & cross
      px(ctx, 135, 45, 50, 69, "#211a29");
      px(ctx, 150, 55, 20, 20, pal.lit);
      px(ctx, 158, 48, 4, 16, "#554466"); // cross
      px(ctx, 152, 53, 16, 4, "#554466");
    } else if (l.includes("subway")) {
      // Brick arch & rail tracks
      px(ctx, 40, 45, 240, 69, "#12141a");
      px(ctx, 0, baseY + 12, 320, 2, "#555");
      px(ctx, 0, baseY + 20, 320, 2, "#555");
    } else if (l.includes("checkpoint")) {
      // Sandbags & searchlight
      for (let sby = baseY - 16; sby < baseY; sby += 5) {
        for (let sbx = 40; sbx < 160; sbx += 14) {
          px(ctx, sbx, sby, 12, 4, "#6b6f4e");
        }
      }
    } else if (l.includes("docks")) {
      // Harbor water with moving ripples
      for (let wy = baseY + 6; wy < 180; wy += 8) {
        const off = Math.sin(t * 0.08 + wy) * 6;
        px(ctx, 20 + off, wy, 280, 2, "#366b7a");
      }
      // Boat silhouette
      px(ctx, 180, baseY - 18, 90, 20, "#192329");
      px(ctx, 210, baseY - 32, 30, 14, "#2a3942");
    }
  },

  drawEntities(ctx, state, isBase, t) {
    const baseY = 114;
    const scene = (state.scene || "").toLowerCase();
    const mode = state.mode;
    const party = state.party || [];

    // 1. Draw Player Character
    const playerColors = {
      head: "#f0c8a0",
      body: "#385642",
      leg: "#202e24",
      arm: "#d0aa80",
    };
    const playerX = isBase ? 115 : 75;
    const playerY = isBase ? baseY - 4 : baseY - 2;
    this.drawPerson(ctx, playerX, playerY, playerColors, 2, t);

    // 2. Draw Companions in Base
    if (isBase) {
      const npcCols = {
        marcus: { head: "#c89462", body: "#2a425e", leg: "#192430", arm: "#c89462" },
        lena: { head: "#e0e8db", body: "#84a689", leg: "#333e36", arm: "#e0e8db" },
        kid: { head: "#f5d787", body: "#5e4b2a", leg: "#3a2d18", arm: "#f5d787" },
        miriam: { head: "#eeddcc", body: "#3f2d57", leg: "#231830", arm: "#eeddcc" },
        ghost: { head: "#9fb5c7", body: "#2b343d", leg: "#1a2026", arm: "#9fb5c7" },
        butcher: { head: "#e5b394", body: "#6e2121", leg: "#381010", arm: "#e5b394" },
      };

      party.slice(0, 4).forEach((n, idx) => {
        const cols = npcCols[n.id] || npcCols.marcus;
        const nx = 145 + idx * 24;
        const scale = n.id === "kid" ? 1.5 : 2;
        this.drawPerson(ctx, nx, baseY - 2, cols, scale, t + idx * 3);
      });

      // Dog (Scraps)
      if (state.world && state.world.flags && state.world.flags.has_dog) {
        this.drawDog(ctx, 92, baseY + 6, t);
      }
    }

    // 3. Draw Foes / Encounters in Field & Combat
    if (!isBase) {
      if (mode === "combat" || ["shambler", "runner", "bloater", "armored", "stalker"].includes(scene)) {
        const enemyKind = state.combat && state.combat.enemy_id ? state.combat.enemy_id : scene;
        this.drawEnemy(ctx, 210, baseY - 2, enemyKind, t);
      } else if (["lena", "marcus", "kid", "miriam", "ghost", "butcher"].includes(scene)) {
        const npcCols = {
          marcus: { head: "#c89462", body: "#2a425e", leg: "#192430", arm: "#c89462" },
          lena: { head: "#e0e8db", body: "#84a689", leg: "#333e36", arm: "#e0e8db" },
          kid: { head: "#f5d787", body: "#5e4b2a", leg: "#3a2d18", arm: "#f5d787" },
          miriam: { head: "#eeddcc", body: "#3f2d57", leg: "#231830", arm: "#eeddcc" },
          ghost: { head: "#9fb5c7", body: "#2b343d", leg: "#1a2026", arm: "#9fb5c7" },
          butcher: { head: "#e5b394", body: "#6e2121", leg: "#381010", arm: "#e5b394" },
        };
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
    // Body & Head
    px(ctx, x, y - 6, 12, 6, "#9e774d");
    px(ctx, x + 9, y - 10, 5, 5, "#9e774d");
    px(ctx, x + 13, y - 8, 3, 3, "#422e1b"); // snout
    // Ears
    px(ctx, x + 8, y - 12, 2, 3, "#543b23");
    // Legs
    px(ctx, x + 2, y, 2, 4, "#543b23");
    px(ctx, x + 8, y, 2, 4, "#543b23");
    // Wagging tail
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

    // Armor shield
    if (kind === "armored") {
      px(ctx, x - 4, y - 14, 4, 16, "#666e66");
      px(ctx, x - 3, y - 12, 2, 4, "#8df"); // visor
    } else if (kind === "butcher_fight") {
      // Heavy meat cleaver in hand
      px(ctx, x - 5, y - 18, 5, 8, "#d1d5db");
      px(ctx, x - 3, y - 10, 2, 5, "#522");
    }
  },    drawWeather(ctx, weather, t) {

    if (weather === "rain" || weather === "storm") {
      ctx.fillStyle = "rgba(180, 210, 255, 0.45)";
      const count = weather === "storm" ? 85 : 45;
      for (let i = 0; i < count; i++) {
        const rx = (i * 43 + t * 9) % 320;
        const ry = (i * 29 + t * 15) % 180;
        ctx.fillRect(rx, ry, 1, 6);
        // ground splash
        if (ry > 114) {
          ctx.fillRect(rx - 1, ry + 6, 3, 1);
        }
      }
    }

    if (weather === "fog") {
      for (let i = 0; i < 3; i++) {
        const fy = 80 + i * 25;
        const drift = Math.sin(t * 0.02 + i) * 20;
        ctx.fillStyle = "rgba(190, 205, 200, 0.14)";
        ctx.fillRect(0, fy, 320, 30);
      }
    }

    if (weather === "storm") {
      // Lightning flash
      if ((t % 95) < 3) {
        ctx.fillStyle = "rgba(230, 240, 255, 0.45)";
        ctx.fillRect(0, 0, 320, 180);
      }
    }
  },
};

// Expose on window — ui.js/game.js gate on `window.Scene` (const is not auto-on-window).
window.Scene = Scene;
