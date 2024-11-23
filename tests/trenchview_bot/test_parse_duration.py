from datetime import timedelta

from trenchview.trenchview_bot import DEFAULT_DURATION, parse_duration


class TestParseDuration:
    def test_m(self):
        for i in range(30):
            s = f"{i}m"

            if i == 0:
                assert parse_duration(s) == DEFAULT_DURATION 
            else:
                assert parse_duration(s) == timedelta(minutes=i)

    def test_h(self):
        for i in range(30):
            s = f"{i}h"

            if i == 0:
                assert parse_duration(s) == DEFAULT_DURATION 
            else:
                assert parse_duration(s) == timedelta(hours=i)

    def test_d(self):
        for i in range(30):
            s = f"{i}d"

            if i == 0:
                assert parse_duration(s) == DEFAULT_DURATION 
            else:
                print(s)
                assert parse_duration(s) == timedelta(days=i)

    def test_hybrid(self):
        s1 = "1d23h2m"
        assert parse_duration(s1) == timedelta(days=1, hours=23, minutes=2)

        s2 = "2d21m"
        assert parse_duration(s2) == timedelta(days=2, minutes=21)


        s3 = "2h1m"
        assert parse_duration(s3) == timedelta(hours=2, minutes=1)