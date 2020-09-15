import boto3
import json
import calendar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from aws import *
from panda_helpers import *


costs_exp = boto3.client("ce")


current_year = datetime.now().year
current_month = datetime.now().month
previous_year = current_year - 1

MONTHLY_START_DATE = f"{previous_year}-{current_month:02d}-01"
MONTHLY_END_DATE = f"{current_year}-{current_month:02d}-01"

DAILY_MAX_DAYS = 30
previous = datetime.now() - timedelta(days=DAILY_MAX_DAYS)
DAILY_START_DATE = previous.strftime("%Y-%m-%d")
DAILY_END_DATE = datetime.now().strftime("%Y-%m-%d")


def main():
    plt.style.use("seaborn")
    get_and_write_costs_to_files()
    service_usage_data = import_cost_file_into_df(
        "results_service_usage_type_monthly.tsv"
    )
    try:
        max_monthly_cost = create_services_over_time_options(
            service_usage_data, "monthly"
        )
        # Service
        create_plots_for_service_multicharts(
            service_usage_data,
            max_monthly_cost,
            "monthly",
            MONTHLY_START_DATE,
            MONTHLY_END_DATE,
        )

        # Service/Usage
        create_plots_for_service_usage_multicharts(
            service_usage_data,
            max_monthly_cost,
            "monthly",
            MONTHLY_START_DATE,
            MONTHLY_END_DATE,
        )

        # Service/Type tag
        service_type_tag_data = import_cost_file_into_df(
            "results_service_tag_monthly.tsv"
        )
        create_plots_for_service_tag_type_multicharts(
            service_type_tag_data,
            max_monthly_cost,
            "monthly",
            MONTHLY_START_DATE,
            MONTHLY_END_DATE,
        )

    except AttributeError as e:
        print(e)
        print("Not enough monthly data for charts")

    # Usage Type
    service_usage_data = import_cost_file_into_df(
        "results_service_usage_type_daily.tsv"
    )
    max_cost = create_services_over_time_options(service_usage_data, "daily")
    create_plots_for_service_multicharts(
        service_usage_data, max_cost, "daily", DAILY_START_DATE, DAILY_END_DATE
    )
    create_plots_for_service_usage_multicharts(
        service_usage_data, max_cost, "daily", DAILY_START_DATE, DAILY_END_DATE
    )

    # Operartion
    service_operation_data = import_cost_file_into_df(
        "results_service_operation_daily.tsv"
    )
    create_plots_for_service_operation_multicharts(
        service_operation_data, max_cost, "daily", DAILY_START_DATE, DAILY_END_DATE
    )

    # Tags
    service_tag_type_data = import_cost_file_into_df("results_service_tag_daily.tsv")
    create_plots_for_service_tag_type_multicharts(
        service_tag_type_data, max_cost, "daily", DAILY_START_DATE, DAILY_END_DATE
    )


def get_and_write_costs_to_files():
    get_and_write_single_cost_file(
        MONTHLY_START_DATE, MONTHLY_END_DATE, "MONTHLY", ["SERVICE", "USAGE_TYPE"]
    )
    get_and_write_single_cost_file(
        DAILY_START_DATE, DAILY_END_DATE, "DAILY", ["SERVICE", "USAGE_TYPE"]
    )
    get_and_write_single_cost_file(
        DAILY_START_DATE, DAILY_END_DATE, "DAILY", ["SERVICE", "OPERATION"]
    )

    ## Temp costs by tag. Data is correct, move it to create tsv file
    tag_costs_monthly = get_costs_for_group_by_tag_type(
        MONTHLY_START_DATE, MONTHLY_END_DATE, "MONTHLY", "SERVICE"
    )
    formatted = format_costs(tag_costs_monthly)
    print("\n\n Costs by tag")
    with open(f"results_service_tag_monthly.tsv", "w") as file:
        file.write("Type\tStart\tEnd\tGroup1\tGroup2\tCosts\n")
        for line in formatted:
            file.write("Type\t" + line + "\n")

    tag_costs_daily = get_costs_for_group_by_tag_type(
        DAILY_START_DATE, DAILY_END_DATE, "DAILY", "SERVICE"
    )
    formatted = format_costs(tag_costs_daily)
    print("\n\n Costs by tag")
    with open(f"results_service_tag_daily.tsv", "w") as file:
        file.write("Type\tStart\tEnd\tGroup1\tGroup2\tCosts\n")
        for line in formatted:
            file.write("Type\t" + line + "\n")


def get_and_write_single_cost_file(start, end, time_grouping, groupby):
    time_grouping_lower = time_grouping.lower()
    specific_grouping = groupby[1].lower()
    costs = get_costs_for_group(start, end, time_grouping, groupby)

    formatted_json = json.dumps(costs, indent=3, default=str)
    with open("results_sample_cost.json", "w") as file:
        file.write(formatted_json)
    formatted = format_costs(costs)
    formatted_with_newlines = ["Usage\t" + i + "\n" for i in formatted]
    with open(
        f"results_service_{specific_grouping}_{time_grouping_lower}.tsv", "w"
    ) as file:
        file.write("Type\tStart\tEnd\tGroup1\tGroup2\tCosts\n")
        file.writelines(formatted_with_newlines)


def import_cost_file_into_df(filename):
    service_usage_data = pd.read_csv(filename, sep="\t")
    service_usage_data["Start"] = pd.to_datetime(
        service_usage_data["Start"], format="%Y-%m-%d"
    )
    print(service_usage_data)
    print(service_usage_data.info())
    return service_usage_data


def create_services_over_time_options(service_usage_data, filename_qualifier):
    top_services = group_data_by_top_and_others(service_usage_data, "Group1", 5)
    print(top_services)
    print(top_services.to_frame().info())
    max_monthly_cost = top_services.max()
    print(f"max_monthly_cost:  {max_monthly_cost}")
    top_services.unstack().plot(kind="line", legend=True)
    plt.savefig("plot_top_services_line")

    top_services.unstack().plot(kind="bar", stacked=True, width=0.9, legend=True)
    plt.savefig("plot_top_services_bar")

    ax = top_services.unstack().plot(
        figsize=(10, 4), kind="area", stacked=True, legend=True
    )
    ax.legend(frameon=True)

    plt.savefig(f"plot_top_services_area_{filename_qualifier}")
    return max_monthly_cost


def create_plots_for_service_multicharts(
    service_usage_data, max_monthly_cost, filename_qualifier, start, end
):
    top_services_list = get_top_groupings(service_usage_data, "Group1", 5)
    count = 0
    for current_service in top_services_list:
        count = count + 1
        service_counts = get_single_grouping(
            service_usage_data, "Group1", current_service
        )
        print(f"\n\nService: {current_service}")
        print(service_counts)
        title = simplify_service_name(current_service)
        ax = service_counts.plot(
            figsize=(2, 1.75),
            kind="line",
            legend=False,
            ylim=(0, max_monthly_cost + 2),
            xlim=(start, end),
            title=title,
        )
        ax.title.set_size(10)
        # x_axis = ax.xaxis
        # x_axis.set_label_text('foo')
        # x_axis.label.set_visible(False)
        plt.axis("off")
        plt.savefig(f"plot_top_service_line_{filename_qualifier}_{count}")


def create_plots_for_service_usage_multicharts(
    service_usage_data, max_monthly_cost, filename_qualifier, start, end
):
    create_plots_for_service_group_multicharts(
        service_usage_data,
        max_monthly_cost,
        filename_qualifier,
        start,
        end,
        "usage_type",
    )


def create_plots_for_service_operation_multicharts(
    service_operation_data, max_monthly_cost, filename_qualifier, start, end
):
    create_plots_for_service_group_multicharts(
        service_operation_data,
        max_monthly_cost,
        filename_qualifier,
        start,
        end,
        "operation",
    )


def create_plots_for_service_tag_type_multicharts(
    service_tag_type_data, max_monthly_cost, filename_qualifier, start, end
):
    create_plots_for_service_group_multicharts(
        service_tag_type_data,
        max_monthly_cost,
        filename_qualifier,
        start,
        end,
        "tag_type",
    )


def create_plots_for_service_group_multicharts(
    service_data, max_monthly_cost, filename_qualifier, start, end, groupby_name
):
    top_services_list = get_top_groupings(service_data, "Group1", 5)
    count = 0
    for current_service in top_services_list:
        count = count + 1
        filtered_df = service_data[service_data["Group1"] == current_service]
        service_counts = group_data_by_top_and_others(
            filtered_df, "Group2", 3
        ).unstack()
        print(f"\n\nService Usage: {current_service}")
        print(service_counts)
        title = simplify_service_name(current_service)
        ax = service_counts.plot(
            figsize=(2, 3.5),
            kind="bar",
            stacked=True,
            legend=False,
            ylim=(0, max_monthly_cost + 2),
            xlim=(start, end),
            title=title,
            color=["#0000FF", "#b36b00", "#ff9900", "#DCDCDC"],
        )
        box = ax.get_position()
        ax.set_position(
            [box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9]
        )
        ax.title.set_size(10)
        ax.legend(
            prop={"size": 8},
            loc="upper center",
            bbox_to_anchor=(0.5, -0.05),
            fancybox=True,
            shadow=True,
            ncol=1,
        )
        plt.axis("off")
        plt.savefig(f"plot_top_service_{groupby_name}_{filename_qualifier}_{count}")


if __name__ == "__main__":
    main()
