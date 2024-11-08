from datetime import datetime
from typing import Sequence, TypeVar, cast

import matplotlib.pyplot as plot
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.figure import Figure
from sqlalchemy import func, select

from icm.database import Session
from icm.record import Record
from icm.utility import DATETIME_FORMAT

T = TypeVar("T")


def show_plot(records: Sequence[Record]):
    figure, axes = cast(tuple[Figure, Sequence[Axes]], plot.subplots(2, sharex=True))
    colormap = LinearSegmentedColormap.from_list("", ["green", "yellow", "red"], 16)

    first_package_record: dict[datetime, Record] = {}
    for record in records:
        if (
            record.renewal_date not in first_package_record
            or record.date < first_package_record[record.renewal_date].date
        ):
            first_package_record[record.renewal_date] = record

    dates = np.array([record.date for record in records], dtype=np.datetime64)
    consumed_units = np.array([record.consumed_units for record in records], dtype=np.float64)
    remaining_units = np.array([record.remaining_units for record in records], dtype=np.float64)
    time_left = np.array([record.time_left for record in records], dtype=np.timedelta64)

    timedeltas = np.ediff1d(dates)
    consumed_since_last = np.ediff1d(consumed_units)
    projected_consumption = remaining_units[:-1] * (timedeltas / time_left[:-1])
    projected_consumption_daily = remaining_units / (time_left / np.timedelta64(1, "D"))
    average_consumption_daily = (
        consumed_units
        - np.array(
            [
                first_package_record[record.renewal_date].consumed_units
                for record in records
            ],
            dtype=np.float64,
        )
    ) / (
        (
            dates
            - np.array(
                [first_package_record[record.renewal_date].date for record in records],
                dtype=np.datetime64,
            )
        )
        / np.timedelta64(1, "D")
    )

    axes[0].plot(dates, remaining_units, color="blue", marker="o")
    axes[0].set_ylabel("Remaining units")
    axes[1].bar(
        dates[:-1],
        consumed_since_last,
        width=timedeltas,
        color=colormap(TwoSlopeNorm(1, 0, 1.5)(consumed_since_last / projected_consumption)),
        align="edge",
        linewidth=1,
        edgecolor="white",
        label="Consumed units",
    )
    axes[1].plot(dates, projected_consumption_daily, linestyle="--", label="Projected daily consumption")
    axes[1].plot(dates, average_consumption_daily, color="red", label="Average daily consumption")
    axes[1].set_ylabel("Units")
    axes[1].legend()

    for axis in axes:
        axis.set_xlim(dates.min(), None)
        axis.set_ylim(0, None)
        axis.set_xlabel("Date and time")

    figure.suptitle(
        f"{len(records)} record(s) from {dates.min().astype(datetime).strftime(DATETIME_FORMAT)}"
        f" to {dates.max().astype(datetime).strftime(DATETIME_FORMAT)}"
    )
    plot.show()


def main():
    with Session() as session:
        latest_renewal_date = select(func.max(Record.renewal_date)).scalar_subquery()
        records = list(
            session.scalars(
                select(Record)
                .where(Record.renewal_date == latest_renewal_date)
                .order_by(Record.date)
            )
        )
        if records:
            show_plot(records)
        else:
            print("No records were found.")


if __name__ == "__main__":
    main()
