import time
from contextvars import ContextVar

from sqlalchemy import create_engine,event
from sqlalchemy.orm import declarative_base,sessionmaker

from app.config import DATABASE_URL

request_stats=ContextVar("request_stats",default=None)

engine=create_engine(DATABASE_URL,pool_pre_ping=True)
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)
Base=declarative_base()

@event.listens_for(engine,"before_cursor_execute")
def before_cursor_execute(conn,cursor,statement,parameters,context,executemany):
    conn.info.setdefault("query_start_time",[]).append(time.perf_counter())

@event.listens_for(engine,"after_cursor_execute")
def after_cursor_execute(conn,cursor,statement,parameters,context,executemany):
    start=conn.info["query_start_time"].pop()
    stats=request_stats.get()
    if stats is not None:
        stats["db_time"]+=(time.perf_counter()-start)*1000
        stats["queries"]+=1

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()