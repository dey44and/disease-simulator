import datetime

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


class Timer(object):
    def __init__(self, start_time, end_time, num_weeks, time_step_seconds):
        """
        Constructor for Timer class.
        :param start_time: Start time of the simulation.
        :param end_time: End time of the simulation.
        :param num_weeks: Number of weeks to simulate.
        :param time_step_seconds: Time step in seconds.
        """
        self.__num_weeks = num_weeks
        self.__time_step_seconds = time_step_seconds

        # Parse daily times
        fmt = "%H:%M"
        self.__daily_start_time = datetime.datetime.strptime(start_time, fmt).time()
        self.__daily_end_time = datetime.datetime.strptime(end_time, fmt).time()

        # We start on next Monday
        today = datetime.date.today()
        base_date = today if today.weekday() == 0 else today + datetime.timedelta(days=7 - today.weekday())
        self.__day_of_week = 0  # 0=Monday, ..., 4=Friday
        self.__current_week = 1

        # Our "current_time_of_day" starts at daily_start_time
        self.__current_date = base_date
        self.__current_time_of_day = datetime.datetime.combine(base_date, self.__daily_start_time)

    @property
    def current_week(self) -> int:
        """
        Get the current week of the simulation.
        :return: A number representing the current week of the simulation.
        """
        return self.__current_week

    @property
    def day_of_week_str(self) -> str:
        """
        Get the current day of the week string.
        :return: A string representing the current day of the week.
        """
        return WEEKDAYS[self.__day_of_week]

    @property
    def time_str(self) -> str:
        """
        Get the current time string.
        :return: A string representing the current time formatted.
        """
        return self.__current_time_of_day.strftime("%H:%M:%S")

    def tick(self) -> datetime.datetime:
        """
        Tick the simulation.
        :return: The current time of the simulation.
        """
        self.__current_time_of_day += datetime.timedelta(seconds=self.__time_step_seconds)
        return self.__current_time_of_day

    def check_finished(self) -> bool:
        """
        Check if the simulation has finished.
        :return: A boolean indicating if the simulation has finished.
        """
        # Check if we've passed today's end_time
        today_end_dt = datetime.datetime.combine(self.__current_date, self.__daily_end_time)
        if self.__current_time_of_day >= today_end_dt:
            # Move to next day
            self.__day_of_week += 1
            if self.__day_of_week > 4:
                # Jump from Friday to next Monday
                self.__day_of_week = 0
                self.__current_week += 1
                if self.__current_week > self.__num_weeks:
                    return True
                # Skip Sat+Sun => +3 days
                days_to_add = 3
            else:
                days_to_add = 1

            self.__current_date += datetime.timedelta(days=days_to_add)
            self.__current_time_of_day = datetime.datetime.combine(
                self.__current_date,
                self.__daily_start_time
            )
        return False
