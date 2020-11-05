import numpy as np
import scipy.stats as si
import sympy as sy
import matplotlib as mpl
import random
import pandas as pd
import streamlit as st
from sympy.stats import Normal, cdf
from sympy import init_printing
from matplotlib import pyplot as plt
import seaborn as sns
init_printing()

# include values in millions

#Financial Statement Variables
by = 2019
byNI = 31534
pyBV = 177628
byBV = 201442
byDiv = 0

#CAPM Variables
vRf = 0.0085
vMRP = 0.058
Bta = 1.11
vMR = vRf + vMRP
Kc = (vRf * (1 - Bta)) + (Bta*vMR)

pytrt = byDiv / byNI #payout ratio defined as Dividend (base year) / NI (base year), assume will contineu for seven years

def fun(currentyear, finalyear, BVpy, pytrt, vROE):
  Book_Values = []
  BVcy = BVpy
  for i in range(int(currentyear), int(finalyear)):
    BVcy = BVcy*(1+((1-pytrt)*vROE))
    Book_Values.append(float(BVcy))
  return Book_Values
 

def some(voxvalues, Kc):
    temp = []
    n = 1
    for i in voxvalues:
        temp.append(i/((1+Kc)**(n)))
        n = n+1
    return temp

def ValuationStatement(currentprice, intrinsicprice, ValueComparison):
    if currentprice -  intrinsicprice >= 0:
        statement = "Shares overvalued by {}".format(ValueComparison)
    elif currentprice - intrinsicprice <= 0:
        statement = "Shares undervalued by {}".format(ValueComparison)
    
    return statement

def SurplusModel(vROE_input,vROE):
    Book_Values = fun(by + 1, by + vROE_input - 1, byBV, pytrt, vROE)

    Book_Values.insert(0,byBV)

    vOX_Values = [i * (vROE - Kc) for i in Book_Values]

    vPA = byBV + sum(some(vOX_Values, Kc))

    numshares = 333630000 #float(input("Number of Shares Outstanding: "))
    #sample data: 81,143,767

    Share_Value = vPA / (numshares / 1000000)
    
    return Share_Value


def crude_monte_carlo(num_samples):

    sum_of_samples = 0

    Value_var = []
    roe_len_Var = []
    roe_var = []

    for i in range(num_samples):
        x1 = random.uniform(z1,z2) # range of vROE len 3,20
        x2 = random.uniform(n1,n2) # range of vROE, 0.08,0.23
        
        sum_of_samples += SurplusModel(x1,x2)
        
        Value_var.append(SurplusModel(x1,x2))
        roe_len_Var.append(x1)
        roe_var.append(x2)

    print(float(sum_of_samples/num_samples))

    return (Value_var,roe_len_Var,roe_var) #float(sum_of_samples/num_samples)

#Streamlit Section for WebApp
st.title("Monte Carlo: Share Price of Google")

sim1 = st.slider('How many simulations would you like to run?',100,100000,1000)

st.subheader("Variable #1: Length of expected earnings surprise (RoE > cost of capital).")
z1 = st.slider('Lower bound of expected earnings surprise.',1,100,3)
z2 = st.slider('Upper bound of expected earnings surprise.',1,100,20)

st.subheader("Variable #2: Expected RoE over the period.")
n1 = st.slider('Lower bound of expected RoE.',0.01,0.50,0.08)
n2 = st.slider('Upper bound of expected RoE.',0.01,0.50,0.23)

Monte_Distribution = crude_monte_carlo(sim1)

value_list = Monte_Distribution[0]
roe_len_list = Monte_Distribution[1]
roe_list = Monte_Distribution[2]

monte_df = pd.DataFrame({'Valuation':value_list, 'Years of RoE > Kc':roe_len_list,"RoE":roe_list})

avrg_value = monte_df['Valuation'].sum() / len(monte_df.index)

st.subheader("Simulated Mean Share Price")
st.write('Average value of Google Share Price simulated {} times'.format(len(monte_df.index)))
st.write(avrg_value)

# Graphs & Density Distribution
monte_df[['Valuation']].plot(kind='density') # or pd.Series()
plt.title('Google Share Price Distribution')
st.pyplot()

ax = sns.histplot(value_list)
plt.title('Google Share Price Distribution')
ax.set(xlabel='Share Valuation', ylabel='Frequency')
st.pyplot()

st.subheader("All Simulations of Share Price")
st.table(monte_df)
