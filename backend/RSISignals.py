import pandas
import numpy
import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
import config
from backend.signalparser import buy_or_sell

class RSISignals:
	def __init__(self, price_data, window):
		self.window = window
		self.rsi = self.load_rsi(price_data)

	def load_rsi(self, price_data):
		avg_gains = []
		avg_losses = []
		rsi = []

		gains = 0
		losses = 0
		price_data = list(price_data["close"])
		prev = price_data[0]

		# multiply by 15 to get 14 data points
		cutoff = self.window * 15
		for i in range(self.window, cutoff, self.window):
			try:
				last = price_data[i]
				net = last - prev
				if net > 0:
					gains += net
				if net < 0:
					losses += -net
				prev = last
			except IndexError as e:
				return
		avg_gains.append(gains / 14)
		avg_losses.append(losses / 14)
		rsi.append(self.calculate_rsi(avg_gains[-1], avg_losses[-1]))

		for i in range(cutoff, len(price_data), self.window):
			avg_gain = avg_gains[-1] * 13
			avg_loss = avg_losses[-1] * 13
			last = price_data[i]
			net = last - prev
			if net > 0:
				avg_gain += net
			if net < 0:
				avg_loss += -net
			prev = last
			avg_gains.append(avg_gain / 14)
			avg_losses.append(avg_loss / 14)
			rsi.append(self.calculate_rsi(avg_gains[-1], avg_losses[-1]))
		return rsi

	def calculate_rsi(self, gains, losses):
		if losses == 0: 
			return 100
		return 100 - (100 / (1 + (gains / losses)))

	def signals(self):
		signals = {}
		if not self.rsi:
			return signals
		last_rsi = self.rsi[-1]
		if last_rsi > 70:
			signals["{:d}-hour RSI > 70".format(self.window)] = -15
			signals["{:d}-hour RSI > 80".format(self.window)] = -buy_or_sell(last_rsi, 80, dismiss_negative=True, weight=15)
			signals["{:d}-hour RSI is decreasing while above 70".format(self.window)] = -buy_or_sell(self.rsi[-2], last_rsi, dismiss_negative=True, weight=10);
		elif last_rsi < 30:
			signals["{:d}-hour RSI < 30".format(self.window)] = 15
			signals["{:d}-hour RSI < 20".format(self.window)] = buy_or_sell(20, last_rsi, dismiss_negative=True, weight=15)
			signals["{:d}-hour RSI is increasing while below 30".format(self.window)] = buy_or_sell(last_rsi, self.rsi[-2], dismiss_negative=True, weight=10);
		else:
			crossed = 0
			for hours in range(2, 11):
				if crossed > 0:
					signals["{:d}-hour RSI crossed above 30 within past {:d} frames".format(self.window, hours)] = crossed
				elif crossed < 0:
					signals["{:d}-hour RSI crossed below 70 within past {:d} frames".format(self.window, hours)] = crossed
				else:
					crossed_above = buy_or_sell(30, self.rsi[-hours], dismiss_negative=True, weight=5)
					if crossed_above > 0:
						signals["{:d}-hour RSI crossed above 30 within past {:d} frames".format(self.window, hours)] = crossed_above
						crossed = 5

					crossed_below = -buy_or_sell(self.rsi[-hours], 70, dismiss_negative=True, weight=5)
					if crossed_below < 0:
						signals["{:d}-hour RSI crossed below 70 within past {:d} frames".format(self.window, hours)] = crossed_below
						crossed = -5

		return signals