import datetime

from interaction.agent import Agent

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


class SceneOrchestrator:
    def __init__(
            self,
            agents: list[Agent],
            start_time: str,
            end_time: str,
            num_weeks: int,
            time_step_seconds: int
    ):
        self.__agents = agents
        self.__num_weeks = num_weeks
        self.__time_step_sec = time_step_seconds  # how many sim-seconds we jump each "simulate()" call

        # Parse daily times
        fmt = "%H:%M"
        self.__daily_start_time = datetime.datetime.strptime(start_time, fmt).time()
        self.__daily_end_time = datetime.datetime.strptime(end_time, fmt).time()

        # We start on next Monday
        today = datetime.date.today()
        base_date = today if today.weekday() == 0 else today + datetime.timedelta(days=7-today.weekday())
        self.__day_of_week = 0  # 0=Monday, ..., 4=Friday
        self.__current_week = 1

        # Our "current_time_of_day" starts at daily_start_time
        self.__current_date = base_date
        self.__current_time_of_day = datetime.datetime.combine(base_date, self.__daily_start_time)

        self.__finished = False

    def simulate_once(self):
        """Jump by self.__time_step_sec in simulation time."""
        if self.__finished:
            return

        self.__current_time_of_day += datetime.timedelta(seconds=self.__time_step_sec)

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
                    self.__finished = True
                    return
                # Skip Sat+Sun => +3 days
                days_to_add = 3
            else:
                days_to_add = 1

            self.__current_date += datetime.timedelta(days=days_to_add)
            self.__current_time_of_day = datetime.datetime.combine(
                self.__current_date,
                self.__daily_start_time
            )

    def get_current_week(self) -> int:
        return self.__current_week

    def get_day_of_week_str(self) -> str:
        return WEEKDAYS[self.__day_of_week]

    def get_time_str(self) -> str:
        return self.__current_time_of_day.strftime("%H:%M:%S")

    def is_finished(self) -> bool:
        return self.__finished
