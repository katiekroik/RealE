from building import Building
from building import Unit
import requests 
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import json

ZILLOW_URL = "http://files.zillowstatic.com/research/public/"
IR_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=FEDFUNDS&scale=left&cosd=1954-07-01&coed=2019-09-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Monthly&fam=avg&fgst=lin&fgsnd=2009-06-01&line_index=1&transformation=lin&vintage_date=2019-10-02&revision_date=2019-10-02&nd=1954-07-01"
TIINGO_URL = "https://api.tiingo.com/tiingo/daily/SNP/prices"
TIINGO_API_TOKEN = "bb20f7ef5da6b4b3ac01311be07706721d5b8018"
# home values
# http://files.zillowstatic.com/research/public/Neighborhood/Neighborhood_Zhvi_Summary_AllHomes.csv
# rental values
# http://files.zillowstatic.com/research/public/Neighborhood/Neighborhood_Zri_AllHomesPlusMultifamily_Summary.csv
# http://files.zillowstatic.com/research/public/Neighborhood/Neighborhood_Zri_AllHomesPlusMultifamily.csv
# http://files.zillowstatic.com/research/public/Neighborhood/Neighborhood_ZriPerSqft_AllHomes.csv
# rental forecast
# http://files.zillowstatic.com/research/public/ZriForecast_Public.csv


# fed fund - https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=FEDFUNDS&scale=left&cosd=1954-07-01&coed=2019-09-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Monthly&fam=avg&fgst=lin&fgsnd=2009-06-01&line_index=1&transformation=lin&vintage_date=2019-10-02&revision_date=2019-10-02&nd=1954-07-01
# snp 500 - tiingo - https://api.tiingo.com/tiingo/daily/SNP/prices?startDate=2012-1-1&endDate=2016-1-1
delim = "%7C"
#/for-sale/manhattan/status:open%7Cprice:100000-1000000

def main():
	# get interest rates and SNP data
	ratesMap = getInterestRates()
	snpData = getSnp()

	# get rent chart
	csv = getZillowCSV("Neighborhood", "Neighborhood_ZriPerSqft_AllHomes.csv")
	rows = csv.split("\n")
	headers = rows[0].strip().replace('"', '').split(",")
	f, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=False)
	ax1.set_xlim([convertToDateYYmm(headers[7]), convertToDateYYmm(headers[len(headers) - 1])])

	ax1.set_title('rent')
	ax2.set_title('interest rates')
	ax3.set_title('snp')

	for row in rows:
		arr = row.replace('"', '').split(",")
		if len(arr) > 1 and "New York" == arr[2]:
			for i in range(7, len(headers)):
				ax1.plot_date(convertToDateYYmm(headers[i]),arr[i], 'bo')
				ax2.plot_date(convertToDateYYmm(headers[i]),ratesMap[convertToDateYYmm(headers[i])], 'bo')
				ax3.plot_date(convertToDateYYmm(headers[i]),snpData[findSmallestDate(convertToDateYYmm(headers[i]),snpData)], 'bo')
			break
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
	snpText = get(TIINGO_URL + "?startDate=2010-1-1&endDate=" + today, headers=headers)
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