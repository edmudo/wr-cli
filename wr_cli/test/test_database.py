import unittest

from wr_cli.database import Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.database = Database(data_dir='wr_cli/data',
                                 db_path='wine.db',
                                 schema_path='wr_cli/schema.txt')
        self.database.load_data()

    def test_nocolumn(self):
        self.assertRaises(ValueError, self.database.do_query,
                          kw=dict(_keyword='review', no_column='test'))

    def test_doquery(self):
        # test cases take a tuple(dict, int) where int is the expected number
        # of results. int may be >=0 for a specific length, -1 for any
        # greater than or equal 0.
        cases = [(dict(_keyword='wine', variety='Red Blend'), -1),
                 (dict(_keyword='review', points=89), -1),
                 (dict(_keyword='review', variety='Red Blend'), -1),
                 (dict(_keyword='reviewer', taster_name='Jim Gordon'), -1),
                 ]

        for (case, length) in cases:
            results = self.database.do_query(case)

            self.assertIsNotNone(results,
                                 msg=f'Results returned None on case `{case}`')

            if length >= 0:
                self.assertEqual(len(results), length,
                                 msg=f'Length of results {length} not as \
                                         expected on case `{case}`')
            elif length == -1:
                self.assertGreater(len(results), 0,
                                   msg=f'Length of results {length} not as \
                                           expected on case `{case}`')

            if length == 0:
                continue

            for key, value in case.items():
                if key == '_keyword':
                    continue
                actual = results[0][key]
                self.assertEqual(actual, value,
                                 msg=f'Failed on case `{case}` for key `{key}` \
                                         that expected `{value}` instead got \
                                         `{actual}`')

        self.database.close()
