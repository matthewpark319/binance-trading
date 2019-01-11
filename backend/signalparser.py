import math

def buy_or_sell(val1, val2, dismiss_negative=False, weight=1):
	if val1 is None or val2 is None or math.isnan(val1) or math.isnan(val2): 
		return 0

	if val1 > val2:
		return weight
	if val1 == val2 or dismiss_negative:
		return 0
	return -weight