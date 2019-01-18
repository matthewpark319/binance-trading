import sys
sys.path.append("C:/Users/matth/Desktop/crypto")
from flask import Flask, render_template, jsonify, request
from backend.SignalCollector import SignalCollector
import json
from Formatter import Formatter
from BacktestFormatter import BacktestFormatter
import os
import config
import signal_utils
from datetime import datetime, timedelta

app = Flask(__name__)

signals = None
formatter = None

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
    
@app.route("/")
def main():
	global signals
	global formatter
	if (signal_utils.check_data_updated() == False):
		os.system("python C:/Users/matth/Desktop/crypto/backend/WebScraper.py True")
	(signals, formatter) = update_formatter()
	return formatter.load_main()

@app.route("/json")
def json():
	global signals
	return jsonify(signals=signals)

@app.route("/coin/<coin>")
def coin(coin):
	global formatter
	return formatter.load_coin_page(coin)

@app.route("/research/<coin>", methods=["GET", "POST"])
def research(coin):
	global formatter
	if request.method == "GET":
		return formatter.load_research_page(coin)
	if request.method == "POST":
		return formatter.fetch_research_data(request)

@app.route("/backtest")
def backtest():
	formatter = BacktestFormatter()
	return formatter.load_backtest()

def update_formatter():
	signal_collector = SignalCollector()
	signals = signal_collector.signals()
	return (signals, Formatter(signals))

if __name__ == "__main__":
	app.run(debug=True)