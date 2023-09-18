import reflex as rx
from collections import defaultdict
import os
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional
class LoggedExercise(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    idx: int
    ename: str
    enum: int
    reps: int
    weight: float
    # _li: list

    def __init__(self, idx, ename, enum, reps, weight):
        self.idx: int = idx
        self.ename: str = ename
        self.enum: int = enum
        self.reps: int = reps
        self.weight: float = weight
        # self._li = [idx, ename, enum, reps, weight]

    def __repr__(self) -> str:
        return f'{self.idx},{self.ename},{self.enum},{self.reps},{self.weight}'
    
    # def __iter__(self):
    #     return self._li

    # def __getitem__(self, item):
    #     return self._li[item]

class WState(rx.State):
    
    # logged_exercises: list[LoggedExercise]


    exercise_names: list[str] = [
        "Scan",
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
    
    def delete_logged_exercise(self, id:int):
        with rx.session() as session:
            statement = select(LoggedExercise).where(LoggedExercise.id == id)
            result = session.exec(statement).first()
            session.delete(result)
            session.commit()


        # # Adjust other exercise idx
        # for ex in self.logged_exercises[idx:]:
        #     ex.idx -= 1
        # # Adjust current total sets
        # self.total_set_number -= 1

        # del self.logged_exercises[idx - 1] 
        

    def add_logged_exercise(self):
        self.exercise_counter[self.current_exercise] += 1

        new_exercise = LoggedExercise(
                self.total_set_number,
                self.current_exercise,
                self.exercise_counter[self.current_exercise],
                self.reps,
                self.weight
        )
        # Add to database
        with rx.session() as session:
            session.add(
                new_exercise
            )
            session.commit()
            # print(new_exercise.id)

        # self.logged_exercises.append(
        #     LoggedExercise(
        #         self.total_set_number,
        #         self.current_exercise,
        #         self.exercise_counter[self.current_exercise],
        #         self.reps,
        #         self.weight
        #     )
        # )
        self.total_set_number += 1
    
    @rx.var
    def iterate_logged_exercises(self) -> list[LoggedExercise]:
        # Computed var processed each time 
        with rx.session() as session:
            
            ## Possible to do it using sqlmodel methods:
            # statement = select(LoggedExercise)
            # results = session.exec(statement)
            # print(results)
            # for r in results:
            #     print(r)

            ## But for now we follow reflex method as per https://reflex.dev/docs/database/queries/
            logged_exercises = session.query(LoggedExercise).all()
            return logged_exercises


    
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
    
