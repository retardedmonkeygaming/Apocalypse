const socket = new GameSocket(`ws://${location.host}/ws`);

socket.on("state", updateUI);
socket.on("status", (s) => {
  document.getElementById("status").textContent = s;
});

socket.connect();

// Button clicks → same as physical buttons
document.querySelectorAll(".choice").forEach(btn => {
  btn.addEventListener("click", () => {
    const key = btn.dataset.key;
    btn.classList.add("pressed");
    setTimeout(() => btn.classList.remove("pressed"), 150);

    if (key === "confirm") {
      socket.send({ action: "medkit" });
    } else {
      socket.send({ action: "choice", key });
    }
  });
});

document.getElementById("new-game").addEventListener("click", () => {
  if (confirm("Start a new survival run?")) {
    socket.send({ action: "new_game" });
  }
});

// Keyboard support (for development)
document.addEventListener("keydown", (e) => {
  const map = { "1": "red", "2": "blue", "3": "green", "4": "yellow", " ": "confirm" };
  if (map[e.key]) {
    const key = map[e.key];
    if (key === "confirm") socket.send({ action: "medkit" });
    else socket.send({ action: "choice", key });
  }
});