# Author: Gustav Lundborg
# Date: 25-03-2024
# Revision date: 18-04-2024

import requests
from getBusinessDayDates import business_day_one_month_ago, last_business_day
import pandas
import time
from tkinter import *

API_KEY = 'nVUyzXwpWmFk9yLMMxD0nfq6gXlhI1IH'  # API key for the API polygon.io
INDEX_SYMBOL = 'SPY'  # This is the ticker for the index (SPDR S&P 500 ETF Trust)
unable_to_get_data = False  # If there was a problem getting data from the API this will be set to True
start_time_status_code_429 = 0  # Gets the time whenever a (status code 429 = data rate limit) happens
stock_dict = {}  # main dictionary holding all of the objects of the class Stock


class Stock:
    """
    Represents a stock and provides methods to gather both technical and fundamental data,
    calculate various metrics, and interact with the Polygon.io API.

    Attributes:
        symbol (str): The ticker symbol of the stock.
        company_name (str): The full name of the company.
        highest_price (float): The highest price of the stock within a specified period.
        lowest_price (float): The lowest price of the stock within a specified period.
        stock_return (float): The return of the stock calculated based on historical prices.
        beta_value (float): The beta value of the stock, indicating its volatility relative to a market index.
        closing_price_list (list): A list of the last 30 daily closing prices for the stock.
        has_beta_value (bool): Flag indicating whether the beta value has been calculated.
        pe_value (float): The price-to-earnings (P/E) ratio of the stock.
        ps_value (float): The price-to-sales (P/S) ratio of the stock.
        equity_ratio (float): The equity ratio of the stock.
    """

    def __init__(self, symbol):
        """Initializes the class and declares each attributed that is used"""
        self.symbol = symbol
        self.company_name = self.get_company_name()
        self.highest_price = ""
        self.lowest_price = ""
        self.stock_return = ""
        self.beta_value = ""
        self.closing_price_list = []
        self.has_beta_value = False

        self.pe_value = ""
        self.ps_value = ""
        self.equity_ratio = ""

    def get_technical_data(self):
        """Calls each function that is used to gather the technical data for the stock"""

        self.calculate_closing_price_list()
        if unable_to_get_data:
            return  # return nothing
        self.stock_return = self.calculate_stock_return()
        self.highest_price, self.lowest_price = self.get_price_extremes()

    def calculate_beta_value(self, index_return):
        """Calculates the beta value by dividing the stock return by the index"""
        self.beta_value = self.stock_return / index_return
        self.has_beta_value = True

    def calculate_closing_price_list(self):
        """Gets a list of the last 30 daily closing prices for the stock"""

        endpoint = (f"https://api.polygon.io/v2/aggs/ticker/{self.symbol}/range/1/day/"
                    f"{business_day_one_month_ago()}/{last_business_day()}?apiKey={API_KEY}")
        response = requests.get(endpoint)

        if response_successful(response):
            global unable_to_get_data
            self.closing_price_list = []

            try:
                stock_data = response.json()
                stock_prices = stock_data['results']

                for price_candle in stock_prices:
                    current_close = price_candle['c']
                    self.closing_price_list.append(current_close)
            except KeyError:
                unable_to_get_data = True
                draw_error_window("Unable to get the daily closing prices; try another stock")
            except Exception as e:
                unable_to_get_data = True
                show_error_message(e)

    def calculate_stock_return(self):
        """Calculates the stock return by getting the latest and the oldest price and dividing it"""
        latest_price = self.closing_price_list[-1]
        oldest_price = self.closing_price_list[0]

        stock_return = latest_price / oldest_price
        return stock_return

    def get_price_extremes(self):
        """
        Sorts the closing price list
        then takes the first and last element to extract the highest and lowest price
        """
        temp_price_list = self.closing_price_list
        temp_price_list.sort()
        highest_price = temp_price_list[-1]
        lowest_price = temp_price_list[0]

        return highest_price, lowest_price

    def get_fundamental_data(self):
        """
        Gets the relevant fundamental data from the polygon.io API,
        calculates each fundamental data point and assigns it to the class's attributes.
        """
        endpoint_financials = f"https://api.polygon.io/vX/reference/financials?ticker={self.symbol}&apiKey={API_KEY}"
        endpoint_tickers = f"https://api.polygon.io/v3/reference/tickers/{self.symbol}?apiKey={API_KEY}"
        response_financials = requests.get(endpoint_financials)
        response_tickers = requests.get(endpoint_tickers)

        if response_successful(response_financials) and response_successful(response_tickers):
            global unable_to_get_data

            try:
                latest_quarter = 0
                financial_data = response_financials.json()['results'][latest_quarter]['financials']

                eps = financial_data['income_statement']['basic_earnings_per_share']['value']
                total_revenue = financial_data['income_statement']['revenues']['value']
                assets = financial_data['balance_sheet']['assets']['value']
                equity = financial_data['balance_sheet']['equity']['value']

                ticker_data = response_tickers.json()
                market_cap = ticker_data['results']['market_cap']

                self.calculate_closing_price_list()
                latest_price = self.closing_price_list[-1]

                self.pe_value = latest_price / eps
                self.ps_value = market_cap / total_revenue
                self.equity_ratio = equity / assets
            except KeyError:
                draw_error_window("Unable to find latest financial data; try another stock")
                unable_to_get_data = True
            except Exception as e:
                unable_to_get_data = True
                draw_error_window(e)

    def get_company_name(self):
        """Gets the full name of the company from the API (polygon.io)"""

        endpoint_financials = f"https://api.polygon.io/vX/reference/financials?ticker={self.symbol}&apiKey={API_KEY}"
        response_financials = requests.get(endpoint_financials)

        if response_successful(response_financials):
            global unable_to_get_data
            try:
                latest_quarter = 0
                company_name = response_financials.json()['results'][latest_quarter]['company_name']
                return company_name  # returns the full company name of the stock
            except Exception as e:
                unable_to_get_data = True
                draw_error_window(e)


class Index(Stock):
    """
    Subclass of Stock;
    used to specify Indices which dont need to display a full company name in this program
    """

    def get_company_name(self):
        """
        Used to override the get_company_name method from Stock as to avoid
        requesting the API for data that is never used for the index
        """
        pass


def response_successful(response):
    """
    Checks if a response is successful by asking for its status code.
    Takes in the parameter 'response' as the response
    """
    global unable_to_get_data
    global start_time_status_code_429

    if response.status_code == 200:  # status code 200 == successful request
        return True  # return true
    elif response.status_code == 429:
        '''
        If a status code 429 happens it most likely means 
        it has reached the data request limit (5 requests per minute) for this API
        '''
        unable_to_get_data = True
        start_time_status_code_429 = get_current_time()
        draw_error_window("You have surpassed the rate limit for retrieving data; wait 1 minute.")
        return False  # returns False to avoid gathering data from a failed response
    else:
        draw_error_window(f"Failed to retrieve data. Status code: {response.status_code}")
        unable_to_get_data = True
        return False  # returns False to avoid gathering data from a failed response


def show_error_message(error):
    draw_error_window(f"There was an error when gathering the data; {error}")


def fetch_sp500_tickers():
    """Gets a list of the current 500 stocks in the S&P 500 index"""
    sp_wikipedia_data = pandas.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    sp_symbol_list = []

    for symbol in sp_wikipedia_data['Symbol']:
        sp_symbol_list.append(symbol)
    return sp_symbol_list  # returns a list of all the symbols in the S&P 500


sp500_symbol_list = fetch_sp500_tickers()


def is_in_sp500(stock_symbol):
    """Checks if the parameter 'stock symbol' is in the S&P 500 symbol list"""
    if stock_symbol in sp500_symbol_list:
        return True  # return True (the stock_symbol is in the list)
    else:
        draw_error_window("This ticker is not in the S&P 500")
        return False  # return False (the stock_symbol is not in the list)


def get_current_time():
    """Gets the current time in seconds since the Epoch"""
    current_time = time.time()
    return current_time  # returns the current time since epoch


def is_within_rate_limit():
    """Checks if 60 seconds have gone since the start time (the API has 5 requests per minute limit)"""
    global unable_to_get_data
    global start_time_status_code_429

    end_time = get_current_time()
    elapsed_time = end_time - start_time_status_code_429

    if elapsed_time < 60:
        time_left = round(60 - elapsed_time, 2)
        draw_error_window(f"You load data too often; wait {time_left} seconds")
        return False  # if the elapsed time since the status_code_429 happened is below 60s, return False
    else:
        start_time_status_code_429 = 0
        unable_to_get_data = False
        return True  # return True


def sort_stocks_by_beta():
    """Sorts each of the Stock objects in 'stock_dict' by their beta value"""
    temp_stock_list = []

    for stock in stock_dict.values():

        if stock.has_beta_value:
            temp_stock_list.append(stock)

    if not temp_stock_list:
        draw_error_window("You need to do to a technical analysis of a stock")
        return  # return nothing, get out of the function

    sorted_stocks_by_beta = sorted(temp_stock_list, key=lambda stock: stock.beta_value, reverse=True)
    draw_stock_ranking(sorted_stocks_by_beta)


def remove_all_widgets(window):
    """Destroy all widgets in the window"""
    for widget in window.winfo_children():
        widget.destroy()


def create_main_menu():
    """Creates the main menu of the program"""
    remove_all_widgets(root)

    fundamental_button = Button(root, text="1. Fundamental analysis", command=ask_for_fundamental_ticker)
    fundamental_button.grid(row=0, column=0, columnspan=1, sticky=W)

    technical_button = Button(root, text="2. Technical analysis", command=ask_for_technical_ticker)
    technical_button.grid(row=1, column=0, columnspan=1, sticky=W)

    ranking_button = Button(root, text="3. Rank stocks by beta value", command=sort_stocks_by_beta)
    ranking_button.grid(row=2, column=0, columnspan=1, sticky=W)

    exit_button = Button(root, text="4. Exit", command=lambda: destroy_window(root))
    exit_button.grid(row=3, column=0, columnspan=1, sticky=W)


def ask_for_fundamental_ticker():
    """
    Checks if the API is within in its rate limit, then runs the ask_for_ticker function
    with the main function that drive the fundamental analysis 'run_fundamental_analysis' as parameter.
    This is so the right type of analysis can be executed in 'ask_for_ticker' depending on which analysis is chosen
    """
    if is_within_rate_limit():
        ask_for_ticker(run_fundamental_analysis)


def ask_for_technical_ticker():
    """
    Checks if the API is within in its rate limit, then runs the ask_for_ticker function
    with the main function that drive the fundamental analysis 'run_technical_analysis' as parameter.
    This is so the right type of analysis can be executed in 'ask_for_ticker' depending on which analysis is chosen
    """
    if is_within_rate_limit():
        ask_for_ticker(run_technical_analysis)


def destroy_window(window):
    """Destroys the 'window' that is being input as parameter"""
    window.destroy()


def entry_is_valid_ticker_in_sp_500(entry):
    """
    If the 'entry' parameter (a string of text) only consists of letters and is in the S&P 500 list:
    return True, otherwise False
    """
    if any(not char.isalpha() for char in entry):
        draw_error_window("A stock ticker consists only of capital letters")
        return False  # does not consist of only letters; return True

    if not is_in_sp500(entry):
        return False  # Is not in the S&P 500, return False

    return True  # entry is valid; return True


def ask_for_ticker(analysis_type_function):
    """
    This displays the screen asking for a stock ticker
    It creates a label, entry and button to get an entry from the user,
    then runs 'get_ticker' the button is clicked
    The parameter 'analysis_type_calculation'
    is used to get the main function for the type of analysis that is being done
    """
    remove_all_widgets(root)

    def get_ticker():
        """
        This checks if it's within the API rate limit
        then gets the users entry and does an analysis
        based on the overarching functions parameter 'analysis_type_function',
        so f.e 'run_fundamental_analysis' can be used
        if the entry is a valid ticker in the S&P 500; run the analysis function
        """
        if not is_within_rate_limit():
            return  # return nothing, get out of the function

        users_stock_symbol = ticker_entry.get().upper()

        if entry_is_valid_ticker_in_sp_500(users_stock_symbol):
            analysis_type_function(users_stock_symbol)

    # Create all the widgets
    input_ticker_label = Label(root, text="Input a ticker from the S&P 500")
    input_ticker_label.grid(row=0, column=0, columnspan=1, sticky=W)

    ticker_entry = Entry(root)
    ticker_entry.grid(row=1, column=0, columnspan=1, sticky=W)

    get_input_button = Button(root, text="Calculate", command=get_ticker)  # if command is executed; get the users entry
    get_input_button.grid(row=2, column=0, columnspan=1, sticky=W)

    back_button = Button(root, text="Back", command=create_main_menu)  # if command is executed; return to the main menu
    back_button.grid(row=3, column=0, columnspan=1, sticky=W)


def run_technical_analysis(stock_symbol):
    """
    The main function that runs the technical analysis,
    it takes the stock's symbol as a parameter
    it gets the technical data from the index and the current stock, so it can print the results in the GUI
    Inbetween each function that gathers data from the API; it checks if it was unable to get data through this process
    if so it will return out of the function, so it doesn't waste any more requests to the API.
    """
    index = Index(INDEX_SYMBOL)
    if unable_to_get_data:
        return  # return nothing
    index.get_technical_data()
    if unable_to_get_data:
        return  # return nothing

    current_stock = ""
    if stock_symbol in stock_dict:  # if the stock already exists as an object
        current_stock = stock_dict[stock_symbol]
    else:
        current_stock = Stock(stock_symbol)

    if unable_to_get_data:
        return  # return nothing
    current_stock.get_technical_data()
    if unable_to_get_data:
        return  # return nothing
    current_stock.calculate_beta_value(index.stock_return)

    draw_technical_data(current_stock)
    stock_dict[stock_symbol] = current_stock


def run_fundamental_analysis(stock_symbol):
    """
    The main function that runs the fundamental analysis,
    it takes the stock's symbol as a parameter
    it gets the fundamental data from the current stock, so it can print the results in the GUI
    Inbetween each function that gathers data from the API; it checks if it was unable to get data through this process
    if so it will return out of the function, so it doesn't waste any more requests to the API.
    """
    current_stock = ""
    if stock_symbol in stock_dict:  # if the stock already exists as an object
        current_stock = stock_dict[stock_symbol]
    else:
        current_stock = Stock(stock_symbol)

    if unable_to_get_data:
        return  # return nothing
    current_stock.get_fundamental_data()
    if unable_to_get_data:
        return  # return nothing

    stock_dict[stock_symbol] = current_stock
    draw_fundamental_data(current_stock)


def draw_technical_data(stock):
    """
    Cleans the root window,
    Takes the stock object as parameter
    Takes its technical attributes and makes it presentable (rounding them)
    then creates widgets to present these technical data points
    """
    remove_all_widgets(root)

    stock_return = round(stock.stock_return * 100 - 100, 2)
    beta_value = round(stock.beta_value, 3)
    lowest_price = "{:.2f}".format(stock.lowest_price)
    highest_price = "{:.2f}".format(stock.highest_price)

    company_name_lbl = Label(root, text=f"Technical analysis for {stock.company_name}")
    company_name_lbl.grid(row=0, column=0, columnspan=1, sticky=W)
    beta_value_lbl = Label(root, text=f"The beta value is {beta_value}")
    beta_value_lbl.grid(row=1, column=0, columnspan=1, sticky=W)
    stock_return_lbl = Label(root, text=f"The stock return is {stock_return}%")
    stock_return_lbl.grid(row=2, column=0, columnspan=1, sticky=W)
    lowest_price_lbl = Label(root, text=f"The lowest price is {lowest_price}")
    lowest_price_lbl.grid(row=3, column=0, columnspan=1, sticky=W)
    highest_price_lbl = Label(root, text=f"The highest price is {highest_price}")
    highest_price_lbl.grid(row=4, column=0, columnspan=1, sticky=W)
    continue_lbl = Button(root, text="Continue", command=create_main_menu)  # Go back button; return to main menu
    continue_lbl.grid(row=5, column=0, columnspan=1, sticky=W)


def draw_fundamental_data(stock):
    """
    Cleans the root window,
    Takes the stock object as parameter
    Takes its fundamental attributes and makes it presentable (rounding them)
    then creates widgets to present these fundamental data points
    """
    remove_all_widgets(root)

    equity_ratio = round(stock.equity_ratio, 2)
    pe_value = round(stock.pe_value, 2)
    ps_value = round(stock.ps_value, 2)

    company_name_lbl = Label(root, text=f"Fundamental analysis for {stock.company_name}")
    company_name_lbl.grid(row=0, column=0, columnspan=1, sticky=W)
    equity_ratio_lbl = Label(root, text=f"The equity ratio is {equity_ratio}")
    equity_ratio_lbl.grid(row=1, column=0, columnspan=1, sticky=W)
    pe_value_lbl = Label(root, text=f"The p/e value is {pe_value}")
    pe_value_lbl.grid(row=2, column=0, columnspan=1, sticky=W)
    ps_value_lbl = Label(root, text=f"The p/s value is {ps_value}")
    ps_value_lbl.grid(row=3, column=0, columnspan=1, sticky=W)
    continue_lbl = Button(root, text="Continue", command=create_main_menu)  # Continue button; return to main menu
    continue_lbl.grid(row=4, column=0, columnspan=1, sticky=W)


def draw_stock_ranking(sorted_stocks_by_beta):
    """
    Takes a list of sorted stocks objects by their beta value as parameter
    Creates the widgets and displays the stocks sorted by their beta value procedurally
    by how many stocks that have calculated a beta value
    """
    row_iteration = 0
    remove_all_widgets(root)
    for rank, stock in enumerate(sorted_stocks_by_beta, start=1):
        company_name = stock.company_name
        beta_value = round(stock.beta_value, 3)
        row_iteration = rank - 1

        rank_lbl = Label(root, text=f"{rank}. {company_name} {beta_value}")
        rank_lbl.grid(row=row_iteration, column=0, columnspan=1, sticky=W)

    back_button = Button(root, text="Back", command=create_main_menu)  # Go back button; return to main menu
    back_button.grid(row=row_iteration + 1, column=0, columnspan=1, sticky=W)


def draw_error_window(show_error_message):
    """
    Takes in an error_message (string) as parameter
    Creates a new window to display this error message
    as well creates a 'OK' button that closes the window
    """
    error_window = Tk()
    error_window.title("Attention")

    error_lbl = Label(error_window, text=show_error_message)
    error_lbl.pack()
    ok_button = Button(error_window, text="OK", command=lambda: destroy_window(error_window))
    ok_button.pack()
    error_window.mainloop()


# root window
root = Tk()
root.title("Stock Analyser")
create_main_menu()
root.mainloop()
