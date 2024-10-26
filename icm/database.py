from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from icm.record import Base

from icm import path

engine = create_engine(f"sqlite:///{path.DATABASE}")
Base.metadata.create_all(engine)
Session = sessionmaker(engine)
