/* WebAudio stingers — mirrors the Pi buzzer when you are on a laptop. */
const SFX = {
  ctx: null,
  ensure() {
    if (!this.ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (AC) this.ctx = new AC();
    }
    if (this.ctx && this.ctx.state === "suspended") this.ctx.resume();
    return this.ctx;
  },
  beep(freq, dur, type, gain) {
    const c = this.ensure();
    if (!c) return;
    const o = c.createOscillator();
    const g = c.createGain();
    o.type = type || "square";
    o.frequency.value = freq;
    g.gain.value = gain || 0.04;
    o.connect(g);
    g.connect(c.destination);
    o.start();
    g.gain.exponentialRampToValueAtTime(0.0001, c.currentTime + dur);
    o.stop(c.currentTime + dur + 0.02);
  },
  play(fx) {
    if (!fx) return;
    if (fx === "success" || fx === "craft" || fx === "heal" || fx === "join") {
      this.beep(523, 0.08);
      setTimeout(() => this.beep(659, 0.08), 80);
      setTimeout(() => this.beep(784, 0.12), 160);
    } else if (fx === "danger" || fx === "shake" || fx === "hit") {
      this.beep(180, 0.12, "sawtooth", 0.05);
      setTimeout(() => this.beep(90, 0.18, "square", 0.05), 80);
    } else if (fx === "night") {
      this.beep(220, 0.25, "triangle", 0.04);
      setTimeout(() => this.beep(174, 0.35, "triangle", 0.03), 200);
    } else if (fx === "infect") {
      this.beep(300, 0.08, "square", 0.03);
      setTimeout(() => this.beep(240, 0.1, "square", 0.03), 90);
    } else if (fx === "gun") {
      this.beep(90, 0.06, "sawtooth", 0.07);
    } else if (fx === "fire") {
      this.beep(140, 0.2, "sawtooth", 0.05);
    } else if (fx === "miss" || fx === "flee") {
      this.beep(200, 0.08, "triangle", 0.03);
    }
  },
};
