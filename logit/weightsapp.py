import reflex as rx
from collections import defaultdict
import os
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional
from datetime import date, datetime
class LoggedExercise(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # idx: int
    ename: str
    enum: int
    reps: int
    weight: float
    # _li: list

    def __init__(self, ename, enum, reps, weight):
        # self.idx: int = idx
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
        # TODO: Not necessary once date/name db filtering implemented
        self.exercise_counter[self.current_exercise] += 1

        new_exercise = LoggedExercise(
                # self.total_set_number,
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


    
 