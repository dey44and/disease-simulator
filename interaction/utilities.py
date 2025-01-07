style_probabilities = {
    "lazy": 0.2,
    "neutral": 0.5,
    "smart": 0.8
}

behaviour_probabilities = {
    "quiet": 0.2,
    "active": 0.8
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

class Activity(object):
    IDLE = 1
    MOVING = 2
    OUTSIDE = 3

class Place(object):
    ENTRANCE = 1
    BACKSPOT = 2
    WHITEBOARD = 3
    DESK = 4
    TEACHER_DESK = 5