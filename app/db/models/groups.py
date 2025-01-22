from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from ..db_session import SqlAlchemyBase
from .group_pair import group_pair_association
from .pairs import Pair


class Group(SqlAlchemyBase):
    __tablename__: str = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    id_curator: Mapped[int] = mapped_column(
        __name_pos=ForeignKey("users.id"), nullable=False, index=True
    )

    _id_group: Mapped[int] = mapped_column(unique=True, nullable=False, index=True)

    name: Mapped[str] = mapped_column(
        __name_pos=String(100), unique=True, nullable=False, index=True
    )
    curator: Mapped["Teacher"] = relationship(
        argument="Teacher",
        back_populates="curated_groups",
        foreign_keys=[id_curator],
        lazy="selectin",
        cascade="save-update",
    )

    students: Mapped[list["Student"]] = relationship(
        argument="Student",
        back_populates="group",
        foreign_keys="Student.group_id",
        lazy="joined",
        cascade="save-update",
    )

    pairs: Mapped[list["Pair"]] = relationship(
        "Pair",
        secondary=group_pair_association,
        back_populates="groups",
        lazy="joined",) # type: ignore
    
    attendance_logs = relationship(
        "GroupAttendanceLog",
        back_populates="group" ,
        lazy="selectin",
    )


    __table_args__ = (Index("idx_curator_group", id_curator, _id_group),)

    def __repr__(self) -> str:
        return f"<Group(name={self.name}, id={self.id})>"



