import pickle
from datetime import datetime
from typing import Any

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    def _repr(self, *fields: str) -> str:
        fields_info = ", ".join([f"{field}={getattr(self, field)!r}" for field in fields])
        return f"{self.__class__.__name__}({fields_info})"


class Record(Base):
    __tablename__ = "icm"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime]
    renewal_date: Mapped[datetime]
    remaining_units: Mapped[float]
    consumed_units: Mapped[float]

    def __repr__(self) -> str:
        return self._repr("id", "date", "renewal_date", "remaining_units", "consumed_units")

    @property
    def package_size(self) -> float:
        return self.remaining_units + self.consumed_units


class State(Base):
    __tablename__ = "icm_state"

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[bytes]

    def __repr__(self) -> str:
        return self._repr("key", "loaded_value")

    @property
    def loaded_value(self) -> Any:
        return pickle.loads(self.value)
