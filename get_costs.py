import boto3
import json
import calendar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from aws import *
from panda_helpers import *


costs_exp = boto3.client("ce")


MONTHLY_START_DATE = "2019-04-01"
MONTHLY_END_DATE = "2020-04-01"

def main():
	plt.style.use("seaborn")
	get_and_write_costs_to_files()
	service_usage_data = import_cost_file_into_df()




	top_services = group_data_by_top_and_others(service_usage_data, "Group1", 5)
	print(top_services)
	print(top_services.to_frame().info())
	max_monthly_cost = top_services.max()
	print(f"max_monthly_cost:  {max_monthly_cost}")
	top_services.unstack().plot(kind="line", legend=True)
	plt.savefig("plot_top_services_line")

	top_services.unstack().plot(kind="bar", stacked=True, width=.9, legend=True)
	plt.savefig("plot_top_services_bar")

	top_services.unstack().plot(figsize=(10, 4), kind="area", stacked=True, legend=True)
	plt.savefig("plot_top_services_area")


	create_plots_for_service_multicharts(service_usage_data, max_monthly_cost)
	create_plots_for_service_usage_multicharts(service_usage_data, max_monthly_cost)


	tag_costs = get_costs_for_group_by_tag_type(MONTHLY_START_DATE, MONTHLY_END_DATE, "MONTHLY", "SERVICE")
	formatted = format_costs(tag_costs)
	#print("Start\tEnd\tService\tTag\tCosts")
##	for line in formatted:
##		print("Type\t" + line)



def import_cost_file_into_df():
	service_usage_data = pd.read_csv("results.tsv", sep="\t")
	service_usage_data["Start"] =  pd.to_datetime(service_usage_data["Start"], format="%Y-%m-%d")
	print(service_usage_data)
	print(service_usage_data.info())
	return service_usage_data

def get_and_write_costs_to_files():
	costs = get_costs_for_group(MONTHLY_START_DATE, MONTHLY_END_DATE, "MONTHLY", ["SERVICE", "USAGE_TYPE"] )
	formatted_json = json.dumps(costs, indent=3, default=str)
	with open("results_sample_cost.json", "w") as file:
		file.write(formatted_json)
	formatted = format_costs(costs)
	formatted_with_newlines = ["Usage\t" + i + "\n" for i in formatted]
	with open("results.tsv", "w") as file:
		file.write("Type\tStart\tEnd\tGroup1\tGroup2\tCosts\n")
		file.writelines(formatted_with_newlines)


def create_plots_for_service_multicharts(service_usage_data, max_monthly_cost):
	top_services_list = get_top_groupings(service_usage_data, "Group1", 5)
	count = 0
	for current_service in top_services_list:
		count = count + 1
		service_counts = get_single_grouping(service_usage_data, "Group1", current_service)
		print(f"\n\nService: {current_service}")
		print(service_counts)
		title = simplify_service_name(current_service)
		ax = service_counts.plot(figsize=(2, 1.75), kind="line", legend=False, ylim=(0,max_monthly_cost + 2), xlim=(MONTHLY_START_DATE, MONTHLY_END_DATE), title=title)
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
		ax = service_counts.plot(figsize=(2, 2.25), kind="line", legend=True, ylim=(0,max_monthly_cost + 2), xlim=(MONTHLY_START_DATE, MONTHLY_END_DATE), title=title, color=["#0000FF", "#6495ED", "#B0C4DE"])
		box = ax.get_position()
		ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.8])
		ax.title.set_size(10)
		ax.legend(prop={"size":6}, loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=1)
		plt.axis("off")
		plt.savefig(f"plot_top_service_usage_{count}")






if __name__ == "__main__":
	main()


