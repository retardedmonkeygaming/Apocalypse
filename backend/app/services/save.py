from backend.app.core.state import GameState


class SaveService:
    def save(self, state: GameState):
        state.save()

    def load(self) -> GameState:
        return GameState.load()
