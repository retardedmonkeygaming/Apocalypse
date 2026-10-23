function updateUI(state) {
  document.getElementById("day").textContent = state.world.day;
  document.getElementById("health").textContent = state.player.health;
  document.getElementById("infection").textContent = state.player.infection;
  document.getElementById("morale").textContent = state.player.morale;
  document.getElementById("location").textContent = state.world.location;

  document.getElementById("food").textContent = state.player.food;
  document.getElementById("water").textContent = state.player.water;
  document.getElementById("ammo").textContent = state.player.ammo;
  document.getElementById("scrap").textContent = state.player.scrap;
  document.getElementById("medkits").textContent = state.player.medkits;

  const event = state.current_event;
  if (event) {
    document.getElementById("event-title").textContent = event.title;
    document.getElementById("event-text").textContent = event.text;

    // Update button labels
    const keyToBtn = { red: "btn-red", blue: "btn-blue", green: "btn-green", yellow: "btn-yellow" };
    event.choices.forEach(c => {
      const btn = document.getElementById(keyToBtn[c.key]);
      if (btn) btn.textContent = c.label;
    });
  }

  // Log
  const logEl = document.getElementById("log");
  logEl.innerHTML = state.log.map(l => `<div>${l}</div>`).join("");
  logEl.scrollTop = logEl.scrollHeight;

  // Night class
  document.body.classList.toggle("night", state.world.is_night);

  // Game over
  if (state.game_over) {
    document.getElementById("event-title").textContent = state.victory ? "EXTRACTION" : "YOU DIED";
    document.getElementById("event-text").textContent = state.victory
      ? "You survived long enough for rescue."
      : "The infection took you... or the dead did.";
  }
}