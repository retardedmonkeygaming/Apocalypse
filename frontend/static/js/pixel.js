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

    // DEAD RIDGE story mode has its own procedural renderer
    if (state.scenario === "dead_ridge") {
      this.drawRidge(ctx, state, t);
      return;
    }

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

  /* ══════════════════════════════════════════════════════════════
     THE WATCHERS OF DEAD RIDGE — procedural 2.5D watchtower scenes
     ══════════════════════════════════════════════════════════════ */

  drawRidge(ctx, state, t) {
    const w = state.world || {};
    const flags = w.flags || {};
    const p = state.player || {};
    const night = !!w.is_night || !!flags.rd_eclipse;
    const scene = (state.scene || "ridge_tower").toLowerCase();
    const sanity = p.morale != null ? p.morale : 100;
    const wind = 0.5 + (p.humanity || 0) / 120; // wind rises with awareness

    // Sky / fog backdrop
    this.drawRidgeSky(ctx, night, t, flags.rd_eclipse);

    if (scene === "ridge_tower" || scene === "ridge_radio" || scene === "ridge_laptop") {
      this.drawRidgePines(ctx, night, t, wind, 96);
      this.drawRidgeCabin(ctx, flags, p, t, sanity);
    } else if (scene === "ridge_bridge") {
      this.drawRidgeBridge(ctx, t);
    } else if (scene === "ridge_mine") {
      this.drawRidgeMine(ctx, t);
    } else if (scene === "ridge_cabins") {
      this.drawRidgePines(ctx, night, t, wind, 104);
      this.drawRidgeCabinSite(ctx, t, sanity);
    } else if (scene === "ridge_radar") {
      this.drawRidgeRadar(ctx, t, flags);
    } else if (scene === "ridge_tower3") {
      this.drawRidgePines(ctx, night, t, wind, 118);
      this.drawTower3(ctx, t);
    } else if (scene === "ridge_entity") {
      this.drawRidgePines(ctx, night, t, wind * 1.6, 110);
      this.drawRidgeEntity(ctx, t, sanity);
    } else if (scene === "ridge_forest") {
      this.drawRidgePines(ctx, night, t, wind, 120);
      this.drawRidgeWalker(ctx, t, sanity);
    } else if (scene.startsWith("ridge_loc")) {
      this.drawRidgeLoc(ctx, state, t, night);
    } else if (scene === "ridge_ending") {
      this.drawRidgePines(ctx, true, t, 2.2, 110);
      this.drawRidgeEnding(ctx, t, state.victory);
    } else {
      this.drawRidgePines(ctx, night, t, wind, 110);
    }

    // Sanity tint — the world bleeds red as the mind frays
    if (sanity <= 45) {
      const alpha = (45 - sanity) / 45 * 0.16 + Math.sin(t * 0.08) * 0.02;
      ctx.fillStyle = `rgba(150, 10, 30, ${Math.max(0, alpha)})`;
      ctx.fillRect(0, 0, 320, 180);
    }
    // Eclipse — permanent violet-black cold
    if (flags.rd_eclipse) {
      ctx.fillStyle = "rgba(20, 8, 40, 0.20)";
      ctx.fillRect(0, 0, 320, 180);
    }
  },

  drawRidgeSky(ctx, night, t, eclipse) {
    const grad = ctx.createLinearGradient(0, 0, 0, 140);
    if (eclipse) {
      grad.addColorStop(0, "#05030a");
      grad.addColorStop(1, "#120a16");
    } else if (night) {
      grad.addColorStop(0, "#04070c");
      grad.addColorStop(1, "#0c141b");
    } else {
      grad.addColorStop(0, "#3d4a52");
      grad.addColorStop(1, "#8a968e"); // overcast Appalachian haze
    }
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 320, 180);

    if (night && !eclipse) {
      for (let i = 0; i < 40; i++) {
        const sx = (i * 67 + 9) % 320;
        const sy = (i * 37 + 4) % 90;
        const blink = Math.sin(t * 0.04 + i * 1.7) > 0.2;
        px(ctx, sx, sy, 1, 1, blink ? "#cfd9e6" : "rgba(120,140,170,0.35)");
      }
      px(ctx, 278, 14, 9, 9, "#d9e2ec");
      px(ctx, 275, 12, 7, 7, night ? "#04070c" : "#3d4a52");
    } else if (!night) {
      // Pale drowned sun behind the haze
      px(ctx, 50, 22, 12, 12, "#e8e3cf");
      px(ctx, 47, 19, 18, 18, "rgba(232,227,207,0.18)");
    } else {
      // Eclipse disc
      px(ctx, 240, 18, 14, 14, "#2a1030");
      px(ctx, 238, 16, 18, 18, "rgba(190,80,255,0.12)");
    }
  },

  drawRidgePines(ctx, night, t, wind, baseY) {
    const layers = [
      { y: baseY - 34, c: night ? "#0a1210" : "#26362c", h: 34, sway: 0.5 },
      { y: baseY - 18, c: night ? "#0d1814" : "#1d2b23", h: 44, sway: 1.0 },
      { y: baseY, c: night ? "#050a08" : "#101a14", h: 58, sway: 1.6 },
    ];
    layers.forEach((L, li) => {
      let x = -8 + li * 5;
      let i = 0;
      while (x < 330) {
        const h = L.h * (0.65 + ((i * 37 + li * 11) % 40) / 100);
        // Procedural tree sway: amplitude scales with wind metric
        const sway = Math.sin(t * 0.045 + i * 1.3 + li) * L.sway * wind * 2.2;
        const topX = x + sway;
        const w = h * 0.42;
        // Trunk
        px(ctx, x - 1 + sway * 0.2, L.y - h * 0.35, 2, h * 0.35, night ? "#0b0f0c" : "#241c14");
        // Three stacked boughs (pixel fir)
        for (let s = 0; s < 3; s++) {
          const sy = L.y - h + (h * 0.28) * s;
          const sw = (w * (0.45 + s * 0.28));
          const off = sway * (1 - s * 0.25);
          px(ctx, topX - sw / 2 + off * 0.3, sy, sw, h * 0.3, L.c);
          px(ctx, topX - sw / 2 + off * 0.3, sy + h * 0.3 - 1, sw, 1, night ? "#0e1512" : "#2c3d31");
        }
        x += 14 + ((i * 23) % 12);
        i++;
      }
    });
    // Rolling fog banks between the layers
    for (let f = 0; f < 3; f++) {
      const fy = baseY - 30 + f * 14;
      const drift = ((t * (0.25 + f * 0.12)) % 420) - 60;
      ctx.fillStyle = `rgba(180, 195, 190, ${0.10 - f * 0.02})`;
      ctx.fillRect(0, fy, 320, 9 + f * 3);
      ctx.fillStyle = `rgba(200, 212, 208, ${0.07})`;
      ctx.fillRect((320 - drift) % 340 - 20, fy - 2, 120, 6);
      ctx.fillRect((drift + 160) % 360 - 30, fy + 4, 90, 5);
    }
    // Ground
    px(ctx, 0, baseY, 320, 180 - baseY, night ? "#05080a" : "#141c17");
  },

  drawRidgeCabin(ctx, flags, p, t, sanity) {
    const seal = (window.__rdState && window.__rdState.world && window.__rdState.world.fortification) || 3;
    // Cabin walls & floor
    px(ctx, 0, 0, 320, 180, "rgba(20,14,10,0.0)");
    px(ctx, 14, 22, 292, 12, "#241a12");   // ceiling beam
    px(ctx, 14, 132, 292, 30, "#2b2016");  // floorboards
    for (let fx = 20; fx < 300; fx += 26) {
      px(ctx, fx, 133, 1, 28, "#1d150e");
    }
    // Big glass window pane — translucent so the pine/fog layers show through
    px(ctx, 34, 36, 252, 94, "rgba(10,17,22,0.28)");
    ctx.strokeStyle = "#3a2c1e";
    ctx.lineWidth = 3;
    ctx.strokeRect(34, 36, 252, 94);
    // Mullions
    px(ctx, 118, 36, 3, 94, "#3a2c1e");
    px(ctx, 198, 36, 3, 94, "#3a2c1e");
    px(ctx, 34, 80, 252, 3, "#3a2c1e");

    // THE WINDOW LIES — below 50 sanity a false companion stands outside
    if (sanity < 50 && Math.floor(t / 70) % 3 === 1) {
      ctx.globalAlpha = 0.55;
      this.drawPerson(ctx, 232, 126, { head: "#9fb0b4", body: "#3d545c", leg: "#263238", arm: "#9fb0b4" }, 2, t);
      ctx.globalAlpha = 1;
      px(ctx, 234, 74, 6, 1, "rgba(190,205,210,0.4)"); // where its breath would fog the glass
    }

    // Scratching three-beat marks on the glass under high awareness/siege
    const aware = (p && p.humanity) || 0;
    if (flags.rd_siege_night || aware >= 40) {
      const beat = Math.floor(t / 9) % 4;
      for (let i = 0; i < beat; i++) {
        const sx = 48 + i * 5;
        px(ctx, sx, 46 + i * 3, 1, 7, "rgba(225,235,240,0.55)");
      }
    }

    // Cracks — grow as the tower seal drops
    const cracks = Math.max(0, 3 - seal);
    for (let c = 0; c < cracks; c++) {
      const cx = 60 + c * 70;
      ctx.strokeStyle = "rgba(210,225,235,0.5)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(cx, 40);
      ctx.lineTo(cx + 8 + Math.sin(t * 0.02 + c) * 0.5, 60);
      ctx.lineTo(cx - 4, 78);
      ctx.lineTo(cx + 10, 100);
      ctx.stroke();
    }

    // Three-beat finger taps (siege nights)
    if (flags.rd_siege_night) {
      const beat = Math.floor(t / 8) % 3;
      const tapX = 70 + beat * 60;
      px(ctx, tapX, 52, 2, 10, "rgba(190,200,205,0.7)");
      px(ctx, tapX + 3, 50, 2, 12, "rgba(190,200,205,0.55)");
    }

    // Desk with FORESTOS laptop (amber glow) and shortwave radio
    px(ctx, 40, 128, 88, 8, "#3e2b1d");
    px(ctx, 52, 112, 40, 18, "#171d21");            // laptop body
    const flick = Math.sin(t * 0.6) > -0.85 ? 1 : 0.6;
    px(ctx, 54, 114, 36, 13, `rgba(229,142,60,${0.75 * flick})`); // amber screen
    px(ctx, 56, 116, 22, 1, "rgba(30,16,4,0.8)");
    px(ctx, 56, 119, 30, 1, "rgba(30,16,4,0.8)");
    px(ctx, 56, 122, 16, 1, "rgba(30,16,4,0.8)");
    // Radio with glowing dial
    px(ctx, 100, 118, 24, 12, "#1a2126");
    const dial = Math.sin(t * 0.2) > 0 ? "#ffcc66" : "#ff9933";
    px(ctx, 116, 121, 3, 3, dial);
    px(ctx, 122, 114, 1, 8, "#666"); // antenna
    // Candle on the sill
    px(ctx, 276, 120, 4, 8, "#d8c8a8");
    px(ctx, 277, 116 + (t % 6 < 3 ? 0 : 1), 2, 4, (t % 9 < 5) ? "#ffe680" : "#ffaa33");

    // Companions at the window
    const npcs = (window.__rdState && window.__rdState.party) || [];
    const cols = ["#7ab8d4", "#c8d47a", "#d4a07a"];
    npcs.slice(0, 3).forEach((n, idx) => {
      const alive = n.alive !== false;
      if (!alive) return;
      const x = 150 + idx * 34;
      this.drawPerson(ctx, x, 130, { head: "#d8b28c", body: cols[idx], leg: "#22201c", arm: "#d8b28c" }, 2, t + idx * 4);
    });
  },

  drawRidgeBridge(ctx, t) {
    // Ravine walls
    px(ctx, 0, 120, 60, 60, "#141c17");
    px(ctx, 260, 120, 60, 60, "#141c17");
    // Suspension cables
    ctx.strokeStyle = "#4a3a2a";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 40); ctx.quadraticCurveTo(160, 92, 320, 40);
    ctx.stroke();
    // Deck
    px(ctx, 0, 96, 320, 10, "#3a2f24");
    for (let x = 0; x < 320; x += 12) px(ctx, x, 106, 2, 6, "#241c14");
    // Vertical suspenders
    for (let x = 16; x < 320; x += 28) {
      const sag = 92 - Math.abs(160 - x) * 0.0;
      ctx.strokeStyle = "rgba(90,72,50,0.8)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x, 40 + Math.abs(160 - x) * 0.17);
      ctx.lineTo(x, 96);
      ctx.stroke();
    }
    // Abandoned truck, doors open, radio alive
    px(ctx, 190, 74, 36, 22, "#2c4438");
    px(ctx, 194, 78, 12, 9, "#0a0f12");
    px(ctx, 226, 78, 6, 14, "#22382e"); // open door
    const rn = (t % 24 < 12) ? "#ffcc66" : "#885522";
    px(ctx, 210, 82, 3, 2, rn); // dashboard radio glow
    // Wheels
    px(ctx, 194, 96, 6, 4, "#0c0f0c");
    px(ctx, 216, 96, 6, 4, "#0c0f0c");
    // Instant fog wall creeping from the left
    const fogX = (t * 0.8) % 400;
    ctx.fillStyle = "rgba(190,202,198,0.20)";
    ctx.fillRect(Math.max(0, 160 - fogX), 30, 160, 120);
  },

  drawRidgeMine(ctx, t) {
    px(ctx, 0, 0, 320, 180, "#07090b");
    // Limestone walls with teeth marks
    px(ctx, 20, 0, 30, 180, "#2a2b28");
    px(ctx, 270, 0, 30, 180, "#2a2b28");
    for (let y = 20; y < 160; y += 18) {
      px(ctx, 24, y, 20, 3, "#191a18");
      px(ctx, 274, y + 8, 20, 3, "#191a18");
    }
    // Generator + breaker
    px(ctx, 120, 90, 80, 60, "#23302f");
    px(ctx, 128, 100, 18, 14, "#10181a");
    const glow = (t % 30 < 15) ? "#7dff9a" : "#2f7d4a";
    px(ctx, 132, 104, 4, 4, glow);
    px(ctx, 160, 96, 8, 26, "#3c4a48"); // breaker handle
    px(ctx, 160, 96 + (t % 40 < 20 ? 0 : 8), 8, 10, "#8a9a96");
    // Elevator shaft mouth (right) — the voice comes from below
    px(ctx, 226, 40, 34, 140, "#020304");
    ctx.strokeStyle = "rgba(120,130,140,0.35)";
    ctx.strokeRect(226, 40, 34, 140);
    // Lantern light cone
    const flick = 0.5 + Math.sin(t * 0.35) * 0.15 + Math.sin(t * 1.7) * 0.05;
    const g = ctx.createRadialGradient(90, 70, 4, 90, 70, 90);
    g.addColorStop(0, `rgba(255,190,90,${0.30 * flick})`);
    g.addColorStop(1, "rgba(255,190,90,0)");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 320, 180);
    px(ctx, 86, 60, 6, 10, "#caa25c");
    px(ctx, 87, 56, 4, 4, "#ffe6a0");
    // Whisper puffs drifting from the shaft
    if (Math.floor(t / 20) % 3 === 0) {
      ctx.fillStyle = "rgba(180,190,200,0.10)";
      ctx.fillRect(200 - (t % 20) * 1.5, 120, 14, 4);
    }
  },

  drawRidgeCabinSite(ctx, t, sanity) {
    // Cabin 2 exterior with rotted skylight
    px(ctx, 60, 70, 200, 70, "#2c2118");
    // Roof
    ctx.fillStyle = "#1f1710";
    ctx.beginPath();
    ctx.moveTo(50, 74); ctx.lineTo(160, 44); ctx.lineTo(270, 74);
    ctx.closePath(); ctx.fill();
    // Skylight hole
    px(ctx, 140, 56, 40, 14, "#0a0d10");
    px(ctx, 140, 56, 40, 1, "#4a3a28");
    // The thing on the roof — elongated silhouette, scaling
    const bob = Math.sin(t * 0.12) * 2;
    const sc = 1 + Math.sin(t * 0.07) * 0.12; // breathing scale
    const ex = 152, ey = 40 + bob;
    px(ctx, ex, ey - 26 * sc, 6 * sc, 26 * sc, "#3a3f3c");   // torso
    px(ctx, ex + 1, ey - 32 * sc, 4 * sc, 6 * sc, "#565b57"); // head
    px(ctx, ex - 4, ey - 22 * sc, 3, 16 * sc, "#3a3f3c");     // arm
    px(ctx, ex + 7, ey - 22 * sc, 3, 16 * sc, "#3a3f3c");     // arm
    px(ctx, ex + 1, ey - 28 * sc, 4, 2, "#7a5c3a");           // Pendelton collar
    // Window glow inside
    const gl = (t % 40 < 20) ? "rgba(229,142,60,0.5)" : "rgba(229,142,60,0.25)";
    px(ctx, 90, 92, 22, 18, gl);
    px(ctx, 200, 92, 22, 18, gl);
    px(ctx, 148, 92, 22, 26, "rgba(229,142,60,0.35)");
  },

  drawRidgeRadar(ctx, t, flags) {
    px(ctx, 0, 0, 320, 180, "#04120a");
    if (flags.rd_radar_dead) {
      ctx.fillStyle = "#e58e3c";
      ctx.font = "8px monospace";
      ctx.textAlign = "center";
      ctx.fillText("OUT OF RANGE // SENSOR ARRAYS COMPROMISED", 160, 90);
      return;
    }
    ctx.strokeStyle = "rgba(60,220,120,0.18)";
    ctx.lineWidth = 0.5;
    for (let x = 0; x < 320; x += 12) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 180); ctx.stroke(); }
    for (let y = 0; y < 180; y += 12) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(320, y); ctx.stroke(); }
    // Density vectors drifting west→east
    for (let i = 0; i < 22; i++) {
      const vx = (i * 47 + t * 1.6) % 340 - 10;
      const vy = (i * 31) % 170 + 5;
      px(ctx, vx, vy, 3, 1, "rgba(90,240,150,0.55)");
    }
    // The void anomaly — sitting dead center, moving against the wind
    const ax = 160 + Math.sin(t * 0.03) * 18;
    const pulse = 10 + Math.sin(t * 0.1) * 3;
    const grad = ctx.createRadialGradient(ax, 90, 2, ax, 90, pulse + 8);
    grad.addColorStop(0, "rgba(255,60,60,0.7)");
    grad.addColorStop(0.6, "rgba(160,20,20,0.35)");
    grad.addColorStop(1, "rgba(120,10,10,0)");
    ctx.fillStyle = grad;
    ctx.beginPath(); ctx.arc(ax, 90, pulse + 8, 0, Math.PI * 2); ctx.fill();
    px(ctx, ax - 1, 89, 2, 2, "#ffcccc");
  },

  drawRidgeEntity(ctx, t, sanity) {
    // Silhouette scaling against the fog layer
    const sc = 1.6 + Math.sin(t * 0.05) * 0.35 + (60 - Math.min(60, sanity)) * 0.008;
    const cx = 210 + Math.sin(t * 0.02) * 10;
    const baseY = 150;
    px(ctx, cx, baseY - 70 * sc, 10 * sc, 70 * sc, "#23282a");    // elongated torso
    px(ctx, cx + 1.5 * sc, baseY - 82 * sc, 7 * sc, 12 * sc, "#3c4240"); // wet-ash head
    px(ctx, cx - 6 * sc, baseY - 60 * sc, 4 * sc, 46 * sc, "#23282a");   // arms
    px(ctx, cx + 12 * sc, baseY - 60 * sc, 4 * sc, 46 * sc, "#23282a");
    // No eyes — just a seam
    px(ctx, cx + 3 * sc, baseY - 77 * sc, 4 * sc, 1, "#0d1112");
    // Hand-scratching particles on the glass panel (right edge, three-beat)
    const beat = Math.floor(t / 7) % 4;
    for (let i = 0; i < beat + 1; i++) {
      const sx = 300 - i * 4 - ((t * 3) % 3);
      const sy = 30 + i * 9 + Math.sin(t * 0.4 + i) * 2;
      px(ctx, sx, sy, 1, 6, "rgba(235,245,250,0.75)");
      if (i % 2 === 0) px(ctx, sx + 1, sy + 5, 2, 1, "rgba(235,245,250,0.4)");
    }
  },

  /* Location-aware viewport: each overworld node gets its own pixel
     composition — the center screen TRAVELS with the player. */
  drawRidgeLoc(ctx, state, t, night) {
    const p = state.player || {};
    const scene = (state.scene || "").toLowerCase();
    const fogD = 0.25 + Math.min(0.5, ((p.humanity || 0) / 200));

    this.drawRidgePines(ctx, night, t, 0.8, 118);

    if (scene.includes("t1") || scene.includes("tower1")) {
      // Decommissioned Tower 1 — dark, service light dead after day 10
      px(ctx, 130, 52, 6, 66, "#141a1d");
      px(ctx, 118, 44, 30, 9, "#1d2429");
      px(ctx, 122, 36, 22, 8, "#232b30");
      const lit = (state.world.day || 1) < 10 && (t % 50 < 25);
      px(ctx, 126, 38, 14, 3, lit ? "#ffb45e" : "#0a0d10");
      px(ctx, 131, 20, 1, 16, "#333"); // dead antenna
      // Path from the south, boot prints heading IN, none heading out
      for (let fy = 150; fy > 122; fy -= 9) px(ctx, 158 + Math.sin(fy) * 3, fy, 3, 4, night ? "#0c1114" : "#2a2620");
    } else if (scene.includes("ravine")) {
      // The Northern Ravine — 300ft drop, fog pouring like water
      px(ctx, 0, 110, 120, 70, night ? "#070a0c" : "#161d1a");
      px(ctx, 200, 110, 120, 70, night ? "#070a0c" : "#161d1a");
      for (let i = 0; i < 4; i++) {
        const fy = 116 + i * 15;
        const off = ((t * (0.5 + i * 0.2)) % 260) - 40;
        ctx.fillStyle = `rgba(185,200,196,${0.16 - i * 0.03})`;
        ctx.fillRect(off, fy, 140, 8);
        ctx.fillRect(320 - off - 60, fy + 6, 110, 6);
      }
      // Far suspension cable of the Copperhead Bridge
      ctx.strokeStyle = "rgba(80,64,44,0.7)";
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(110, 60); ctx.quadraticCurveTo(160, 78, 210, 60); ctx.stroke();
    } else if (scene.includes("ruins")) {
      // Ranger Station Ruins — charred foundation, cellar light
      px(ctx, 70, 106, 180, 12, "#191410");
      px(ctx, 78, 96, 14, 10, "#241c15"); px(ctx, 226, 96, 14, 10, "#241c15");
      px(ctx, 150, 100, 26, 8, "#100c09"); // cellar mouth
      const flick = (t % 37 < 18) ? "rgba(229,142,60,0.55)" : "rgba(229,142,60,0.18)";
      px(ctx, 153, 103, 20, 4, flick); // something reading below
      // Charred beams
      px(ctx, 90, 70, 3, 40, "#0d0b09");
      px(ctx, 210, 62, 3, 48, "#0d0b09");
      px(ctx, 90, 70, 123, 3, "#0d0b09");
    } else if (scene.includes("railcar")) {
      // Overturned Railcar — tilted carriage on the ravine floor
      ctx.save();
      ctx.translate(160, 118); ctx.rotate(0.12);
      px(ctx, -70, -26, 140, 30, night ? "#13191c" : "#2c343a");
      for (let wx = -60; wx < 60; wx += 24) px(ctx, wx, -20, 12, 10, "#0a0e10");
      px(ctx, -80, -6, 14, 26, "#0f1417"); px(ctx, 66, -6, 14, 26, "#0f1417");
      ctx.restore();
      // Black ice sheen
      if (t % 90 < 30) { ctx.fillStyle = "rgba(190,220,235,0.12)"; ctx.fillRect(80, 140, 160, 3); }
      // Lockbox glint
      px(ctx, 196, 132, 5, 4, (t % 40 < 20) ? "#c8a24a" : "#6a5222");
    } else if (scene.includes("sinkhole")) {
      // Limestone Sinkhole — breathing pit
      const g = ctx.createRadialGradient(160, 140, 4, 160, 140, 66);
      g.addColorStop(0, "#000"); g.addColorStop(0.7, night ? "#05080a" : "#101614"); g.addColorStop(1, "rgba(16,22,20,0)");
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.ellipse(160, 140, 66, 26, 0, 0, Math.PI * 2); ctx.fill();
      // Mist rising in breaths
      const breathe = Math.sin(t * 0.06) * 0.5 + 0.5;
      ctx.fillStyle = `rgba(190,205,200,${0.05 + breathe * 0.10})`;
      ctx.fillRect(120, 128 - breathe * 20, 80, 20 + breathe * 20);
      // Flare gun glint on the rim
      px(ctx, 228, 128, 6, 2, (t % 60 < 30) ? "#d44" : "#611");
    } else if (scene.includes("clearing")) {
      // The impossible clearing — pines stepped back in a perfect arc
      px(ctx, 0, 118, 320, 62, night ? "#0a0f0c" : "#18221b");
      // Stump ring
      for (let a = 0; a < 8; a++) {
        const ax = 160 + Math.cos(a * 0.785) * 74;
        const ay = 140 + Math.sin(a * 0.785) * 20;
        px(ctx, ax - 3, ay - 4, 6, 6, "#241c12");
        px(ctx, ax - 3, ay - 5, 6, 1, "#3a2c1c");
      }
      // Jar glint at center (Ash's beetle)
      px(ctx, 157, 132, 6, 8, "rgba(180,200,190,0.35)");
      px(ctx, 159, 134, 2, 2, (t % 30 < 15) ? "#e8c46a" : "#4a3a1a");
      // The tree line leaning in, listening
      ctx.strokeStyle = "rgba(10,16,12,0.9)"; ctx.lineWidth = 3;
      for (let tx = 8; tx < 320; tx += 26) {
        const lean = Math.sin(t * 0.03 + tx) * 2 + 3;
        ctx.beginPath(); ctx.moveTo(tx, 118); ctx.lineTo(tx + lean, 88); ctx.stroke();
      }
    }

    // Fog layer scales with awareness (threat) — the world closes in
    for (let i = 0; i < 3; i++) {
      const fy = 96 + i * 22;
      const drift = ((t * (0.3 + i * 0.15)) % 400) - 60;
      ctx.fillStyle = `rgba(186,200,196,${fogD * 0.16})`;
      ctx.fillRect(drift, fy, 180, 12);
      ctx.fillRect((340 - drift) % 380 - 30, fy + 8, 130, 9);
    }
  },

  drawRidgeWalker(ctx, t, sanity) {
    // Something at the treeline that is not a tree
    const lean = Math.sin(t * 0.03) * 3;
    const sc = 1.8 + Math.sin(t * 0.06) * 0.2;
    const x = 232 + lean;
    px(ctx, x, 150 - 62 * sc, 7 * sc, 62 * sc, "#0c1110");
    px(ctx, x + 1, 150 - 72 * sc, 5 * sc, 10 * sc, "#141a18");
    // Asymmetric stride when it steps
    if (Math.floor(t / 30) % 2 === 0) {
      px(ctx, x - 3, 150 - 6, 3, 6, "#0c1110");
    }
  },

  drawTower3(ctx, t) {
    // Distant southern tower — green morse: H·E·L·P
    px(ctx, 150, 60, 4, 60, "#1a1f22");
    px(ctx, 140, 52, 24, 8, "#232a2e");
    px(ctx, 144, 46, 16, 6, "#2c343a");
    // Morse: three rhythmic bursts repeating H-E-L-P rhythm
    const morseOn = (t % 64) < 8 || (t % 64) >= 16 && (t % 64) < 24 || (t % 64) >= 32 && (t % 64) < 40 || (t % 64) >= 48 && (t % 64) < 56;
    const c = morseOn ? "#4dff88" : "#0d3a1e";
    px(ctx, 146, 48, 6, 3, c);
    if (morseOn) {
      ctx.fillStyle = "rgba(80,255,140,0.10)";
      ctx.beginPath(); ctx.arc(149, 49, 14, 0, Math.PI * 2); ctx.fill();
    }
  },

  drawRidgeEnding(ctx, t, victory) {
    if (victory) {
      // Dawn breaking over the ridge
      const grad = ctx.createLinearGradient(0, 0, 0, 120);
      const k = Math.min(1, (t % 200) / 200);
      grad.addColorStop(0, `rgba(255,190,110,${0.25 + k * 0.3})`);
      grad.addColorStop(1, "rgba(120,90,60,0)");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 320, 120);
      px(ctx, 40, 26, 14, 14, "#ffe8b0");
    } else {
      // Glass shattering inward + fog pouring in
      for (let i = 0; i < 26; i++) {
        const sx = (i * 53 + t * 2) % 320;
        const sy = (i * 29 + t * 3) % 180;
        px(ctx, sx, sy, 2, 2, "rgba(220,235,245,0.5)");
      }
      ctx.fillStyle = `rgba(195,208,205,${0.15 + Math.sin(t * 0.05) * 0.05})`;
      ctx.fillRect(0, 60, 320, 120);
      // The long gray arm
      const reach = Math.min(90, (t % 120) * 0.9);
      px(ctx, 320 - reach, 120, reach, 5, "#5a615e");
      for (let f = 0; f < 4; f++) {
        px(ctx, 320 - reach + f * 3, 116 - f * 2, 2, 6, "#5a615e");
      }
    }
  },
};

// Expose on window — ui.js/game.js gate on `window.Scene` (const is not auto-on-window).
window.Scene = Scene;
