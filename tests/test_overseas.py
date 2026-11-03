import unittest
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

from modules.overseas import get_start_time


class GetStartTimeTests(unittest.TestCase):
    def test_parses_time_area_line_page(self):
        soup = BeautifulSoup(
            """
            <div class="time_area_line">
              <div class="unit">
                <div class="cell cap">発走予定時刻</div>
                <div class="cell time">日本時間<strong>4月26日（日曜）<span>15時35分</span></strong></div>
              </div>
            </div>
            """,
            "html.parser",
        )

        with patch("modules.overseas.bsc.get_soup", return_value=soup):
            start_time = get_start_time("https://example.com/hkch/", 2026)

        self.assertEqual(
            start_time,
            datetime(2026, 4, 26, 15, 35, tzinfo=ZoneInfo("Asia/Tokyo")),
        )

    def test_parses_time_area_grid_page(self):
        soup = BeautifulSoup(
            """
            <div class="time_area_grid">
              <div class="unit">
                <div class="cap">発走予定時刻</div>
                <div class="line">日本時間11月3日（祝日・火曜）13時00分</div>
              </div>
            </div>
            """,
            "html.parser",
        )

        with patch("modules.overseas.bsc.get_soup", return_value=soup):
            start_time = get_start_time("https://example.com/melbourne/", 2026)

        self.assertEqual(
            start_time,
            datetime(2026, 11, 3, 13, 0, tzinfo=ZoneInfo("Asia/Tokyo")),
        )

    def test_converts_afternoon_noon_without_advancing_to_next_day(self):
        soup = BeautifulSoup(
            """
            <div class="time_area_grid">
              <div class="unit">
                <div class="cap">発走予定時刻</div>
                <div class="line">日本時間11月3日（火曜）午後12時00分</div>
              </div>
            </div>
            """,
            "html.parser",
        )

        with patch("modules.overseas.bsc.get_soup", return_value=soup):
            start_time = get_start_time("https://example.com/race/", 2026)

        self.assertEqual(
            start_time,
            datetime(2026, 11, 3, 12, 0, tzinfo=ZoneInfo("Asia/Tokyo")),
        )


if __name__ == "__main__":
    unittest.main()
