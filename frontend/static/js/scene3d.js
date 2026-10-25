/* ==========================================================================
   APOCALYPSE TERMINAL — 3D Scene Engine (Three.js, vendored offline)
   Realistic fire-lookout tower + Appalachian forest, driven by the SAME
   state that runs the 2D pixel engine: companions, Sanity, Awareness,
   weather, day/night, story scenes and locations.

   Quality tiers
     HIGH — denser forest, weather particles, fog sprites, more lights
     LOW  — light enough for Raspberry Pi 4 (pixelRatio 1, fewer instances,
            no particles, cheaper lights) — see README section "3D MODE"
   ========================================================================== */

const Scene3D = (() => {
  let _renderer = null, _canvas = null, _scene = null, _camera = null;
  let _clock = 0, _raf = 0;
  let _quality = localStorage.getItem("apoc3d_quality") || "auto";
  let _tier = "high";              // resolved tier
  let _active = false;             // 3D currently rendering
  let _enabled = localStorage.getItem("apoc3d") !== "off";
  let _state = null;
  let _set = null;                 // current location set name
  let _built = {};                 // lazily-built groups
  let _figs = [], _walker = null, _lieFig = null, _bigFig = null;
  let _candle = null, _sun = null, _hemi = null, _sky = null;
  let _tower3Light = null, _rain = null, _swayGroups = [];
  let _mats = {};

  // ───────────────────────── quality ─────────────────────────
  function _resolveTier() {
    if (_quality === "high") return "high";
    if (_quality === "low") return "low";
    // auto: weak devices get LOW
    const cores = navigator.hardwareConcurrency || 4;
    const dpr = window.devicePixelRatio || 1;
    const mobile = /Mobi|Android/i.test(navigator.userAgent);
    return (cores <= 4 || mobile || dpr >= 2.5) ? "low" : "high";
  }

  function cycleQuality() {
    const order = ["auto", "high", "low", "off"];
    let i = order.indexOf(_quality);
    _quality = order[(i + 1) % order.length];
    if (_quality === "off") {
      localStorage.setItem("apoc3d", "off");
      _enabled = false;
      _active = false;
      _applyVisibility();           // hide WebGL canvas, restore the 2D pixel view
    } else {
      localStorage.setItem("apoc3d", "on"); _enabled = true; localStorage.setItem("apoc3d_quality", _quality);
      _tier = _resolveTier(); _rebuild();
      _applyVisibility();
    }
    return label();
  }

  function label() {
    if (!_enabled || _quality === "off") return "3D: OFF";
    return `3D: ${(_quality === "auto" ? _tier : _quality).toUpperCase()}`;
  }

  function supported() {
    try {
      const c = document.createElement("canvas");
      return !!(window.WebGLRenderingContext && (c.getContext("webgl2") || c.getContext("webgl")));
    } catch (e) { return false; }
  }

  // ───────────────────────── textures ─────────────────────────
  function _tex(draw, w = 128, h = 128) {
    const c = document.createElement("canvas");
    c.width = w; c.height = h;
    draw(c.getContext("2d"), w, h);
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    return t;
  }

  function _makeMaterials() {
    const wet = (base, dark, lines) => _tex((g, w, h) => {
      g.fillStyle = base; g.fillRect(0, 0, w, h);
      for (let i = 0; i < w; i += 4) {
        g.fillStyle = Math.random() < 0.5 ? dark : "rgba(0,0,0,0.12)";
        g.fillRect(i, 0, 2, h);
      }
      if (lines) { g.strokeStyle = "rgba(0,0,0,0.35)"; for (let y = 0; y < h; y += 26) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); } }
      // wet sheen speckle
      for (let i = 0; i < 90; i++) { g.fillStyle = "rgba(255,255,255,0.05)"; g.fillRect(Math.random() * w, Math.random() * h, 2, 1); }
    });

    const woodTex = wet("#4a3826", "#33261a", true);
    const darkWood = wet("#2c2118", "#1c1510", true);
    const metalTex = _tex((g, w, h) => {
      g.fillStyle = "#5b6165"; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 400; i++) { g.fillStyle = Math.random() < 0.3 ? "rgba(120,70,40,0.35)" : "rgba(255,255,255,0.06)"; g.fillRect(Math.random() * w, Math.random() * h, 3, 2); }
      // rust drips
      for (let x = 0; x < w; x += 17) { g.fillStyle = "rgba(110,60,30,0.3)"; g.fillRect(x, 0, 2, Math.random() * h); }
    });
    const barkTex = _tex((g, w, h) => {
      g.fillStyle = "#241a12"; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 60; i++) { g.fillStyle = Math.random() < 0.5 ? "#171009" : "#31241a"; g.fillRect(Math.random() * w, 0, 2 + Math.random() * 3, h); }
    });
    const needleTex = _tex((g, w, h) => {
      g.fillStyle = "#152a1d"; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 500; i++) { g.fillStyle = Math.random() < 0.5 ? "#1d3a26" : "#0e1f15"; g.fillRect(Math.random() * w, Math.random() * h, 3, 3); }
    }, 64, 64);
    const groundTex = _tex((g, w, h) => {
      g.fillStyle = "#1a1712"; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 700; i++) { g.fillStyle = Math.random() < 0.5 ? "#221d16" : "#141109"; g.fillRect(Math.random() * w, Math.random() * h, 4, 4); }
      for (let i = 0; i < 40; i++) { g.fillStyle = "rgba(30,50,34,0.6)"; g.fillRect(Math.random() * w, Math.random() * h, 6, 3); }
    });

    _mats = {
      wood: new THREE.MeshStandardMaterial({ map: woodTex, roughness: 0.72, metalness: 0.04 }),
      darkWood: new THREE.MeshStandardMaterial({ map: darkWood, roughness: 0.8, metalness: 0.02 }),
      metal: new THREE.MeshStandardMaterial({ map: metalTex, roughness: 0.5, metalness: 0.65 }),
      glass: new THREE.MeshStandardMaterial({ color: 0x9fb4bd, roughness: 0.08, metalness: 0.2, transparent: true, opacity: 0.13 }),
      bark: new THREE.MeshStandardMaterial({ map: barkTex, roughness: 0.95 }),
      needle: new THREE.MeshStandardMaterial({ map: needleTex, roughness: 0.92, color: 0x9fb28f }),
      ground: new THREE.MeshStandardMaterial({ map: groundTex, roughness: 0.98 }),
      silhouette: new THREE.MeshStandardMaterial({ color: 0x0a0d0c, roughness: 1 }),
      rock: new THREE.MeshStandardMaterial({ color: 0x39413f, roughness: 0.95 }),
      snow: new THREE.MeshStandardMaterial({ color: 0xcfdae0, roughness: 0.85 }),
      amber: new THREE.MeshStandardMaterial({ color: 0x2a1e10, emissive: 0xe58e3c, emissiveIntensity: 1.4 }),
      greenLed: new THREE.MeshStandardMaterial({ color: 0x081408, emissive: 0x22ff66, emissiveIntensity: 0 }),
    };
  }

  // ───────────────────────── renderer ─────────────────────────
  function _init() {
    if (_renderer || !supported() || !_enabled) return;
    _canvas = document.getElementById("view3d");
    if (!_canvas) return;
    _tier = _resolveTier();
    try {
      _renderer = new THREE.WebGLRenderer({
        canvas: _canvas, antialias: _tier === "high",
        powerPreference: _tier === "high" ? "high-performance" : "low-power",
      });
    } catch (e) { _renderer = null; return; }
    _renderer.setPixelRatio(_tier === "high" ? Math.min(window.devicePixelRatio || 1, 1.5) : 1);
    _scene = new THREE.Scene();
    _scene.fog = new THREE.FogExp2(0x0b1216, 0.045);
    _camera = new THREE.PerspectiveCamera(62, 16 / 9, 0.1, 400);
    _camera.position.set(0, 1.6, 0);
    _makeMaterials();
    _lights();
    _resize();
    window.addEventListener("resize", _resize);
    _active = true;
    _applyVisibility();
    _setLocation("cabin");
    _loop();
  }

  function _applyVisibility() {
    const wrap = document.querySelector(".canvas-wrapper");
    if (!wrap || !_canvas) return;
    const on = _enabled && !!_renderer;
    _canvas.style.display = on ? "block" : "none";
    wrap.classList.toggle("threed", on);
    const old = document.getElementById("view");
    if (old) old.style.display = on ? "none" : "block";
    const btn = document.getElementById("btn-3d");
    if (btn) btn.textContent = label();
  }

  function _rebuild() {
    if (!_enabled) { if (_renderer) { _active = false; } _applyVisibility(); return; }
    if (!_renderer) { _init(); return; }
    _tier = _resolveTier();
    // tear down location groups; they rebuild at the new tier
    Object.values(_built).forEach((g) => _scene.remove(g));
    _built = {}; _figs = []; _walker = null; _lieFig = null; _bigFig = null;
    _candle = null; _sun = null; _hemi = null; _tower3Light = null; _rain = null; _swayGroups = [];
    _scene.children.slice().forEach((c) => { if (c.isLight || c.isSprite) _scene.remove(c); });
    _scene.background = null;
    _lights();
    _renderer.setPixelRatio(_tier === "high" ? Math.min(window.devicePixelRatio || 1, 1.5) : 1);
    _applyVisibility();
    _setLocation(_set || "cabin");
  }

  function _resize() {
    if (!_renderer) return;
    const wrap = document.querySelector(".canvas-wrapper");
    if (!wrap) return;
    const w = wrap.clientWidth || 640, h = wrap.clientHeight || 360;
    _renderer.setSize(w, h, false);
    _camera.aspect = w / h;
    _camera.updateProjectionMatrix();
  }

  function _lights() {
    _hemi = new THREE.HemisphereLight(0x6a7f8f, 0x181410, 0.55);
    _scene.add(_hemi);
    _sun = new THREE.DirectionalLight(0xbfd2e2, 0.6);
    _sun.position.set(-30, 40, -20);
    _scene.add(_sun);
    _candle = new THREE.PointLight(0xffb055, 0.0, 14, 2);
    _candle.position.set(-1.2, 1.1, -1.6);
    _scene.add(_candle);
  }

  // ───────────────────────── geometry helpers ─────────────────────────
  function _box(w, h, d, mat, x, y, z, parent) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
    m.position.set(x, y, z);
    (parent || _scene).add(m);
    return m;
  }

  function _figure(colorBody, height = 1.0) {
    // Slim humanoid: legs, torso, head, arms — reads as a person at distance
    const g = new THREE.Group();
    const mat = new THREE.MeshStandardMaterial({ color: colorBody, roughness: 1 });
    const legG = new THREE.CylinderGeometry(0.06 * height, 0.05 * height, 0.45 * height, 5);
    const l1 = new THREE.Mesh(legG, mat); l1.position.set(-0.09 * height, 0.22 * height, 0); g.add(l1);
    const l2 = l1.clone(); l2.position.x = 0.09 * height; g.add(l2);
    const torso = new THREE.Mesh(new THREE.CylinderGeometry(0.16 * height, 0.13 * height, 0.5 * height, 6), mat);
    torso.position.y = 0.68 * height; g.add(torso);
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.11 * height, 7, 6), mat);
    head.position.y = 1.0 * height; g.add(head);
    const armG = new THREE.CylinderGeometry(0.045 * height, 0.04 * height, 0.46 * height, 5);
    const a1 = new THREE.Mesh(armG, mat); a1.position.set(-0.2 * height, 0.66 * height, 0); a1.rotation.z = 0.14; g.add(a1);
    const a2 = a1.clone(); a2.position.x = 0.2 * height; a2.rotation.z = -0.14; g.add(a2);
    return g;
  }

  function _pine(x, z, scale, parent) {
    const g = new THREE.Group();
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.11 * scale, 0.17 * scale, 1.6 * scale, 5), _mats.bark);
    trunk.position.y = 0.8 * scale;
    g.add(trunk);
    const tiers = _tier === "high" ? 3 : 2;
    for (let i = 0; i < tiers; i++) {
      const r = (1.05 - i * 0.24) * scale;
      const cone = new THREE.Mesh(new THREE.ConeGeometry(r, 1.5 * scale, 7), _mats.needle);
      cone.position.y = (1.6 + i * 0.95) * scale;
      g.add(cone);
    }
    g.position.set(x, 0, z);
    (parent || _scene).add(g);
    return g;
  }

  // ───────────────────────── location sets ─────────────────────────
  function _buildCabinInterior() {
    const g = new THREE.Group();
    // floor & ceiling
    _box(6, 0.15, 6, _mats.wood, 0, -0.07, 0, g);
    _box(6, 0.15, 6, _mats.darkWood, 0, 3.0, 0, g);
    // walls built around a big window opening (3.4 wide x 1.5 tall at eye level)
    const wallH = 3.0, winY0 = 1.0, winY1 = 2.5, winW = 3.6;
    const mkWall = (rotY, len) => {
      const wg = new THREE.Group();
      const sideW = (len - winW) / 2;
      _box(sideW, wallH, 0.14, _mats.darkWood, -(winW / 2 + sideW / 2), wallH / 2, 0, wg);
      _box(sideW, wallH, 0.14, _mats.darkWood, (winW / 2 + sideW / 2), wallH / 2, 0, wg);
      _box(winW, winY0, 0.14, _mats.darkWood, 0, winY0 / 2, 0, wg);            // sill wall
      _box(winW, wallH - winY1, 0.14, _mats.darkWood, 0, winY1 + (wallH - winY1) / 2, 0, wg); // lintel
      // mullions
      _box(0.07, winY1 - winY0, 0.07, _mats.wood, 0, (winY0 + winY1) / 2, 0, wg);
      _box(winW, 0.07, 0.07, _mats.wood, 0, (winY0 + winY1) / 2, 0, wg);
      // glass
      const glass = new THREE.Mesh(new THREE.PlaneGeometry(winW, winY1 - winY0), _mats.glass);
      glass.position.y = (winY0 + winY1) / 2;
      glass.receiveShadow = false;
      wg.add(glass);
      wg.rotation.y = rotY;
      g.add(wg);
    };
    mkWall(0, 6);           // north (main view)
    mkWall(Math.PI / 2, 6);
    mkWall(Math.PI, 6);
    mkWall(-Math.PI / 2, 6);
    // desk + laptop + radio + candle (south-east corner)
    _box(1.7, 0.08, 0.7, _mats.wood, -1.0, 0.95, -2.3, g);
    _box(0.08, 0.9, 0.08, _mats.darkWood, -1.7, 0.45, -2.3, g);
    _box(0.08, 0.9, 0.08, _mats.darkWood, -0.3, 0.45, -2.3, g);
    const lap = _box(0.42, 0.26, 0.03, _mats.amber, -1.15, 1.12, -2.45, g);
    lap.rotation.x = -0.15;
    _box(0.46, 0.03, 0.3, _mats.darkWood, -1.15, 1.0, -2.3, g);
    _box(0.36, 0.2, 0.16, _mats.metal, -0.55, 1.06, -2.3, g);   // radio
    const ant = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.55, 4), _mats.metal);
    ant.position.set(-0.45, 1.38, -2.3); g.add(ant);
    const candleBody = _box(0.05, 0.12, 0.05, _mats.snow, -2.3, 1.06, -2.35, g);
    candleBody.material = new THREE.MeshStandardMaterial({ color: 0xd8c8a8 });
    // cot
    _box(1.1, 0.18, 0.55, _mats.darkWood, 1.9, 0.2, -2.1, g);
    _box(1.0, 0.1, 0.5, new THREE.MeshStandardMaterial({ color: 0x4b4438, roughness: 1 }), 1.9, 0.34, -2.1, g);
    // rug
    _box(2.4, 0.02, 1.8, new THREE.MeshStandardMaterial({ color: 0x3a2c22, roughness: 1 }), 0, 0.02, 0.4, g);
    return g;
  }

  function _buildExteriorCommon(parent) {
    // Ground disc
    const ground = new THREE.Mesh(new THREE.CircleGeometry(180, 24), _mats.ground);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -22;               // tower stands on a ridge: forest floor far below
    parent.add(ground);
    // Tower legs (viewed when outside)
    for (const [lx, lz] of [[-1.4, -1.4], [1.4, -1.4], [-1.4, 1.4], [1.4, 1.4]]) {
      const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.16, 23, 5), _mats.metal);
      leg.position.set(lx, -11.5, lz);
      parent.add(leg);
    }
    return parent;
  }

  function _buildForest(parent, count, radiusMin = 16, radiusMax = 95, y = 0) {
    const forest = new THREE.Group();
    forest.position.y = y;
    const n = count;
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2 + Math.random() * 0.4;
      const r = radiusMin + Math.pow(Math.random(), 0.7) * (radiusMax - radiusMin);
      const s = 1.6 + Math.random() * 3.4;
      _pine(Math.cos(a) * r, Math.sin(a) * r, s, forest);
    }
    _swayGroups.push(forest);
    parent.add(forest);
    return forest;
  }

  function _buildTower1(parent, x, z) {
    const g = new THREE.Group();
    for (const [lx, lz] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
      const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.13, 14, 4), _mats.metal);
      leg.position.set(lx, 7, lz); g.add(leg);
    }
    _box(2.6, 1.6, 2.6, _mats.darkWood, 0, 14.8, 0, g);
    _box(3, 0.3, 3, _mats.metal, 0, 15.75, 0, g);
    const win = _box(1.6, 0.5, 0.05, _mats.amber, 0, 14.9, 1.33, g);
    win.name = "t1win";
    g.position.set(x, -22, z);
    parent.add(g);
    return g;
  }

  function _buildTower3(parent, x, z) {
    const g = _buildTower1(parent, x, z);
    const led = new THREE.Mesh(new THREE.SphereGeometry(0.3, 6, 6), _mats.greenLed);
    led.position.set(0, 15.2, 1.5);
    g.add(led);
    _tower3Light = led;
    return g;
  }

  // The "cabin" set: interior walls + the real world visible through the glass
  function _buildCabin() {
    const g = _buildCabinInterior();
    _buildForest(g, _tier === "high" ? 170 : 70, 22, 110, -22);
    _buildTower1(g, -70, -85);
    _buildTower3(g, 48, -120);
    return g;
  }

  // The "exterior" set: ground-level establishing shot of the whole tower
  function _buildExteriorTower() {
    const g = new THREE.Group();
    _buildExteriorCommon(g);
    // cabin pod at top (world y ≈ 0 = camera height inside)
    _box(6, 3.2, 6, _mats.darkWood, 0, 1.4, 0, g);
    _box(6.6, 0.35, 6.6, _mats.metal, 0, 3.2, 0, g);
    const win = _box(1.6, 0.5, 0.05, _mats.amber, 0, 14.9, 1.33, g);
    win.name = "t1win";
    // forest far below + surrounding pines at ridge level
    _buildForest(g, _tier === "high" ? 170 : 70, 22, 110, -22);
    _buildTower1(g, -70, -85);
    _buildTower3(g, 48, -120);
    return g;
  }

  // The Northern Ravine — a gorge with fog pouring through it like water
  function _buildRavine() {
    const g = new THREE.Group();
    const floor = new THREE.Mesh(new THREE.CircleGeometry(120, 20), _mats.rock);
    floor.rotation.x = -Math.PI / 2; floor.position.y = -14; g.add(floor);
    // steep rock walls either side, gap in the middle
    _box(46, 34, 70, _mats.rock, -30, -2, -14, g);
    _box(46, 34, 70, _mats.rock, 30, -2, -14, g);
    // scree slopes leading down into the gap
    for (const sx of [-1, 1]) {
      const slope = _box(16, 1.2, 60, _mats.rock, sx * 12.5, -7, -14, g);
      slope.rotation.z = sx * 0.62;
    }
    // deadfall: blown-down trunks resting on the near ledge
    const ledge = _box(22, 3, 20, _mats.rock, 0, -3.5, 16, g);   // shelf the player stands on
    ledge.rotation.x = 0.04;
    for (const [tx, tz, tr] of [[-4, 12, 0.5], [5, 8, -0.8]]) {
      const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.45, 11, 7), _mats.bark);
      trunk.position.set(tx, -1.6, tz);
      trunk.rotation.z = Math.PI / 2 + tr * 0.3;
      trunk.rotation.y = tr;
      g.add(trunk);
    }
    // far bridge cable visible across the gap (ties it to the Copperhead)
    const cable = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 44, 4), _mats.metal);
    cable.rotation.z = Math.PI / 2; cable.position.set(0, 9, -46); g.add(cable);
    // fog sprites drifting through the gorge (the signature look)
    const mistTex = _tex((c, w, h) => {
      const gr = c.createRadialGradient(w / 2, h / 2, 4, w / 2, h / 2, w / 2);
      gr.addColorStop(0, "rgba(196,208,204,0.5)"); gr.addColorStop(1, "rgba(196,208,204,0)");
      c.fillStyle = gr; c.fillRect(0, 0, w, h);
    }, 64, 64);
    for (let i = 0; i < (_tier === "high" ? 10 : 4); i++) {
      const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: mistTex, transparent: true, depthWrite: false, opacity: 0.45 }));
      sp.position.set((Math.random() - 0.5) * 26, -9 + Math.random() * 7, -30 + Math.random() * 36);
      sp.scale.setScalar(9 + Math.random() * 7);
      sp.userData.drift = i;
      g.add(sp);
    }
    _buildForest(g, _tier === "high" ? 110 : 45, 40, 105);
    _buildTower1(g, -62, -95);
    return g;
  }

  function _buildBridge() {
    const g = new THREE.Group();
    const ground = new THREE.Mesh(new THREE.CircleGeometry(140, 20), _mats.rock);
    ground.rotation.x = -Math.PI / 2; ground.position.y = -30; g.add(ground);
    // cliff edges
    _box(30, 30, 26, _mats.rock, -26, -15, 0, g);
    _box(30, 30, 26, _mats.rock, 26, -15, 0, g);
    // deck
    _box(26, 0.5, 4, _mats.metal, 0, 0, 0, g);
    // towers + cables
    for (const sx of [-9, 9]) {
      _box(0.6, 7, 0.6, _mats.metal, sx, 3.5, -1.8, g);
      _box(0.6, 7, 0.6, _mats.metal, sx, 3.5, 1.8, g);
      for (const sz of [-1.8, 1.8]) {
        const cable = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 26, 4), _mats.metal);
        cable.rotation.z = Math.PI / 2;
        cable.position.set(0, 5.6 + Math.abs(sx) * 0.06, sz);
        g.add(cable);
      }
    }
    for (let x = -12; x <= 12; x += 2) {
      for (const sz of [-1.8, 1.8]) {
        const hang = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 4.4, 3), _mats.metal);
        hang.position.set(x, 3.4, sz); g.add(hang);
      }
    }
    // abandoned truck
    _box(3.2, 1.4, 1.7, new THREE.MeshStandardMaterial({ color: 0x2f4a3c, roughness: 0.7, metalness: 0.4 }), 5.5, 1.1, 0, g);
    _box(1.1, 1.0, 1.7, new THREE.MeshStandardMaterial({ color: 0x27392f, roughness: 0.7 }), 7.4, 0.9, 0, g);
    const dash = _box(0.3, 0.18, 0.4, _mats.amber, 6.4, 1.5, 0, g);
    _buildForest(g, _tier === "high" ? 120 : 50, 34, 100);
    _buildTower3(g, 70, -105);
    return g;
  }

  function _buildRuins() {
    const g = new THREE.Group();
    const ground = new THREE.Mesh(new THREE.CircleGeometry(90, 20), _mats.ground);
    ground.rotation.x = -Math.PI / 2; g.add(ground);
    // charred foundation
    _box(12, 0.6, 9, _mats.darkWood, 0, 0.3, 0, g);
    for (const [bx, bz, bh] of [[-5.5, -4, 4], [5.5, -4, 3], [0, -4, 5.2], [-5.5, 4, 2.4], [5.5, 4, 3.6]]) {
      _box(0.4, bh, 0.4, _mats.silhouette, bx, 0.6 + bh / 2, bz, g);
    }
    _box(12, 0.35, 0.4, _mats.silhouette, 0, 5.4, -4, g);
    // cellar mouth with warm glow
    _box(2.4, 0.1, 2, _mats.silhouette, 1, 0.62, 1, g);
    const glow = new THREE.Mesh(new THREE.PlaneGeometry(1.8, 1.4), _mats.amber);
    glow.rotation.x = -Math.PI / 2; glow.position.set(1, 0.58, 1); g.add(glow);
    const gl = new THREE.PointLight(0xe58e3c, 1.2, 8, 2); gl.position.set(1, 0.8, 1); g.add(gl);
    _buildForest(g, _tier === "high" ? 110 : 45, 20, 80);
    _buildTower1(g, -55, -70);
    return g;
  }

  function _buildRailcar() {
    const g = new THREE.Group();
    const ground = new THREE.Mesh(new THREE.CircleGeometry(90, 20), _mats.rock);
    ground.rotation.x = -Math.PI / 2; g.add(ground);
    // tilted freight car
    const car = new THREE.Group();
    _box(14, 3.4, 3.4, _mats.metal, 0, 1.7, 0, car);
    for (let x = -5; x <= 5; x += 2.5) _box(1.4, 1.2, 0.1, _mats.silhouette, x, 2.2, 1.76, car);
    for (const wx of [-4.5, 4.5]) {
      const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.7, 0.4, 10), _mats.silhouette);
      wheel.rotation.x = Math.PI / 2; wheel.position.set(wx, 0.7, 1.4); car.add(wheel);
    }
    car.rotation.z = 0.16; car.position.set(0, 0.4, 0);
    g.add(car);
    const lockbox = _box(0.8, 0.5, 0.5, _mats.metal, 3.4, 1.0, 2.2, g);
    lockbox.material = new THREE.MeshStandardMaterial({ color: 0x8a6a2a, roughness: 0.5, metalness: 0.7, emissive: 0x332200 });
    _buildForest(g, _tier === "high" ? 100 : 40, 24, 85);
    return g;
  }

  function _buildSinkhole() {
    const g = new THREE.Group();
    const ground = new THREE.Mesh(new THREE.CircleGeometry(90, 24), _mats.ground);
    ground.rotation.x = -Math.PI / 2; g.add(ground);
    // the pit: open cylinder sunk into ground
    const pit = new THREE.Mesh(new THREE.CylinderGeometry(7, 5, 30, 20, 1, true), new THREE.MeshStandardMaterial({ color: 0x07090a, roughness: 1, side: THREE.BackSide }));
    pit.position.y = -15; g.add(pit);
    const mouth = new THREE.Mesh(new THREE.TorusGeometry(7.1, 0.6, 6, 22), _mats.rock);
    mouth.rotation.x = Math.PI / 2; mouth.position.y = 0.1; g.add(mouth);
    // mist sprites rising
    const mistTex = _tex((c, w, h) => {
      const gr = c.createRadialGradient(w / 2, h / 2, 4, w / 2, h / 2, w / 2);
      gr.addColorStop(0, "rgba(210,220,215,0.55)"); gr.addColorStop(1, "rgba(210,220,215,0)");
      c.fillStyle = gr; c.fillRect(0, 0, w, h);
    }, 64, 64);
    for (let i = 0; i < (_tier === "high" ? 8 : 3); i++) {
      const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: mistTex, transparent: true, depthWrite: false, opacity: 0.5 }));
      const a = Math.random() * Math.PI * 2, r = Math.random() * 5;
      sp.position.set(Math.cos(a) * r, -1 - i * 2, Math.sin(a) * r);
      sp.scale.setScalar(5 + Math.random() * 4);
      sp.userData.mist = i;
      g.add(sp);
    }
    _buildForest(g, _tier === "high" ? 110 : 45, 16, 80);
    return g;
  }

  function _buildRuinsHuts() { /* Compass Cabins site */
    const g = new THREE.Group();
    const ground = new THREE.Mesh(new THREE.CircleGeometry(90, 20), _mats.ground);
    ground.rotation.x = -Math.PI / 2; g.add(ground);
    const cabinAt = (x, z, rot) => {
      const c = new THREE.Group();
      _box(5, 2.4, 4, _mats.darkWood, 0, 1.2, 0, c);
      const roof = new THREE.Mesh(new THREE.ConeGeometry(3.6, 1.6, 4), _mats.metal);
      roof.position.y = 3.2; roof.rotation.y = Math.PI / 4; c.add(roof);
      const door = _box(0.9, 1.5, 0.1, _mats.silhouette, 0, 0.75, 2.02, c);
      const w1 = _box(0.8, 0.7, 0.06, _mats.amber, -1.5, 1.5, 2.02, c);
      c.position.set(x, 0, z); c.rotation.y = rot; g.add(c);
      return c;
    };
    cabinAt(-6, -3, 0.3); cabinAt(6, -5, -0.4); cabinAt(4, 7, 2.6); cabinAt(-7, 6, 1.9);
    _buildForest(g, _tier === "high" ? 120 : 50, 20, 85);
    _buildTower3(g, 66, -80);
    return g;
  }

  function _buildMine() {
    const g = new THREE.Group();
    const ground = new THREE.Mesh(new THREE.CircleGeometry(80, 20), _mats.rock);
    ground.rotation.x = -Math.PI / 2; g.add(ground);
    // limestone cliff + black portal
    _box(26, 14, 10, _mats.rock, 0, 7, -8, g);
    const portal = _box(4.4, 5.4, 1, _mats.silhouette, 0, 2.7, -3.4, g);
    // timber frame
    _box(5.2, 0.5, 0.6, _mats.darkWood, 0, 5.7, -3.2, g);
    _box(0.5, 5.6, 0.6, _mats.darkWood, -2.4, 2.8, -3.2, g);
    _box(0.5, 5.6, 0.6, _mats.darkWood, 2.4, 2.8, -3.2, g);
    // generator glow inside
    const gl = new THREE.PointLight(0x7dff9a, 0.8, 10, 2); gl.position.set(0, 2, -6); g.add(gl);
    // track
    for (let z = -3; z < 14; z += 2.4) _box(3, 0.1, 0.3, _mats.darkWood, 0, 0.06, z, g);
    _buildForest(g, _tier === "high" ? 110 : 45, 22, 80);
    return g;
  }

  function _buildClearing() {
    const g = new THREE.Group();
    const ground = new THREE.Mesh(new THREE.CircleGeometry(90, 24), _mats.ground);
    ground.rotation.x = -Math.PI / 2; g.add(ground);
    // stump ring
    for (let i = 0; i < 9; i++) {
      const a = (i / 9) * Math.PI * 2;
      const stump = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.6, 0.7, 7), _mats.bark);
      stump.position.set(Math.cos(a) * 9, 0.35, Math.sin(a) * 9);
      g.add(stump);
    }
    // jar glint at the center
    const jar = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.35, 8), new THREE.MeshStandardMaterial({ color: 0x9fb8a8, transparent: true, opacity: 0.5, emissive: 0x334422 }));
    jar.position.y = 0.35; g.add(jar);
    // pines stepped back in an arc — leave a clean 12m gap toward the camera
    const forest = new THREE.Group();
    for (let i = 0; i < (_tier === "high" ? 140 : 55); i++) {
      const a = (i / 140) * Math.PI * 2;
      if (Math.abs(a - Math.PI / 2) < 0.5) continue; // the gap that shouldn't be there
      const r = 14 + Math.pow(Math.random(), 0.7) * 70;
      _pine(Math.cos(a) * r, Math.sin(a) * r, 1.8 + Math.random() * 3.2, forest);
    }
    _swayGroups.push(forest);
    g.add(forest);
    return g;
  }

  function _buildCity() {
    // Generic ruined-city view for the classic scenarios
    const g = new THREE.Group();
    const ground = new THREE.Mesh(new THREE.CircleGeometry(160, 20), _mats.ground);
    ground.rotation.x = -Math.PI / 2; g.add(ground);
    const bMat = new THREE.MeshStandardMaterial({ color: 0x1b2129, roughness: 0.9 });
    const bMat2 = new THREE.MeshStandardMaterial({ color: 0x232a33, roughness: 0.9 });
    for (let i = 0; i < (_tier === "high" ? 70 : 34); i++) {
      const a = (i / 70) * Math.PI * 2 + Math.random() * 0.1;
      const r = 24 + Math.random() * 110;
      const h = 6 + Math.random() * 34;
      _box(6 + Math.random() * 8, h, 6 + Math.random() * 8, Math.random() < 0.5 ? bMat : bMat2,
        Math.cos(a) * r, h / 2, Math.sin(a) * r, g);
    }
    return g;
  }

  // Map scene ids → set builders
  const SET_BUILDERS = {
    cabin: _buildCabin, bridge: _buildBridge, ruins: _buildRuins, railcar: _buildRailcar,
    sinkhole: _buildSinkhole, cabins: _buildRuinsHuts, mine: _buildMine, clearing: _buildClearing,
    city: _buildCity, exterior: _buildExteriorTower, ravine: _buildRavine,
  };

  // Camera vantage per set: [pos, lookAt]
  const VANTAGE = {
    cabin: [null, null],                 // handled specially (interior)
    exterior: [[6, -20.2, 30], [0, 1.2, 0]],
    bridge: [[-14, 2.2, 5], [4, 1.2, 0]],
    ruins: [[0, 2.4, 10], [0, 1.2, 0]],
    railcar: [[-10, 3.2, 8], [2, 1.5, 0]],
    sinkhole: [[0, 2.6, 13], [0, -1, 0]],
    cabins: [[-2, 2.6, 15], [0, 1.6, 0]],
    mine: [[0, 3.0, 13], [0, 3.0, -4]],
    clearing: [[0, 2.2, 13], [0, 1.0, 0]],
    city: [[0, 12, 40], [0, 8, -20]],
    ravine: [[0, 3.4, 20], [0, -5, -20]],
  };

  function _setLocation(name) {
    if (!_scene) return;
    if (_set === name && _built[name]) { _applyVantage(name); return; }
    _set = name;
    if (!_built[name]) {
      const builder = SET_BUILDERS[name] || SET_BUILDERS.cabin;
      const g = builder();
      _scene.add(g);
      _built[name] = g;
      if (name === "cabin") _spawnCabinFigures(g);
    }
    // hide other sets
    Object.entries(_built).forEach(([k, g]) => { g.visible = (k === name); });
    // interior-only light follows the camera view
    if (_candle) _candle.intensity = 0;
    _applyVantage(name);
    _clearFigures();
    if (name === "cabin") {
      if (!_figs.length) _spawnCabinFigures(_built.cabin);
      _figs.forEach((f) => (f.visible = true));
    }
    _resize();
  }

  let _cabinFigBuilt = false;
  function _spawnCabinFigures(g) {
    if (_cabinFigBuilt && _figs.length) { _figs.forEach(f => (f.visible = true)); return; }
    _cabinFigBuilt = true;
    const colors = [0x2f4a5e, 0x4c5a2f, 0x5e4432]; // mark, chloe, sam body colors
    _figs = colors.map((c, i) => {
      const f = _figure(c, 0.92);
      f.position.set(-1.6 + i * 1.5, 0, -1.4);
      f.rotation.y = Math.PI + (i - 1) * 0.35;  // facing the window
      g.add(f);
      return f;
    });
  }

  function _applyVantage(name) {
    const v = VANTAGE[name] || VANTAGE.exterior;
    if (name === "cabin") {
      // Interior: standing at the north window looking out over the forest
      _camera.position.set(0, 1.62, 1.55);
      _camera.lookAt(0, 1.35, -40);
      if (_candle) { _candle.position.set(-2.3, 1.3, -2.3); _candle.intensity = 0; }
    } else {
      _camera.position.set(...v[0]);
      _camera.lookAt(...v[1]);
      if (_candle) _candle.intensity = 0;
    }
  }

  function _clearFigures() {
    _figs.forEach((f) => (f.visible = false));
    [_walker, _lieFig, _bigFig].forEach((f) => { if (f) f.visible = false; });
  }

  // ───────────────────────── threats from state ─────────────────────────
  function _updateThreats(st, t) {
    const w = st.world || {}, p = st.player || {};
    const flags = w.flags || {};
    const sanity = p.morale != null ? p.morale : 100;
    const awareness = p.humanity || 0;
    const night = !!w.is_night || !!flags.rd_eclipse;
    const scene = (st.scene || "").toLowerCase();

    // Tall figure: scripted scenes or wandering at treeline
    if (!_bigFig) { _bigFig = _figure(0x07090a, 2.2); _scene.add(_bigFig); _bigFig.visible = false; }
    const wantsBig =
      scene.includes("entity") || scene.includes("treeline") ||
      (st.scenario === "dead_ridge" && awareness >= 55 && night && Math.sin(t * 0.35) > 0.4) ||
      (sanity < 30 && Math.sin(t * 0.5) > 0.7);
    if (_set === "cabin" || _set === "exterior") {
      _bigFig.visible = wantsBig;
      if (wantsBig) {
        // beyond the treeline, visible through the north window
        _bigFig.position.set(Math.sin(t * 0.05) * 6, -21.6, -46);
        _bigFig.rotation.y = Math.sin(t * 0.2) * 0.3;
      }
    } else _bigFig.visible = false;

    // Window LIE: a companion standing outside who is inside (low sanity)
    if (!_lieFig) {
      _lieFig = _figure(0x3d545c, 1.0);
      _scene.add(_lieFig);
      _lieFig.visible = false;
    }
    const lie = st.scenario === "dead_ridge" && sanity < 50 && _set === "cabin" && Math.sin(t * 0.21) > 0.55;
    _lieFig.visible = lie;
    if (lie) { _lieFig.position.set(6.5, -21.6, -24); _lieFig.rotation.y = 0; }

    // Walker crossing the ridge at high awareness
    if (!_walker) { _walker = _figure(0x0b0e0c, 1.7); _scene.add(_walker); _walker.visible = false; }
    const walk = _set === "cabin" && awareness >= 40 && night && Math.sin(t * 0.13) > 0.1;
    _walker.visible = walk;
    if (walk) {
      const prog = ((t * 1.4) % 60) - 30;
      _walker.position.set(prog, -21.6, -55);
      _walker.rotation.y = Math.PI / 2;
      _walker.position.y = -21.6 + Math.abs(Math.sin(t * 4)) * 0.06; // gait bob
    }
  }

  // ───────────────────────── day / night / weather ─────────────────────────
  const DAY_SKY = new THREE.Color(0x8fa3ad);
  const NIGHT_SKY = new THREE.Color(0x04070b);
  const ECLIPSE_SKY = new THREE.Color(0x0a0512);
  const _skyTmp = new THREE.Color();

  function _updateAtmosphere(st, t) {
    const w = st.world || {}, p = st.player || {};
    const flags = w.flags || {};
    const eclipse = !!flags.rd_eclipse;
    const night = !!w.is_night;
    const isRidge = st.scenario === "dead_ridge";
    const awareness = p.humanity || 0;
    const sanity = p.morale != null ? p.morale : 100;

    // Weather from the classic state when present
    const weather = (w.weather || "clear").toLowerCase();

    let dayF = night ? 0 : 1;
    if (eclipse) dayF = 0;
    // Dawn/dusk tint on the classic clock: keep simple, snap by flag.

    _skyTmp.copy(NIGHT_SKY).lerp(DAY_SKY, dayF);
    if (eclipse) _skyTmp.copy(ECLIPSE_SKY);
    if (!_scene.background) _scene.background = _skyTmp.clone();
    else _scene.background.copy(_skyTmp);

    if (_hemi) {
      _hemi.intensity = 0.22 + dayF * 0.5;
      _hemi.color.set(dayF > 0.5 ? 0x9fb2bf : 0x2b3a4a);
    }
    if (_sun) {
      _sun.intensity = 0.12 + dayF * 0.7;
      _sun.color.set(eclipse ? 0x6a4a7a : (dayF > 0.5 ? 0xd8e2e8 : 0x5a6f8a));
      _sun.position.set(Math.cos(t * 0.005) * 40, 30 + dayF * 20, -25);
    }
    if (_candle) {
      const flick = 0.85 + Math.sin(t * 9.1) * 0.1 + Math.sin(t * 23.7) * 0.05;
      _candle.intensity = (1.0 - dayF * 0.6) * 1.6 * flick + 0.25;
    }

    // FOG: base + night + awareness (threat closes in) + weather
    let density = 0.03 + (night ? 0.016 : 0.0) + Math.min(0.03, awareness * 0.00035);
    if (weather === "fog") density += 0.02;
    if (weather === "storm" || weather === "rain") density += 0.008;
    if (isRidge === false && weather === "clear") density -= 0.005;
    if (sanity < 40) density += (40 - sanity) * 0.0006;  // low sanity literally fogs the world
    if (_scene.fog) _scene.fog.density = density;

    // Rain / storm particles (HIGH tier only)
    const wantRain = (weather === "rain" || weather === "storm") && _tier === "high";
    if (wantRain && !_rain) _rain = _makeRain();
    if (_rain) { _rain.visible = wantRain; if (wantRain) _animateRain(_rain, t); }

    // Wind sway: amplitude from awareness metric (matches the 2D engine's wind)
    const wind = 0.4 + awareness / 100 * 1.6 + (weather === "storm" ? 1.2 : 0);
    _swayGroups.forEach((grp, i) => {
      grp.rotation.z = Math.sin(t * 0.6 + i) * 0.004 * wind;
      grp.rotation.x = Math.cos(t * 0.45 + i * 1.3) * 0.003 * wind;
    });

    // Fog sprites: slow drift through ravine / sinkhole (breathing mist)
    Object.values(_built).forEach((grp) => {
      if (!grp.visible) return;
      grp.traverse((o) => {
        if (!o.isSprite) return;
        const i = o.userData.drift != null ? o.userData.drift : o.userData.mist;
        if (i == null) return;
        if (o.userData.drift != null) {
          o.position.x += Math.sin(t * 0.25 + i * 2.1) * 0.012 * wind;
          o.position.y += Math.sin(t * 0.4 + i) * 0.004;
        } else {
          o.position.y += Math.sin(t * 0.6 + i * 1.7) * 0.006 + 0.003; // mist breathes upward
          if (o.position.y > 1.5) o.position.y = -10;
        }
        o.material.opacity = 0.32 + Math.sin(t * 0.5 + i * 1.3) * 0.13;
      });
    });

    // Tower-3 morse (green H-E-L-P rhythm) at night when the player has seen it
    if (_tower3Light) {
      const ph = (t % 64);
      const on = (ph < 8) || (ph >= 16 && ph < 24) || (ph >= 32 && ph < 40) || (ph >= 48 && ph < 56);
      const active = night && (flags.rd_tower3_seen || st.world.day >= 2);
      _tower3Light.material.emissiveIntensity = active && on ? 3.0 : (active ? 0.2 : 0);
    }

    // T1 window light dies after day 10
    const t1 = _built.cabin && _built.cabin.getObjectByName("t1win");
    if (t1 && t1.material && t1.material.emissiveIntensity !== undefined) {
      t1.material.emissiveIntensity = (st.world.day || 1) < 10 ? 1.2 : 0.02;
    }
  }

  function _makeRain() {
    const n = _tier === "high" ? 900 : 0;
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 60;
      pos[i * 3 + 1] = Math.random() * 40;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 60;
    }
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    const mat = new THREE.PointsMaterial({ color: 0xa9c4d8, size: 0.12, transparent: true, opacity: 0.6 });
    const pts = new THREE.Points(geo, mat);
    pts.visible = false;
    _scene.add(pts);
    return pts;
  }

  function _animateRain(rain, t) {
    const arr = rain.geometry.attributes.position.array;
    for (let i = 1; i < arr.length; i += 3) {
      arr[i] -= 0.55;
      if (arr[i] < -2) arr[i] = 38;
    }
    rain.geometry.attributes.position.needsUpdate = true;
    if (_camera) { rain.position.set(_camera.position.x, 0, _camera.position.z); }
  }

  // ───────────────────────── scene routing from game state ─────────────────────────
  function _sceneToSet(st) {
    const sc = (st.scene || "").toLowerCase();
    if (st.scenario !== "dead_ridge") return "city";   // classic mode = city view
    if (sc.includes("bridge")) return "bridge";
    if (sc.includes("ravine")) return "ravine";
    if (sc.includes("ruins")) return "ruins";
    if (sc.includes("railcar")) return "railcar";
    if (sc.includes("sinkhole")) return "sinkhole";
    if (sc.includes("cabins")) return "cabins";
    if (sc.includes("mine")) return "mine";
    if (sc.includes("clearing")) return "clearing";
    if (sc.includes("tower3") || sc.includes("t1")) return "cabin";   // watch them from the window
    if (sc.includes("entity") || sc.includes("forest") || sc.includes("walker")) return "exterior";
    if (sc.includes("ending")) return "exterior";
    return "cabin";                                     // hub, laptop, radio, radar…
  }

  function update(state) {
    if (!state) return;
    _state = state;
    if (!_enabled) return;
    if (!_renderer) { _init(); if (!_renderer) return; }
    const set = _sceneToSet(state);
    if (set !== _set) _setLocation(set);
    if (set === "cabin" && _figs.length) {
      // Companions visible in the cabin match who is actually alive at base
      const party = state.party || [];
      _figs.forEach((f, i) => { f.visible = i < Math.min(3, party.length); });
      // idle breathing bob
      _figs.forEach((f, i) => { f.position.y = Math.sin(_clock * 1.4 + i) * 0.01; });
    }
  }

  function _loop() {
    _raf = requestAnimationFrame(_loop);
    if (!_enabled || !_renderer || !_scene || !_camera) return;   // idle silently when OFF
    _clock += 1 / 60;
    const st = _state;
    if (st) {
      _updateAtmosphere(st, _clock);
      _updateThreats(st, _clock);
    }
    // idle camera breathing (cinematic handheld feel)
    if (_set === "cabin") {
      _camera.position.x = Math.sin(_clock * 0.35) * 0.03;
      _camera.position.y = 1.62 + Math.sin(_clock * 0.6) * 0.015;
      _camera.lookAt(Math.sin(_clock * 0.13) * 0.8, 1.35 + Math.sin(_clock * 0.2) * 0.1, -40);
    }
    _renderer.render(_scene, _camera);
  }

  // ───────────────────────── public ─────────────────────────
  return {
    get active() { return _active && _enabled && !!_renderer; },
    get tier() { return _tier; },
    supported,
    label,
    init() { if (_enabled && supported()) _init(); else _applyVisibility(); },
    update,
    cycleQuality,
    // Used by tests / debugging
    _internal: () => ({ set: _set, tier: _tier, enabled: _enabled, sets: Object.keys(_built) }),
  };
})();

window.Scene3D = Scene3D;
document.addEventListener("DOMContentLoaded", () => Scene3D.init());
