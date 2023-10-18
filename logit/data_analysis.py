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
from typing import Tuple, List, Dict, Set


def estimate_1rm(reps, kg):
    # Brzycki formula
    return kg / (1.0278 - 0.0278 * reps)

# to_dt = partial()
def to_dt(text_date):
    return datetime.strptime(text_date, "%d-%m-%y")

def this_week_dates() -> Tuple[datetime, datetime]:
    end = datetime.today()
    start = end - timedelta(days=end.weekday())
    return (start, end)

def last_week_dates() -> Tuple[datetime, datetime]:
    end = datetime.today() - \
            timedelta(days=datetime.today().weekday())
    start = end - timedelta(days=7)
    return (start, end)

def summary_daterange_df(
        df,
        start: datetime, 
        end: datetime,
        ename: Set[str] = None,
        return_summary=True
    ) -> rx.Component:
    """
    Filter a dataframe by date range, and
    if return_summary, returns a grouped df with summed volume by exercise,
    else return raw df
    """
    # df = log_as_df()
    try:
        df['date'] = df.date.apply(lambda x: to_dt(x))
    except TypeError:
        # Already dt
        pass
    print(start, end)
    df = df[(df.date >= start) & (df.date < end)]
    df.loc[:,'date'] = df.date.apply(lambda x: x.strftime("%d-%m-%y"))
    
    if ename is not None:
        df = df[df.ename.isin(ename)]

    grpby = df.groupby(['ename', 'kg'], as_index=False).aggregate(
        sets=("enum", lambda x: len(set(x))),
        # max_kg=("kg", "max"),
        volume=("reps", "sum")
    ).rename(columns={'ename':'exercise'})
    
    return grpby if return_summary else df

def stat_block_summary(
        raw_df: pd.DataFrame,
        ename: Set[str],
        this_week_range: Tuple[datetime],
        last_week_range: Tuple[datetime] = None,
        stat: str = 'load',
        comparison: str = 'absolute'
        ) -> Tuple[str, float, float]:
    '''
    Compute, for ename, 1) single value summary statistic for this week (e.g. load)
    and 2) relative change (%)
    stat is one of 'load', 'max_kg', 'volume', 'vol_at_max'
    df is raw log_as_df()
    '''
    def _stat_value(df, stat):
        if stat == 'load':
            stat_val = (df.reps * df.kg).sum()
        elif stat == 'volume':
            stat_val = df.reps.sum()
        elif stat == 'max_kg':
            stat_val = df.kg.max()
        else:
            stat_val = 0
        return stat_val
    
    df = summary_daterange_df(raw_df, *this_week_range, ename, return_summary=False)
    # print(df)
    this_week_stat_val = 0 if len(df) == 0 else  _stat_value(df, stat)
    
    if last_week_range is not None:
        last_df = summary_daterange_df(raw_df, *last_week_range, ename, return_summary=False)
        last_week_stat_val = _stat_value(last_df, stat)
        
        if comparison=='relative':
            last_week_stat_val = (this_week_stat_val - last_week_stat_val) / \
                     this_week_stat_val
    else:
        last_week_stat_val = 0

    # print(last_week_stat_val)
    return ename, this_week_stat_val, last_week_stat_val





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
    df['load'] = df.reps * df.kg * df.rpe
    start_days_after_monday = timedelta(days=df.date.min().weekday())
    end_days_before_monday = timedelta(days=(7 - date.today().weekday()))

    try:
        bins = pd.date_range(start=df.date.min() - start_days_after_monday, end=date.today() + end_days_before_monday, freq='7D', inclusive='both')
    except Exception as e:
        print(e)
    df['week'] = pd.cut(df.date, bins=bins, right=False, include_lowest=True)
    df['week'] = df.week.apply(lambda x: x.right)
    
    try:
        grp = df.groupby(['week','ename'], as_index=True).aggregate(
            vol=("reps", 'sum'),
            intensity=("kg", 'max'),
            load=("load",'sum')
        ).reset_index(names=['week', 'ename', 'vol', 'intensity', 'load'])
        grp.intensity.fillna(0, inplace=True)
        # grp['week'] = grp.week.dt.strftime("%y-%m-%d")
    except Exception as e:
        print(e)
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
                x=data['week'].values, 
                y=data[metric], 
                name=metric, 
            ),
            secondary_y=i==1
        )
        
        fig.update_yaxes(title_text=y_label[i], secondary_y=(i==1))
    # RX requires plotly layout values (e.g. tickvalues) to be text, not ndarray or dt objects.
    # Plotly also by default interprets dates as yy-mm-dd
    tv = data.week.sort_values().dt.strftime("%y-%m-%d").tolist()
    tt = tv
    
    fig.update_layout(title_text=ename)
    fig.update_xaxes(title_text='Week Ending', tickvals=tv, ticktext=tt, tickangle=-45)


    
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
            return fig
        proj = proj.sort_values(by='date', ascending=False).iloc[0,:]

        if proj.date.date() < date.today() - timedelta(weeks=8):
            fig.update_layout(title_text=f'Last benchmark for {ename} was {proj.date.strftime("%d-%m")}') 
            # fig.add_annotation(dict(
            #     font=dict(color='yellow', size=15),
            #     x=10,
            #     y=-0.12,
            #     showarrow=False,
            #     text=f'Last benchmark for {ename} was {proj.date.strftime("%d-%m")}'
            # ))
            return fig

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
        tv = proj.date.sort_values().dt.strftime("%y-%m-%d").tolist()
        tt = tv
        
        # fig.update_layout(title_text=ename)
        fig.update_xaxes(
            title_text='Week Beginning', 
            tickvals=tv, 
            ticktext=tt, 
            tickangle=-45, 
            minor=dict(ticks='inside', showgrid=True, dtick=24*60*60*1000, griddash='dot', gridcolor='white'))

    return fig
