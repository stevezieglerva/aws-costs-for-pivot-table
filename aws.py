import boto3
import numpy as np

costs_exp = boto3.client("ce")


def get_costs_for_group(start, end, granularity, groupby):
    groupby_list = []
    for grouping in groupby:
        item = {}
        item["Type"] = "DIMENSION"
        item["Key"] = grouping
        groupby_list.append(item)
    costs = costs_exp.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity=granularity,
        Metrics=["BLENDED_COST"],
        GroupBy=groupby_list,
    )
    return costs


def get_costs_for_group_by_tag_type(start, end, granularity, groupby_value):
    groupby_list = []
    item = {}
    item["Type"] = "DIMENSION"
    item["Key"] = groupby_value
    groupby_list.append(item)
    item = {}
    item["Type"] = "TAG"
    item["Key"] = "env"
    groupby_list.append(item)
    costs = costs_exp.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity=granularity,
        Metrics=["BLENDED_COST"],
        GroupBy=groupby_list,
    )
    return costs


def format_costs(costs):
    lines = []
    for time_period in costs["ResultsByTime"]:
        start = time_period["TimePeriod"]["Start"]
        end = time_period["TimePeriod"]["End"]
        for group in time_period["Groups"]:
            group1 = group["Keys"][0]
            group2 = group["Keys"][1].replace("Type$", "")
            if group2 == "":
                group2 = "none"
            blended_cost = group["Metrics"]["BlendedCost"]["Amount"]
            if blended_cost != "0":
                line = f'{start}\t{end}\t"{group1}"\t"{group2}"\t{blended_cost}'
                lines.append(line)
    return lines


def update_dictionary_item_list(current_dict, field_name, value):
    current_list = current_dict.get(field_name, [])
    current_list.append(value)
    current_dict[field_name] = current_list
    return current_dict


def format_dataframe_json(costs):
    results = {}
    for time_period in costs["ResultsByTime"]:
        start = time_period["TimePeriod"]["Start"]
        end = time_period["TimePeriod"]["End"]

        for group in time_period["Groups"]:
            results = update_dictionary_item_list(results, "Start", start)
            results = update_dictionary_item_list(results, "End", end)

            group1 = group["Keys"][0]
            results = update_dictionary_item_list(results, "Group1", group1)
            group2 = group["Keys"][1]
            results = update_dictionary_item_list(results, "Group2", group2)
            blended_cost = group["Metrics"]["BlendedCost"]["Amount"]
            results = update_dictionary_item_list(results, "Costs", blended_cost)

    return results

