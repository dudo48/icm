from datetime import datetime, timedelta

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from icm.utility import DATETIME_FORMAT


class Base(DeclarativeBase):
    pass


class Record(Base):
    __tablename__ = "icm"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime]
    renewal_date: Mapped[datetime]
    remaining_units: Mapped[float]
    consumed_units: Mapped[float]

    def __repr__(self) -> str:
        fields = ["id", "date", "renewal_date", "remaining_units", "consumed_units"]
        fields_info = ", ".join([f"{field}={getattr(self, field)!r}" for field in fields])
        return f"{self.__class__.__name__}({fields_info})"

    def __str__(self) -> str:
        data_dict = {
            "Date": self.date.strftime(DATETIME_FORMAT),
            "Renewal Date": self.renewal_date.strftime(DATETIME_FORMAT),
            "Remaining Units": f"{self.remaining_units:.2f}",
            "Consumed Units": f"{self.consumed_units:.2f}",
        }

        key_align = len(max(data_dict.keys(), key=len)) + 1
        value_align = len(max(data_dict.values(), key=len))
        return "\n".join(
            (k + ":").ljust(key_align) + v.rjust(value_align) for k, v in data_dict.items()
        )

    @property
    def time_left(self) -> timedelta:
        return self.renewal_date - self.date

    @property
    def package_size(self) -> float:
        return self.remaining_units + self.consumed_units
