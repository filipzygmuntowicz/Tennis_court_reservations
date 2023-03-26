from datetime import datetime
from court import Court
from reservation import Reservation

court = Court()
court.add_reservations_from_json("unit_tests_data")

test_start_time1 = datetime.strptime(
        "10.01.2022 13:00", "%d.%m.%Y %H:%M")
test_start_time2 = datetime.strptime(
        "10.03.2022 13:01", "%d.%m.%Y %H:%M")
test_start_time3 = datetime.strptime(
        "01.04.2023 13:00", "%d.%m.%Y %H:%M")
test_start_time4 = datetime.strptime(
                "01.04.2023 17:00", "%d.%m.%Y %H:%M")
test_end_time = datetime.strptime(
        "15.01.2022 14:00", "%d.%m.%Y %H:%M")
test_end_time2 = datetime.strptime(
        "15.03.2022 14:00", "%d.%m.%Y %H:%M")
test_reservation = Reservation(
    name="Grzegorz Brzęczyszczykiewicz", start_time=test_start_time1,
    end_time=test_end_time)


class Test:

    def test_is_reserved_for_name(self):
        assert test_reservation.is_reserved_for_name(
            "Grzegorz Brzęczyszczykiewicz") is True and\
            test_reservation.is_reserved_for_name(
            "Adaś Miauczyński") is False

    def test_is_reserved_for_time(self):
        assert test_reservation.is_reserved_for_time(
            test_start_time1) is True and\
            test_reservation.is_reserved_for_time(
            test_start_time2) is False

    def test_is_reserved_for_duration(self):
        assert test_reservation.is_reserved_for_duration(
            test_start_time1, test_end_time) is True and\
            test_reservation.is_reserved_for_duration(
            test_start_time2, test_end_time2) is False

    def test_find_closest_available_time(self):
        closest_available_time = court.find_closest_available_time(
            test_start_time4)[
                "closest_available_time"]
        durations = court.find_closest_available_time(
            test_start_time4)[
                "available_durations"]
        failed_closest_time = court.find_closest_available_time(
            datetime.strptime(
                "25.03.2023 14:00", "%d.%m.%Y %H:%M"))
        assert closest_available_time == datetime(
                2023, 4, 1, 19, 0, 1) and durations == [30, 60, 90] and\
            failed_closest_time is False

    def test_is_the_week_overbooked(self):
        assert court.is_the_week_overbooked(
            datetime.strptime(
                "25.03.2023 09:00", "%d.%m.%Y %H:%M"),
            "Robert Brzozowski") is True and\
            court.is_the_week_overbooked(
            datetime.strptime(
                "01.06.2023 09:00", "%d.%m.%Y %H:%M"),
            "Robert Brzozowski") is False

    def test_get_available_durations(self):
        durations1 = court.get_available_durations(test_start_time3)
        durations2 = court.get_available_durations(test_start_time4)
        assert (durations1 == [30, 60] and durations2 == [])

    def test_make_reservation(self):
        court.make_reservation(
            "Grzegorz Brzęczyszczykiewicz", test_start_time1, "60")
        i = 0
        for reservation in court.reservations[
                test_start_time1.replace(
                hour=0, minute=0, second=0, microsecond=0)]:
            if test_start_time1 == reservation.start_time:
                i = 1
                break
        assert i == 1

    def test_cancel_reservation(self):
        validation_succesful = court.cancel_reservation(
            test_start_time4, "Marcin Wiśniewski")
        i = 0
        for reservation in court.reservations[
                test_start_time4.replace(
                hour=0, minute=0, second=0, microsecond=0)]:
            if test_start_time4 == reservation.start_time:
                i = 1
                break
        assert i == 0 and validation_succesful
