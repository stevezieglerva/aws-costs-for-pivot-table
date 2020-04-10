import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def group_data_by_top_and_others(dataframe, column_name, size):
	top_groupings_list = get_top_groupings(dataframe, column_name, size)
	print(f"top_groupings: {top_groupings_list}")
	top_groupings = dataframe[dataframe[column_name].isin(top_groupings_list)]
	top_grouping_counts = top_groupings.groupby(by=["Start", column_name])["Costs"].sum().rename("Costs")

	bottom_groupings_list =  get_bottom_groupings(dataframe, column_name, size)
	print(f"bottom_groupings: {bottom_groupings_list}")
	bottom_groupings = dataframe[dataframe[column_name].isin(bottom_groupings_list)]
	bottom_grouping_counts = bottom_groupings.groupby(by=["Start"])["Costs"].sum().to_frame()

	for index, row in bottom_grouping_counts.iterrows():
		print(row)
		start =  index
		column_name = "Other"
		costs = row["Costs"]
		print(f"{start}/{column_name}/{costs}")
		top_grouping_counts[start, column_name] = costs

	print("_____")
	print(top_grouping_counts)
	return top_grouping_counts


def get_single_grouping(dataframe, column, filter_value):
	filtered_df = dataframe[dataframe[column] == filter_value]
	grouped = filtered_df.groupby(by="Start")["Costs"].sum().to_frame()
	return grouped


def get_single_usage_grouping(dataframe, column, filter_value, size):
	filtered_df = dataframe[dataframe[column] == filter_value]
	print(filtered_df)
	top_usages_list = get_top_groupings(filtered_df, "Group2", size)
	print(f"top_usages_list: {top_usages_list}")
	filtered_df = filtered_df[filtered_df["Group2"].isin(top_usages_list)]
	grouped = filtered_df.groupby(by=["Start", "Group2"])["Costs"].sum().to_frame()
	return grouped


def get_top_groupings(dataframe, column_name, size, filter_column="", filter_name=""):
	dataframe = dataframe.groupby(by=[column_name])["Costs"].sum().nlargest(size).to_frame()
	return dataframe.index.values.tolist()


def get_bottom_groupings(dataframe, column_name, except_top_size):
	total_groups = len(dataframe.groupby(by=[column_name])["Costs"].sum().to_frame().index)
	bottom_size = total_groups - except_top_size
	print(f"bottom_size: {bottom_size}")
	groupings = dataframe.groupby(by=[column_name])["Costs"].sum().nsmallest(bottom_size).to_frame()
	return groupings.index.values.tolist()


def simplify_service_name(name):
	new_name = name.replace("Amazon", "").replace("AWS", "")
	new_name = new_name.replace("Elastic File System", "EFS")
	new_name = new_name.replace("Elastic Load Balancing", "ELB")
	new_name = new_name.replace("Elastic Compute Cloud", "EC2")
	new_name = new_name.replace("Relational Database Service", "RDS")
	new_name = new_name.replace("Simple Storage Service", "S3")
	return new_name

    