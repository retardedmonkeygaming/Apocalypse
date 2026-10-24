/* ==========================================================================
   FORESTOS v4.2 — Laptop overlay & Weather Station UI (Dead Ridge mode)
   A graphical amber-phosphor window layered over the CRT. It mirrors the
   backend's text choices as clickable apps — the socket protocol is
   unchanged, every click just calls press(key) from game.js.
   ========================================================================== */

const LaptopOS = (() => {
  let _overlay = null, _panel = null, _body = null, _title = null;
  let _lastId = "";
  let _dismissed = false;
  let _radarCanvas = null, _radarAnim = 0;

  function _state() {
    return window.__rdState || null;
  }

  function _create() {
    const overlay = document.createElement("div");
    overlay.id = "laptop-overlay";
    overlay.className = "hidden";

    const panel = document.createElement("div");
    panel.id = "laptop-panel";

    const bar = document.createElement("div");
    bar.id = "laptop-titlebar";
    bar.innerHTML =
      '<span class="lap-dot"></span>' +
      '<span id="laptop-title">FORESTOS v4.2</span>' +
      '<span class="lap-clock" id="laptop-clock">--:--</span>' +
      '<button id="laptop-close" title="Close laptop lid (returns to game view)">▼ LID</button>';
    bar.querySelector("#laptop-close").addEventListener("click", () => LaptopOS.dismiss());

    const body = document.createElement("div");
    body.id = "laptop-body";

    panel.appendChild(bar);
    panel.appendChild(body);
    overlay.appendChild(panel);

    const screen = document.getElementById("crt-screen");
    if (screen) {
      screen.style.position = "relative";
      screen.appendChild(overlay);
    } else {
      document.body.appendChild(overlay);
    }
    return { overlay, panel, body };
  }

  function _init() {
    if (_overlay) return;
    const parts = _create();
    _overlay = parts.overlay;
    _panel = parts.panel;
    _body = parts.body;
    _title = document.getElementById("laptop-title");
  }

  // ── choice helpers ───────────────────────────────────────────────

  function _btn(choice) {
    const b = document.createElement("button");
    b.className = "lap-choice";
    b.dataset.key = choice.key;
    b.innerHTML = `<span class="lap-key">${choice.key.toUpperCase().slice(0, 1)}</span>${_esc(choice.label)}`;
    b.addEventListener("click", () => {
      if (window.press) press(choice.key);
    });
    return b;
  }

  function _esc(s) {
    return String(s || "").replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  }

  function _choicesRow(ev) {
    const row = document.createElement("div");
    row.className = "lap-choices";
    (ev.choices || []).forEach((c) => row.appendChild(_btn(c)));
    // LOCK SYNC is the confirm button in the calibration screen
    if (ev.title && ev.title.includes("CALIBRATION")) {
      const lock = document.createElement("button");
      lock.className = "lap-choice lap-lock";
      lock.innerHTML = '<span class="lap-key">␣</span>LOCK SYNC';
      lock.addEventListener("click", () => window.press && press("confirm"));
      row.appendChild(lock);
    }
    return row;
  }

  // ── app screens ──────────────────────────────────────────────────

  function _renderDock(ev, state) {
    const flags = (state.world && state.world.flags) || {};
    const unread = (flags.rd_inbox || []).filter((m) => !m.read).length;
    const cal = flags.rd_cal ? "OK" : "DUE";
    _body.innerHTML = `
      <div class="lap-boot">FORESTOS v4.2 (c) 1995 WOODSVC SYS<br>MEM 640K OK · RADIO: WARM · BARO: ${cal}<br><br></div>
      <div class="lap-doc">${_esc(ev.text)}</div>`;
    // App icons double as the four text choices
    const dock = document.createElement("div");
    dock.className = "lap-dock";
    const icons = ["📥", "🌡", "📝", "🛰"];
    (ev.choices || []).forEach((c, i) => {
      const app = document.createElement("button");
      app.className = "lap-app";
      app.innerHTML = `<span class="lap-app-icon">${icons[i] || "▪"}</span><span class="lap-app-name">${_esc(c.label.replace(/\s*\(.*\)$/, ""))}</span>${i === 0 && unread ? `<span class="lap-badge">${unread}</span>` : ""}`;
      app.addEventListener("click", () => window.press && press(c.key));
      dock.appendChild(app);
    });
    _body.appendChild(dock);
    _body.appendChild(_choicesRow(ev));
  }

  function _renderInbox(ev, state) {
    const inbox = ((state.world.flags || {}).rd_inbox) || [];
    _body.innerHTML = '<div class="lap-menubar">FILE  EDIT  VIEW  SYSTEM &nbsp;—&nbsp; INBOX (POP3)</div>';
    const list = document.createElement("div");
    list.className = "lap-mail-list";
    inbox.slice().reverse().forEach((m) => {
      const row = document.createElement("div");
      row.className = "lap-mail" + (m.read ? "" : " unread");
      row.innerHTML =
        `<div class="lap-mail-head"><span class="lap-mail-from">${_esc(m.frm)}</span>` +
        `<span class="lap-mail-subj">${_esc(m.subject)}</span></div>` +
        `<div class="lap-mail-body">${_esc(m.body)}</div>`;
      list.appendChild(row);
    });
    if (!inbox.length) list.innerHTML = '<div class="lap-empty">— NO MESSAGES. THE SYSTEM IS QUIET. —</div>';
    _body.appendChild(list);
    _body.appendChild(_choicesRow(ev));
  }

  function _renderCalibration(ev, state) {
    const f = (state.world.flags || {});
    const coeff = f.rd_coeff || 1005;
    const n = f.rd_n || 982, v = f.rd_v || 994, s = f.rd_south || 988;
    const fraud = !!f.rd_fraud;
    // deviation vs the honest target (matches backend _target())
    const vals = fraud ? [n, v] : [n, v, s];
    vals.sort((a, b) => a - b);
    const target = vals[Math.floor(vals.length / 2)];
    const dev = coeff - target;
    const devCls = Math.abs(dev) <= 2 ? "ok" : (Math.abs(dev) <= 8 ? "warn" : "crit");

    _body.innerHTML = `
      <div class="lap-menubar">SENSOR DAEMON v0.9 — RUNNING · NEXT SYNC IN 12H</div>
      <div class="cal-grid">
        <div class="cal-dev ${devCls}">
          <span class="cal-dev-label">CURRENT DIGITAL DEVIATION</span>
          <span class="cal-dev-value">${dev > 0 ? "+" : ""}${dev} mb</span>
          <span class="cal-dev-hint">${Math.abs(dev) <= 2 ? "SYNC — LOCK TO VERIFY" : "<-- CRITICAL IMBALANCE"}</span>
        </div>
        <div class="cal-arrays">
          <div class="cal-array"><span>NORTH ARRAY</span><b>${n} mb</b><i class="stable">STABLE</i></div>
          <div class="cal-array"><span>VALLEY COIL</span><b>${v} mb</b><i class="stable">STABLE</i></div>
          <div class="cal-array ${fraud ? "fraud" : ""}"><span>SOUTH ARRAY</span><b>${s} mb</b><i class="${fraud ? "bad" : "stable"}">${fraud ? "MIMICRY INTERFERENCE" : "STABLE"}</i></div>
        </div>
        <div class="cal-gauge">
          <div class="cal-gauge-track"><div class="cal-gauge-fill" style="width:${Math.max(2, Math.min(100, 50 + dev * 3))}%"></div></div>
          <div class="cal-gauge-marks"><span>-20</span><span>0</span><span>+20</span></div>
        </div>
      </div>
      ${fraud ? '<div class="cal-warning">⚠ SOUTH ARRAY LOCKED AT 1013mb PATTERN — EXCLUDE FROM MEDIAN. CALIBRATE ON NORTH + VALLEY ONLY.</div>' : ""}`;
    _body.appendChild(_choicesRow(ev));
  }

  function _renderLogEngine(ev, state) {
    const code = ((ev.text || "").match(/DR-\d{2}-\d{3}/) || ["DR-??-???"])[0];
    _body.innerHTML = `
      <div class="lap-menubar">LOGENGINE v2.1 — MANUAL ENTRY REQUIRED</div>
      <div class="lap-term">
        <div>&gt; open enviro-log --day ${(state.world || {}).day}</div>
        <div class="term-err">CRITICAL: BAROMETRIC SYNC NOT VERIFIED — CHECK SUM FAILED</div>
        <div>&gt; validation_string: <span class="term-code">${code}</span></div>
        <div>&gt; awaiting operator input_<span class="term-caret"></span></div>
      </div>`;
    _body.appendChild(_choicesRow(ev));
  }

  function _renderRadar(ev, state) {
    _body.innerHTML = `<div class="lap-menubar">WEATHERRADAR v1.9 — DOPPLER ARRAY · TOWER 2</div>
      <div class="radar-wrap"><canvas id="lap-radar" width="300" height="150"></canvas>
      <div class="radar-legend"><span class="rl-g"></span> DENSITY VECTOR <span class="rl-r"></span> VOID SIGNATURE</div></div>
      <div class="lap-doc">${_esc(ev.text)}</div>`;
    _body.appendChild(_choicesRow(ev));
    _radarCanvas = document.getElementById("lap-radar");
    _startRadar();
  }

  function _renderGeneric(ev) {
    _body.innerHTML = `<div class="lap-doc lap-doc-full">${_esc(ev.text).replace(/\n/g, "<br>")}</div>`;
    _body.appendChild(_choicesRow(ev));
  }

  // ── animated radar canvas ────────────────────────────────────────

  function _startRadar() {
    _stopRadar();
    const cv = _radarCanvas;
    if (!cv) return;
    const ctx = cv.getContext("2d");
    let t = 0;
    const step = () => {
      if (!_radarCanvas || !document.getElementById("lap-radar")) { _radarAnim = 0; return; }
      t++;
      ctx.fillStyle = "#04120a";
      ctx.fillRect(0, 0, 300, 150);
      ctx.strokeStyle = "rgba(60,220,120,0.16)";
      ctx.lineWidth = 0.5;
      for (let x = 0; x < 300; x += 12) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 150); ctx.stroke(); }
      for (let y = 0; y < 150; y += 12) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(300, y); ctx.stroke(); }
      // density vectors drifting east
      for (let i = 0; i < 18; i++) {
        const vx = (i * 43 + t * 1.4) % 320 - 10;
        const vy = (i * 29) % 140 + 5;
        ctx.fillStyle = "rgba(90,240,150,0.55)";
        ctx.fillRect(vx, vy, 3, 1);
      }
      // void anomaly — dead center, breathing, drifting against the wind
      const ax = 150 + Math.sin(t * 0.025) * 16;
      const pulse = 11 + Math.sin(t * 0.09) * 3;
      const g = ctx.createRadialGradient(ax, 75, 2, ax, 75, pulse + 8);
      g.addColorStop(0, "rgba(255,70,70,0.75)");
      g.addColorStop(0.6, "rgba(170,20,20,0.35)");
      g.addColorStop(1, "rgba(120,10,10,0)");
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(ax, 75, pulse + 8, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#ffcccc";
      ctx.fillRect(ax - 1, 74, 2, 2);
      // sweep line
      const sweep = (t * 3) % 300;
      ctx.fillStyle = "rgba(120,255,170,0.20)";
      ctx.fillRect(sweep, 0, 2, 150);
      // scanlines
      ctx.fillStyle = "rgba(0,0,0,0.25)";
      for (let y = 1; y < 150; y += 3) ctx.fillRect(0, y, 300, 1);
      _radarAnim = requestAnimationFrame(step);
    };
    step();
  }

  function _stopRadar() {
    if (_radarAnim) { cancelAnimationFrame(_radarAnim); _radarAnim = 0; }
    _radarCanvas = null;
  }

  // ── router ───────────────────────────────────────────────────────

  function _route(ev, state) {
    const t = ev.title || "";
    if (t.includes("FORESTOS v4.2")) return _renderDock(ev, state);
    if (t.includes("INBOX")) return _renderInbox(ev, state);
    if (t.includes("CALIBRATION")) return _renderCalibration(ev, state);
    if (t.includes("LOG ENGINE")) return _renderLogEngine(ev, state);
    if (t.includes("WEATHERRADAR")) return _renderRadar(ev, state);
    if (t.includes("DOCUMENT")) return _renderGeneric(ev);
    if (t.includes("REJECTED")) return _renderLogEngine(ev, state);
    return null;
  }

  function _isLaptopEvent(ev) {
    const t = (ev && ev.title) || "";
    return /FORESTOS|INBOX|CALIBRATION|LOG ENGINE|WEATHERRADAR|DOCUMENTS|REJECTED/.test(t);
  }

  return {
    init() { _init(); },

    dismiss() {
      _dismissed = true;
      _stopRadar();
      if (_overlay) _overlay.classList.add("hidden");
    },

    update(state) {
      _init();
      if (!state || state.scenario !== "dead_ridge" || !state.current_event) {
        if (_overlay && !_overlay.classList.contains("hidden")) {
          _overlay.classList.add("hidden");
          _stopRadar();
        }
        return;
      }
      const ev = state.current_event;
      const evId = (ev.title || "") + "|" + (ev.id || "");

      if (!_isLaptopEvent(ev)) {
        // Lid auto-closes when the game leaves the laptop screens
        if (_lastId !== evId && !_overlay.classList.contains("hidden")) {
          _overlay.classList.add("hidden");
          _stopRadar();
        }
        if (!_isLaptopEvent(ev)) { if (_lastId !== evId) _dismissed = false; _lastId = evId; }
        return;
      }

      if (evId !== _lastId) { _lastId = evId; _dismissed = false; }
      if (_dismissed) return;

      _title.textContent = ev.title;
      const clock = document.getElementById("laptop-clock");
      if (clock && state.world) clock.textContent = `DAY ${state.world.day}`;
      _route(ev, state);
      _overlay.classList.remove("hidden");
    },
  };
})();

document.addEventListener("DOMContentLoaded", () => LaptopOS.init());
window.LaptopOS = LaptopOS;

/* ==========================================================================
   WEATHER STATION — standalone instrument panel (combo 2+4 / key W)
   Animated ridge radar + barometric readouts pulled from the live state.
   ========================================================================== */

const WeatherStation = (() => {
  let _el = null, _anim = 0;

  function _state() { return window.__rdState || null; }

  function _create() {
    const el = document.createElement("div");
    el.id = "weather-station";
    el.className = "hidden";
    el.innerHTML = `
      <div id="ws-titlebar"><span>🛰 DEAD RIDGE WEATHER STATION — PEAK 2</span><button id="ws-close">✕</button></div>
      <div id="ws-main">
        <canvas id="ws-radar" width="300" height="160"></canvas>
        <div id="ws-readouts">
          <div class="ws-row"><span>PRESSURE NORTH</span><b id="ws-n">--- mb</b></div>
          <div class="ws-row"><span>PRESSURE VALLEY</span><b id="ws-v">--- mb</b></div>
          <div class="ws-row" id="ws-south-row"><span>PRESSURE SOUTH</span><b id="ws-s">--- mb</b></div>
          <div class="ws-row"><span>WIND / DRIFT</span><b id="ws-wind">0 kts</b></div>
          <div class="ws-row"><span>VISIBILITY</span><b id="ws-vis">---</b></div>
          <div class="ws-row"><span>ANOMALY</span><b id="ws-anom">SCANNING…</b></div>
        </div>
      </div>
      <div id="ws-footer">AUTO-TRACE <span class="ws-blink">▮</span> — updates from Tower 2 Doppler array</div>`;
    const screen = document.getElementById("crt-screen");
    if (screen) { screen.style.position = "relative"; screen.appendChild(el); }
    else document.body.appendChild(el);
    el.querySelector("#ws-close").addEventListener("click", () => WeatherStation.hide());
    return el;
  }

  function _readouts() {
    const st = _state();
    if (!st || st.scenario !== "dead_ridge") return;
    const f = st.world.flags || {};
    const p = st.player || {};
    const set = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
    set("ws-n", `${f.rd_n || "—"} mb`);
    set("ws-v", `${f.rd_v || "—"} mb`);
    set("ws-s", `${f.rd_south || "—"} mb`);
    const southRow = document.getElementById("ws-south-row");
    if (southRow) {
      southRow.classList.toggle("fraud", !!f.rd_fraud);
      const b = southRow.querySelector("b");
      if (b && f.rd_fraud) b.textContent = "1013 mb ⚠ MIMIC";
    }
    set("ws-wind", `${Math.round((p.humanity || 0) * 0.5)} kts`);
    const eclipse = !!f.rd_eclipse;
    set("ws-vis", eclipse ? "0 m — ECLIPSE" : (st.world.is_night ? "80 m — NIGHT" : "450 m — FOG"));
    const anom = document.getElementById("ws-anom");
    if (anom) {
      anom.textContent = f.rd_radar_dead ? "SENSOR ARRAYS COMPROMISED" :
        ((st.world.day || 1) >= 8 ? "VOID SIGNATURE — MOVING AGAINST WIND" : "NOMINAL");
      anom.classList.toggle("bad", (st.world.day || 1) >= 8 || !!f.rd_radar_dead);
    }
  }

  function _loop() {
    const cv = document.getElementById("ws-radar");
    if (!cv) { _anim = 0; return; }
    const ctx = cv.getContext("2d");
    let t = 0;
    const step = () => {
      if (!document.getElementById("ws-radar")) { _anim = 0; return; }
      t++;
      ctx.fillStyle = "#04120a";
      ctx.fillRect(0, 0, 300, 160);
      // grid
      ctx.strokeStyle = "rgba(60,220,120,0.15)";
      ctx.lineWidth = 0.5;
      for (let x = 0; x < 300; x += 12) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 160); ctx.stroke(); }
      for (let y = 0; y < 160; y += 12) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(300, y); ctx.stroke(); }
      // contour rings around the peak
      ctx.strokeStyle = "rgba(70,200,130,0.35)";
      for (let r = 18; r < 76; r += 19) { ctx.beginPath(); ctx.arc(150, 80, r, 0, Math.PI * 2); ctx.stroke(); }
      // tower marker
      ctx.fillStyle = "#e58e3c";
      ctx.fillRect(149, 79, 3, 3);
      ctx.font = "7px monospace";
      ctx.fillText("TWR2", 154, 78);
      // density vectors
      for (let i = 0; i < 20; i++) {
        const vx = (i * 41 + t * 1.5) % 320 - 10;
        const vy = (i * 31) % 150 + 5;
        ctx.fillStyle = "rgba(90,240,150,0.5)";
        ctx.fillRect(vx, vy, 3, 1);
      }
      // void anomaly
      const st = _state();
      const day = (st && st.world && st.world.day) || 1;
      if (day >= 4 && !(st.world.flags || {}).rd_radar_dead) {
        const ax = 150 + Math.sin(t * 0.02) * 14;
        const pulse = 10 + Math.sin(t * 0.08) * 3;
        const g = ctx.createRadialGradient(ax, 80, 2, ax, 80, pulse + 9);
        g.addColorStop(0, "rgba(255,70,70,0.7)");
        g.addColorStop(1, "rgba(120,10,10,0)");
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(ax, 80, pulse + 9, 0, Math.PI * 2); ctx.fill();
      }
      // sweep
      ctx.fillStyle = "rgba(120,255,170,0.16)";
      ctx.fillRect((t * 2.4) % 300, 0, 2, 160);
      // scanlines
      ctx.fillStyle = "rgba(0,0,0,0.25)";
      for (let y = 1; y < 160; y += 3) ctx.fillRect(0, y, 300, 1);
      _readouts();
      _anim = requestAnimationFrame(step);
    };
    step();
  }

  return {
    toggle() { this.isVisible() ? this.hide() : this.show(); },
    isVisible() { return _el && !_el.classList.contains("hidden"); },
    show() {
      if (!_el) _el = _create();
      _el.classList.remove("hidden");
      if (window.SFX) { SFX.ensure(); SFX.beep(880, 0.05, "square", 0.03); }
      if (!_anim) _loop();
    },
    hide() {
      if (_el) _el.classList.add("hidden");
      if (_anim) { cancelAnimationFrame(_anim); _anim = 0; }
    },
    update(state) {
      // keep readouts fresh while open
      if (this.isVisible()) _readouts();
    },
  };
})();

document.addEventListener("DOMContentLoaded", () => { /* lazily created on show */ });
window.WeatherStation = WeatherStation;
