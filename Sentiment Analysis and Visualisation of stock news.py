import datetime as dt
import pandas as pd
import yfinance as yf
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



class StockAnalysis:
    def __init__(self, name, days):  # Initialising all the variables im going to use
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

    def get_stock_data(self):
        # Download stock data from Yahoo finance
        self.stock_data = yf.download(self.stocks, start=self.days_ago, end=self.todays_date)
        if self.stock_data.empty:
            raise ValueError(f"Ticker '{self.name}' not found or no data available.")
        self.data_cols = self.stock_data[['Open', 'High', 'Low', 'Adj Close']]
        self.trade_volume = self.stock_data[['Volume']]
        self.df_close_prices = self.stock_data[['Adj Close']]
        self.current_price = float(self.df_close_prices.iloc[-1].iloc[0])

    def calculate_statistics(self):
        # T-test for volume significance
        todays_volume = self.trade_volume.iloc[-1]['Volume']
        t_statistic, p_value = stats.ttest_1samp(self.trade_volume, todays_volume)

        df_mean = self.data_cols.mean(axis=1)
        average_stock_price = df_mean.iloc[1].mean()
        squared_diffs = (df_mean - average_stock_price) ** 2
        self.Volatility = (squared_diffs.mean()) ** 0.5  # Volatility formula

        return t_statistic, p_value, df_mean

    def web_scraping(self):
        # Scrape news headlines from Finviz
        self.records = []
        req = Request(url=f'https://finviz.com/quote.ashx?t={self.name}&p=d', headers={'user-agent': 'my-app'})
        response = urlopen(req)
        soup = BeautifulSoup(response, 'html.parser')
        news_table = soup.find(id='news-table')
        results = news_table.find_all('a')
        for result in results:
            headline = result.text
            self.records.append(headline)

    def sentiment_analysis(self):
        # Perform sentiment analysis on headlines
        analyser = SentimentIntensityAnalyzer()
        compound_scores = [analyser.polarity_scores(text)['compound'] for text in self.records]
        self.average_compound_scores = sum(compound_scores) / len(compound_scores)

    def print_results(self, p_value, df_mean_for_seven_days):
        # Printing the stock analysis results
        print(f'The current Price the stock is trading at is: {self.current_price}')
        print('--------------------------------------------------------------')
        alpha = 0.05
        if p_value < alpha:
            print(
                f'The volume of trades today is significantly different from the mean volume of trades from the past {self.days} days')
        else:
            print(
                f'The volume of trades today is not significantly different from the mean volume of trades from the past {self.days} days.')
        print('--------------------------------------------------------------')
        if df_mean_for_seven_days.iloc[0] < df_mean_for_seven_days.iloc[-1]:
            print(f'Currently the stock is Growing in value in the past {self.days} days')
        else:
            print(f'Currently the stock is Not growing in value in the past {self.days} days')
        print('--------------------------------------------------------------')
        print(f'The volatility of {self.name} over the past {self.days} days is: {self.Volatility}')
        print('--------------------------------------------------------------')
        if self.average_compound_scores <= -0.5:
            print(
                f'The average compound sentiment score for the most recent headlines found on finviz is: {self.average_compound_scores} which is fairly negative')
        if self.average_compound_scores >= 0.5:
            print(
                f'The average compound sentiment score for the most recent headlines found on finviz is: {self.average_compound_scores} which is fairly positive')
        if -0.5 <= self.average_compound_scores <= 0.5:
            print(
                f'The average compound sentiment score for the most recent headlines found on finviz is: {self.average_compound_scores} which is fairly neutral')
        print('--------------------------------------------------------------')
        print(f'''Here's some of the most recent headlines:{self.records[:3]}''')

    def plot_stock_data(self, df_mean_for_seven_days):
        # Plotting the stock data
        start_date = pd.to_datetime(self.days_ago)
        todays_date = pd.to_datetime('today')
        list_of_dates = pd.date_range(start=start_date, end=todays_date, freq='B')
        aligned_date_list = list_of_dates[-len(df_mean_for_seven_days):]

        plt.figure(figsize=(10, 6))
        plt.plot(aligned_date_list, df_mean_for_seven_days, linestyle='-')
        plt.xticks(rotation=45, ticks=[start_date, todays_date])
        locator = mdates.DayLocator(interval=int(self.days) // 4)  # Want fewer date label's on x-axis to avoid clutter
        plt.gca().xaxis.set_major_locator(locator)

        plt.title("Mean Value of the Stock per-day (Excluding Weekends)")
        plt.xlabel("Days")
        plt.ylabel("Change in Value")

        plt.show()

    def run_analysis(self):
        # Run the complete analysis
        self.get_stock_data()
        t_statistic, p_value, df_mean_for_seven_days = self.calculate_statistics()
        self.web_scraping()
        self.sentiment_analysis()
        self.print_results(p_value, df_mean_for_seven_days)
        self.plot_stock_data(df_mean_for_seven_days)
        self.dashboard()
        self.tickersearch(self.name)


# Run the stock analysis
analysis = StockAnalysis("NVDA", 7)
analysis.run_analysis()
