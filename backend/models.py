from sqlalchemy import Column, Integer, Float, Boolean, DateTime
from database import Base
from datetime import datetime

class TimerState(Base):
    __tablename__ = "timer_state"
    
    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=True)
    elapsed_seconds = Column(Float, default=0.0)
    is_running = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)