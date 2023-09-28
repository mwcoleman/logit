import plotly.express as px
import plotly.graph_objects as go

import asyncio
import reflex as rx
from collections import defaultdict
import os
from sqlmodel import Field, Session, SQLModel, create_engine, select, TIMESTAMP, Column, text
from typing import Optional, List, Dict
from datetime import datetime, date, timedelta
from sqlalchemy.sql import func
from sqlalchemy import Column, DateTime
import pandas as pd
import numpy as np

try:
    from logit.data_analysis import progression_figure, load_intensity_figure
except:
    # For notebook debug
    from data_analysis import progression_figure, load_intensity_figure

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

    def __init__(self, created_datetime, ename, enum, reps, weight):
        # self.idx: int = idx
        self.created_datetime: str = created_datetime
        self.ename: str = ename
        self.enum: int = enum
        self.reps: int = reps
        self.weight: float = weight
        # self._li = [created_datetime, ename, enum, reps, weight]

    def _li(self) -> List:
        return [self.created_datetime, self.ename, self.enum, self.reps, self.weight]
    
    def __repr__(self) -> str:
        return f'{self.ename},{self.enum},{self.reps},{self.weight}'
    
    def __iter__(self):
        return self._li

    def __getitem__(self, item):
        return self._li[item]

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


    # total_set_number: int = 1
    # exercise_counter: dict = {ename:0 for ename in exercise_names}
    
    # Each key represents a different exercise_selector state var
    current_exercise: Dict[int, str] = {1: exercise_names[0], 2: exercise_names[0], 3: exercise_names[0]}
    reps: Dict[int, str] = {1: 5, 2: 5, 3: 5}
    weight: Dict[int, float] = {1: 70, 2: 70, 3: 70}

    is_benchmark: Dict[int, bool] = {1:False, 2:False, 3:False}
    # fig: go.Figure = None

    # Used for selecting dates when returning log
    datepicker: str = None

    visualise_ename: str = "Scan"

    # Overload the set_... methods to specify the row_id of the selector
    def set_current_exercise(self, selector_id: int, exercise: str):
        self.current_exercise[selector_id] = exercise

    def set_weight(self, selector_id: int, weight: float):
        self.weight[selector_id] = weight

    def set_reps(self, selector_id: int, reps: int):
        self.reps[selector_id] = reps

    
    def computed_current_exercise(self, row_id) -> str:
        return self.current_exercise[row_id]

    # async def set_rest(self, selector_id: int):
    #     self.rest[selector_id] = 10
    #     await self.tick(selector_id)


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
        # self.exercise_counter[self.current_exercise[selector_id]] += 1
        
        # for k,v in self.exercise_counter.items():
        #     if k=="Scan" or k=="deadlift":
        #         print(f"{k} : {v}")
        
        # Add to database
        with rx.session() as session:
            
            matching_exercises = (
                session.query(LoggedExercise)
                .filter(LoggedExercise.ename.contains(self.current_exercise[selector_id]))
                .filter(LoggedExercise.created_datetime.contains(self.today_date()))
                .all()
            )
                
            
            session.add(
                LoggedExercise(
                # self.total_set_number,
                # date.today().strftime("%d-%m-%y"),
                    created_datetime=self.today_date(),
                    ename=self.current_exercise[selector_id],
                    enum=len(matching_exercises),#self.exercise_counter[self.current_exercise[selector_id]],
                    reps=self.reps[selector_id],
                    weight=self.weight[selector_id]#
                )
            )
            session.commit()
            # print(new_exercise.id)
        # self.countdown(selector_id)
        # self.total_set_number += 1
    
    def _log_as_dataframe(self, model=LoggedExercise) -> pd.DataFrame:
        
        with rx.session() as session:
            ex_list = session.query(LoggedExercise).all()

        ex_list = [ex._li() for ex in ex_list]  

        data_columns = ["date", "ename", "enum", "reps", "kg"]
        data_types = {'ename':str, 'enum': int, 'reps': int, 'kg': float}

        df = pd.DataFrame(
            ex_list,
            columns=data_columns
        ).astype(data_types)
        
        return df
    
    ### COMPUTED VARIABLES

    @rx.var
    def log_as_dataframe(self, model=LoggedExercise) -> pd.DataFrame:
        return self._log_as_dataframe()
    
    @rx.var
    def iterate_logged_exercises(self) -> List[LoggedExercise]:
        # Computed var processed each time 
        with rx.session() as session:
            
            ## Possible to do it using sqlmodel methods:
            # statement = select(LoggedExercise)
            # results = session.exec(statement)
            # print(results)
            # for r in results:
            #     print(r)

            ## But for now we follow reflex method as per https://reflex.dev/docs/database/queries/
            
            if self.datepicker is None:
                logged_exercises = session.query(LoggedExercise).all()

            else:
                logged_exercises = (
                    session.query(LoggedExercise)
                    .filter(LoggedExercise.created_datetime.contains(self.datepicker))
                    .all()
                )
            
            return logged_exercises[::-1]
    
    # We put this here as a computed var as we want it to re-compute any time the
    # state var (current_exercise) values change.
    # Also we need to operate on the current_exercise var which can't be done outside state easily
    @rx.var
    def last_logged_exercise_max(self) -> List[LoggedExercise]:
        last_logged_exercises = []
        with rx.session() as session:
            for selector_id, ename in self.current_exercise.items():
                if selector_id > 2:
                    break
                statement = (
                    select(LoggedExercise)
                    .where(LoggedExercise.ename == ename)
                    .where(LoggedExercise.created_datetime != WState.today_date())
                )
                results = session.exec(statement).all()
                
                # Need this or else error when no past results (list empty)
                if len(results) == 0:
                    continue
                date = results[-1].created_datetime

                results = [r for r in results if r.created_datetime == date]
                results = sorted(results, key= lambda ex: ex.weight, reverse=True)
                last_logged_exercises.append(results[0])

        return last_logged_exercises
    
    # @rx.var
    # def _figure_load_intensity(self) -> go.Figure:
    #     print("HI")
    #     return load_intensity_figure(self._log_as_dataframe())

    ## TODO: Needs to be in state to access current_exercise
    @rx.var
    def projected_progression_figure(self) -> go.Figure:

        df = self._log_as_dataframe(model=LoggedExercise)
        proj = self._log_as_dataframe(model=LoggedExercise)
        return progression_figure('deadlift', df, proj)
        
    # Need to store layout in seperate computed var,
    # can't access it in front end
    @rx.var
    def projected_layout(self) -> Dict:
        return self.projected_progression_figure.to_dict()['layout']




        


        

