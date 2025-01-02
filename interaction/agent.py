
style_probabilities = {
    "lazy": 0.2,
    "neutral": 0.5,
    "smart": 0.8
}

behaviour_probabilities = {
    "quiet": 0.3,
    "active": 0.7
}

mask_protection_probabilities = {
    "no-mask": 0,
    "cloth": 0.3,
    "surgical": 0.5,
    "n95": 0.85
}

vaccine_protection_probabilities = {
    "no-vax": 0,
    "any": 0.31,
    "astra-zeneca": 0.67,
    "pfizer/moderna": 0.88
}

class PandemicStatus(object):
    SUSCEPTIBLE = 1
    INFECTED = 2
    QUARANTINED = 3
    RECOVERED = 4

class Agent(object):
    def __init__(self, style="lazy", behaviour="quiet", mask="no-mask", vaccine="no-vax", desk_id=1):
        if style not in ["lazy", "smart", "neutral"]:
            raise ValueError("Invalid agent style")
        if behaviour not in ["quiet", "active"]:
            raise ValueError("Invalid agent behaviour")
        if mask not in ["no-mask", "cloth", "surgical", "n95"]:
            raise ValueError("Invalid agent mask")
        if vaccine not in ["no-vax", "any", "astra-zeneca", "pfizer/moderna"]:
            raise ValueError("Invalid agent vaccine")
        self.x = -1
        self.y = -1
        self.style = style
        self.behaviour = behaviour
        self.mask = mask
        self.vaccine = vaccine
        self.desk_id = desk_id
        # Current state of the agent : [susceptible, infected, quarantined, recovered]
        self.pandemic_status = PandemicStatus.SUSCEPTIBLE

    def act(self):
        # i.e., The student is present in the classroom
        if self.pandemic_status == PandemicStatus.SUSCEPTIBLE:
            # Apply the logic (so he can move from one place to the other one)
            pass
        elif self.pandemic_status == PandemicStatus.INFECTED:
            # The agent will be quarantined
            self.pandemic_status = PandemicStatus.QUARANTINED
        elif self.pandemic_status == PandemicStatus.QUARANTINED:
            # The agent is staying at home during this phase
            pass
        elif self.pandemic_status == PandemicStatus.RECOVERED:
            # Now the agent is immune
            pass
