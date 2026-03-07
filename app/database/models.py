from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database.base import Base
import datetime

class IncidentDB(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, index=True)
    signal_type = Column(String)
    value = Column(Float)
    reliability = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
