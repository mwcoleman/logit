import reflex as rx
from collections import defaultdict
import pandas as pd
import os


class LoggedExercise(rx.Model, table=True):
    idx: int
    ename: str
    enum: int
    reps: int
    weight: float
    _li: list

    def __init__(self, idx, ename, enum, reps, weight):
        self.idx = idx
        self.ename = ename
        self.enum = enum
        self.reps = reps
        self.weight = weight
        self._li = [idx, ename, enum, reps, weight]

    def __repr__(self) -> str:
        return f'{self.idx},{self.ename},{self.enum},{self.reps},{self.weight}'
    
    def __iter__(self):
        return self._li

    def __getitem__(self, item):
        return self._li[item]

class WState(rx.State):
    
    logged_exercises: list[LoggedExercise]
    # [
    #     LoggedExercise(1,"Testing", 1, 5, 100),
    # ]

    exercise_names: list[str] = [
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

    current_exercise: str = exercise_names[0]

    total_set_number: int = 1
    exercise_counter: dict = {ename:0 for ename in exercise_names}
    reps: int = 0
    weight: float = 0
    
    def delete_logged_exercise(self, idx:int):
        # Adjust other exercise idx
        for ex in self.logged_exercises[idx:]:
            ex.idx -= 1
        # Adjust current total sets
        self.total_set_number -= 1

        del self.logged_exercises[idx - 1] 
        

    def add_logged_exercise(self):
        self.exercise_counter[self.current_exercise] += 1
        
        self.logged_exercises.append(
            LoggedExercise(
                self.total_set_number,
                self.current_exercise,
                self.exercise_counter[self.current_exercise],
                self.reps,
                self.weight
            )
        )
        self.total_set_number += 1
    
    # def exercise_details(ex: LoggedExercise) -> list:
    #     return [ex.idx, ex.ename, ex.enum, ex.reps, ex.weight]


# class WState(rx.State):
#     # TODO: Reflex doesn't have defaultdict implementation? This defaults to reflex.vars.dict
    
#     total_set_number: int = 0
#     sets: defaultdict = defaultdict(int)
#     reps: int = 0
#     weight: float = 0

#     exercises: list[str] = [
#         "deadlift",
#         "benchpress",
#         "weighted pull-up",
#         "single arm press",
#         "kb swing",
#         "HB: SC 20mm",
#         "HB: IMR 20mm",
#         "HB: MRP 20mm",
#         "HB: IM 20mm",
#         "HB: MR 20mm"
#     ]

#     exercise: str = exercises[0]

#     session_history: list[tuple[int,int,float]]

#     # @rx.var
#     def current_exercise(self, exercise: str):
#         self.exercise = exercise
#         # return self.exercises[self.exptr]
    
#     def set_reps(self, reps: int):
#         self.reps = reps

#     def set_weight(self, weight: float):
#         self.weight = weight

#     def delete_row(self, set_number):
#         self.total_set_number -= 1
#         self.session_history.pop(set_number - 1)
#         self.session_history = [(idx + 1, *row[1:]) for idx, row in enumerate(self.session_history)]


#     def add_set(self):
#         print(type(self.sets))
#         # exercise = self.current_exercise()
#         self.total_set_number += 1
#         try:
#             self.sets[self.exercise] += 1
#         except:
#             self.sets[self.exercise] = 1

#         self.session_history.append((self.total_set_number, self.exercise, self.sets[self.exercise], self.reps, self.weight))
    
