import reflex as rx
from collections import defaultdict

class WState(rx.State):
    # TODO: Reflex doesn't have defaultdict implementation? This defaults to reflex.vars.dict
    total_set_number: int = 0

    sets: defaultdict = defaultdict(int)
    reps: int = 0
    weight: float = 0

    exercises: list[str] = [
        "deadlift",
        "benchpress",
        "weighted pull-up",
        "single arm press",
        "kb swing",
        "HB: SC 20mm",
        "HB: IMR 20mm",
        "HB: MRP 20mm",
        "HB: IM 20mm",
        "HB: MR 20mm"
    ]

    exercise: str = exercises[0]

    session_history: list[tuple[int,int,float]]

    # @rx.var
    def current_exercise(self, exercise: str):
        self.exercise = exercise
        # return self.exercises[self.exptr]
    
    def set_reps(self, reps: int):
        self.reps = reps

    def set_weight(self, weight: float):
        self.weight = weight

    def delete_row(self, set_number):
        print("BLAH")
        self.total_set_number -= 1
        self.session_history.pop(set_number - 1)
        self.session_history = [(idx + 1, *row[1:]) for idx, row in enumerate(self.session_history)]


    def add_set(self):
        print(type(self.sets))
        # exercise = self.current_exercise()
        self.total_set_number += 1
        try:
            self.sets[self.exercise] += 1
        except:
            self.sets[self.exercise] = 1

        self.session_history.append((self.total_set_number, self.exercise, self.sets[self.exercise], self.reps, self.weight))
    