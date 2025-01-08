import datetime
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Date, String, Index
from ..db_session import SqlAlchemyBase
from .group_pair import group_pair_association

class Pair(SqlAlchemyBase):
    __tablename__ = "pairs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False, index=True)
    pair_number: Mapped[int] = mapped_column(Integer, nullable=False)
    discipline: Mapped[str] = mapped_column(String(255), nullable=False)

    groups: Mapped[List["Group"]] = relationship(
        "Group", secondary=group_pair_association, back_populates="pairs"
    )
    visits: Mapped[List["Visiting"]] = relationship("Visiting", back_populates="pair")

    __table_args__ = (
        Index("idx_date_pair", "date", "pair_number"),  
    )

    def __repr__(self):
        return f"<Pair(date={self.date}, pair_number={self.pair_number}, discipline={self.discipline})>"


