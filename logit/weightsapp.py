import reflex as rx
from collections import defaultdict
import os
from sqlmodel import Field, Session, SQLModel, create_engine, select, TIMESTAMP, Column, text
from typing import Optional, List, Dict
from datetime import datetime, date
from sqlalchemy.sql import func
from sqlalchemy import Column, DateTime
# from datetime import date, datetime
class LoggedExercise(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # TODO: This was going to be server-created but too many issues with sqlite..
    created_datetime: str
    # idx: int
    ename: str
    enum: int
    reps: int
    weight: float
    # _li: list

    def __init__(self, log_date, ename, enum, reps, weight):
        # self.idx: int = idx
        self.created_datetime: str = log_date
        self.ename: str = ename
        self.enum: int = enum
        self.reps: int = reps
        self.weight: float = weight
        # self._li = [idx, ename, enum, reps, weight]

    def __repr__(self) -> str:
        return f'{self.ename},{self.enum},{self.reps},{self.weight}'
    
    # def __iter__(self):
    #     return self._li

    # def __getitem__(self, item):
    #     return self._li[item]

class WState(rx.State):
    

    # exercise_selector_count: int = 1

    exercise_names: List[str] = [
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


    total_set_number: int = 1
    exercise_counter: dict = {ename:0 for ename in exercise_names}
    
    current_exercise: Dict[int, str] = {1: exercise_names[0], 2: exercise_names[0], 3: exercise_names[0]}
    reps: Dict[int, str] = {1: 0, 2: 0, 3: 0}
    weight: Dict[int, float] = {1: 0, 2: 0, 3: 0}


    # def increment_exercise_selector_count(self):
    #     self.exercise_selector_count += 1
    
    # def get_selector_count_range(self) -> List[int]:
    #     return [i for i in range(self.exercise_selector_count)]

    # Overload the set_... methods to specify the row_id of the selector
    def set_current_exercise(self, selector_id: int, exercise: str):
        self.current_exercise[selector_id] = exercise

    def set_weight(self, selector_id: int, weight: float):
        self.weight[selector_id] = weight
        
    def set_reps(self, selector_id: int, reps: int):
        self.reps[selector_id] = reps


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
    @staticmethod
    def today_date() -> str:
        return date.today().strftime("%d-%m-%y") 

    def add_logged_exercise(self, selector_id: int):
        # TODO: Not necessary once date/name db filtering implemented
        self.exercise_counter[self.current_exercise[selector_id]] += 1

        new_exercise = LoggedExercise(
                # self.total_set_number,
                # date.today().strftime("%d-%m-%y"),
                self.today_date(),
                self.current_exercise[selector_id],
                self.exercise_counter[self.current_exercise[selector_id]],
                self.reps[selector_id],
                self.weight[selector_id]
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
    def iterate_logged_exercises(self, date: str = None) -> List[LoggedExercise]:
        # Computed var processed each time 
        with rx.session() as session:
            
            ## Possible to do it using sqlmodel methods:
            # statement = select(LoggedExercise)
            # results = session.exec(statement)
            # print(results)
            # for r in results:
            #     print(r)

            ## But for now we follow reflex method as per https://reflex.dev/docs/database/queries/
            
            if date is None:
                logged_exercises = (
                    session.query(LoggedExercise)
                    .filter(LoggedExercise.created_datetime.contains(self.today_date()))
                    .all()
                )
            else:
                logged_exercises = session.query(LoggedExercise).all()

            return logged_exercises


    
class VisualiseState(rx.State):
