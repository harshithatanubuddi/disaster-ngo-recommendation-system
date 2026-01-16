from app.database import engine, Base
from app.models.disaster import Disaster
from app.models.ngo import NGO
from app.models.volunteer import Volunteer

Base.metadata.create_all(bind=engine)
