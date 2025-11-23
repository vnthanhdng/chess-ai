# Utility functions for chess AI
import random

def flipCoin(epsilon: float):
  r = random.random()
  if r < epsilon:
    return True
  return False