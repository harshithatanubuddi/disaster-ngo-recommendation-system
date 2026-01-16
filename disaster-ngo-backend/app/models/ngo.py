from sqlalchemy import Column, Integer, String, Date
from geoalchemy2 import Geometry
from app.database import Base

class NGO(Base):
    __tablename__ = "ngos"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    cause = Column(String)   # rescue, health, food

    # SERVICE REGIONS
    service_area = Column(
        Geometry("MULTIPOLYGON", srid=4326),
        nullable=False
    )

    source = Column(String)
    data_collected_on = Column(Date)
    reference_url = Column(String)
