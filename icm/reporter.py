from typing import Any, Iterable, Sequence, TypeVar, cast

import matplotlib.pyplot as plot
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.figure import Figure

from icm.models import Record
from icm.path import REPORT_TABLE, REPORT_TABLE_TEMPLATE, REPORT_VISUAL
from icm.utility import DATETIME_SHORT_FORMAT

T = TypeVar("T")


def get_dataframe(records: Iterable[Record]) -> pd.DataFrame:
    combined_dataframe = pd.DataFrame([record.asdict() for record in records]).sort_values("date")
    dataframes: list[pd.DataFrame] = []
    for _, df in combined_dataframe.groupby("renewal_date"):
        df["time_left"] = df["renewal_date"] - df["date"]
        df["delta_consumed_units"] = df["consumed_units"].diff()
        df["delta_date"] = df["date"].diff()
        df["delta_date_hours"] = df["delta_date"] / pd.to_timedelta(1, "h")
        df["predicted_delta_consumed_units"] = df["remaining_units"] * (df["delta_date"] / df["time_left"])
        df["predicted_delta_consumed_units_ratio"] = df["delta_consumed_units"] / df["predicted_delta_consumed_units"]
        df["days_left"] = df["time_left"] / pd.to_timedelta(1, "D")
        df["predicted_daily_consumed_units"] = df["remaining_units"] / df["days_left"]

        first = df.iloc[0]
        df["average_daily_consumed_units"] = (
            df["consumed_units"] - first["consumed_units"]
        ) / (first["days_left"] - df["days_left"])
        df["predicted_remaining_units"] = first["remaining_units"] - (
            first["predicted_daily_consumed_units"] * (first["days_left"] - df["days_left"])
        )
        dataframes.append(df)
    return pd.concat(dataframes)


def create_plot(records: pd.DataFrame):
    figure, axes = cast(tuple[Figure, Sequence[Axes]], plot.subplots(2, sharex=True))
    colormap = LinearSegmentedColormap.from_list("", ["green", "yellow", "red"], 16)

    minmax_records = records.loc[[records["date"].idxmin(), records["date"].idxmax()]]
    max_record = minmax_records.iloc[1]

    axes[0].plot(minmax_records["date"], minmax_records["predicted_remaining_units"], linestyle="--", label="Predicted remaining units")
    axes[0].plot(records["date"], records["remaining_units"], label="Remaining units")
    axes[0].annotate(
        f"{max_record["predicted_remaining_units"]:.2f}",
        xy=(max_record["date"], max_record["predicted_remaining_units"]),
    )
    axes[0].annotate(
        f"{max_record["remaining_units"]:.2f}",
        xy=(max_record["date"], max_record["remaining_units"]),
    )

    axes[1].bar(
        records["date"][:-1],
        records["delta_consumed_units"][1:],
        width=records["delta_date"][1:],
        color=colormap(TwoSlopeNorm(1, 0, 1.5)(records["predicted_delta_consumed_units_ratio"][1:])),
        align="edge",
        linewidth=1,
        edgecolor="white",
        label="Consumed units",
    )
    axes[1].plot(records["date"], records["predicted_daily_consumed_units"], linestyle="--", label="Predicted daily consumption")
    axes[1].plot(records["date"], records["average_daily_consumed_units"], label="Average daily consumption")
    axes[1].annotate(
        f"{max_record["predicted_daily_consumed_units"]:.2f}",
        xy=(max_record["date"], max_record["predicted_daily_consumed_units"]),
    )
    axes[1].annotate(
        f"{max_record["average_daily_consumed_units"]:.2f}",
        xy=(max_record["date"], max_record["average_daily_consumed_units"]),
    )

    min_date = minmax_records.iloc[0]["date"]
    max_date = minmax_records.iloc[1]["date"]
    for axis in axes:
        axis.set_xlim(min_date, None)
        axis.set_ylim(0, None)
        axis.set_xlabel("Date / Time")
        axis.set_ylabel("Units")
        axis.legend()

    figure.suptitle(
        f"{len(records)} record(s) from {min_date.strftime(DATETIME_SHORT_FORMAT)} to {max_date.strftime(DATETIME_SHORT_FORMAT)}"
    )
    figure.supxlabel(f"Time until renewal: {max_record["days_left"]:.1f}d")
    return figure


def save_plot(records: pd.DataFrame):
    figure = create_plot(records)
    figure.set_size_inches(24, 10)
    figure.savefig(REPORT_VISUAL, dpi=100, bbox_inches="tight")


def save_table(records: pd.DataFrame):
    """
    Save the tabular report of the records present in the given dataframe to the report file.

    Args:
        records (pd.DataFrame): DataFrame of records.
    """
    def date_formatter(date: Any):
        return date.strftime(DATETIME_SHORT_FORMAT)

    def time_formatter(suffix: str):
        return ("{:.1f}" + suffix).format

    columns = {
        "date": "Date",
        "remaining_units": "Remaining",
        "consumed_units": "Consumed",
        "delta_date_hours": "Δ Date",
        "delta_consumed_units": "Δ Consumed",
        "predicted_delta_consumed_units": "Pred. Δ Consumed",
        "average_daily_consumed_units": "Avg. Daily",
        "predicted_daily_consumed_units": "Pred. Daily",
        "days_left": "Time Left",
    }

    records = records[columns.keys()].sort_values("date", ascending=False).rename(columns=columns)
    records.index += 1
    table = records.to_html(
        formatters={
            "Date": date_formatter,
            "Δ Date": time_formatter("h"),
            "Time Left": time_formatter("d"),
        },
        float_format="{:.2f}".format,
    )

    with open(REPORT_TABLE_TEMPLATE, "r") as template_file, open(REPORT_TABLE, "w") as report_file:
        report_file.write(template_file.read().format(table=table))


def show_plot(records: pd.DataFrame):
    create_plot(records)
    plot.show()
