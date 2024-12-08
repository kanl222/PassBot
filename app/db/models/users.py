from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.security import dict_to_str, encode_data, decode_data, str_to_dict
from app.core.security import dict_to_str
from ..db_session import SqlAlchemyBase
from enum import Enum as PyEnum


class UserRole(str, PyEnum):
    STUDENT = "student"
    TEACHER = "teacher"


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    # Поля таблицы
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    _kodstud = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=True)
    _encrypted_data_user = Column(String(500), nullable=True)

    group = relationship('Group', back_populates='students')
    absences = relationship('Absence', back_populates='student')

    def __repr__(self):
        """The string representation of the User object."""
        return f"<User(id={self.id}, full_name={self.full_name}, role={self.role})>"

    def set_encrypted_data(self, user_data: dict[str, str]):
        """
        Sets the encrypted user data.

        :param user_data: Dictionary with user data (for example, username and password).
        """
        try:
            encoded = encode_data(dict_to_str(user_data))
            self._encrypted_data_user = encoded
        except Exception as e:
            raise ValueError(f"Data encryption error: {e}")

    def get_encrypted_data(self) -> dict:
        """
        Receives the decrypted user data.

        :return: Dictionary with user data.
        """
        if not self._encrypted_data_user:
            raise ValueError("There is no encrypted data for this user.")

        try:
            decoded = decode_data(self._encrypted_data_user)
            return str_to_dict(decoded)
        except Exception as e:
            raise ValueError(f"Error decrypting the data: {e}")
