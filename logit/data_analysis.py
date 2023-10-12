'''Contains scripts for processing dataframes, generating and returning figures.'''

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
from plotly.subplots import make_subplots
from functools import partial



def estimate_1rm(reps, kg):
    # Brzycki formula
    return kg / (1.0278 - 0.0278 * reps)

# to_dt = partial()
def to_dt(text_date):
    return datetime.strptime(text_date, "%d-%m-%y")


# TODO: Currently this cant be a computed var, 'cant pickle'. but the other figure can be....????
def load_intensity_figure(ename: str, df: pd.DataFrame) -> go.Figure:
    # pass
    '''
    Generates a twin-y scatter plot of sesion load (reps * vol) and intensity (max kg)
    df: LoggedExercise table extract as dataframe
    ename: string of exercise
    returns: go.Figure
    '''
    

    # Groupby date and generate statistics
    try:
        df['date'] = df.date.apply(lambda x: datetime.strptime(x, "%d-%m-%y"))
    except:
        pass
    df['load'] = df.reps * df.kg

    grp = df.groupby(['date','ename'], as_index=False).aggregate(
        vol=("reps", 'sum'),
        intensity=("kg", 'max'),
        load=("load",'sum')
    )

    # What we care about and corresponding labels
    metrics = ['load', 'intensity']
    y_label = ['Total Kg Moved', 'Max Kg Moved']

    data = grp[grp.ename==ename]

    fig = make_subplots(specs=[[{'secondary_y':True}]])

    # Add traces
    # Second trace gets secondary y flag
    for i,metric in enumerate(metrics):
        fig.add_trace(
            go.Scatter(
                x=data['date'].values, 
                y=data[metric], 
                name=metric, 
            ),
            secondary_y=i==1
        )
        
        fig.update_yaxes(title_text=y_label[i], secondary_y=(i==1))

    fig.update_layout(title_text=ename)
    fig.update_xaxes(title_text='Date')

    
    return fig

def progression_figure(
        enames: List[str], 
        exercise_df: pd.DataFrame,
        benchmark_df: pd.DataFrame,
        progression_rate: tuple = (2.5,5)) -> go.Figure:
    '''
    df: dataframe extract of LoggedExercise table (all)
    proj: dataframe extract of LoggedBenchmark table (all)
    ename: string of exercise to display
    progression_rate: % band to project from previous benchmark result
    '''
    fig = go.Figure()
    try:
        exercise_df['date'] = exercise_df.date.apply(lambda x: datetime.strptime(x,  "%d-%m-%y"))
        benchmark_df['date'] = benchmark_df.date.apply(lambda x: datetime.strptime(x, "%d-%m-%y"))
    except Exception as e:
        pass
    
    for ename in enames: 
        df_filtered = exercise_df[exercise_df.ename==ename]
        # Dummy
        proj = benchmark_df[benchmark_df.ename==ename]
        if len(proj) == 0:
            print(f"No Benchmarks {ename}")
            return go.Figure()
        proj = proj.sort_values(by='date', ascending=False).iloc[0,:]
        # print(proj.date) 
        df = df_filtered.groupby('date', as_index=False).aggregate(
            max_kg=('kg','max')
            )
        # obtain reps for max kg
        df['reps'] = df.max_kg.apply(lambda x: df_filtered[df_filtered.kg==x]['reps'].max())
        
        # Convert to 1rm estimate
        
        df['1rm_estimate'] = df.apply(lambda x: estimate_1rm(x.reps, x.max_kg), axis=1)

        future_dates = [proj.date + timedelta(weeks=x) for x in range(8)]
        # print(future_dates)
        l, h = (p/100 for p in progression_rate) if any((p > 1 for p in progression_rate)) else progression_rate

        future_kg_min = [proj.kg + (i * l) * proj.kg for i in range(len(future_dates))]
        future_kg_max = [proj.kg + (i * h) * proj.kg for i in range(len(future_dates))]
        
        proj = pd.DataFrame({'date':future_dates, 'kg_min':future_kg_min, 'kg_max':future_kg_max})

        try:
            # fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    name=f'Logged {ename}',
                    x=df['date'].values, 
                    y=df['1rm_estimate'],
                    showlegend=False,
                )#, mode='lines')
            )
            # From https://plotly.com/python/continuous-error-bars/
            fig.add_trace(
                go.Scatter(
                    name=f'{ename} {progression_rate[0]}%', 
                    x=proj['date'].values, 
                    y=proj['kg_min'],
                    mode='lines',
                    showlegend=False,
                    marker=dict(color='#444'),
                    line=dict(width=0),
                    # hoverinfo='skip'
                )
            ),
            fig.add_trace(
                go.Scatter(
                    name=f'{ename} {progression_rate[1]}%', 
                    x=proj.date.values, 
                    y=proj['kg_max'], 
                    fill='tonexty', 
                    fillcolor='rgba(68,68,68,0.3)',
                    mode='lines',
                    showlegend=False,
                    marker=dict(color='#444'),
                    line=dict(width=0),
                    # hoverinfo='skip'
                    )#,, )
            )
        except Exception as e:
            print(f'Exception during projected figure! {e}')

        fig.update_layout(title_text="Progression Plan")

    return fig
