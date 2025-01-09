import logging
import random

from datetime import datetime, timedelta
from interaction.utilities import PandemicStatus


def gamma_random(mean_days, shape=2.0):
    """
    Return a random sample (in days) from Gamma distribution with given mean.
    mean = shape * scale => scale = mean_days / shape
    :param mean_days: The average number of days to sample.
    :param shape: The shape of the distribution.
    :return: A random sample from the Gamma distribution with given mean and shape.
    """
    scale = mean_days / shape
    return random.gammavariate(shape, scale)

class PandemicStateManager:
    """
    Tracks an agent's infection timeline & status, with pre-symptomatic and symptomatic phases.
    However:
      - We do NOT immediately quarantine upon becoming symptomatic.
      - Quarantine is forced at the END OF THE DAY if agent is symptomatic.
    """
    def __init__(self, agent_id):
        """
        :param agent_id: The agent ID.
        """
        # Set logger properties
        self.__logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO)

        self.__agent_id = agent_id
        self.__status = PandemicStatus.SUSCEPTIBLE

        # Timers
        self.__infection_start = None      # When agent got infected
        self.__pre_symp_end = None         # End of pre-symptomatic period
        self.__symp_end = None             # End of symptomatic period (unused if we quarantine at day’s end)
        self.__quarantine_end = None       # End of quarantine period

        # Disease timeline means (days)
        self.incubation_mean = 5.2       # total incubation on average
        self.pre_symp_mean = 2.3         # portion that is pre-symptomatic (infectious)
        self.post_symp_mean = 3.2        # symptomatic window
        self.quarantine_days = 14        # total quarantine time

        # Internal flags
        self.__is_pre_symptomatic = False
        self.__is_symptomatic = False

    @property
    def agent_id(self):
        return self.__agent_id

    @agent_id.setter
    def agent_id(self, value):
        self.__agent_id = value

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = value

    def become_infected(self, current_dt: datetime):
        """
        Called when agent transitions from SUSCEPTIBLE to INFECTED.
        We sample how long each period lasts.
        :param current_dt: The current datetime object.
        """
        if self.status != PandemicStatus.SUSCEPTIBLE:
            return  # no effect if already infected or quarantined

        self.status = PandemicStatus.INFECTED
        self.__infection_start = current_dt

        # Pre-symptomatic sub-duration
        pre_symp_dur = gamma_random(self.pre_symp_mean, shape=2.0)
        self.__pre_symp_end = current_dt + timedelta(days=pre_symp_dur)

        # Symptomatic sub-duration (though we might quarantine at end of day)
        post_symp_dur = gamma_random(self.post_symp_mean, shape=2.0)
        self.__symp_end = self.__pre_symp_end + timedelta(days=post_symp_dur)

        self.__is_pre_symptomatic = True
        self.__is_symptomatic = False
        self.__logger.info(f"[PSM] Agent {self.agent_id} became infected at {current_dt}. pre_symp_end={self.__pre_symp_end}")

    def update_status_during_day(self, current_dt: datetime):
        """
        Called each simulation tick (or periodically) DURING the day.
        If agent is INFECTED and pre-symptomatic, check if we've reached pre_symp_end.
        If so => become symptomatic (but still remain INFECTED).
        We do NOT quarantine here— that happens at day’s end check.
        :param current_dt: The current datetime object.
        """
        if self.status == PandemicStatus.INFECTED:
            if self.__is_pre_symptomatic and current_dt >= self.__pre_symp_end:
                self.__is_pre_symptomatic = False
                self.__is_symptomatic = True
                # We remain status=INFECTED but symptomatic
                # Quarantine is delayed until end_of_day_test()

        elif self.status == PandemicStatus.QUARANTINED:
            # possibly do partial day checks, or skip logic here if you handle day-based
            pass

    def end_of_day_test(self, current_dt: datetime):
        """
        Called at the END of day:
         - If agent is symptomatic => forced into QUARANTINE for 14 days
         - If already quarantined => no change unless we want partial-day logic
         :param current_dt: The current datetime object.
        """
        if self.status == PandemicStatus.INFECTED and self.__is_symptomatic:
            # Agent discovered at day end => quarantine
            self.status = PandemicStatus.QUARANTINED
            self.__quarantine_end = current_dt + timedelta(days=self.quarantine_days)
            self.__logger.info(f"[PSM] Agent {self.agent_id} quarantined at end_of_day. Until {self.__quarantine_end}")

    def update_quarantine(self, current_dt: datetime):
        """
        Called once per day (or tick) to see if quarantine has ended => become RECOVERED.
        :param current_dt: The current datetime object.
        """
        if self.status == PandemicStatus.QUARANTINED:
            if current_dt >= self.__quarantine_end:
                self.status = PandemicStatus.RECOVERED
                self.__is_symptomatic = False
                self.__is_pre_symptomatic = False
                self.__logger.info(f"[PSM] Agent {self.agent_id} recovered after quarantine.")

    def is_infectious(self):
        """
        Check if the agent is infected, and it is in the presymptomatic or symptomatic stage.
        :return: A boolean value indicating if agent is infectious.
        """
        return self.status == PandemicStatus.INFECTED and (self.__is_pre_symptomatic or self.__is_symptomatic)

    def is_quarantined(self):
        """
        Check if the agent is quarantined.
        :return: A boolean value indicating if agent is quarantined.
        """
        return self.status == PandemicStatus.QUARANTINED

    def is_susceptible(self):
        """
        Check if the agent is susceptible.
        :return: A boolean value indicating if agent is susceptible.
        """
        return self.status == PandemicStatus.SUSCEPTIBLE

    def is_infected(self):
        """
        Check if the agent is infected.
        :return: A boolean value indicating if agent is infected.
        """
        return self.status == PandemicStatus.INFECTED

    def is_recovered(self):
        """
        Check if the agent is recovered.
        :return: A boolean value indicating if agent is recovered.
        """
        return self.status == PandemicStatus.RECOVERED
