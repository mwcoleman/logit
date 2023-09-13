import reflex as rx


class State(rx.state):
    set: int = 0
    reps: int = 0
    weight: float = 0

    session_history: list[tuple[set, reps, weight]]

    def set_setnumbers(self, reps: int, weight: float):
        self.reps = reps
        self.weight = weight

    def add_set(self):
        set += 1
        self.session_history.append()