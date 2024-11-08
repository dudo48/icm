from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from icm.config import config
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
        keys = [
            "Date:",
            "Renewal Date:",
            "Renewal Days Left",
            "Remaining Units:",
            "Consumed Units:",
            "Average Consumption (Daily):",
            "Projected Consumption (Daily):",
        ]
        values = [
            self.date.strftime(DATETIME_FORMAT),
            self.renewal_date.strftime(DATETIME_FORMAT),
            f"{self.days_left:.1f}",
            f"{self.remaining_units:.2f}",
            f"{self.consumed_units:.2f}",
            f"{self.average_consumption:.2f}",
            f"{self.projected_consumption:.2f}",
        ]

        key_align = len(max(keys, key=len)) + 1
        value_align = len(max(values, key=len))
        return "\n".join(
            k.ljust(key_align) + v.rjust(value_align) for k, v in zip(keys, values)
        )

    @property
    def days_left(self) -> float:
        return (self.renewal_date - self.date).total_seconds() / 86400

    @property
    def package_size(self) -> float:
        return self.remaining_units + self.consumed_units

    @property
    def average_consumption(self) -> float:
        return self.consumed_units / (config["subscription"]["lifespan"] - self.days_left)

    @property
    def projected_consumption(self) -> float:
        return self.remaining_units / self.days_left
