import boto3
import json


costs_exp = boto3.client("ce")


def main():
	costs = get_costs_for_group("2019-04-01", "2020-04-01","MONTHLY", ["SERVICE", "USAGE_TYPE"] )
	#print(json.dumps(costs, indent=3, default=str))
	formatted = format_costs(costs)
	print("Type\tStart\tEnd\tGroup1\tGroup2\tCosts")
	for line in formatted:
		print("Usage\t" + line)


	tag_costs = get_costs_for_group_by_tag_type("2019-04-01", "2020-04-01","MONTHLY", "SERVICE")
	formatted = format_costs(tag_costs)
	#print("Start\tEnd\tService\tTag\tCosts")
	for line in formatted:
		print("Type\t" + line)





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
			group2 = group["Keys"][1]
			blended_cost = group["Metrics"]["BlendedCost"]["Amount"]
			if blended_cost != "0":
				line = f"{start}\t{end}\t\"{group1}\"\t\"{group2}\"\t{blended_cost}"
				lines.append(line)
	return lines



if __name__ == "__main__":
	main()


