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
st.image('unsub_extender2.png')

file = "Unsub_Elsevier_2021_cancellations.csv"
#uploaded_file = st.sidebar.file_uploader('Upload new .csv file:', type='csv')
#if uploaded_file is not None:
#    file = uploaded_file

df = pd.read_csv(file)
st.write('Analyzing file "' + str(file) + '"')
#st.write("Here's an attempt to make looking at the Unsub data easier:")

with st.beta_expander("FAQ"):
    st.write('''
             What is this? What do I need? How does it work?
             
             Unsub is a tool that helps libraries analyze their journal subscriptions.
             
             Step 1: Get an Unsub report and choose export file to .csv
             ''')


my_slot1 = st.empty()   #save this spot to fill in later for how many rows get selected


# Sliders and filter
price_slider = st.sidebar.slider('Price ($) between:', min_value=0, max_value=max(df['subscription_cost']), value=(0,max(df['subscription_cost'])))
downloads_slider = st.sidebar.slider('Downloads between:', min_value=0, max_value=max(df['downloads']), value=(0,max(df['downloads'])))
citations_slider = st.sidebar.slider('Citations between:', min_value=0.0, max_value=max(df['citations']), value=(0.0,max(df['citations'])))
authorships_slider = st.sidebar.slider('Authorships between:', min_value=0.0, max_value=max(df['authorships']), value=(0.0,max(df['authorships'])))
weighted_usage_slider = st.sidebar.slider('Weighted usage (DL + x*Cit + y*Auth) between:', min_value=0, max_value=max(df['weighted usage']), value=(0,max(df['weighted usage'])))
OA_percent_slider = st.sidebar.slider('OA % between:', min_value=0, max_value=max(df['free_instant_usage_percent']), value=(0,max(df['free_instant_usage_percent'])))


filt = ( (df['free_instant_usage_percent'] >= OA_percent_slider[0]) & (df['free_instant_usage_percent'] <= OA_percent_slider[1]) &
        (df['downloads'] >= downloads_slider[0]) & (df['downloads'] <= downloads_slider[1]) &
        (df['citations'] >= citations_slider[0]) & (df['citations'] <= citations_slider[1]) &
        (df['subscription_cost'] >= price_slider[0]) & (df['subscription_cost'] <= price_slider[1]) &
        (df['authorships'] >= authorships_slider[0]) & (df['authorships'] <= authorships_slider[1]) &
        (df['weighted usage'] >= weighted_usage_slider[0]) & (df['weighted usage'] <= weighted_usage_slider[1])
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


#set up the color maps
domain = ['TRUE', 'FALSE', 'MAYBE', ' ']
range_ = ['blue', 'red', 'green', 'gray']

#weighted usage in log by cost (x), colored by subscribed
weighted_vs_cost = alt.Chart(df[filt]).mark_circle(size=75, opacity=0.5).encode(
    x='subscription_cost:Q',
    y=alt.Y('weighted usage:Q', scale=alt.Scale(type='log'), title='Weighted Usage (dl + cit + auth'),
    color=alt.Color('subscribed:N', scale=alt.Scale(domain=domain, range=range_)),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
    ).interactive()
st.altair_chart(weighted_vs_cost, use_container_width=True)

#Altair scatter plot
#cit vs dl
cit_vs_dl = alt.Chart(df[filt]).mark_circle(size=75, opacity=0.5).encode(
    x='downloads:Q',
    y='citations:Q',
    color=alt.Color('subscribed:N', scale=alt.Scale(domain=domain, range=range_)),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
    ).interactive()
st.altair_chart(cit_vs_dl, use_container_width=True)

#Altair scatter plot
#auth vs dl
auth_vs_dl = alt.Chart(df[filt]).mark_circle(size=75, opacity=0.5).encode(
    x='downloads',
    y='authorships',
    color=alt.Color('subscribed:N', scale=alt.Scale(domain=domain, range=range_)),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
    ).interactive()
st.altair_chart(auth_vs_dl, use_container_width=True)

#Altair scatter plot
#auth vs cit, colord by subscribed
auth_vs_cit = alt.Chart(df[filt]).mark_circle(size=75, opacity=0.5).encode(
    x='citations:Q',
    y='authorships:Q',
    color=alt.Color('subscribed:N', scale=alt.Scale(domain=domain, range=range_)),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
    ).interactive()
st.altair_chart(auth_vs_cit, use_container_width=True)

#cit vs dl, by cpu_rank 5 buckets, colred by subscribed
#NOT DONE
cit_vs_dl_by_cpurank = alt.Chart(df[filt]).mark_circle(size=75, opacity=0.5).encode(
    x='downloads:Q',
    y='citations:Q',
    color=alt.Color('subscribed:N', scale=alt.Scale(domain=domain, range=range_)),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
    ).interactive()
st.altair_chart(cit_vs_dl_by_cpurank, use_container_width=True)


#cpu_Rank y vs. subject, colored by subscribed
#what Altair calls a "stripplot"
cpurank_vs_subject = alt.Chart(df[filt], width=40).mark_circle(size=40, opacity=0.5).encode(
    x=alt.X('subject:N', title=None, axis=alt.Axis(values=[0], ticks=True, grid=False, labels=False), scale=alt.Scale(),
            ),
    y=alt.Y('cpu_rank:Q'),
    color=alt.Color('subscribed:N', scale=alt.Scale(domain=domain, range=range_)),   #Nominal data type
    column=alt.Column(
        'subscribed:N',
        header=alt.Header(
            labelAngle=-90,
            titleOrient='top',
            labelOrient='bottom',
            labelAlign='right',
            labelPadding=3,
            ),
        ),
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
    ).interactive()
st.altair_chart(cpurank_vs_subject, use_container_width=True)









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



