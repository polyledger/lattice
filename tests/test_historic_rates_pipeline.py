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
        granularity = 3600  # Every hour
        pipeline_1 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-02', granularity)
        assert pipeline_1.get_request_count() == 1  # ceil(24 / 200) = 1

        granularity = 60  # Every minute
        pipeline_2 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-02', granularity)
        assert pipeline_2.get_request_count() == 8 # ceil((24 * 60) / 200) = 8

        granularity = 1  # Every second
        pipeline_3 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-02', granularity)
        assert pipeline_3.get_request_count() == 432 # ceil((24 * 60 * 60) / 200) = 432

    def test_partition_request(self):
        pipeline_1 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-02', 3600)
        partitions = pipeline_1.partition_request()
        assert type(partitions) is list
        assert len(partitions) == 1
        assert partitions == [('2017-01-01T00:00:00', '2017-01-02T00:00:00')]

        pipeline_2 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-02', 60)
        partitions = pipeline_2.partition_request()
        assert type(partitions) is list
        assert len(partitions) == 8

        pipeline_3 = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01', '2017-01-02', 1)
        partitions = pipeline_3.partition_request()
        assert type(partitions) is list
        assert len(partitions) == 432

    def test_to_file(self):
        path = tempfile.mkstemp()[1]
        pipeline = lattice.HistoricRatesPipeline('BTC-USD', '2017-01-01T00:00:00', '2017-01-01T01:00:00', 3600)

        try:
            pipeline.to_file(filename = 'test', path = tempfile.gettempdir())
            with open(path, 'rb') as f:
                contents = f.read()
        finally:
            os.remove(path)

        self.assertEqual(contents, b'1483228800,969.9,973.4,973.37,970.27,184.70460239999997\r\n')

if __name__ == '__main__':
    unittest.main()
