from sqlalchemy import Column, Integer, String, Boolean
from geoalchemy2 import Geometry
from app.database import Base

class Volunteer(Base):
    __tablename__ = "volunteers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    skill = Column(String)           # medical, logistics, rescue
    available = Column(Boolean, default=True)

    location = Column(
        Geometry("POINT", srid=4326),
        nullable=False
    )
