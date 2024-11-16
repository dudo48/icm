from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from icm import path
from icm.models import Base

engine = create_engine(f"sqlite:///{path.DATABASE}")
Base.metadata.create_all(engine)
Session = sessionmaker(engine)
