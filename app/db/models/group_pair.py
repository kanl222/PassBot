from sqlalchemy import Column, ForeignKey, Integer, Table  # Import Column and Integer
from ..db_session import SqlAlchemyBase


group_pair_association = Table(
    "group_pair",
    SqlAlchemyBase.metadata,
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True), 
    Column("pair_id", Integer, ForeignKey("pairs.id", ondelete="CASCADE"), primary_key=True), 
)
