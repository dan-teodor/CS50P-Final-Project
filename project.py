import streamlit as st
# activate in terminal using the command "streamlit run project.py"
# from tabulate import tabulate
import pandas as pd
#import numpy as np
import yfinance as yf
#import matplotlib.pyplot as plt
import csv

def main(tick = None):
    #display commands
    st.title("Welcome to Financials50")
    tick = st.text_input("Choose a ticker and explore different actions")
    if tick == None:
        st.write("Choose a Security")
    else:
        page = st.radio("What do you want to do today ?", ["Explore Ticker","See portfolio","See financial statements"])

        #explore Ticker
        if page == "Explore Ticker":
            request = yf.Ticker(tick)
            if tick != "":
                left,right=st.columns(2)
                with left:
                    st.title(request.info["longName"])
                with right:
                    if st.button ("Add security to portfolio"):
                        add_security(tick,request.info["longName"].replace(',','.'),request.info['currentPrice'])
                st.header(f"{tick} : {request.info['exchange']}")
                st.subheader(f"{request.info['sector'].split()[0]} ➡️ {request.info['industry'].split()[0]}")
                a, b, c = st.columns(3)
                with a:
                    st.metric("Price",f"{request.info['currentPrice']} {request.info['currency']}",delta=price_delta(tick))
                with b:
                    try:
                        st.metric("Shares Outstanding",f"{round(request.info['sharesOutstanding']/1000000)} M")
                    except:
                        KeyError("")
                with c:
                    try:
                        st.metric("Beta",request.info['beta'])
                    except:
                        KeyError("")
                chart_lit(tick)

        #explore Portfolio
        if page == "See portfolio":
            portfolio_display()

        if page =="See financial statements":
            fs_display(tick)

def chart_lit(n):
    tick = yf.Ticker(n)
    period_lit = st.slider("Period for the chart",min_value=1,max_value=10)
    chart_data = pd.DataFrame(tick.history(interval="1d",period=f"{period_lit}y"))
    st.line_chart(chart_data,y="Close")
    
def price_delta(tick):
    request = yf.Ticker(tick)
    hist = request.history(period = "2d")
    price_delta = round(request.info['currentPrice'] - hist["Close"][0],2)
    return price_delta

def portfolio_display():    
    ptf = pd.DataFrame(columns=("Ticker","Name","Current Price","History"))
    with open("portfolio.csv") as file:
        for line in file: 
            ticker, name, price = str(line).split(',')
            chart_data = list(yf.Ticker(ticker).history(interval="1d",period="1y")['Close'])           
            add = pd.DataFrame([[ticker,name,price,chart_data]],columns=("Ticker","Name","Current Price","History"))
            ptf = pd.concat([ptf,add])
    st.dataframe(ptf,use_container_width=1,hide_index=1,column_config={"History":st.column_config.LineChartColumn("History (5y)")})
    if st.button("Clear Data Base"):
        clear_database() 

def add_security(ticker,name,price):
    with open ("portfolio.csv", "a",newline='') as file:
        writer = csv.writer(file)
        writer.writerow([ticker,name,price])

def clear_database():
    f = open("portfolio.csv","w")
    f.truncate()

def fs_display(tick):
    request = yf.Ticker(tick)
    st.write(f"In {request.info['currency']}")
    a, b, c, d = st.columns(4)
    with a:
        try:
            st.metric("Revenue",f"{round(request.info['totalRevenue']/1000000000)} Bn",delta=request.info['revenueGrowth'])
        except:
            KeyError("")
    with b:
        try:
            st.metric("EBITDA",f"{round(request.info['ebitda']/1000000000)} Bn")
        except:
            KeyError("")
    with c:
        try:
            st.metric("FCF",f"{round(request.info['freeCashflow']/1000000000)} Bn")
        except:
            KeyError("")
    with d:
        try:
            st.metric("EV",f"{round(request.info['enterpriseValue']/1000000000)} Bn")
        except:
            KeyError("")
    
    try:
        df = pd.DataFrame(request.income_stmt)
        d = {"Revenue" : list(df.loc["Total Revenue"][0:3]),"EBITDA" : list(df.loc["EBITDA"][0:3]),"Profit":list(df.loc["Gross Profit"][0:3])}
        global_financials = pd.DataFrame(data = d,index=["2023","2022","2021"])
        st.line_chart(data=global_financials,use_container_width=1)
    except:
        KeyError(st.write("No data available"))

if __name__ == "__main__":
    main()


