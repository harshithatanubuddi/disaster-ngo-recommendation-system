from sqlalchemy import Column, Integer, String, DateTime
from geoalchemy2 import Geometry
from app.database import Base

class Disaster(Base):
    __tablename__ = "disasters"

    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)
    disaster_type = Column(String, nullable=False)   # flood, cyclone
    severity = Column(String)                        # low / medium / high
    event_date = Column(DateTime)

    # AFFECTED REGION
    geom = Column(
        Geometry("POLYGON", srid=4326),
        nullable=False
    )

    source = Column(String)
