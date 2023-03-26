from reservation import Reservation
from json import dump, load
from collections import defaultdict
from datetime import datetime, timedelta
from csv import DictWriter


class Court:

    def __init__(self):
        self.reservations = defaultdict(lambda: [])

#   used to print the schedule for the timeframe provided in arguments
    def print_schedule(self, start_time, end_time):
        end_date = end_time.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = start_time.replace(
            hour=0, minute=0, second=0, microsecond=0)
        duration = (end_date - start_date).days
        weekdays = ["Monday", "Tuesday", "Wednesday",
                    "Thursday", "Friday", "Saturday", "Sunday"]
        for i in range(duration + 1):
            date = start_date + timedelta(days=i)
            print("{} ({}):".format(
                weekdays[date.weekday()], datetime.strftime(date, "%d.%m.%Y")))
            reservations = self.reservations[date]
            if reservations == []:
                print("* No Reservations")
                continue
            reservations = sorted(
                reservations, key=lambda reservation: reservation.start_time)
            to_print = []
            for reservation in reservations:
                if reservation.start_time >= start_time\
                        and reservation.start_time <= end_time:
                    to_print.append(
                        "* {} {} - {}".format(
                            reservation.name, reservation.start_time,
                            reservation.end_time))
            if to_print == []:
                print("* No Reservations")
            else:
                for printable in to_print:
                    print(printable)

#   used to find the closest time to the one given in start_time
#   that is not reserved
    def find_closest_available_time(self, date, start_time):
        date_reservations = self.reservations[date]
        date_reservations = sorted(
            date_reservations, key=lambda reservation: reservation.end_time)
        for i in range(len(date_reservations)):
            available_durations = []
            proposed_time = date_reservations[i].end_time + \
                timedelta(seconds=1)
            if proposed_time < start_time:
                continue
            for duration in [30, 60, 90]:
                if (proposed_time + timedelta(minutes=int(duration))).day ==\
                    date.day and self.is_the_reservation_time_taken(
                        proposed_time, proposed_time +
                        timedelta(minutes=int(duration), seconds=-2)) is False:
                    available_durations.append(duration)
            if available_durations != []:
                return {
                    "available_durations": available_durations,
                    "closest_available_time": proposed_time
                }
        return False

#   used to add data from a json file to the Court object
    def add_reservations_from_json(self, filename):
        with open("{}.json".format(filename), "r", encoding="utf8") as file:
            reservations_json = load(file)
        for reservation_date in reservations_json:
            reservation_date_datetime = datetime.strptime(
                reservation_date, "%d.%m.%Y")
            for reservation in reservations_json[reservation_date]:
                start_hour = int(
                    reservation["start_time"][:reservation["start_time"].find(
                        ":")])
                start_minute = int(
                    reservation["start_time"][reservation["start_time"].find(
                        ":")+1:])
                end_hour = int(reservation["end_time"]
                               [:reservation["end_time"].find(":")])
                end_minute = int(
                    reservation["end_time"][reservation["end_time"].find(
                        ":")+1:])
                start_time = reservation_date_datetime.replace(
                    hour=start_hour, minute=start_minute)
                end_time = reservation_date_datetime.replace(
                    hour=end_hour, minute=end_minute)
                self.reservations[
                    reservation_date_datetime].append(Reservation(
                        reservation["name"],
                        start_time, end_time))

#   checks if for a given name, there are more than 2 reservations already for
#   the week of the given date
    def is_the_week_overbooked(self, date, name):
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_of_the_week = date.weekday()
        dates_to_check = []
        monday = date - timedelta(days=day_of_the_week)
        for i in range(7):
            dates_to_check.append(
                self.reservations[monday + timedelta(days=i)])
        bookings = 0
        for date_reservations in dates_to_check:
            for date_reservation in date_reservations:
                if date_reservation.is_reserved_for_name(name):
                    bookings += 1
                if bookings == 2:
                    return True
        return False

#   checks if the court is already reserved for the provided
#   start_time and end_time
    def is_the_reservation_time_taken(self, start_time, end_time):
        date = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        for reservation in self.reservations[date]:
            if reservation.is_reserved_for_duration(start_time, end_time):
                return True
        return False

#   checks if the court is not booked for a given duration and start_time
    def duration_valid(self, start_time, duration):
        duration = timedelta(minutes=int(duration))
        end_time = start_time + duration
        if self.is_the_reservation_time_taken(start_time, end_time):
            return False
        return True

#   returns a list of durations that the user is available to choose from
#   for reserving a court on a given start_time
    def get_available_durations(self, start_time):
        available_durations = []
        for duration in [30, 60, 90]:
            if self.duration_valid(start_time, duration):
                available_durations.append(duration)
        return available_durations

#   Validates if a given start_time meets the criteria for the reservation:
#       * User doesn't have more than 2 reservations already this week.
#       * Court isn't reserved for the time user specified.
#       * The date user gives is atleast an one hour from now.
#   In case the court is reserved, the system will suggest a closest available
#   time for that day. The suggested time is always later than the initial
#   start_date, and if it's impossible to find such time for atleast the
#   duration of 30 minutes, the system will inform the user that the court is
#   fully booked for that day. In case of successfully choosing an available
#   time, the function returns a dictionary containing the available time,
#   available duration, and whether or not the validation has succeeded.
    def validate_date(self, start_time, name):
        available_durations = []
        failed_validation = {
            "start_time": start_time,
            "available_durations": available_durations,
            "validation_succesful": False
        }
        date = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        now = datetime.now()
        td = start_time - now
        if self.is_the_week_overbooked(date, name):
            print(
                "You have reached the limit of reservations for that week (2)")
            return failed_validation
        elif td.total_seconds()//60 < 0:
            print("You can't book a reservation for the past.")
            return failed_validation
        elif td.total_seconds()//60 < 60:
            print(
                "You can't book a reservation for a time less than an hour away from now.")
            return failed_validation
        available_durations = self.get_available_durations(start_time)
        if available_durations == []:
            closest_available_time_object = self.find_closest_available_time(
                date, start_time)
            if closest_available_time_object is False:
                print(
                    "The court is fully booked for the entire day on and after the specified hour. Please choose another day or an earlier hour.")
                return failed_validation
            proposed_start_time = closest_available_time_object[
                "closest_available_time"]
            available_durations = closest_available_time_object[
                "available_durations"]
            if available_durations != []:
                choice = input(
                    "The desired reservation time is taken. Would you like make a reservation for {}:{} instead? (yes/no) ".format(
                        str(proposed_start_time.hour).zfill(2),
                        str(proposed_start_time.minute).zfill(2)))
                if choice.lower() != "yes" and choice.lower() != "y":
                    return failed_validation
                start_time = proposed_start_time - timedelta(seconds=1)
        return {
            "start_time": start_time,
            "available_durations": available_durations,
            "validation_succesful": True
        }

#   makes a reservation for a given start_time and duration, doesn't check for
#   anything so should used be only after the validating functions
    def make_reservation(self, name, start_time, duration):
        duration = timedelta(minutes=int(duration))
        date = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + duration
        self.reservations[date].append(Reservation(name, start_time, end_time))
        return True

#   Cancels a reservation for a given name and start_time, validation fails
#   and returns an appropriate message if:
#       * There is no reservation for this user on specified date.
#       * The date user gives is less than one hour from now.
    def cancel_reservation(self, start_time, name):
        date = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        if self.reservations[date] == []:
            print("No reservations found for the given date.")
            return False
        now = datetime.now()
        td = start_time - now
        if td.total_seconds()//60 < 0:
            print("You can't cancel a reservation from the past.")
            return False
        elif td.total_seconds()//60 < 60:
            print(
                "You can't cancel a reservation that is booked for less than an hour away from now.")
            return False
        for index, reservation in enumerate(self.reservations[date]):
            if reservation.is_reserved_for_time(start_time) and\
                    reservation.is_reserved_for_name(name):
                self.reservations[date].pop(index)
                return True
        print("No reservation found for a given name and date.")
        return False

#   saves the scheduled reservations from the given time range in a json file
    def save_schedule_to_json(self, filename, start_time, end_time):
        dict_to_dump = {}
        start_date = start_time.replace(
            hour=0, minute=0, second=0, microsecond=0)
        end_date = end_time.replace(hour=0, minute=0, second=0, microsecond=0)
        duration = (end_date - start_date).days
        for i in range(duration + 1):
            date = start_date + timedelta(days=i)
            dump_key = date.strftime("%d.%m.%Y")
            dict_to_dump[dump_key] = []
            for reservation in self.reservations[date]:
                dict_to_dump[dump_key].append(
                    {
                        "name": reservation.name,
                        "start_time": "{}:{}".format(
                            str(reservation.start_time.hour).zfill(2),
                            str(reservation.start_time.minute).zfill(2)),
                        "end_time": "{}:{}".format(
                            str(reservation.end_time.hour).zfill(2),
                            str(reservation.end_time.minute).zfill(2))
                    })
        with open('{}.json'.format(filename), 'w', encoding="utf8") as outfile:
            dump(dict_to_dump, outfile)

#   saves the scheduled reservations from the given time range in a csv file
    def save_schedule_to_csv(self, filename, start_time, end_time):
        start_date = start_time.replace(
            hour=0, minute=0, second=0, microsecond=0)
        end_date = end_time.replace(hour=0, minute=0, second=0, microsecond=0)
        duration = (end_date - start_date).days
        with open("{}.csv".format(filename), "w", encoding="utf8") as csvfile:
            fieldnames = ["name", "start_time", "end_time"]
            writer = DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(duration + 1):
                date = start_date + timedelta(days=i)
                for reservation in self.reservations[date]:
                    writer.writerow(
                        {
                            "name": reservation.name,
                            "start_time": datetime.strftime(
                                reservation.start_time, "%d.%m.%Y %H:%M"),
                            "end_time": datetime.strftime(
                                reservation.end_time, "%d.%m.%Y %H:%M")
                        })
