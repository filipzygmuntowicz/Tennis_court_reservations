from sqlite3 import connect, OperationalError
from court import Court, datetime
from db_functions import get_reservations_from_db, make_reservation_db,\
    cancel_reservation_db, db_fill
import os
if __name__ == "__main__":
    court = Court()
    use_db = False
    is_db_empty = False
    db_choice = input("Do you want to use sqlite database? (yes, no) ")
    if db_choice.lower() == "yes" or db_choice.lower() == "y":
        while True:
            try:
                db_name = input("Please input the name of your database: ")
                if os.path.isfile("{}.sqlite".format(db_name)) is False:
                    is_db_empty = True
                con = connect("{}.sqlite".format(db_name))
                break
            except (OperationalError):
                print("Incorrect filename.")
        cur = con.cursor()
        if is_db_empty:
            fill_db_choice = input(
                "Do you want to fill the new database with some sample data? (yes, no) ")
            if fill_db_choice.lower() == "yes" or fill_db_choice.lower() == "y":
                court.add_reservations_from_json("23.03-30.03")
            db_fill(cur, con, court)
        use_db = True
    while True:
        if use_db:
            court.reservations = get_reservations_from_db(cur)
        menu_choice = input(
            """
Choose the action you want to take:
1) Make a reservation.
2) Cancel a reservation.
3) Print schedule.
4) Save schedule to a file.
5) Exit the program.
""")
        if menu_choice == "1":
            name = input("What's your name? ")
            while True:
                try:
                    start_time = input(
                        "When would you like to book? {DD.MM.YYYY HH:MM} ")
                    start_time = datetime.strptime(
                        start_time, "%d.%m.%Y %H:%M")
                    break
                except ValueError:
                    print(
                        "Incorrect value. Please input the date in the correct format {DD.MM.YYYY HH:MM}.")
            validation = court.validate_date(start_time, name)
            if validation["validation_succesful"]:
                start_time = validation["start_time"]
                durations = validation["available_durations"]
                durations_string = ""
                for index, duration in enumerate(durations):
                    durations_string = durations_string + \
                        " {}) {} minutes\n".format(index+1, duration)
                while True:
                    choice = input(
                        "For how long would you like to book the court?\n{}".format(
                            durations_string))
                    try:
                        duration = durations[int(choice) - 1]
                        break
                    except (ValueError, IndexError):
                        print(
                            "Incorrect value, you need to choose one of the given options.")
                if court.make_reservation(name, start_time, duration):
                    if use_db:
                        make_reservation_db(
                            cur, con, name, start_time, duration)
                    print(
                        "Succesfully created reservation.")
        elif menu_choice == "2":
            name = input("What's your name? ")
            while True:
                try:
                    start_time = input(
                        "Please input a date of reservation you want to cancel. {DD.MM.YYYY HH:MM} ")
                    start_time = datetime.strptime(
                        start_time, "%d.%m.%Y %H:%M")
                    break
                except ValueError:
                    print(
                        "Incorrect value. Please input the date in the correct format {DD.MM.YYYY HH:MM}.")
            if court.cancel_reservation(start_time, name):
                if use_db:
                    cancel_reservation_db(cur, con, start_time)
                print("Succesfully cancelled reservation.")
        elif menu_choice == "3":
            while True:
                try:
                    start_time = input(
                        "From which date should the schedule start {DD.MM.YYYY HH:MM}? ")
                    start_time = datetime.strptime(
                        start_time, "%d.%m.%Y %H:%M")
                except ValueError:
                    print(
                        "Incorrect value. Please input the date in the correct format {DD.MM.YYYY HH:MM}.")
                    continue
                try:
                    end_time = input(
                        "At which date should the schedule end? {DD.MM.YYYY HH:MM} ")
                    end_time = datetime.strptime(
                        end_time, "%d.%m.%Y %H:%M")
                    if start_time <= end_time:
                        break
                    print("Starting date can not be later than ending date.")
                except ValueError:
                    print(
                        "Incorrect value. Please input the date in the correct format {DD.MM.YYYY HH:MM}.")
            court.print_schedule(start_time, end_time)
        elif menu_choice == "4":
            while True:
                try:
                    print(
                        "Please choose the range of dates for desired data {DD.MM.YYYY HH:MM}:")
                    start_time = input("Start date: ")
                    start_time = datetime.strptime(
                        start_time, "%d.%m.%Y %H:%M")
                except ValueError:
                    print(
                        "Incorrect value. Please input the date in the correct format {DD.MM.YYYY HH:MM}.")
                    continue
                try:
                    end_time = input("End date: ")
                    end_time = datetime.strptime(
                        end_time, "%d.%m.%Y %H:%M")
                    if start_time <= end_time:
                        break
                    print("Starting date can not be later than ending date.")
                except ValueError:
                    print(
                        "Incorrect value. Please input the date in the correct format {DD.MM.YYYY HH:MM}.")
            while True:
                format = input("Please choose the file format (csv, json): ")
                if format == "json" or format == "csv":
                    break
                print("Incorrect format.")
            while True:
                filename = input("Please enter the filename: ")
                if format == "json":
                    try:
                        court.save_schedule_to_json(
                            filename, start_time, end_time)
                        break
                    except (OSError, FileNotFoundError):
                        print("Incorrect filename.")
                elif format == "csv":
                    try:
                        court.save_schedule_to_csv(
                            filename, start_time, end_time)
                        break
                    except (OSError, FileNotFoundError):
                        print("Incorrect filename.")
        elif menu_choice == "5":
            break
