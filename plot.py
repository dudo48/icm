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


def get_dataframes(query: Select[tuple[Record]]):
    query = query.order_by(Record.date)
    dataframes: list[pd.DataFrame] = []
    for _, df in pd.read_sql(query, engine).groupby("renewal_date"):
        df["time_left"] = df["renewal_date"] - df["date"]
        df["delta_consumed_units"] = df["consumed_units"].diff()
        df["delta_date"] = df["date"].diff()
        df["projected_delta_consumed_units"] = df["remaining_units"] * (df["delta_date"] / df["time_left"])
        df["projected_delta_consumed_units_ratio"] = df["delta_consumed_units"] / df["projected_delta_consumed_units"]
        df["days_left"] = df["time_left"] / pd.to_timedelta(1, "D")
        df["projected_daily_consumed_units"] = df["remaining_units"] / df["days_left"]

        first = df.iloc[0]
        df["average_daily_consumed_units"] = (
            df["consumed_units"] - first["consumed_units"]
        ) / (first["days_left"] - df["days_left"])
        df["projected_remaining_units"] = first["remaining_units"] - (
            first["projected_daily_consumed_units"] * (first["days_left"] - df["days_left"])
        )

        dataframes.append(df)

    return dataframes


def show_plot(records_list: list[pd.DataFrame]):
    figure, axes = cast(tuple[Figure, Sequence[Axes]], plot.subplots(2, sharex=True))
    colormap = LinearSegmentedColormap.from_list("", ["green", "yellow", "red"], 16)
    records = records_list[-1]
    minmax_records = records.loc[[records["date"].idxmin(), records["date"].idxmax()]]

    axes[0].plot(minmax_records["date"], minmax_records["projected_remaining_units"], linestyle="--", label="Projected remaining units")
    axes[0].plot(records["date"], records["remaining_units"], label="Remaining units")

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

    min_date = minmax_records.iloc[0]["date"]
    max_date = minmax_records.iloc[1]["date"]
    for axis in axes:
        axis.set_xlim(min_date, None)
        axis.set_ylim(0, None)
        axis.set_xlabel("Date / Time")
        axis.set_ylabel("Units")
        axis.legend()

    figure.suptitle(
        f"{len(records)} record(s) from {min_date.strftime(DATETIME_FORMAT)} to {max_date.strftime(DATETIME_FORMAT)}"
    )
    plot.show()


def main():
    latest_renewal_date = select(func.max(Record.renewal_date)).scalar_subquery()
    query = select(Record).where(Record.renewal_date == latest_renewal_date)
    records_list = get_dataframes(query)
    if records_list:
        show_plot(records_list)
    else:
        print("No records were found.")


if __name__ == "__main__":
    main()
