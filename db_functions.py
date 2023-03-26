from datetime import datetime, timedelta
from collections import defaultdict
from reservation import Reservation


#   used to fill the database with Court object currently in memory
def db_fill(cur, con, court):
    cur.execute(
        """
CREATE TABLE court(
    reservation_date TEXT PRIMARY KEY)
            """)
    cur.execute(
        """
CREATE TABLE reservations(
    start_time TEXT PRIMARY KEY,
    end_time TEXT,
    name TEXT,
    reservation_date TEXT,
    FOREIGN KEY (reservation_date)
    REFERENCES courts(reservation_date)
    )
            """)
    for reservation in court.reservations:
        cur.execute(
            """
            INSERT INTO court(reservation_date)
            VALUES(?)
            """, (datetime.strftime(reservation, "%d.%m.%Y %H:%M"),))

    for reservation_date in court.reservations:
        reservations = court.reservations[reservation_date]
        reservation_date = datetime.strftime(
            reservation_date, "%d.%m.%Y %H:%M")
        for reservation in reservations:
            start_time = datetime.strftime(
                reservation.start_time, "%d.%m.%Y %H:%M")
            end_time = datetime.strftime(
                reservation.end_time, "%d.%m.%Y %H:%M")
            cur.execute(
                """
                INSERT INTO reservations(
                    start_time, end_time, name, reservation_date)
                VALUES(?,?,?,?)
                    """, (
                    start_time, end_time,
                    reservation.name, reservation_date))
    con.commit()


# used to retrieve reservations from connected database
def get_reservations_from_db(cur):
    new_dict = defaultdict(lambda: [])
    select = cur.execute("SELECT * FROM court")
    reservations_dates = select.fetchall()
    for reservation_date in reservations_dates:
        reservation_date = reservation_date[0]  # because fetchall returns a list of tuples
        select = cur.execute(
            "SELECT * FROM reservations WHERE reservation_date=(?)", (
                reservation_date,))
        reservations = select.fetchall()
        for reservation in reservations:
            new_dict[
                datetime.strptime(reservation_date, "%d.%m.%Y %H:%M")].append(
                Reservation(
                    reservation[2], datetime.strptime(
                        reservation[0], "%d.%m.%Y %H:%M"), datetime.strptime(
                        reservation[1], "%d.%m.%Y %H:%M")
                            ))
    return new_dict


#  used to create a new reservation in database
def make_reservation_db(cur, con, name, start_time, duration):
    duration = timedelta(minutes=int(duration))
    date = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = start_time + duration
    date = datetime.strftime(date, "%d.%m.%Y %H:%M")
    start_time = datetime.strftime(start_time, "%d.%m.%Y %H:%M")
    end_time = datetime.strftime(end_time, "%d.%m.%Y %H:%M")
    cur.execute(
        """
                INSERT OR IGNORE INTO court(reservation_date)
                VALUES(?)
                    """, (date,))
    cur.execute(
        """
                INSERT INTO reservations(
                    start_time, end_time, name, reservation_date)
                VALUES(?,?,?,?)
                    """, (start_time, end_time, name, date))
    con.commit()


#  used to cancel a reservation in database
def cancel_reservation_db(cur, con, start_time):
    start_time = datetime.strftime(start_time, "%d.%m.%Y %H:%M")
    cur.execute(
        """
        DELETE FROM reservations
        WHERE start_time=(?);
            """, (start_time,))
    con.commit()
