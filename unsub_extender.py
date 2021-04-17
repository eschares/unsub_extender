# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 21:16:06 2021

@author: eschares
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt


#st.title('Unsub Extender')
st.image('unsub_extender.png')

file = "Unsub_Elsevier_2021_cancellations.csv"
uploaded_file = st.sidebar.file_uploader('Upload new .csv file:', type='csv')
if uploaded_file is not None:
    file = uploaded_file

df = pd.read_csv(file)
st.write('Analyzing file "' + str(file) + '"')
#st.write("Here's an attempt to make looking at the Unsub data easier:")

with st.beta_expander("FAQ"):
    st.write('''
             What is this? What do I need? How does it work?
             
             <href a=unsub.org>Unsub</href> is a collection analysis tool that helps libraries analyze their journal subscriptions.
             
             
             Step 1: Get an Unsub report and choose export file to .csv
             ''')


my_slot1 = st.empty()   #save this spot to fill in later for how many rows get selected


# Sliders and filter
OA_percent_slider = st.sidebar.slider('OA % between:', min_value=0, max_value=max(df['free_instant_usage_percent']), value=(0,max(df['free_instant_usage_percent'])))
downloads_slider = st.sidebar.slider('Downloads between:', min_value=0, max_value=max(df['downloads']), value=(0,max(df['downloads'])))
citations_slider = st.sidebar.slider('Citations between:', min_value=0.0, max_value=max(df['citations']), value=(0.0,max(df['citations'])))
price_slider = st.sidebar.slider('Price ($) between:', min_value=0, max_value=max(df['subscription_cost']), value=(0,max(df['subscription_cost'])))

filt = ( (df['free_instant_usage_percent'] >= OA_percent_slider[0]) & (df['free_instant_usage_percent'] <= OA_percent_slider[1]) &
        (df['downloads'] >= downloads_slider[0]) & (df['downloads'] <= downloads_slider[1]) &
        (df['citations'] >= citations_slider[0]) & (df['citations'] <= citations_slider[1]) &
        (df['subscription_cost'] >= price_slider[0]) & (df['subscription_cost'] <= price_slider[1])
        )   


if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df[filt])

#Report the summary stats of what you selected
selected_jnls = str(df[filt].shape[0])
total_jnls = str(df.shape[0])
cost_sum = df[filt]['subscription_cost'].sum()  #cost of selected journals
currency_string = "${:,.0f}".format(cost_sum)   #format with $, commas, and no decimal points
my_slot1.subheader(selected_jnls + ' rows selected out of ' + total_jnls + ' rows, costing ' + currency_string)


#Altair scatter plot
dl_vs_cit = alt.Chart(df[filt]).mark_circle(size=75, opacity=0.5).encode(
    x='downloads:Q',
    y='citations:Q',
    color='subscribed:N',
    tooltip=['title','downloads','citations','authorships','subscription_cost'],
    ).interactive()
st.altair_chart(dl_vs_cit, use_container_width=True)

#Altair scatter plot
dl_vs_auth = alt.Chart(df[filt]).mark_circle(size=75, opacity=0.5).encode(
    x='downloads',
    y='authorships',
    color='subscribed:N',   #Nominal data type
    tooltip=['title','downloads','citations','authorships','subscription_cost'],
    ).interactive()
st.altair_chart(dl_vs_auth, use_container_width=True)











if (0):
    #Altair scatter plot with selection
    brush = alt.selection(type='interval')
    points = alt.Chart(df).mark_point().encode(
        x='downloads',
        y='citations',
        color=alt.condition(brush, 'Cylinders:O', alt.value('grey'))
    ).add_selection(brush)
    points
    
    ranked_text = alt.Chart(df).mark_text().encode(
        y=alt.Y('row_number:O', axis=None)
    ).transform_window(
        row_number='row_number()'
    ).transform_filter(
        brush
    ).transform_window(
        rank='rank(row_number)'
    ).transform_filter(
        alt.datum.rank<20
    )
    
    # Data Tables
    horsepower = ranked_text.encode(text='downloads:N').properties(title='Horsepower')
    mpg = ranked_text.encode(text='citations:N').properties(title='MPG')
    origin = ranked_text.encode(text='authorships:N').properties(title='Origin')
    text = alt.hconcat(horsepower, mpg, origin) # Combine data tables
    
    alt.hconcat(
        points,
        text
    ).resolve_legend(
        color="independent"
    )



