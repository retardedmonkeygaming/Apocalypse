/* Procedural pixel scenes. 320x180, nearest-neighbor scaled. */
const PAL = {
  base: { sky: ["#1a2430", "#0d1014"], ground: "#2a2318", accent: "#6b4a2a", lit: "#c47a3a" },
  streets: { sky: ["#2a3040", "#12151c"], ground: "#3a3a3a", accent: "#4a5560", lit: "#6ec8ff" },
  mall: { sky: ["#2a1828", "#100810"], ground: "#2a2430", accent: "#804060", lit: "#ff79b0" },
  hospital: { sky: ["#1c2824", "#0c1210"], ground: "#243028", accent: "#8aa28a", lit: "#9dffb0" },
  radio: { sky: ["#102030", "#050810"], ground: "#1a2030", accent: "#3a5068", lit: "#6ec8ff" },
  warehouse: { sky: ["#241810", "#0c0806"], ground: "#3a2a1a", accent: "#8a4a2a", lit: "#e07a3a" },
  church: { sky: ["#1a1428", "#080610"], ground: "#2a2430", accent: "#5a4068", lit: "#d4b5ff" },
  subway: { sky: ["#080a10", "#020308"], ground: "#1a1c24", accent: "#3a4860", lit: "#a0b4c8" },
  checkpoint: { sky: ["#203018", "#0c140a"], ground: "#3a4030", accent: "#5a6840", lit: "#c8d48a" },
  school: { sky: ["#283040", "#10141c"], ground: "#3a3428", accent: "#d4c48a", lit: "#ffe08a" },
  docks: { sky: ["#102028", "#061018"], ground: "#1a2830", accent: "#2a5060", lit: "#6ad0c8" },
  gas: { sky: ["#201810", "#0c0804"], ground: "#2a2418", accent: "#c45a2a", lit: "#ffb030" },
  ending: { sky: ["#100808", "#000000"], ground: "#1a1010", accent: "#4a2020", lit: "#ff3b4e" },
};

const SCENE_MAP = {
  HomeBase: "base",
  "Home Base": "base",
  base: "base",
  Streets: "streets",
  streets: "streets",
  horde: "streets",
  survivor: "streets",
  "Abandoned Mall": "mall",
  mall: "mall",
  runner: "mall",
  Hospital: "hospital",
  hospital: "hospital",
  lena: "hospital",
  fever: "hospital",
  "Radio Tower": "radio",
  radio: "radio",
  marcus: "radio",
  Warehouse: "warehouse",
  warehouse: "warehouse",
  butcher: "warehouse",
  Church: "church",
  church: "church",
  miriam: "church",
  "Subway Tunnels": "subway",
  subway: "subway",
  ghost: "subway",
  "Military Checkpoint": "checkpoint",
  checkpoint: "checkpoint",
  armored: "checkpoint",
  School: "school",
  school: "school",
  kid: "school",
  Docks: "docks",
  docks: "docks",
  "Gas Station": "gas",
  gas: "gas",
  bloater: "gas",
  craft: "base",
  talk: "base",
  quiet: "base",
  combat: "streets",
  shambler: "streets",
  map: "streets",
  base_night: "base",
  rain: "streets",
  fog: "streets",
  storm: "base",
  tower: "streets",
};

function palFor(scene, loc) {
  const id = (scene || "").toLowerCase();
  if (PAL[id]) return PAL[id];
  const key = (SCENE_MAP[scene] || SCENE_MAP[loc] || "").toLowerCase();
  return PAL[key] || PAL.streets;
}

function px(ctx, x, y, w, h, c) {
  ctx.fillStyle = c;
  ctx.fillRect(x | 0, y | 0, w | 0, h | 0);
}

function ditherSky(ctx, c0, c1, night) {
  const g = ctx.createLinearGradient(0, 0, 0, 110);
  g.addColorStop(0, night ? "#04060a" : c0);
  g.addColorStop(1, c1);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 320, 180);
  ctx.fillStyle = night ? "rgba(0,0,0,0.25)" : "rgba(255,255,255,0.03)";
  for (let y = 0; y < 110; y += 2) ctx.fillRect(0, y, 320, 1);
}

function person(ctx, x, y, cols, scale) {
  const s = scale || 2;
  px(ctx, x + s, y, s * 2, s * 2, cols.head);
  px(ctx, x, y + s * 2, s * 4, s * 3, cols.body);
  px(ctx, x, y + s * 5, s, s * 3, cols.leg);
  px(ctx, x + s * 3, y + s * 5, s, s * 3, cols.leg);
  px(ctx, x - s, y + s * 3, s, s * 2, cols.arm);
  px(ctx, x + s * 4, y + s * 3, s, s * 2, cols.arm);
}

function zombie(ctx, x, y, kind) {
  const tints = {
    shambler: { head: "#8aaa70", body: "#4a5a38", leg: "#3a4a30", arm: "#6a7a50" },
    runner: { head: "#c8d890", body: "#5a3028", leg: "#3a2018", arm: "#8a5040" },
    bloater: { head: "#6a8050", body: "#3a6028", leg: "#2a4018", arm: "#508038" },
    armored: { head: "#90a090", body: "#3a4438", leg: "#2a3028", arm: "#6a7060" },
  };
  const c = tints[kind] || tints.shambler;
  const sc = kind === "bloater" ? 3 : 2;
  person(ctx, x, y, c, sc);
  if (kind === "armored") px(ctx, x, y - 2, 8, 3, "#555");
}

function drawWeather(ctx, weather, t) {
  if (weather === "rain" || weather === "storm") {
    ctx.fillStyle = "rgba(180,200,255,0.45)";
    const n = weather === "storm" ? 70 : 40;
    for (let i = 0; i < n; i++) {
      const x = (i * 47 + t * 8) % 320;
      const y = (i * 31 + t * 14) % 180;
      ctx.fillRect(x, y, 1, 6);
    }
  }
  if (weather === "fog") {
    ctx.fillStyle = "rgba(180,190,180,0.18)";
    ctx.fillRect(0, 80, 320, 100);
    ctx.fillStyle = "rgba(200,210,200,0.12)";
    ctx.fillRect(0, 100, 320, 50);
  }
  if (weather === "storm") {
    if ((t % 80) < 2) {
      ctx.fillStyle = "rgba(220,230,255,0.35)";
      ctx.fillRect(0, 0, 320, 180);
    }
  }
}

function silhouetteBuildings(ctx, pal, variant) {
  const baseY = 108;
  px(ctx, 0, baseY, 320, 72, pal.ground);
  px(ctx, 0, baseY, 320, 3, "#111");
  const heights = variant || [40, 28, 55, 22, 48, 33, 60, 26];
  let x = 0;
  heights.forEach((h, i) => {
    const w = 40;
    px(ctx, x, baseY - h, w - 2, h, i % 2 ? pal.accent : "#1a1e18");
    for (let wy = baseY - h + 6; wy < baseY - 8; wy += 8) {
      for (let wx = x + 4; wx < x + w - 6; wx += 8) {
        px(
          ctx,
          wx,
          wy,
          3,
          3,
          ((wx * 13 + wy * 7) % 5 === 0) ? pal.lit : "#0a0a08"
        );
      }
    }
    x += w;
  });
}

function drawBase(ctx, pal, fort, night, partyN) {
  ditherSky(ctx, pal.sky[0], pal.sky[1], night);
  silhouetteBuildings(ctx, pal, [24, 18, 30, 16, 22, 28, 20, 18]);
  px(ctx, 90, 70, 140, 70, "#2a2218");
  px(ctx, 96, 76, 40, 28, night ? "#3a2a10" : "#6a5030");
  px(ctx, 150, 90, 22, 50, "#1a140e");
  px(ctx, 188, 80, 34, 22, pal.lit);
  for (let i = 0; i < Math.min(10, fort); i++) {
    px(ctx, 84 + i * 14, 128, 12, 8, "#5a4030");
    px(ctx, 86 + i * 14, 122, 8, 6, "#3a2818");
  }
  person(
    ctx,
    118,
    118,
    { head: "#e8c8a0", body: "#3a5a48", leg: "#2a3028", arm: "#e8c8a0" },
    2
  );
  const extras = [
    { head: "#d0b090", body: "#3a6a88", leg: "#243038", arm: "#d0b090" },
    { head: "#c8e0c0", body: "#2a4a38", leg: "#1a3028", arm: "#c8e0c0" },
    { head: "#f0d080", body: "#5a4a28", leg: "#3a3020", arm: "#f0d080" },
    { head: "#d4b5ff", body: "#3a2850", leg: "#201830", arm: "#d4b5ff" },
  ];
  for (let i = 0; i < Math.min(4, partyN); i++) {
    person(ctx, 150 + i * 22, 122, extras[i], 2);
  }
}

function drawGeneric(ctx, pal, night, locName) {
  ditherSky(ctx, pal.sky[0], pal.sky[1], night);
  silhouetteBuildings(ctx, pal);
  person(
    ctx,
    70,
    120,
    { head: "#e8c8a0", body: "#3a5a48", leg: "#2a3028", arm: "#e8c8a0" },
    2
  );
  px(ctx, 8, 8, 4, 4, pal.lit);
}

const NPC_BODIES = {
  lena: { head: "#d8e8d0", body: "#8aa28a", leg: "#445", arm: "#d8e8d0" },
  marcus: { head: "#c09060", body: "#2a3a50", leg: "#1a2430", arm: "#c09060" },
  kid: { head: "#f0d080", body: "#5a4a28", leg: "#3a3020", arm: "#f0d080" },
  miriam: { head: "#e8d8c8", body: "#3a2850", leg: "#201830", arm: "#e8d8c8" },
  ghost: { head: "#a0b4c8", body: "#2a3038", leg: "#1a2028", arm: "#a0b4c8" },
  butcher: { head: "#e0b090", body: "#6a2020", leg: "#3a1010", arm: "#e0b090" },
  survivor: { head: "#d0b090", body: "#4a5a68", leg: "#2a3038", arm: "#d0b090" },
};

const Scene = {
  t: 0,
  last: null,
  init() {
    this.canvas = document.getElementById("view");
    this.ctx = this.canvas.getContext("2d");
    this.ctx.imageSmoothingEnabled = false;
  },
  render(state) {
    if (!this.ctx) this.init();
    const ctx = this.ctx;
    this.t += 1;
    const night = !!(state.world && state.world.is_night);
    const scene = (state.scene || "streets").toLowerCase();
    const loc = (state.world && state.world.location) || "";
    const pal = palFor(scene, loc);
    const weather = (state.world && state.world.weather) || "clear";
    const partyN = (state.party || []).length;
    const fort = (state.world && state.world.fortification) || 0;

    const isBase = scene === "base" || scene === "craft" || scene === "talk" || scene === "quiet";
    const isHomeLoc = loc.toLowerCase() === "home base";
    if (isBase || (isHomeLoc && (state.mode === "hub" || state.mode === "menu"))) {
      drawBase(ctx, pal, fort, night, partyN);
    } else {
      drawGeneric(ctx, pal, night, loc);
      const combatKinds = ["shambler", "runner", "bloater", "armored", "horde"];
      if (combatKinds.includes(scene) || state.mode === "combat") {
        const kind =
          ["runner", "bloater", "armored", "shambler"].includes(scene)
            ? scene
            : "shambler";
        zombie(ctx, 200, 118, kind);
        if (scene === "horde") {
          zombie(ctx, 230, 122, "shambler");
          zombie(ctx, 250, 116, "runner");
        }
      }
      if (
        ["lena", "marcus", "kid", "miriam", "ghost", "butcher", "survivor"].includes(
          scene
        )
      ) {
        const body = NPC_BODIES[scene];
        if (body) person(ctx, 210, 118, body, scene === "kid" ? 1 : 2);
      }
    }
    drawWeather(ctx, weather, this.t);
    if (
      state.infection_stage === "turning" || state.infection_stage === "lucid"
    ) {
      ctx.fillStyle = "rgba(80,180,40,0.08)";
      ctx.fillRect(0, 0, 320, 180);
    }
    if (night) px(ctx, 260, 18, 8, 8, "#d0d8e8");
    else px(ctx, 40, 16, 10, 10, "#e8d48a");
  },
};
