from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512))
    category = Column(String(128))
    ingredients = Column(Text)
    steps = Column(Text)
    url = Column(String(1024))
    loves = Column(Integer, default=0)