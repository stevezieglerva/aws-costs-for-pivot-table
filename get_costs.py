import boto3
import json
import calendar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from aws import *


costs_exp = boto3.client("ce")


START_DATE = "2019-04-01"
END_DATE = "2020-04-01"

def main():


	costs = get_costs_for_group(START_DATE, END_DATE, "MONTHLY", ["SERVICE", "USAGE_TYPE"] )
	formatted_json = json.dumps(costs, indent=3, default=str)
##	with open("results_sample_cost.json", "w") as file:
##		file.write(formatted_json)
	formatted = format_costs(costs)
	formatted_with_newlines = ["Usage\t" + i + "\n" for i in formatted]
	with open("results.tsv", "w") as file:
		file.write("Type\tStart\tEnd\tGroup1\tGroup2\tCosts\n")
		file.writelines(formatted_with_newlines)

	plt.style.use("seaborn")

	service_usage_data = pd.read_csv("results.tsv", sep="\t")
	service_usage_data["Start"] =  pd.to_datetime(service_usage_data["Start"], format="%Y-%m-%d")
	print(service_usage_data)
	print(service_usage_data.info())

	df_json = service_usage_data.to_json(orient="columns")
	with open("results_df.json", "w") as file:
		file.write(df_json)


	top_services = group_data_by_top_and_others(service_usage_data, "Group1", 5)
	print(top_services)
	print(top_services.to_frame().info())
	max_monthly_cost = top_services.max()
	print(f"max_monthly_cost:  {max_monthly_cost}")
	top_services.unstack().plot(kind="line", legend=True)
	plt.savefig("plot_top_services_line")

	top_services.unstack().plot(kind="bar", stacked=True, legend=True)
	plt.savefig("plot_top_services_bar")

	top_services.unstack().plot(figsize=(10, 4), kind="area", stacked=True, legend=True)
	plt.savefig("plot_top_services_area")


	create_plots_for_service_multicharts(service_usage_data, max_monthly_cost)
	create_plots_for_service_usage_multicharts(service_usage_data, max_monthly_cost)


	tag_costs = get_costs_for_group_by_tag_type(START_DATE, END_DATE, "MONTHLY", "SERVICE")
	formatted = format_costs(tag_costs)
	#print("Start\tEnd\tService\tTag\tCosts")
##	for line in formatted:
##		print("Type\t" + line)


def create_plots_for_service_multicharts(service_usage_data, max_monthly_cost):
	top_services_list = get_top_groupings(service_usage_data, "Group1", 5)
	count = 0
	for current_service in top_services_list:
		count = count + 1
		service_counts = get_single_grouping(service_usage_data, "Group1", current_service)
		print(f"\n\nService: {current_service}")
		print(service_counts)
		title = simplify_service_name(current_service)
		ax = service_counts.plot(figsize=(2, 1.75), kind="line", legend=False, ylim=(0,max_monthly_cost + 2), xlim=(START_DATE, END_DATE), title=title)
		ax.title.set_size(10)
		plt.axis("off")
		plt.savefig(f"plot_top_service_line_{count}")


def create_plots_for_service_usage_multicharts(service_usage_data, max_monthly_cost):
	top_services_list = get_top_groupings(service_usage_data, "Group1", 5)
	count = 0
	for current_service in top_services_list:
		count = count + 1
		service_counts = get_single_usage_grouping(service_usage_data, "Group1", current_service, 3).unstack()
		print(f"\n\nService Usage: {current_service}")
		print(service_counts)
		title = simplify_service_name(current_service)
		ax = service_counts.plot(figsize=(2, 2.25), kind="bar", stacked=True, legend=True, ylim=(0,max_monthly_cost + 2), xlim=(START_DATE, END_DATE), title=title, color=["#0000FF", "#6495ED", "#B0C4DE"])
		box = ax.get_position()
		ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.8])
		ax.title.set_size(10)
		ax.legend(prop={"size":6}, loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=1)
		plt.axis("off")
		plt.savefig(f"plot_top_service_usage_{count}")





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
	#if filter_column != "":
	#	dataframe = dataframe[dataframe[filter_column] == filter_name]
	dataframe = dataframe.groupby(by=[column_name])["Costs"].sum().nlargest(size).to_frame()
	return dataframe.index.values.tolist()


def get_bottom_groupings(dataframe, column_name, except_top_size):
	total_groups = len(dataframe.groupby(by=[column_name])["Costs"].sum().to_frame().index)
	bottom_size = total_groups - except_top_size
	print(f"bottom_size: {bottom_size}")
	groupings = dataframe.groupby(by=[column_name])["Costs"].sum().nsmallest(bottom_size).to_frame()
	return groupings.index.values.tolist()


def update_dictionary_item_list(current_dict, field_name, value):
	current_list = current_dict.get(field_name, [])
	current_list.append(value)
	current_dict[field_name] = current_list
	return current_dict


def simplify_service_name(name):
	new_name = name.replace("Amazon", "").replace("AWS", "")
	new_name = new_name.replace("Elastic File System", "EFS")
	new_name = new_name.replace("Elastic Load Balancing", "ELB")
	new_name = new_name.replace("Elastic Compute Cloud", "EC2")
	new_name = new_name.replace("Relational Database Service", "RDS")
	new_name = new_name.replace("Simple Storage Service", "S3")



	return new_name


if __name__ == "__main__":
	main()


