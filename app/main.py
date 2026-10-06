from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.database import Base,engine,request_stats
from app.routes import auth,specialists,appointments,summary

Base.metadata.create_all(bind=engine)

app=FastAPI(title="Сервис записи на приём к специалисту",version="1.0.0")

@app.middleware("http")
async def db_stats_middleware(request,call_next):
    stats={"db_time":0.0,"queries":0}
    token=request_stats.set(stats)
    try:
        response=await call_next(request)
        response.headers["X-DB-Time-Ms"]=f"{stats['db_time']:.4f}"
        response.headers["X-DB-Queries"]=str(stats["queries"])
        return response
    finally:
        request_stats.reset(token)

app.mount("/static",StaticFiles(directory="app/static"),name="static")

app.include_router(auth.router,prefix="/api/auth",tags=["auth"])
app.include_router(specialists.router,prefix="/api",tags=["specialists"])
app.include_router(appointments.router,prefix="/api",tags=["appointments"])
app.include_router(summary.router,prefix="/api",tags=["summary"])

@app.get("/")
def root():
    return FileResponse("app/static/index.html")