import sys
sys.path.extend(["/home/matt/code/logit/"])
import reflex as rx
from sqlmodel import create_engine, Session, select
from logit.weightsapp import LoggedExercise, LoggedBenchmark
import datetime
from datetime import datetime
from sqlmodel import SQLModel



if __name__=="__main__":
    sqlite_fn = "/home/matt/code/logit/data.db"
    sqlite_url = f"sqlite:///{sqlite_fn}"

    engine = create_engine(sqlite_url, echo=True)
    SQLModel.metadata.create_all(engine)