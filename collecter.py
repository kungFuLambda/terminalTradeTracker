import yfinance as yf
import datetime
import math
import os
import sys
import time
import string
import requests
import json



# Where USD is the base currency you want to use
url = 'https://prime.exchangerate-api.com/v5/15638aa65a1c548c69c7a8dc/latest/USD'


#user variables: TICKER,QUANTITY,BOUGHT Price,STOP LOSS, PORTFOLIO SIZE
#calculated variables: CURRENT PRICE, % ALLOCATION, ALLOCATION £, P/L % , P/L £

class Portfolio:
    value = 0
    invested = 0
    cash = 0
    profitLoss = 0
    stocks = []
    sold =[]

    def addStock(self,stock):
        self.stocks.append(stock)
        self.invested += float(stock.buyPrice) *int(stock.quantity)
        self.profitLoss += stock.profitLoss

    def addSold(self,stock):
        self.sold.append(stock)


    def update_prices(self):
        for stock in self.stocks:
            stock.update_price()



    def print_portfolio(self):
        os.system("clear")
        if len(self.stocks) != 0:
            banner = "|   stock   |   qty   |   value ($)   |   allocation   |   buyPrice ($)   |   currentPrice ($)   |   P/L   |   P/L ($)   |   P/L (£)   |"
            print("-"*len(banner))
            print(banner)
            print("-"*len(banner))
            for stock in self.stocks:
                stock.printRight([
                (stock.ticker,11),#ticker
                (stock.quantity,9), #quantity
                (stock.value,15), #value 
                (str(100*(int(stock.quantity)*float(stock.buyPrice)/self.invested))[:4:]+"%",16), #allocation %
                (stock.buyPrice,18), #buy price
                (stock.currentPrice,22), #current price
                (str(float(stock.profitLoss)/float(stock.value)*100)[:4:]+"%",9), #p/l
                (str(stock.profitLoss)[:6:],13), #p/l pounds
                (str(stock.profitLoss*rate)[:6:],13),
                ])
            print("-"*len(banner))
            
        print("\n"*3)
        if len(self.sold) != 0:
            banner = "|   stock   |   qty   |   value ($)   |   buyPrice ($)   |   sellPrice ($)   |   P/L   |   P/L ($)   |   P/L (£)   |"
            
            print(" "*(math.floor(len(banner)/2)) + "CLOSED POSITIONS" + " "*(math.ceil(len(banner)/2)))
            print("-"*len(banner))

            print(banner)
            print("-"*len(banner))

            for stock in self.sold:
                stock.printRight([
                (stock.ticker,11),#ticker
                (stock.quantity,9), #quantity
                (stock.value,15), #value 
                (stock.buyPrice,18), #buy price
                (stock.sellPrice,19), #current price
                (str(float(stock.profitLoss)/float(stock.value)*100)[:4:]+"%",9), #p/l
                (str(stock.profitLoss)[:6:],13), #p/l pounds
                (str(stock.profitLoss*rate)[:6:],13),
                ])
            print("-"*len(banner))

        print("")
        print("Capital invested: " + str(self.invested))
        print("profit/loss: "+str(self.profitLoss)[:6:])

class Position:

    ticker = None
    quantity=0
    buyPrice = 0
    stopLoss = 0
    profitLoss = 0
    currentPrice = 0
    sellPrice = 0
    value = 0

    def __init__(self,ticker,quantity,buyPrice,stopLoss,**kwargs):
        self.ticker = ticker
        self.quantity = quantity
        self.buyPrice = buyPrice
        self.stopLoss = stopLoss
        if 'sold' in kwargs:
            self.sellPrice = kwargs['sold']
                






        
        req = str(yf.download(ticker,datetime.datetime.now().date())['Close'][0]).split(".")
        os.system("clear")
        self.currentPrice = ".".join([req[0],req[1][:3:]])
        if self.sellPrice != 0:
            self.profitLoss = (float(self.sellPrice) - float(self.buyPrice))*int(self.quantity)
        else:
            self.profitLoss = (float(self.currentPrice) - float(self.buyPrice))*int(self.quantity)
        self.value = str(int(self.quantity)*float(self.currentPrice))[:6:]



    def printRight(self,values):
        print("|",end="")
        for val in values:
            
            tik = val[0]
            wide = val[1]
            print(" "*math.floor((wide-len(tik))/2),end="")
            print(tik,end="")
            print(" "*math.ceil((wide-len(tik))/2) + "|",end="")
        print("")

    def update_price(self):
        req = yf.download(self.ticker,datetime.datetime.now().date())['Close']
        req = str(req[len(req)-1]).split(".")
        os.system("clear")
        self.currentPrice = ".".join([req[0],req[1][:3:]])





if __name__ == "__main__":

    
    if ("portfolio.txt" not in os.listdir()):
        f = open("portfolio.txt","w+")
        f.close()



    
    if len(sys.argv) == 2:
        response = requests.get(url)
        exchangeRates = response.json()
        rate = exchangeRates['conversion_rates']['GBP']
    
    
    #initialize portfolio
        if sys.argv[1] == "track":
            os.system("clear")
            myPorfolio = Portfolio()
            

            #read all data from file
            with open("portfolio.txt","r") as f:
                
                for line in f:
                    line = line.strip()
                    
                    
                    #get balance value
                    if "balance" in line:
                        balance = float(line.split(":")[1])
                        myPorfolio.value = balance


                    #get all stocks in portfolio
                    else:
                        data = line.split(",")
                        if len(data) == 4:
                            
                            p = Position(data[0],data[1],data[2],data[3])
                            myPorfolio.addStock(p)
                        elif len(data) ==5:
                            p = Position(data[0],data[1],data[2],data[3],sold=data[4])
                            myPorfolio.addSold(p)

                while True:
                    myPorfolio.update_prices()
                    myPorfolio.print_portfolio()
                    time.sleep(20)
    


        if sys.argv[1] == "add":
            while True:
                tik = input("enter ticker: ").upper()
                
                qty = input("enter quantity: ")
                price = input("enter buy price: ")
                stopLoss = input("enter stop loss (enter 0 if no stop loss): ")
                ans = input("so you are adding {} shares of {} at {}. Does this seem right? (y/n)".format(qty,tik,price)).lower()
                if ans == "y":
                    with open("portfolio.txt","a") as p:
                        p.write("\n{},{},{},{}".format(tik,qty,price,stopLoss))
                        print("added {}".format(tik))
                        break


        elif sys.argv[1] == "close":
            tik = input("enter ticker: ").upper()
            pos = []
            with open("portfolio.txt","r+") as p:
                for line in p:

                    line = line.strip().split(",")
                    
                    if line[0] == tik:
                        stock = line
                        ans = input("So you want to close {} share of {} at {}? (y/n)".format(stock[0],stock[1],stock[2]))
                        if ans == "y":
                            close = input("Enter closing price: ")
                            stock.append(close)
                            pos.append(",".join(stock))
                            print("stock closed")
                    else:
                        pos.append(",".join(line))

            with open("portfolio.txt","w+") as p:
                for position in pos:
                    p.write(position+"\n")

            if stock == 0:
                ans = input("the stock wasn't in your portfolio, did you mean another stock? (y/n) ")
                
                    
    else:
        print("invalid input\nsyntax: python(3)  portfolio.py [track/add/close]")
        sys.exit()