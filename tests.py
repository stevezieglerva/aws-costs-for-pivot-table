import unittest
from unittest.mock import patch, Mock, MagicMock, PropertyMock
from get_costs import *
import pandas as pd



cost_data = {
   "GroupDefinitions": [
      {
         "Type": "DIMENSION",
         "Key": "SERVICE"
      },
      {
         "Type": "DIMENSION",
         "Key": "USAGE_TYPE"
      }
   ],
   "ResultsByTime": [
      {
         "TimePeriod": {
            "Start": "2019-04-01",
            "End": "2019-05-01"
         },
         "Total": {},
         "Groups": [
            {
               "Keys": [
                  "AWS Budgets",
                  "BudgetsUsage"
               ],
               "Metrics": {
                  "BlendedCost": {
                     "Amount": "1",
                     "Unit": "USD"
                  }
               }
            },
            {
               "Keys": [
                  "AWS Key Management Service",
                  "us-east-1-KMS-Requests"
               ],
               "Metrics": {
                  "BlendedCost": {
                     "Amount": "2",
                     "Unit": "USD"
                  }
               }
            }
		 ]
	  },
      {
         "TimePeriod": {
            "Start": "2019-05-01",
            "End": "2019-06-01"
         },
         "Total": {},
         "Groups": [
            {
               "Keys": [
                  "AWS Budgets",
                  "BudgetsUsage"
               ],
               "Metrics": {
                  "BlendedCost": {
                     "Amount": "3",
                     "Unit": "USD"
                  }
               }
            },
            {
               "Keys": [
                  "AWS Key Management Service",
                  "us-east-1-KMS-Requests"
               ],
               "Metrics": {
                  "BlendedCost": {
                     "Amount": "4",
                     "Unit": "USD"
                  }
               }
            }
		 ]
	  }
   ]
}

grouping_sample = {
	"fruit" : ["apples", "pears", "oranges", "apples", "oranges", "blueberries"],
	"Costs" : [4, 50, 6, 4, 1, 0]
}

class UnitTests(unittest.TestCase):
##	def test_update_dictionary_item_list__given_empty_list__then_one_item_added(self):
##		# Arrange
##		starting_dict = {}
##		item_name = "fieldA"
##		value = "hello"
##	
##		# Act
##		updated_list = update_dictionary_item_list(starting_dict, item_name, value)
##	
##		# Assert
##		self.assertEqual(updated_list["fieldA"], [value])
##
##	def test_update_dictionary_item_list__given_starting_list__then_one_item_added(self):
##		# Arrange
##		starting_dict = {"fieldA" : ["apples"]}
##		item_name = "fieldA"
##		value = "bananas"
##	
##		# Act
##		updated_list = update_dictionary_item_list(starting_dict, item_name, value)
##	
##		# Assert
##		self.assertEqual(updated_list["fieldA"], ["apples", "bananas"])
##
##	def test_format_dataframe_json__given_costs_json__then_format_correct(self):
##		# Arrange
##		input = cost_data
##	
##		# Act
##		results = format_dataframe_json(input)
##		print(json.dumps(results, indent=3, default=str))
##	
##		# Assert
##		self.assertEqual(len(results["Start"]), 4)
##		self.assertEqual(len(results["End"]), 4)
##		self.assertEqual(len(results["Group1"]), 4)
##		self.assertEqual(len(results["Group2"]), 4)
##		self.assertEqual(len(results["Costs"]), 4)
##
##	def test_update_dictionary_item_list__given_starting_list__then_one_item_added(self):
##		# Arrange
##		starting_dict = {"fieldA" : ["apples"]}
##		item_name = "fieldA"
##		value = "bananas"
##	
##		# Act
##		updated_list = update_dictionary_item_list(starting_dict, item_name, value)
##	
##		# Assert
##		self.assertEqual(updated_list["fieldA"], ["apples", "bananas"])
##
##	def test_format_dataframe_json__given_costs_json__then_loads_into_dataframe(self):
##		# Arrange
##		input = cost_data
##	
##		# Act
##		results = format_dataframe_json(input)
##	
##		# Assert
##		cost_df = pd.DataFrame(results)
##		print(cost_df)

	def test_get_top_groupings__given_specific_data__then_top_correct_returned(self):
		# Arrange
		dataframe = pd.DataFrame(grouping_sample)
		print(dataframe)
		print(dataframe.info())

		# Act
		top_groupings = get_top_groupings(dataframe, "fruit", 2)
		print("*** top groupings")
		print(top_groupings)
	
		# Assert
		self.assertEqual(top_groupings, ["pears", "apples"])

	def test_get_bottom_groupings__given_specific_data__then_top_correct_returned(self):
		# Arrange
		dataframe = pd.DataFrame(grouping_sample)
		print(dataframe)
		print(dataframe.info())

		# Act
		groupings = get_bottom_groupings(dataframe, "fruit", 2)
		print("*** bottom groupings")
		print(groupings)
	
		# Assert
		self.assertEqual(groupings, ["blueberries", "oranges"])


if __name__ == "__main__":
	unittest.main()

