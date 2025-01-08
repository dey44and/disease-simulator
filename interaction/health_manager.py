import random

from datetime import datetime, timedelta
from interaction.utilities import PandemicStatus


def gamma_random(mean_days, shape=2.0):
    """
    Return a random sample (in days) from Gamma distribution with given mean.
    mean = shape * scale => scale = mean_days / shape
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
        self.agent_id = agent_id
        self.status = PandemicStatus.SUSCEPTIBLE

        # Timers
        self.infection_start = None      # When agent got infected
        self.pre_symp_end = None         # End of pre-symptomatic period
        self.symp_end = None             # End of symptomatic period (unused if we quarantine at day’s end)
        self.quarantine_end = None

        # Disease timeline means (days)
        self.incubation_mean = 5.2       # total incubation on average
        self.pre_symp_mean = 2.3         # portion that is pre-symptomatic (infectious)
        self.post_symp_mean = 3.2        # symptomatic window
        self.quarantine_days = 14

        # Internal flags
        self.is_pre_symptomatic = False
        self.is_symptomatic = False

    def become_infected(self, current_dt: datetime):
        """
        Called when agent transitions from SUSCEPTIBLE to INFECTED.
        We sample how long until pre-symptomatic ends, etc.
        """
        if self.status != PandemicStatus.SUSCEPTIBLE:
            return  # no effect if already infected or quarantined

        self.status = PandemicStatus.INFECTED
        self.infection_start = current_dt

        # Pre-symptomatic sub-duration
        pre_symp_dur = gamma_random(self.pre_symp_mean, shape=2.0)
        self.pre_symp_end = current_dt + timedelta(days=pre_symp_dur)

        # Symptomatic sub-duration (though we might quarantine at end of day)
        post_symp_dur = gamma_random(self.post_symp_mean, shape=2.0)
        self.symp_end = self.pre_symp_end + timedelta(days=post_symp_dur)

        self.is_pre_symptomatic = True
        self.is_symptomatic = False
        print(f"[PSM] Agent {self.agent_id} became infected at {current_dt}. pre_symp_end={self.pre_symp_end}")

    def update_status_during_day(self, current_dt: datetime):
        """
        Called each simulation tick (or periodically) DURING the day.
        If agent is INFECTED and pre-symptomatic, check if we've reached pre_symp_end.
        If so => become symptomatic (but still remain INFECTED).
        We do NOT quarantine here— that happens at day’s end check.
        """
        if self.status == PandemicStatus.INFECTED:
            if self.is_pre_symptomatic and current_dt >= self.pre_symp_end:
                self.is_pre_symptomatic = False
                self.is_symptomatic = True
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
        """
        if self.status == PandemicStatus.INFECTED and self.is_symptomatic:
            # Agent discovered at day end => quarantine
            self.status = PandemicStatus.QUARANTINED
            self.quarantine_end = current_dt + timedelta(days=self.quarantine_days)
            print(f"[PSM] Agent {self.agent_id} quarantined at end_of_day. Until {self.quarantine_end}")

    def update_quarantine(self, current_dt: datetime):
        """
        Called once per day (or tick) to see if quarantine has ended => become RECOVERED.
        """
        if self.status == PandemicStatus.QUARANTINED:
            if current_dt >= self.quarantine_end:
                self.status = PandemicStatus.RECOVERED
                self.is_symptomatic = False
                self.is_pre_symptomatic = False
                print(f"[PSM] Agent {self.agent_id} recovered after quarantine.")

    def is_infectious(self):
        """
        True if pre-symptomatic => actively shedding.
        Symptomatic => still INFECTED, but we decided to let them remain until day’s end test.
        Typically, you might also allow shedding if symptomatic, but for your spec,
        let's keep the original assumption: only pre-symptomatic sheds in environment.
        (If you want symptomatic to also shed, just check `self.is_symptomatic`.)
        """
        return self.status == PandemicStatus.INFECTED and (self.is_pre_symptomatic or self.is_symptomatic)

    def is_quarantined(self):
        return self.status == PandemicStatus.QUARANTINED

    def is_susceptible(self):
        return self.status == PandemicStatus.SUSCEPTIBLE

    def is_infected(self):
        return self.status == PandemicStatus.INFECTED

    def is_recovered(self):
        return self.status == PandemicStatus.RECOVERED
