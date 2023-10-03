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
    rpe: int
    # _li: list

    def __init__(self, created_datetime, ename, enum, reps, weight, rpe):
        # self.idx: int = idx
        self.created_datetime: str = created_datetime
        self.ename: str = ename
        self.enum: int = enum
        self.reps: int = reps
        self.weight: float = weight
        self.rpe: int = rpe
        # self._li = [created_datetime, ename, enum, reps, weight]

    def _li(self) -> List:
        return [self.created_datetime, self.ename, self.enum, self.reps, self.weight, self.rpe]
    
    def __repr__(self) -> str:
        return f'{self.ename},{self.enum},{self.reps},{self.weight}'
    
    def __iter__(self):
        return self._li

    def __getitem__(self, item):
        return self._li[item]

class LoggedBenchmark(rx.Model, table=True):
    """
    Table model for storing benchmarked strength exercises. Mimics LoggedExercise, but not subclassed.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    # TODO: This was going to be server-created but too many issues with sqlite..
    created_datetime: str
    ename: str
    enum: int 
    reps: int # 1RM, 2RM etc. 
    weight: float 
    rpe: int # doesn't quite make sense, probably always 10. but keeps front end easy.

    def __init__(self, created_datetime, ename, enum, reps, weight, rpe):
        self.created_datetime: str = created_datetime
        self.ename: str = ename
        self.enum: int = enum
        self.reps: int = reps
        self.weight: float = weight
        self.rpe: int = rpe

    def _li(self) -> List:
        return [self.created_datetime, self.ename, self.enum, self.reps, self.weight, self.rpe]
    
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

    date_range: List[str] = [(date.today() - timedelta(days=x))
                              .strftime("%d-%m-%y")
                              for x in range(365)]


    # total_set_number: int = 1
    # exercise_counter: dict = {ename:0 for ename in exercise_names}
    
    # Each key represents a different exercise_selector state var
    current_exercise: Dict[int, str] = {1: exercise_names[0], 2: exercise_names[1], 3: exercise_names[1]}
    reps: Dict[int, str] = {1: 5, 2: 5, 3: 5}
    weight: Dict[int, float] = {1: 70, 2: 70, 3: 70}
    rpe: Dict[int, int] = {1:8, 2:8, 3:8}

    log_date: Dict[int, str] = {1: date.today().strftime("%d-%m-%y"),
                                2: date.today().strftime("%d-%m-%y"),
                                3: date.today().strftime("%d-%m-%y")}

    is_benchmark: Dict[int, bool] = {1:False, 2:False, 3:False}

    # TODO: future- Used for selecting dates when returning log
    datepicker: str = None

    visualise_ename: str = "Scan"

    # Overload the set_... methods to specify the row_id of the selector
    def set_current_exercise(self, selector_id: int, exercise: str):
        self.current_exercise[selector_id] = exercise

    def set_rpe(self, selector_id: int, rpe: int):
        self.rpe[selector_id] = rpe

    def set_weight(self, selector_id: int, weight: float):
        self.weight[selector_id] = weight

    def set_reps(self, selector_id: int, reps: int):
        self.reps[selector_id] = reps

    def set_log_date(self, selector_id: int, datestr: str):
        self.log_date[selector_id] = datestr

    def set_is_benchmark(self, selector_id, flag):
        self.is_benchmark[selector_id] = flag

    # async def set_rest(self, selector_id: int):
        #     self.rest[selector_id] = 10
    #     await self.tick(selector_id)


    def delete_logged_exercise(self, id:int, benchmarks: bool):
        
        model = LoggedBenchmark if benchmarks else LoggedExercise
        
        with rx.session() as session:
            statement = select(model).where(model.id == id)
            result = session.exec(statement).first()
            session.delete(result)
            session.commit()
    
    @staticmethod
    def today_date() -> str:
        return date.today().strftime("%d-%m-%y") 

    def add_logged_exercise(self, selector_id: int):

        with rx.session() as session:
            model = LoggedBenchmark if self.is_benchmark[selector_id] else LoggedExercise

            matching_exercises = (
                session.query(model)
                .filter(model.ename.contains(self.current_exercise[selector_id]))
                .filter(model.created_datetime.contains(self.today_date()))
                .all()
            )
                
            
            session.add(
                model(
                    created_datetime=self.log_date[selector_id],
                    ename=self.current_exercise[selector_id],
                    enum=len(matching_exercises),
                    reps=self.reps[selector_id],
                    weight=self.weight[selector_id],
                    rpe=self.rpe[selector_id]
                )
            )
            session.commit()

    
    def _log_as_dataframe(self, model=LoggedExercise) -> pd.DataFrame:
        
        with rx.session() as session:
            ex_list = session.query(LoggedExercise).all()

        ex_list = [ex._li() for ex in ex_list]  

        data_columns = ["date", "ename", "enum", "reps", "kg", "rpe"]
        data_types = {'ename':str, 'enum': int, 'reps': int, 'kg': float, 'rpe': int}

        df = pd.DataFrame(
            ex_list,
            columns=data_columns
        ).astype(data_types)
        
        return df
    
    ### COMPUTED VARIABLES

    # @rx.var
    # def current_exercise_has_been_logged(self) -> Dict[int, bool]:
    #     """
    #     Holds flags for if each of the current exercises has ben recorded as an exercise and benchmark
    #     """
    #     e_df = self._log_as_dataframe()
        
    #     return {selector_id: len(e_df[e_df.ename==ename]) > 0
    #             for selector_id, ename in self.current_exercise.items()}
    
    # @rx.var
    # def current_exercise_has_been_benchmarked(self) -> Dict[int, bool]:
    #     """
    #     Holds flags for if each of the current exercises has ben recorded as an exercise and benchmark
    #     """
    #     e_df = self._log_as_dataframe(model=LoggedBenchmark)
        
    #     return {selector_id: len(e_df[e_df.ename==ename]) > 0
    #             for selector_id, ename in self.current_exercise.items()}


    @rx.var
    def log_as_dataframe(self, model=LoggedExercise) -> pd.DataFrame:
        return self._log_as_dataframe()
    
    @rx.var
    def iterate_logged_exercises(self) -> List[LoggedExercise]:
        # Computed var processed each time 
        with rx.session() as session:
            
            # Can also select using sqlmethod approach
            # for now we follow reflex method as per https://reflex.dev/docs/database/queries/
            try:
                if self.datepicker is None:
                    logged_exercises = session.query(LoggedExercise).all()

                else:
                    logged_exercises = (
                        session.query(LoggedExercise)
                        .filter(LoggedExercise.created_datetime.contains(self.datepicker))
                        .all()
                    )
            except:
                return []

            logged_exercises = sorted(
                logged_exercises, 
                key= lambda ex: datetime.strptime(ex.created_datetime, "%d-%m-%y"),
                reverse=True,
            )


            return logged_exercises
    
    @rx.var
    def iterate_logged_benchmarks(self) -> List[LoggedBenchmark]:
        """
        Return a list of all logged benchmark exercises 
        """
        # Computed var processed each time 
        with rx.session() as session:
            try:
                if self.datepicker is None:
                    
                    logged_exercises = session.query(LoggedBenchmark).all()

                else:
                    logged_exercises = (
                        session.query(LoggedBenchmark)
                        .filter(LoggedBenchmark.created_datetime.contains(self.datepicker))
                        .all()
                        )
            except Exception as e:
                print(e)
                return []

            return sorted(
                logged_exercises, 
                key= lambda ex: datetime.strptime(ex.created_datetime, "%d-%m-%y"),
                reverse=True,
            )
        
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
    def projected_progression_figure(self) -> go.Figure:# Dict[int, go.Figure]:
        """
        Generate a typical progression from last benchmark for selected exercises
        """
        df = self._log_as_dataframe(model=LoggedExercise)
        proj = self._log_as_dataframe(model=LoggedExercise)
        
        return progression_figure(self.current_exercise.values(), df, proj)
       
    
        
    # Need to store layout in seperate computed var,
    # can't access it in front end
    @rx.var
    def projected_layout(self) -> Dict:
        return self.projected_progression_figure.to_dict()['layout']




        


        

