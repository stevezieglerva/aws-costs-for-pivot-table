import boto3
import json


costs_exp = boto3.client("ce")


def main():
	costs = costs_exp.get_cost_and_usage(TimePeriod={"Start" : "2020-01-01", "End" : "2020-04-01"}, Granularity="MONTHLY", Metrics=["BLENDED_COST"], GroupBy=[{"Type" : "DIMENSION", "Key" : "SERVICE"}, {"Type" : "DIMENSION", "Key" : "USAGE_TYPE"}])
	print(json.dumps(costs, indent=3, default=str))


def get_costs_for_group(start, end, granularity, groupby):
	costs = costs_exp.get_cost_and_usage(TimePeriod={"Start" : "2020-01-01", "End" : "2020-04-01"}, Granularity="MONTHLY", Metrics=["BLENDED_COST"], GroupBy=[{"Type" : "DIMENSION", "Key" : "SERVICE"}])
	print(json.dumps(costs, indent=3, default=str))
	return costs

if __name__ == "__main__":
	main()


