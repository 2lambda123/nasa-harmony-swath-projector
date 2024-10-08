from unittest import TestCase
from unittest.mock import ANY, patch

from harmony.message import Message
from harmony.util import config

from swath_projector.adapter import SwathProjectorAdapter
from tests.test_utils import StringContains, download_side_effect


@patch('swath_projector.adapter.stage', return_value='https://example.com/data')
@patch('swath_projector.adapter.download', side_effect=download_side_effect)
class TestPyResampleReproject(TestCase):
    """A suite of tests to test SwotRepr, using pyresample and the valid input
    interpolation options.

    """

    def test_pyresample_interpolation(self, mock_download, mock_stage):
        """Ensure SwotRepr will successfully complete when using pyresample and
        each specified interpolation.

        """
        valid_interpolations = ['bilinear', 'ewa', 'ewa-nn', 'near']

        for interpolation in valid_interpolations:
            with self.subTest(f'pyresample "{interpolation}" interpolation.'):
                test_data = Message(
                    {
                        'accessToken': 'fake_token',
                        'callback': 'https://example.com/callback',
                        'stagingLocation': 's3://example-bucket/example-path/',
                        'sources': [
                            {
                                'granules': [
                                    {
                                        'url': 'tests/data/VOL2PSST_2017.nc',
                                        'temporal': {
                                            'start': '2020-01-01T00:00:00.000Z',
                                            'end': '2020-01-02T00:00:00.000Z',
                                        },
                                        'bbox': [-180, -90, 180, 90],
                                    }
                                ],
                            }
                        ],
                        'format': {
                            'crs': 'EPSG:32603',
                            'interpolation': interpolation,
                            'width': 1000,
                            'height': 500,
                        },
                    }
                )

                reprojector = SwathProjectorAdapter(test_data, config=config(False))
                reprojector.invoke()

                mock_download.assert_called_once_with(
                    'tests/data/VOL2PSST_2017.nc',
                    ANY,
                    logger=ANY,
                    access_token='fake_token',
                    cfg=ANY,
                )
                mock_stage.assert_called_once_with(
                    StringContains('VOL2PSST_2017_repr.nc'),
                    'VOL2PSST_2017_regridded.nc',
                    'application/x-netcdf',
                    location='s3://example-bucket/example-path/',
                    logger=ANY,
                )

                # Reset mock calls for next interpolation
                mock_download.reset_mock()
                mock_stage.reset_mock()
