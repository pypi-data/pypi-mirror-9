from unittest import TestCase

import os, os.path

from pysoft import SOFTFile


class TestSOFTFileHeader(TestCase):
    def setUp(self):
        self.data_dir = os.path.join('pysoft', 'tests', 'data')

        self.soft = SOFTFile(os.path.join(self.data_dir, 'GDS1099.soft'))

    def tearDown(self):
        pass

    def test_normal_file(self):
        self.assertEqual(self.soft.header['database']['database_name'], 'Gene Expression Omnibus (GEO)')

        self.assertEqual(self.soft.header['dataset']['dataset_type'], 'Expression profiling by array')
        self.assertEqual(len(self.soft.header['dataset']['subsets']), 6)
        self.assertEqual(self.soft.header['dataset']['subsets'][0]['subset_sample_id'], 'GSM37063,GSM37064,GSM37065,GSM37066,GSM37067')

        self.assertEqual(len(self.soft.columns), 37)
        self.assertEqual(self.soft.columns[0].name, 'ID_REF')
        self.assertEqual(self.soft.columns[0].description, 'Platform reference identifier')

        self.assertEqual(len(self.soft.data), 7312)
        self.assertEqual(self.soft.data[0][0], self.soft.data[0]['ID_REF'])
        self.assertEqual(self.soft.data[0][1], self.soft.data[0]['IDENTIFIER'])
        self.assertEqual(self.soft.data[0][-1], self.soft.data[0]['GO:Component ID'])

    def test_assingment(self):
        self.assertEqual(self.soft.data[0][0], 'aas_b2836_at')

        self.soft.data[0][0] = 'foo'
        self.assertEqual(self.soft.data[0][0], 'foo')
        self.assertEqual(self.soft.data[0]['ID_REF'], 'foo')

        self.soft.data[0]['ID_REF'] = 'bar'
        self.assertEqual(self.soft.data[0][0], 'bar')
        self.assertEqual(self.soft.data[0]['ID_REF'], 'bar')

    def test_exceptions(self):
        with self.assertRaises(TypeError):
            self.soft.data[0][3.141]

    def test_gzipped_file(self):
        gz_soft = SOFTFile(os.path.join(self.data_dir, 'GDS1099.soft.gz'))

        self.assertEqual(gz_soft.header, self.soft.header)

        for gzc, c in zip(gz_soft.columns, self.soft.columns):
            self.assertEqual(gzc.name, c.name)
            self.assertEqual(gzc.description, c.description)

    def test_skipped_data(self):
        self.soft = SOFTFile(os.path.join(self.data_dir, 'GDS1099.soft'), skip_data=True)

        self.assertEqual(len(self.soft.data), 0)
