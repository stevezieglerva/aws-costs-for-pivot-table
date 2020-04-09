import boto3
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


costs_exp = boto3.client("ce")


def main():


##	costs = get_costs_for_group("2019-04-01", "2020-04-01","MONTHLY", ["SERVICE", "USAGE_TYPE"] )
##	formatted_json = json.dumps(costs, indent=3, default=str)
##	with open("results_sample_cost.json", "w") as file:
##		file.write(formatted_json)
##	formatted = format_costs(costs)
##	print("Type\tStart\tEnd\tGroup1\tGroup2\tCosts")
##	for line in formatted:
##		print("Usage\t" + line)

##	formatted_with_newlines = ["Usage\t" + i + "\n" for i in formatted]
##	with open("results.tsv", "w") as file:
##		file.write("Type\tStart\tEnd\tGroup1\tGroup2\tCosts\n")
##		file.writelines(formatted_with_newlines)

	plt.style.use("seaborn")

	service_usage_data = pd.read_csv("results.tsv", sep="\t")
	service_usage_data["Start"] =  pd.to_datetime(service_usage_data["Start"], format="%Y-%m-%d")
	print(service_usage_data)
	print(service_usage_data.info())

	df_json = service_usage_data.to_json(orient="columns")
	with open("results_df.json", "w") as file:
		file.write(df_json)


	cw = service_usage_data[service_usage_data["Group2"] == "CW:AlarmMonitorUsage"][["Start", "Costs"]]
	cw["Start"] =  pd.to_datetime(cw["Start"], format="%Y-%m-%d")
	cw.set_index("Start", inplace=True)
	print(cw)
	print(cw.info())
	cw.plot(kind="line")
	plt.savefig("plot_cw_usage")


	top_services = service_usage_data.groupby(by=["Group1"])["Costs"].sum().nlargest(5)
	print(top_services)


	plt.title = "Service Costs/month"
	plt.xlabel = "Date"
	plt.ylabel = "Costs"
	service_grouping = service_usage_data.groupby(by=["Start", "Group1"])["Costs"].sum()
	graph = service_grouping.unstack().plot(legend=False)
	graph.legend(["EC2 - Other"])
	plt.savefig("plot_service_by_month")

	service_grouping["Start"] =  pd.to_datetime(service_usage_data["Start"], format="%Y-%m-%d")
	print("Sums")
	with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
		print(service_grouping)
	print("End Sums")


	tag_costs = get_costs_for_group_by_tag_type("2019-04-01", "2020-04-01", "MONTHLY", "SERVICE")
	formatted = format_costs(tag_costs)
	#print("Start\tEnd\tService\tTag\tCosts")
##	for line in formatted:
##		print("Type\t" + line)


def get_costs_for_group(start, end, granularity, groupby):
	groupby_list = []
	for grouping in groupby:
		item = {}
		item["Type"] = "DIMENSION"
		item["Key"] = grouping
		groupby_list.append(item)
	costs = costs_exp.get_cost_and_usage(TimePeriod={"Start" : start, "End" : end}, Granularity=granularity, Metrics=["BLENDED_COST"], GroupBy=groupby_list)
	return costs


def get_costs_for_group_by_tag_type(start, end, granularity, groupby_value):
	groupby_list = []
	item = {}
	item["Type"] = "DIMENSION"
	item["Key"] = groupby_value
	groupby_list.append(item)
	item = {}
	item["Type"] = "TAG"
	item["Key"] = "Type"
	groupby_list.append(item)
	costs = costs_exp.get_cost_and_usage(TimePeriod={"Start" : start, "End" : end}, Granularity=granularity, Metrics=["BLENDED_COST"], GroupBy=groupby_list)
	return costs


def format_costs(costs):
	lines = []
	for time_period in costs["ResultsByTime"]:
		start = time_period["TimePeriod"]["Start"]
		end = time_period["TimePeriod"]["End"]
		for group in time_period["Groups"]:
			group1 = group["Keys"][0]
			group2 = group["Keys"][1].replace("Type$", "")
			blended_cost = group["Metrics"]["BlendedCost"]["Amount"]
			if blended_cost != "0":
				line = f"{start}\t{end}\t\"{group1}\"\t\"{group2}\"\t{blended_cost}"
				lines.append(line)
	return lines


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


def group_data_by_top_and_others(dataframe, column_name, size):
	top_groupings_list = get_top_groupings(dataframe, column_name, size)
	print(f"top_groupings: {top_groupings_list}")
	top_groupings = dataframe[dataframe[column_name].isin(top_groupings_list)]
	top_grouping_counts = top_groupings.groupby(by=[column_name])["Costs"].sum()
	print(top_grouping_counts)

	bottom_groupings_list =  get_bottom_groupings(dataframe, column_name, size)
	print(f"bottom_groupings: {bottom_groupings_list}")
	bottom_groupings = dataframe[dataframe[column_name].isin(bottom_groupings_list)]


	
	bottom_grouping_counts = bottom_groupings.groupby(by=[column_name])["Costs"].sum()
	print(bottom_grouping_counts)



def get_top_groupings(dataframe, column_name, size):
	groupings = dataframe.groupby(by=[column_name])["Costs"].sum().nlargest(size).to_frame()
	return groupings.index.values.tolist()


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




if __name__ == "__main__":
	main()


