from typing import Sequence, TypeVar, cast

import matplotlib.pyplot as plot
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.figure import Figure
from sqlalchemy import Select, func, select

from icm.database import engine
from icm.record import Record
from icm.utility import DATETIME_FORMAT

T = TypeVar("T")


def get_dataframe(query: Select[tuple[Record]]):
    def calculate_average(record: pd.Series):
        first = first_records.loc[record["renewal_date"]]
        record["average_daily_consumed_units"] = (
            record["consumed_units"] - first["consumed_units"]
        ) / (first["days_left"] - record["days_left"])
        return record

    query = query.order_by(Record.date)
    records = pd.read_sql(query, engine)
    records["time_left"] = records["renewal_date"] - records["date"]
    records["delta_consumed_units"] = records["consumed_units"].diff()
    records["delta_date"] = records["date"].diff()
    records["projected_delta_consumed_units"] = records["remaining_units"] * (records["delta_date"] / records["time_left"])
    records["projected_delta_consumed_units_ratio"] = records["delta_consumed_units"] / records["projected_delta_consumed_units"]
    records["days_left"] = records["time_left"] / pd.to_timedelta(1, "D")
    records["projected_daily_consumed_units"] = records["remaining_units"] / records["days_left"]
    first_records = records.groupby("renewal_date").first()
    records = records.apply(calculate_average, axis=1)
    return records


def show_plot(records: pd.DataFrame):
    figure, axes = cast(tuple[Figure, Sequence[Axes]], plot.subplots(2, sharex=True))
    colormap = LinearSegmentedColormap.from_list("", ["green", "yellow", "red"], 16)

    axes[0].plot(records["date"], records["remaining_units"], color="blue", marker="o", label="Remaining units")
    axes[0].legend()

    axes[1].bar(
        records["date"][:-1],
        records["delta_consumed_units"][1:],
        width=records["delta_date"][1:],
        color=colormap(TwoSlopeNorm(1, 0, 1.5)(records["projected_delta_consumed_units_ratio"][1:])),
        align="edge",
        linewidth=1,
        edgecolor="white",
        label="Consumed units",
    )
    axes[1].plot(records["date"], records["projected_daily_consumed_units"], linestyle="--", label="Projected daily consumption")
    axes[1].plot(records["date"], records["average_daily_consumed_units"], label="Average daily consumption")
    axes[1].legend()

    for axis in axes:
        axis.set_xlim(records["date"].min(), None)
        axis.set_ylim(0, None)
        axis.set_xlabel("Date / Time")
        axis.set_ylabel("Units")

    figure.suptitle(
        f"{len(records)} record(s) from {records["date"].min().strftime(DATETIME_FORMAT)}"
        f" to {records["date"].max().strftime(DATETIME_FORMAT)}"
    )
    plot.show()


def main():
    latest_renewal_date = select(func.max(Record.renewal_date)).scalar_subquery()
    query = select(Record).where(Record.renewal_date == latest_renewal_date)
    records = get_dataframe(query)
    if records.empty:
        print("No records were found.")
    else:
        show_plot(records)


if __name__ == "__main__":
    main()
