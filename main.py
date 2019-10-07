from building import Building
from building import Unit
import requests 
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import datetime
import json

ZILLOW_URL = "http://files.zillowstatic.com/research/public/"
IR_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=FEDFUNDS&scale=left&cosd=1954-07-01&coed=2019-09-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Monthly&fam=avg&fgst=lin&fgsnd=2009-06-01&line_index=1&transformation=lin&vintage_date=2019-10-02&revision_date=2019-10-02&nd=1954-07-01"
TIINGO_URL = "https://api.tiingo.com/tiingo/daily/SNP/prices"
TIINGO_API_TOKEN = "bb20f7ef5da6b4b3ac01311be07706721d5b8018"

AREAS = {"Upper West Side":'b', "Upper East Side":'g', "Lower East Side":'r', "Harlem":'c', "Williamsburg":'m'}
CITY = "New York"
STATE = "NY"
delim = "%7C"

def main():
	# get interest rates and SNP data
	ratesMap = getInterestRates()
	snpData = getSnp()

	# get home value chart
	homeValuesCsv = getZillowCSV("Neighborhood", "Neighborhood_Zhvi_AllHomes.csv")
	homeValuesRows = homeValuesCsv.split("\n")
	headers = homeValuesRows[0].strip().replace('"', '').split(",")

	homeValues = {} # {(neighborhood, city, state) : {year : price}}
	for row in homeValuesRows[1:]:
		arr = row.replace('"', '').split(",")
		if len(arr) > 2 and arr[1] in AREAS:
			homeValues[(arr[1], arr[2], arr[3])] = {}
			for i in range(7, len(headers)):
				date = convertToDateYYmm(headers[i])
				homeValues[(arr[1], arr[2], arr[3])][date] = arr[i]

	# get rent chart
	rentValuesCSV = getZillowCSV("Neighborhood", "Neighborhood_ZriPerSqft_AllHomes.csv")
	rentValuesRows = rentValuesCSV.split("\n")
	rentHeaders = rentValuesRows[0].strip().replace('"', '').split(",")

	rentValues = {}
	for row in rentValuesRows[1:]:
		arr = row.replace('"', '').split(",")
		if len(arr) > 2 and arr[1] in AREAS:
			rentValues[(arr[1], arr[2], arr[3])] = {}
			for i in range(7, len(rentHeaders)):
				date = convertToDateYYmm(rentHeaders[i])
				rentValues[(arr[1], arr[2], arr[3])][date] = arr[i]

	f, axes = plt.subplots(4, sharex=True, sharey=False)
	axes[0].set_xlim([convertToDateYYmm(headers[7]), convertToDateYYmm(headers[len(headers) - 1])])

	axes[0].set_title('Interest Rate')
	axes[1].set_title('SnP Index')
	axes[2].set_title('Home Values')
	axes[3].set_title('Rent')

	# set legend
	custom_lines = []
	for i in AREAS.keys():
		custom_lines.append(Line2D([0], [0], color=AREAS[i]))
	axes[3].legend(custom_lines, AREAS.keys(), loc='upper left', prop={'size': 6})

	for header in headers[7:]:
		date = convertToDateYYmm(header)
		axes[0].plot_date(date,ratesMap[date], 'bo')
		axes[1].plot_date(date,snpData[findSmallestDate(date,snpData)], 'bo')
		for area in AREAS.keys():
			if (area, CITY, STATE) in homeValues:
				try:
					axes[2].plot_date(date,homeValues[(area, CITY, STATE)][date], AREAS[area] + "+")
				except:
					pass
			if (area, CITY, STATE) in rentValues:
				try:
					axes[3].plot_date(date,rentValues[(area, CITY, STATE)][date], AREAS[area] + "+")
				except:
					pass

	plt.savefig('chart.png')

def getInterestRates():
	ratesCSV = get(IR_URL)
	rates = ratesCSV.split("\n")
	ratesMap = {}
	for row in rates:
		data = row.strip().replace("'", "").split(",")
		if len(data) > 1:
			ratesMap[convertToDateYYmmdd(data[0])] = data[1]
	return ratesMap

def getSnp():
	headers = {
        'Content-Type': 'application/json',
        'Authorization' : 'Token ' + TIINGO_API_TOKEN
        }
	today = datetime.datetime.today().strftime('%Y-%m-%d')
	snpText = get(TIINGO_URL + "?startDate=1990-1-1&endDate=" + today, headers=headers)
	snpHistorical = json.loads(snpText)
	snpData = {}
	for snp in snpHistorical:
		snpData[convertToDateFullTimestamp(snp['date'])] = snp['adjHigh']
	return snpData

def convertToDateYYmm(str):
	try:
		return pd.to_datetime(str, format='%Y-%m')
	except:
  		return ""

def convertToDateYYmmdd(str):
	try:
		return pd.to_datetime(str, format='%Y-%m-%d')
	except:
  		return ""

def convertToDateFullTimestamp(str):
	try:
		return pd.to_datetime(str)
	except:
  		return ""

def findSmallestDate(date, arr):
	while not date in arr:
		date += datetime.timedelta(days=1)
	return date

def getZillowCSV(area, csvname):
	return get(ZILLOW_URL + area + "/" + csvname)


def get(URL, headers=None):
	r = requests.get(url=URL, headers=headers) 
	return r.content


if __name__ == "__main__":
	main()