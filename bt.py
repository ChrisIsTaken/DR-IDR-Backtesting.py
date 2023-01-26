from time import time
import datetime
import pandas as pd
from backtesting import Strategy
from backtesting import Backtest
import csv

# Load data from CSV file into a DataFrame
#data = pd.read_csv("data.csv", parse_dates={'timestamp': ['Date', 'Time']}, names=["Date", "Time", "Open", "High", "Low", "Close", "Volume"])
data = pd.read_csv("data\DAT_MT_NSXUSD_M1_2022.csv", names=["Date", "Time", "Open", "High", "Low", "Close", "Volume"])

data['timestamp'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], format='%Y.%m.%d %H:%M')
data['hour'] = data['timestamp'].dt.hour
data['minute'] = data['timestamp'].dt.minute

#define breaklevel function
def breaklevel(open_price, close_price, level):
    print("breaklevel function has been initiated")
    if (open_price > level) and (close_price < level):
        print("broken below")
        return 1
    elif (open_price < level) and (close_price > level):
        print("broken above")
        return 2

# Define your strategy
class MyStrategy(Strategy):

    def init(self):
        print("Reached init(self)")
        #RDR Vars
        self.rdr_session_vars = {
            'session_name': 'RDR',                          #Var to store the sessions name
            'defining_hour_start': "09:30:00",    #Var to store time when session's defining hour starts
            'defining_hour_end': "10:30:00",   #Var to store time when session's defining hour ends
            'session_validity': "13:00:00",      #Var to store time when session is invalid
            'dr_high': None,                                #Var to store dr high
            'dr_high_timestamp': None,                      #dr high timestamp
            'dr_low': None,                                 #Var to store dr low
            'dr_low_timestamp': None,                       #dr low timestamp
            'idr_high': None,                               #Var to store idr high
            'idr_high_timestamp': None,             
            'idr_low': None,                                #Var to store idr low
            'idr_low_timestamp': None,              
            'levelbreaks': [],                              #Variable to store all the breaks of relevant levels
            }

        #ODR Vars
        self.odr_session_vars = {
            'session_name': 'ODR',
            'defining_hour_start': "03:00:00",
            'defining_hour_end': "04:30:00",
            'session_validity': "02:00:00",
            'dr_high': None,
            'dr_high_timestamp': None,
            'dr_low': None,
            'dr_low_timestamp': None,
            'idr_high': None,
            'idr_high_timestamp': None,
            'idr_low': None,
            'idr_low_timestamp': None,
            'levelbreaks': [],
        }

        #ADR Vars
        self.adr_session_vars = {
            'session_name': 'ADR',
            'defining_hour_start': "19:30:00",
            'defining_hour_end': "20:30:00",
            'session_validity': "08:00:00",
            'dr_high': None,
            'dr_high_timestamp': None,
            'dr_low': None,
            'dr_low_timestamp': None,
            'idr_high': None,
            'idr_high_timestamp': None,
            'idr_low': None,
            'idr_low_timestamp': None,
            'levelbreaks': [],
        }

    def next(self):
        print("Reached next(self)")


        for sessions in [self.rdr_session_vars, self.odr_session_vars, self.adr_session_vars]:

            # Your strategy logic here
            #Checking if current time is in between defining hour
            print(sessions['session_name'])
            print(sessions['defining_hour_start'])
            print(sessions['defining_hour_end'])
            if self.data.Time[-1] >= sessions['defining_hour_start'] and self.data.Time[-1] < sessions['defining_hour_end']:
                print("session's defining hour is ongoing")
                #Update levels
                print("updating levels:")
                if (sessions['dr_high'] == None) or (self.data.Close[-1] > sessions['dr_high']):
                    sessions['dr_high'] = self.data.Close[-1]

                if (sessions['dr_low'] == None) or (self.data.Close[-1] < sessions['dr_low']):
                    sessions['dr_low'] = self.data.Close[-1]

                if (sessions['idr_high'] == None) or (self.data.High[-1] > sessions['idr_high']):
                    sessions['idr_high'] = self.data.High[-1]

                if (sessions['idr_low'] == None) or (self.data.Low[-1] < sessions['idr_low']):
                    sessions['idr_low'] = self.data.Low[-1]


                print("Updated values: drhigh:", sessions['dr_high'], "drlow: ", sessions['dr_low'], "idrhigh: ", sessions['idr_high'], "idrlow: ", sessions['idr_low'])


            else:
                print("Sessions hour has passed")
                #Check if session is still valid
                if self.data.Time[-1] > sessions['defining_hour_end'] and self.data.Time[-1] <= sessions['session_validity']:
                    print("session is still valid")
                    
                    levels = [sessions['dr_low'], sessions['idr_low'], sessions['dr_high'], sessions['idr_high']]
                    open_price, close_price = self.data.Open[-1], self.data.Close[-1]
                    print("entering level loop")
                    for level in levels:
                        print("Current level: ", level)
                        print("Current open: ", open_price)
                        print("Current close: ", close_price)
                        result = breaklevel(open_price, close_price, level)
                        print("current result is:", result)
                        if result == 1 or result == 2:
                            print("adding the following to levelbreaks: ", self.data.Time[-1], level, result, open_price, close_price)
                            for item in [self.data.Time[-1], level, result, open_price, close_price]:
                                sessions['levelbreaks'].append(item)
                                print("levelbreaks current state: ", sessions['levelbreaks'])
                else:
                    #session is not valid anymore, append values to csv
                    with open('session_results.csv', 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile, escapechar='\\', quoting=csv.QUOTE_NONE)
                        print("Session is not valid anymore, appending following values to csv: ", sessions['session_name'], sessions['dr_high'], sessions['dr_high_timestamp'], sessions['dr_low'], sessions['dr_low_timestamp'], sessions['idr_high'], sessions['idr_high_timestamp'], sessions['idr_low'], sessions['idr_low_timestamp'], sessions['levelbreaks'])
                        writer.writerow([sessions['session_name'], sessions['dr_high'], sessions['dr_high_timestamp'], sessions['dr_low'], sessions['dr_low_timestamp'], sessions['idr_high'], sessions['idr_high_timestamp'], sessions['idr_low'], sessions['idr_low_timestamp'], sessions['levelbreaks']])
                        #self.csvfile.flush()
        
# Create a Backtest object using the data and the strategy
bt = Backtest(data, MyStrategy, cash=100000, commission=.002)
stats = bt.run()
print(stats)
#bt.plot()
