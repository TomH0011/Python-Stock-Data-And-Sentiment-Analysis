# Imports

import datetime as dt
import pandas as pd
import yfinance as yf
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tkinter as tk
from tkinter import Label, Button
import requests
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class StockAnalysis:
    def __init__(self, name, days):  # Initialising all the variables
        self.suggestions = None
        self.suggestion_listbox = None
        self.ticker_var = None
        self.info_box = None
        self.info_var = None
        self.df_close_prices = None
        self.name = name.strip()
        self.days = days
        self.todays_date = dt.datetime.now()
        self.days_ago = self.todays_date - dt.timedelta(days)
        self.stocks = [self.name]
        self.stock_data = None
        self.data_cols = None
        self.trade_volume = None
        self.current_price = None
        self.Volatility = None
        self.records = None
        self.average_compound_scores = None
        self.root = None
        self.api_key = 'ENTER YOUR OWN API KEY HERE'  # Fill with your own API key from Alpha Vantage

    def get_stock_data(self):  # Downloading the stock data from yahoo finance
        self.stock_data = yf.download(self.stocks, start=self.days_ago, end=self.todays_date)
        if self.stock_data.empty:
            raise ValueError(f"Ticker '{self.name}' not found or no data available.")
        self.data_cols = self.stock_data[['Open', 'High', 'Low', 'Adj Close']]
        self.trade_volume = self.stock_data[['Volume']]
        self.df_close_prices = self.stock_data[['Adj Close']]
        self.current_price = float(self.df_close_prices.iloc[-1].iloc[0])

    def calculate_statistics(self):
        todays_volume = self.trade_volume.iloc[-1]['Volume']
        t_statistic, p_value = stats.ttest_1samp(self.trade_volume, todays_volume)

        df_mean = self.data_cols.mean(axis=1)
        average_stock_price = df_mean.iloc[1].mean()
        squared_diffs = (df_mean - average_stock_price) ** 2
        self.Volatility = (squared_diffs.mean()) ** 0.5  # Calculating volatility of the stock

        return t_statistic, p_value, df_mean

    def web_scraping(self):  # Web scraping headlines from finvis to perform sentiment analysis
        self.records = []
        req = Request(url=f'https://finviz.com/quote.ashx?t={self.name}&p=d', headers={'user-agent': 'my-app'})
        response = urlopen(req)
        soup = BeautifulSoup(response, 'html.parser')
        news_table = soup.find(id='news-table')
        results = news_table.find_all('a')
        for result in results:
            headline = result.text
            self.records.append(headline)

    def sentiment_analysis(self):  # Measuring sentiment and giving scores
        analyser = SentimentIntensityAnalyzer()
        compound_scores = [analyser.polarity_scores(text)['compound'] for text in self.records]
        self.average_compound_scores = sum(compound_scores) / len(compound_scores)

    def plot_stock_data(self, df_mean_for_seven_days):  # Plotting stock data on a canvas to later go on a frame
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        start_date = pd.to_datetime(self.days_ago)  # Start of plot
        todays_date = pd.to_datetime('today')  # End of plot
        list_of_dates = pd.date_range(start=start_date, end=todays_date, freq='B')
        aligned_date_list = list_of_dates[-len(df_mean_for_seven_days):]

        ax.plot(aligned_date_list, df_mean_for_seven_days, linestyle='-')
        ax.set_title("Mean Value of the Stock per-day (Excluding Weekends)")
        ax.set_xlabel("Days")
        ax.set_ylabel("Change in Value")
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=int(self.days) // 4))
        ax.tick_params(axis='x', rotation=45)

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()

        canvas.get_tk_widget().grid(column=3, row=2)

    def search_ticker_suggestions(self, query):  # Makes sure a correct ticker called
        if not query:
            return []
        return self.tickersearch(query)

    def dashboard(self):   # Creating a dashboard with labels, buttons, entries and a search box from AlphaVantage API
        self.root = tk.Tk()  # Creating the frame
        self.root.title("Stock data Dashboard")
        self.root.geometry("1300x450")  # Setting frame size

        Label(self.root, text="Enter the Stock ticker you want to analyse: ").grid(column=0, row=0)  # Giving a piece of text

        self.info_var = tk.StringVar()  # Creating a string variable which allows text inside it to be altered
        self.info_box = Label(self.root, textvariable=self.info_var, wraplength=400)  # Creating area where text can be placed
        self.info_box.grid(column=2, row=2)  # Placing item in grid

        self.ticker_var = tk.StringVar()
        ticker_entry = tk.Entry(self.root, textvariable=self.ticker_var, width=40)  # Creating an entry (Input Field)
        ticker_entry.grid(column=0, row=1)

        self.suggestion_listbox = tk.Listbox(self.root, width=60)  # Creating a drop down listbox
        self.suggestion_listbox.grid(column=0, row=2)  # Placing listbox
        self.suggestion_listbox.bind('<Double-1>', self.cb)  # Binding double click to each item in drop down list
        ticker_entry.bind('<KeyRelease>', self.update_suggestions)

        Button(self.root, text="Quit", command=self.root.destroy).grid(column=2, row=0)  # Allows user to quit dahsboard and stops code from running
        Button(self.root, text='Search', command=self.plotandprint).grid(column=1, row=0)  # Allows user to search and run data code and plotting

        self.root.mainloop()  # Updates the frame

    def tickersearch(self, name):  # Calling the API
        base_url = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH'  # API URL
        url = f'{base_url}&keywords={name}&apikey={self.api_key}'  # Personal url for API

        try: # Make sure request gives a 200
            r = requests.get(url)
            data = r.json()
            r.raise_for_status()

            if 'Error Message' in data or 'Note' in data:
                print(f"Rate limit reached or invalid query. Try again later.")
                return []

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return []

        if 'bestMatches' in data:  # Making sure as we type it matches key stroke toi best result
            matches = data['bestMatches']
            result = []
            for match in matches:
                symbol = match['1. symbol']
                name = match['2. name']
                result.append((symbol, name))

            return result

        else:
            return []

    def cb(self, event):  # Want when we double-click it knows what to call back
        selection = self.suggestion_listbox.curselection()
        if selection:
            index = selection[0]
            selected_item = self.suggestion_listbox.get(index)
            symbol = selected_item.split(' - ')[0]
            self.ticker_var.set(symbol)

    def update_info_box(self, p_value, df_mean_for_seven_days):  # when given a ticker in the input field and then search it will run the code and print this into a label
        output = f"The current Price the stock is trading at is: {self.current_price}\n"
        output += '--------------------------------------------------------------\n'
        alpha = 0.05
        if p_value < alpha: # Testing the data
            output += (f'The volume of trades today is significantly different from the mean volume of trades from the '
                       f'past {self.days} days\n')
        else:
            output += (f'The volume of trades today is not significantly different from the mean volume of trades from '
                       f'the past {self.days} days.\n')

        output += '--------------------------------------------------------------\n'
        if df_mean_for_seven_days.iloc[0] < df_mean_for_seven_days.iloc[-1]:
            output += f'Currently the stock is Growing in value in the past {self.days} days\n'
        else:
            output += f'Currently the stock is Not growing in value in the past {self.days} days\n'

        output += f'The volatility of {self.name} over the past {self.days} days is: {self.Volatility}\n'
        output += '--------------------------------------------------------------\n'

        if self.average_compound_scores <= -0.5:
            output += (f'The average compound sentiment score for the most recent headlines found on finviz is: '
                       f'{self.average_compound_scores} which is fairly negative\n')
        elif self.average_compound_scores >= 0.5:
            output += (f'The average compound sentiment score for the most recent headlines found on finviz is: '
                       f'{self.average_compound_scores} which is fairly positive\n')
        else:
            output += (f'The average compound sentiment score for the most recent headlines found on finviz is: '
                       f'{self.average_compound_scores} which is fairly neutral\n')

        output += '--------------------------------------------------------------\n'
        output += f"Here's some of the most recent headlines: {self.records[:3]}"

        self.info_var.set(output)

    def handle_search(self):  # Tries running of the code within the dashboard for when user presses search
        try:
            self.name = self.ticker_var.get().strip()
            if not self.name:
                raise ValueError("Ticker symbol cannot be empty.")
            self.stocks = [self.name]
            self.get_stock_data()
            t_statistic, p_value, df_mean_for_seven_days = self.calculate_statistics()
            self.web_scraping()
            self.sentiment_analysis()

            self.update_info_box(p_value, df_mean_for_seven_days)

            return df_mean_for_seven_days

        except Exception as e:
            self.info_var.set(f"Error: {str(e)}")
            return None

    def plotandprint(self): # Combining the plotting and data running into one to overflow the search button with multiple functions
        df_mean_for_seven_days = self.handle_search()
        if df_mean_for_seven_days is not None:
            self.plot_stock_data(df_mean_for_seven_days)

    def update_suggestions(self, event):  # Updates the suggestions as you type
        query = self.ticker_var.get().strip()
        self.suggestions = self.search_ticker_suggestions(query)
        self.update_listbox()

    def update_listbox(self):  # Updates the listbox as you type
        self.suggestion_listbox.delete(0, tk.END)
        for symbol, name in self.suggestions:
            self.suggestion_listbox.insert(tk.END, f"{symbol} - {name}")

    def run_analysis(self): # Runs all the code
        self.get_stock_data()
        t_statistic, p_value, df_mean_for_seven_days = self.calculate_statistics()
        self.web_scraping()
        self.sentiment_analysis()
        # self.plot_stock_data(df_mean_for_seven_days)
        self.dashboard()
        self.tickersearch(self.name)

# Example of creating and running the StockAnalysis object
if __name__ == "__main__":
    stock_analysis = StockAnalysis(name="AAPL", days=30)
    stock_analysis.run_analysis()
