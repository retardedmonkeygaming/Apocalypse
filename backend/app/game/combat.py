# Simple risk resolution used by the engine
import random

def resolve_risk(chance: float) -> bool:
    """Return True if the bad thing happens"""
    return random.random() < chance