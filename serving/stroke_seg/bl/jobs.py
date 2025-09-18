from enum import Enum


class JobType(Enum):
    TRAINING = 'TRAINING'
    INFERENCE = 'INFERENCE'