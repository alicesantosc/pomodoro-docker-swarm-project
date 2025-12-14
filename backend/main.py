from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware  # <-- ADICIONE ESTA LINHA
from datetime import datetime
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import TimerState

app = FastAPI()

# ADICIONE ESTAS LINHAS AQUI:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria a tabela no banco
Base.metadata.create_all(bind=engine)

# ... resto do código continua igual

def get_or_create_timer(db: Session) -> TimerState:
    """Pega o timer existente ou cria um novo"""
    timer = db.query(TimerState).first()
    if not timer:
        timer = TimerState()
        db.add(timer)
        db.commit()
        db.refresh(timer)
    return timer

@app.get("/")
def read_root():
    return {"message": "Pomodoro Timer API"}

@app.post("/timer/start")
def start_timer(db: Session = Depends(get_db)):
    timer = get_or_create_timer(db)
    
    if timer.is_running:
        return {"error": "Timer já está rodando"}
    
    timer.start_time = datetime.now()
    timer.is_running = True
    db.commit()
    
    return {
        "status": "started",
        "start_time": timer.start_time.isoformat()
    }

@app.post("/timer/pause")
def pause_timer(db: Session = Depends(get_db)):
    timer = get_or_create_timer(db)
    
    if not timer.is_running:
        return {"error": "Timer não está rodando"}
    
    # Calcula tempo decorrido
    elapsed = (datetime.now() - timer.start_time).total_seconds()
    timer.elapsed_seconds += elapsed
    timer.is_running = False
    timer.start_time = None
    db.commit()
    
    return {
        "status": "paused",
        "elapsed_seconds": timer.elapsed_seconds
    }

@app.get("/timer/elapsed")
def get_elapsed_time(db: Session = Depends(get_db)):
    timer = get_or_create_timer(db)
    
    if timer.is_running and timer.start_time:
        current_elapsed = (datetime.now() - timer.start_time).total_seconds()
        total_elapsed = timer.elapsed_seconds + current_elapsed
    else:
        total_elapsed = timer.elapsed_seconds
    
    return {
        "is_running": timer.is_running,
        "elapsed_seconds": total_elapsed,
        "elapsed_formatted": format_time(total_elapsed)
    }

def format_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

@app.post("/timer/reset")
def reset_timer(db: Session = Depends(get_db)):
    timer = get_or_create_timer(db)
    
    timer.start_time = None
    timer.elapsed_seconds = 0.0
    timer.is_running = False
    db.commit()
    
    return {
        "status": "reset",
        "elapsed_seconds": 0
    }

def format_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"