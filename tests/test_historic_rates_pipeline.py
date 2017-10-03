import unittest
import tempfile
import lattice
import os

class TestHistoricRatesPipeline(unittest.TestCase):

    def test_constructor(self):
        with self.assertRaises(TypeError):
            pipeline = lattice.HistoricRatesPipeline()

        pipeline = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-01', 3600)

    def test_get_request_count(self):

        #==== One day ====#

        granularity = 84600  # Every day
        pipeline_0 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-02', granularity)
        self.assertEqual(pipeline_0.get_request_count(), 1)  # ceil(1 / 200) = 1

        granularity = 3600  # Every hour
        pipeline_1 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-02', granularity)
        self.assertEqual(pipeline_1.get_request_count(), 1)  # ceil(24 / 200) = 1

        granularity = 60  # Every minute
        pipeline_2 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-02', granularity)
        self.assertEqual(pipeline_2.get_request_count(), 8) # ceil((24 * 60) / 200) = 8

        granularity = 1  # Every second
        pipeline_3 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-02', granularity)
        self.assertEqual(pipeline_3.get_request_count(), 432) # ceil((24 * 60 * 60) / 200) = 432

        #==== 15 days ====#

        granularity = 3600  # Every hour
        pipeline_4 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-16', granularity)
        self.assertEqual(pipeline_4.get_request_count(), 2)  # ceil(24 * 15 / 200) = 2

        granularity = 60  # Every minute
        pipeline_5 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-16', granularity)
        self.assertEqual(pipeline_5.get_request_count(), 108) # ceil((24 * 60 * 15) / 200) = 108

        granularity = 1  # Every second
        pipeline_6 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-16', granularity)
        self.assertEqual(pipeline_6.get_request_count(), 6480) # ceil((24 * 60 * 60 * 15) / 200) = 6480

    def test_partition_request(self):
        pipeline_1 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-02', 3600)
        partitions = pipeline_1.partition_request(silent=True)
        self.assertIsInstance(partitions, list)
        self.assertEqual(len(partitions), 1)
        self.assertEqual(partitions, [('2017-01-01T00:00:00', '2017-01-02T00:00:00')])

        pipeline_2 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-02', 60)
        partitions = pipeline_2.partition_request(silent=True)
        self.assertIsInstance(partitions, list)
        self.assertEqual(len(partitions), 8)

        pipeline_3 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-02', 1)
        partitions = pipeline_3.partition_request(silent=True)
        self.assertIsInstance(partitions, list)
        self.assertEqual(len(partitions), 432)

    def test_to_file(self):
        pipeline = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01T00:00:00', '2017-01-01T01:00:00', 3600)
        file_path = tempfile.gettempdir() + '/test.csv'

        try:
            pipeline.to_file(filename='test', path=tempfile.gettempdir(), silent=True)
            with open(file_path, 'rb') as f:
                contents = f.read()
        finally:
            os.remove(file_path)

        self.assertEqual(contents, b'1483228800,969.9,973.4,973.37,970.27,184.70460239999997\r\n')

    def test_to_list(self):
        pipeline = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01T00:00:00', '2017-01-01T01:00:00', 3600)
        test_list = pipeline.to_list(silent=True)
        self.assertIsInstance(test_list, list)
        self.assertEqual(test_list, [[1483228800, 969.9, 973.4, 973.37, 970.27, 184.70460239999997]])

if __name__ == '__main__':
    unittest.main()
