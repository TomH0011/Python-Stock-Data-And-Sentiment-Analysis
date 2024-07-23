import datetime as dt
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from scipy import stats
import matplotlib.dates as mdates


def stock_growth(name, days):
    #Calculating mean
    todays_date = dt.datetime.now()
    days_ago = todays_date - dt.timedelta(days)
    stocks = [name]
    df_days_ago = yf.download(stocks, start=days_ago, end=todays_date)
    highs_lows_perday = df_days_ago[['Open', 'High', 'Low', 'Adj Close']]
    volume_of_trades = df_days_ago[['Volume']]
    todays_volume = volume_of_trades.iloc[-1]['Volume']
    t_statistic, p_value = stats.ttest_1samp(volume_of_trades, todays_volume)
    alpha = 0.05
    df_mean_for_seven_days = highs_lows_perday.mean(axis=1)

    #Calculate what the stock is trading at
    df_close_prices = df_days_ago[['Adj Close']]
    current_price = float(df_close_prices.iloc[-1].iloc[0])

    #Calculating Volatility
    average_stock_price = df_mean_for_seven_days.iloc[1].mean()
    difference_between_each_price_and_the_average_price = []
    squared_list = []
    for j in df_mean_for_seven_days:
        j=0
        k = float(df_mean_for_seven_days.iloc[int(j)] - average_stock_price)
        difference_between_each_price_and_the_average_price.append(k)
        h = float((difference_between_each_price_and_the_average_price[j])**2)
        squared_list.append(h)
        Volatility = (sum(squared_list) / len(squared_list)) ** (float(1/2))
        j+=1

    #Web-scraping
    records = []
    req = Request(url=f'https://finviz.com/quote.ashx?t={name}&p=d', headers={'user-agent': 'my-app'})
    response = urlopen(req)
    soup = BeautifulSoup(response, 'html.parser')
    news_table = soup.find(id='news-table')
    results = news_table.find_all('a')
    for result in results:
        headline = result.text
        records.append(headline)

    #Sentiment analysis
    analyser = SentimentIntensityAnalyzer()
    compound_scores = []
    for text in records:
        scores = analyser.polarity_scores(text)
        compound_scores.append(scores['compound'])
    average_compound_scores = sum(compound_scores) / len(compound_scores)

    #Prinitng statements
    print(f'The current Price the stock is trading at is: {current_price}')
    print('--------------------------------------------------------------')
    if p_value < alpha:
        print(f'The volume of trades today is significantly different from the mean volume of trades from the past {days} days')
    else:
        print(f'The volume of trades today is not significantly different from the mean volume of trades from the past {days} days.')
    print('--------------------------------------------------------------')
    if df_mean_for_seven_days.iloc[0] < df_mean_for_seven_days.iloc[-1]:
        print(f'Currently the stock is Growing in value in the past {days} days')
    else:
        print(f'Currently the stock is Not growing in value in the past {days} days')
    print('--------------------------------------------------------------')
    print(f'The volatility of {name} over the past {days} days is: {Volatility}')
    print('--------------------------------------------------------------')
    if average_compound_scores <= -0.5:
        print(f'The average compound sentiment score for the most recent headlines found on finviz is: {average_compound_scores} which is fairly negative')
    if average_compound_scores >= 0.5:
        print(f'The average compound sentiment score for the most recent headlines found on finviz is: {average_compound_scores} which is fairly positive')
    if -0.5 <= average_compound_scores <= 0.5:
        print(f'The average compound sentiment score for the most recent headlines found on finviz is: {average_compound_scores} which is fairly neutral')
    print('--------------------------------------------------------------')
    print(f'''Here's some of the most recent headlines:{records[slice(3)]}''')

    #Plotting
    start_date = pd.to_datetime(days_ago)
    todays_date = pd.to_datetime('today')
    list_of_dates = pd.date_range(start=start_date, end=todays_date, freq='B')
    aligned_date_list = list_of_dates[-len(df_mean_for_seven_days):]
    plt.plot(figsize = (100,20))
    plt.plot(aligned_date_list, df_mean_for_seven_days, linestyle='-')
    plt.xticks(rotation=45, ticks=[start_date, todays_date])
    locator = mdates.DayLocator(interval=60)
    plt.gca().xaxis.set_major_locator(locator)
    plt.title("Mean Value of the Stock per-day (Excluding Weekends)")
    plt.xlabel("Days")
    plt.ylabel("Change in Value")
    plt.show()
    return


stock_growth("USB", 7)
