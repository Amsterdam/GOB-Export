"""BRK2 kadastraleobjecten utils tests."""


from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from freezegun import freeze_time
from gobexport.exporter.config.brk2.utils import (
    _get_filename_date,
    brk2_directory,
    brk2_filename,
)


class TestBrk2Utils(TestCase):
    @patch("gobexport.exporter.config.brk2.utils._get_filename_date", datetime.now)
    def test_brk2_filename(self):
        self.assertEqual(
            f"AmsterdamRegio/CSV_ActueelMetSubj/BRK_FileName_{datetime.now().strftime('%Y%m%d')}.csv",
            brk2_filename("FileName"),
        )

        self.assertEqual(
            f"AmsterdamRegio/SHP_ActueelMetSubj/BRK_FileName_{datetime.now().strftime('%Y%m%d')}.shp",
            brk2_filename("FileName", file_type="shp"),
        )

        self.assertEqual(
            "AmsterdamRegio/SHP_ActueelMetSubj/BRK_FileName.prj",
            brk2_filename(
                "FileName",
                file_type="prj",
                append_date=False,
            ),
        )

        # Assert undefined file type raises error
        with self.assertRaises(AssertionError):
            brk2_filename("FileName", file_type="xxx")

    @patch("gobexport.exporter.config.brk2.utils._get_filename_date", lambda: None)
    def test_brk2_filename_none_date(self):
        self.assertEqual(
            "AmsterdamRegio/CSV_ActueelMetSubj/BRK_FileName_00000000.csv",
            brk2_filename("FileName"),
        )

    def test_brk2_filename_sensitive(self):
        self.assertEqual(
            "AmsterdamRegio/CSV_ActueelMetSubj/BRK_FileName.csv",
            brk2_filename("FileName", append_date=False, use_sensitive_dir=True),
        )

    def test_brk2_directory(self):
        self.assertEqual(
            "AmsterdamRegio/CSV_Actueel", brk2_directory(use_sensitive_dir=False)
        )

    @patch("gobexport.exporter.config.brk2.utils.requests.get")
    def test_get_filename_date(self, mock_request_get):
        mock_request_get.return_value.status_code = 200
        mock_request_get.return_value.json.return_value = {
            "id": 1,
            "kennisgevingsdatum": "2019-09-03T00:00:00",
        }

        expected_date = datetime(year=2019, month=9, day=3)
        with freeze_time("2021-02-18T00:00:00"):
            self.assertEqual(expected_date, _get_filename_date())
            mock_request_get.assert_called_once()

        mock_request_get.reset_mock()
        with freeze_time("2021-02-18T00:00:09"):
            # Should be cached
            self.assertEqual(expected_date, _get_filename_date())
            mock_request_get.assert_not_called()

        with freeze_time("2021-02-18T00:00:11"):
            self.assertEqual(expected_date, _get_filename_date())
            mock_request_get.assert_called_once()

    @patch("gobexport.exporter.config.brk2.utils.requests.get")
    def test_get_filename_date_404(self, mock_request_get):
        mock_request_get.return_value.status_code = 404
        self.assertIsNone(_get_filename_date())
