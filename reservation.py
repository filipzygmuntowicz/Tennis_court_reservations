
class Reservation:

    def __init__(self, name, start_time, end_time):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time

    def is_reserved_for_name(self, name):
        return self.name == name

    def is_reserved_for_time(self, start_time):
        return self.start_time == start_time

# checks if the reservation takes place in the given duration
    def is_reserved_for_duration(self, start_time, end_time):
        return (start_time >= self.start_time and
                start_time <= self.end_time) or\
            (start_time <= self.start_time and
                end_time > self.start_time)
