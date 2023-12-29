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
FILE_OPTION_BASE_ENV_BASE = "{fob}-{env}".format(fob=FILE_OPTION_BASE, env=ENVIRONMENT)
FILE_OPTION_BASE_ENV_NAME = '{base}.yaml'.format(base=FILE_OPTION_BASE_ENV_BASE)
DEFAULT_ENV_BASE = "{db}-{env}".format(db=DEFAULT_BASE, env=ENVIRONMENT)
DEFAULT_ENV_NAME = '{base}.yaml'.format(base=DEFAULT_ENV_BASE)


FILE_PATH_KEY = 'file_path'
FILE_BASE_KEY = 'file_base'
FILE_NAME_KEY = 'file_name'
FILE_EXTENSION = 'yaml'


TEST_FILE_DIR = '../../data/test_files'


class PathUtilsTests(unittest.TestCase):
    def setUp(self):
        self.test_files = {}

    def tearDown(self):
        self.delete_test_files()

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

    '''    def test_find_path_file_name_with_ext(self):
        self.create_test_file(FILE_OPTION_BASE, FILE_EXTENSION)
        self.create_test_file(FILE_OPTION_BASE_ENV_NAME, FILE_EXTENSION)
        test_file = self.test_files[FILE_OPTION_BASE]
        path = find_path(TEST_FILE_DIR, ENVIRONMENT, test_file[FILE_NAME_KEY], test_file[FILE_BASE_KEY])
        self.assertEqual(test_file[FILE_PATH_KEY], path, "File names did not match.")

    def test_find_path_file_name_with_different_base(self):
        self.create_test_file(FILE_OPTION_BASE, FILE_EXTENSION, do_not_create=True)
        self.create_test_file(FILE_OPTION_BASE_ENV_NAME, FILE_EXTENSION)
        base_dash_simple = "{base}-{simple}".format(base=DEFAULT_BASE, simple=FILE_OPTION_BASE)
        self.create_test_file(base_dash_simple, FILE_EXTENSION)
        test_file = self.test_files[FILE_OPTION_BASE]
        path = find_path(TEST_FILE_DIR, ENVIRONMENT, test_file[FILE_NAME_KEY], DEFAULT_BASE)
        self.assertEqual(self.test_files[base_dash_simple][FILE_PATH_KEY], path, "File names did not match.")

    def test_find_path_file_base_only(self):
        self.create_test_file(FILE_OPTION_BASE, FILE_EXTENSION, do_not_create=True)
        self.create_test_file(FILE_OPTION_BASE_ENV_NAME, FILE_EXTENSION)
        test_file = self.test_files[FILE_OPTION_BASE]
        expected_path = self.test_files[FILE_OPTION_BASE_ENV_NAME][FILE_PATH_KEY]
        path = find_path(TEST_FILE_DIR, ENVIRONMENT, test_file[FILE_BASE_KEY], test_file[FILE_BASE_KEY])
        self.assertEqual(expected_path, path, "File names did not match.")
    '''

    def delete_test_files(self):
        for key in self.test_files.keys():
            if self.test_files[key][FILE_CREATED]:
                os.remove(self.test_files[key][FILE_PATH_KEY])

    def get_file_path(self, file_name):
        return "{dir}/{file}".format(dir=TEST_FILE_DIR, file=file_name)

    def get_file_name(self, file_base, extension):
        return "{file}.{ext}".format(file=file_base, ext=extension)

    def create_test_file(self, file_base, extension, *, do_not_create=False):
        file_name = self.get_file_name(file_base, extension)
        file_path = self.get_file_path(file_name)
        test_file_entry = {FILE_BASE_KEY: file_base, FILE_NAME_KEY: file_name, FILE_PATH_KEY: file_path,
                           FILE_CREATED: not do_not_create}
        self.test_files[file_base] = test_file_entry
        if not do_not_create:
            fp = open(file_path, 'w')
            fp.write('data: THIS IS A TEST FILE\n')
            fp.close()

        return file_path


if __name__=='__main__':
    unittest.main()