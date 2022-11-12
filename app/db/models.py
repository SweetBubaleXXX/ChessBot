from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer(), primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    wins = Column(Integer(), default=0, nullable=False)
    losses = Column(Integer(), default=0, nullable=False)
    settings = relationship("Settings", uselist=False)


class Settings(Base):
    __tablename__ = "settings"

    player_id = Column(Integer(), ForeignKey("players.id"), primary_key=True, nullable=False)
    board_theme = Column(String())
    board_size = Column(Integer())