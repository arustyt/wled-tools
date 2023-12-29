import os
import unittest

from wled_utils.path_utils import find_path, get_file_name_candidates

FILE_CREATED = 'created'

ENVIRONMENT = 'test_env'
DONT_CARE_ENVIRONMENT = 'dont_care'
FILE_OPTION_BASE = 'file_option'
FILE_OPTION_NAME = '{fob}.yaml'.format(fob=FILE_OPTION_BASE)
DEFAULT_BASE = 'default'
DEFAULT_NAME = '{db}.yaml'.format(db=DEFAULT_BASE)
FILE_OPTION_ENV_BASE = "{fob}-{env}".format(fob=FILE_OPTION_BASE, env=ENVIRONMENT)
FILE_OPTION_BASE_ENV_NAME = '{base}.yaml'.format(base=FILE_OPTION_ENV_BASE)
DEFAULT_ENV_BASE = "{db}-{env}".format(db=DEFAULT_BASE, env=ENVIRONMENT)
DEFAULT_ENV_NAME = '{base}.yaml'.format(base=DEFAULT_ENV_BASE)

FILE_PATH_KEY = 'file_path'
FILE_BASE_KEY = 'file_base'
FILE_NAME_KEY = 'file_name'
FILE_EXTENSION = 'yaml'

TEST_FILE_DIR = '../../data/test_files'


class PathUtilsTests(unittest.TestCase):
    def setUp(self):
        self.test_files = []

    def tearDown(self):
        self.delete_test_files()

    # get_file_name_candidates tests ================================================================================

    def test_get_file_name_candidates_file_option_yaml(self):
        candidates = get_file_name_candidates(DONT_CARE_ENVIRONMENT, FILE_OPTION_NAME, FILE_OPTION_BASE)
        self.assertEqual(1, len(candidates), "Number of candidates is incorrect.")
        self.assertEqual([FILE_OPTION_NAME], candidates)

    def test_get_file_name_candidates_env_not_none_file_option_none(self):
        candidates = get_file_name_candidates(ENVIRONMENT, None, DEFAULT_BASE)
        self.assertEqual([DEFAULT_ENV_NAME, DEFAULT_NAME], candidates, "Candidate mismatch.")

    def test_get_file_name_candidates_env_not_none_file_option_not_none(self):
        candidates = get_file_name_candidates(ENVIRONMENT, FILE_OPTION_BASE, DEFAULT_BASE)
        self.assertEqual([FILE_OPTION_BASE_ENV_NAME, FILE_OPTION_NAME],
                         candidates, "Candidate mismatch.")

    def test_get_file_name_candidates_env_none_file_option_none(self):
        candidates = get_file_name_candidates(None, None, DEFAULT_BASE)
        self.assertEqual([DEFAULT_NAME], candidates, "Candidate mismatch.")

    def test_get_file_name_candidates_env_none_file_option_not_none(self):
        candidates = get_file_name_candidates(None, FILE_OPTION_BASE, DEFAULT_BASE)
        self.assertEqual([FILE_OPTION_NAME],
                         candidates, "Candidate mismatch.")

    # find_path tests ================================================================================

    def test_find_path_file_option_yaml(self):
        expected_path = self.create_test_file(FILE_OPTION_BASE, FILE_EXTENSION)
        actual_path = find_path(TEST_FILE_DIR, ENVIRONMENT, FILE_OPTION_NAME, DEFAULT_BASE)
        self.assertEqual(expected_path, actual_path, "File paths do not match.")

    def test_find_path_file_option_yaml_not_exist(self):
        with self.assertRaises(ValueError):
            find_path(TEST_FILE_DIR, ENVIRONMENT, FILE_OPTION_NAME, DEFAULT_BASE)

    def test_find_path_env_not_none_file_option_none_both_exist(self):
        self.create_test_file(DEFAULT_BASE, FILE_EXTENSION)
        expected_path = self.create_test_file(DEFAULT_ENV_BASE, FILE_EXTENSION)
        actual_path = find_path(TEST_FILE_DIR, ENVIRONMENT, None, DEFAULT_BASE)
        self.assertEqual(expected_path, actual_path, "File paths do not match.")

    def test_find_path_env_not_none_file_option_none_env_exists(self):
        expected_path = self.create_test_file(DEFAULT_ENV_BASE, FILE_EXTENSION)
        actual_path = find_path(TEST_FILE_DIR, ENVIRONMENT, None, DEFAULT_BASE)
        self.assertEqual(expected_path, actual_path, "File paths do not match.")

    def test_find_path_env_not_none_file_option_none_default_exists(self):
        expected_path = self.create_test_file(DEFAULT_BASE, FILE_EXTENSION)
        actual_path = find_path(TEST_FILE_DIR, ENVIRONMENT, None, DEFAULT_BASE)
        self.assertEqual(expected_path, actual_path, "File paths do not match.")

    def test_find_path_env_not_none_file_option_none_none_exist(self):
        with self.assertRaises(ValueError):
            find_path(TEST_FILE_DIR, ENVIRONMENT, None, DEFAULT_BASE)

    def test_find_path_env_not_none_file_option_not_none_both_exist(self):
        self.create_test_file(FILE_OPTION_BASE, FILE_EXTENSION)
        expected_path = self.create_test_file(FILE_OPTION_ENV_BASE, FILE_EXTENSION)
        actual_path = find_path(TEST_FILE_DIR, ENVIRONMENT, FILE_OPTION_BASE, DEFAULT_BASE)
        self.assertEqual(expected_path, actual_path, "File paths do not match.")

    def test_find_path_env_not_none_file_option_not_none_env_exists(self):
        expected_path = self.create_test_file(FILE_OPTION_ENV_BASE, FILE_EXTENSION)
        actual_path = find_path(TEST_FILE_DIR, ENVIRONMENT, FILE_OPTION_BASE, DEFAULT_BASE)
        self.assertEqual(expected_path, actual_path, "File paths do not match.")

    def test_find_path_env_not_none_file_option_not_none_file_option_exists(self):
        expected_path = self.create_test_file(FILE_OPTION_BASE, FILE_EXTENSION)
        actual_path = find_path(TEST_FILE_DIR, ENVIRONMENT, FILE_OPTION_BASE, DEFAULT_BASE)
        self.assertEqual(expected_path, actual_path, "File paths do not match.")

    def test_find_path_env_not_none_file_option_not_none_none_exist(self):
        with self.assertRaises(ValueError):
            find_path(TEST_FILE_DIR, ENVIRONMENT, FILE_OPTION_BASE, DEFAULT_BASE)

    def test_find_path_env_none_file_option_none_default_exists(self):
        expected_path = self.create_test_file(DEFAULT_BASE, FILE_EXTENSION)
        actual_path = find_path(TEST_FILE_DIR, None, None, DEFAULT_BASE)
        self.assertEqual(expected_path, actual_path, "File paths do not match.")

    def test_find_path_env_none_file_option_none_none_exist(self):
        with self.assertRaises(ValueError):
            find_path(TEST_FILE_DIR, None, None, DEFAULT_BASE)

    def test_find_path_env_none_file_option_not_none_file_option_exists(self):
        expected_path = self.create_test_file(FILE_OPTION_BASE, FILE_EXTENSION)
        actual_path = find_path(TEST_FILE_DIR, None, FILE_OPTION_BASE, DEFAULT_BASE)
        self.assertEqual(expected_path, actual_path, "File paths do not match.")

    def test_find_path_env_none_file_option_not_none_none_exist(self):
        with self.assertRaises(ValueError):
            find_path(TEST_FILE_DIR, None, FILE_OPTION_BASE, DEFAULT_BASE)

    # helper methods ================================================================================

    def delete_test_files(self):
        for test_file in self.test_files:
            os.remove(test_file)

    def get_file_path(self, file_base, extension):
        return "{dir}/{file}.{ext}".format(dir=TEST_FILE_DIR, file=file_base, ext=extension)

    def create_test_file(self, file_base, extension):
        file_path = self.get_file_path(file_base, extension)
        self.test_files.append(file_path)
        fp = open(file_path, 'w')
        fp.write('data: THIS IS A TEST FILE\n')
        fp.close()

        return file_path


if __name__ == '__main__':
    unittest.main()
