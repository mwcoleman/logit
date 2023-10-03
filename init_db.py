from sqlmodel import create_engine
from sqlmodel import SQLModel
import os

DB_FILE = 'data.db'


if __name__=="__main__":
    root_dir = os.path.dirname(os.path.realpath(__file__))
    sqlite_fn = os.path.join(root_dir, DB_FILE)
    print(sqlite_fn)
    sqlite_url = f"sqlite:///{sqlite_fn}"

    engine = create_engine(sqlite_url, echo=True)
    SQLModel.metadata.create_all(engine)