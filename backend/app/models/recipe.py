from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    ingredients = Column(Text)   # simpan sebagai JSON string atau comma-separated
    instructions = Column(Text)
