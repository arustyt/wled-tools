import unittest

import yaml

from wled_utils.logger_utils import init_logger
from wled_utils.property_tools import PropertyEvaluator


class PropertyToolsTests(unittest.TestCase):
    def setUp(self):
        test_yaml = """
env1:
  qual1:
    prop1: env1.qual1.prop1
  prop2: env1.prop2
env2:
  qual1:
    prop1: env2.qual1.prop1
    
qual1:
  prop1: qual1.prop1
  
qual2:
  env1:
    prop4: qual2.env1.prop4
  env2:
    prop4: qual2.env2.prop4
  prop5: qual2.prop5
  
prop3: prop3

qual3:
  qual4:
    qual5:
      prop5: qual3.qual4.qual5.prop5

qual4:
  qual5:
    prop5: qual4.qual5.prop5

"""
        test_data = yaml.safe_load(test_yaml)
        self.property_evaluator = PropertyEvaluator(test_data, verbose=True)
        init_logger()

    def tearDown(self):
        pass

    def test_get_property_no_env_optional_qual_1_missing_1_present(self):
        actual = self.property_evaluator.get_property("env1", "[qual6.qual4].qual5.prop5")
        self.assertEqual("qual4.qual5.prop5", actual, "Incorrect property value.")

    def test_get_property_env1_ordered(self):
        actual = self.property_evaluator.get_property("env1", "qual1", "prop1")
        self.assertEqual("env1.qual1.prop1", actual, "Incorrect property value.")

    def test_get_property_env1_unordered(self):
        actual = self.property_evaluator.get_property("env1", "qual2", "prop4")
        self.assertEqual("qual2.env1.prop4", actual, "Incorrect property value.")

    def test_get_property_no_env_optional_qual_present(self):
        actual = self.property_evaluator.get_property("env1", "[qual3].qual4.qual5.prop5")
        self.assertEqual("qual3.qual4.qual5.prop5", actual, "Incorrect property value.")

    def test_get_property_no_env_optional_qual_missing(self):
        actual = self.property_evaluator.get_property("env1", "[qual6].qual4.qual5.prop5")
        self.assertEqual("qual4.qual5.prop5", actual, "Incorrect property value.")

    def test_get_property_env2(self):
        actual = self.property_evaluator.get_property("env2", "qual1.prop1")
        self.assertEqual("env2.qual1.prop1", actual, "Incorrect property value.")

    def test_get_property_bogus_env(self):
        actual = self.property_evaluator.get_property("bogus_env", "qual1", "prop1")
        self.assertEqual("qual1.prop1", actual, "Incorrect property value.")

    def test_get_property_no_env(self):
        actual = self.property_evaluator.get_property("env1", "prop3")
        self.assertEqual("prop3", actual, "Incorrect property value.")

    def test_get_property_is_dict(self):
        with self.assertRaises(ValueError):
            self.property_evaluator.get_property("env1.qual1")

