# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 21:16:06 2021

@author: eschares
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import altair as alt


#st.title('Unsub Extender')
st.image('unsub_extender2.png')

file = st.selectbox('Choose file to analyze', ["Unsub_Elsevier_2021_cancellations.csv", "Unsub_test.csv"])

#uploaded_file = st.sidebar.file_uploader('Upload new .csv file:', type='csv')
#if uploaded_file is not None:
#    file = uploaded_file

df = pd.read_csv(file)
#st.write('Analyzing file "' + str(file) + '"')
#Process the data
#change column usage name to weighted usage

#st.write("Here's an attempt to make looking at the Unsub data easier:")

#with st.beta_expander("FAQ"):
#    st.write('''
#             by Eric Schares
#             
#             st.href(https://github.com/eschares/unsub_extender/blob/main/README.md)
#             ''')


my_slot1 = st.empty()   #save this spot to fill in later for how many rows get selected


# Sliders and filter
st.sidebar.markdown('**[About unsub extender](https://github.com/eschares/unsub_extender/blob/main/README.md)**')
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
weighted_vs_cost = alt.Chart(df[filt], title='Weighted Usage vs. Cost').mark_circle(size=75, opacity=0.5).encode(
    x='subscription_cost:Q',
    y=alt.Y('weighted usage:Q', scale=alt.Scale(type='log'), title='Weighted Usage (dl + cit + auth'),
    color=alt.Color('subscribed:N', scale=alt.Scale(domain=domain, range=range_)),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
    ).interactive().properties(height=500)
st.altair_chart(weighted_vs_cost, use_container_width=True)


col1, col2 = st.beta_columns(2)
#Altair scatter plot
#cit vs dl
cit_vs_dl = alt.Chart(df[filt], title='Citations vs. Downloads').mark_circle(size=75, opacity=0.5).encode(
    x='downloads:Q',
    y='citations:Q',
    color=alt.Color('subscribed:N', legend=None, scale=alt.Scale(domain=domain, range=range_)),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
    ).interactive()

#Altair scatter plot
#auth vs dl
auth_vs_dl = alt.Chart(df[filt], title='Authorships vs. Downloads').mark_circle(size=75, opacity=0.5).encode(
    x='downloads:Q',
    y='authorships:Q',
    color=alt.Color('subscribed:N', scale=alt.Scale(domain=domain, range=range_)),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
    ).interactive()


with col1:
    st.altair_chart(cit_vs_dl)#, use_container_width=True)
with col2:
    st.altair_chart(auth_vs_dl)#, use_container_width=True)

#Altair scatter plot
#auth vs cit, colord by subscribed
auth_vs_cit = alt.Chart(df[filt], title='Authorships vs. Citations').mark_circle(size=75, opacity=0.5).encode(
    x='citations:Q',
    y='authorships:Q',
    color=alt.Color('subscribed:N', scale=alt.Scale(domain=domain, range=range_)),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
    ).interactive()
st.altair_chart(auth_vs_cit, use_container_width=True)

#cit vs dl, by cpu_rank 5 buckets, colred by subscribed
#NOT DONE
cit_vs_dl_by_cpurank = alt.Chart(df[filt], title='====NOT DONE, WILL HAVE SELECTOR BY CPU_RANK BUCKETS====').mark_circle(size=75, opacity=0.5).encode(
    x='downloads:Q',
    y='citations:Q',
    color=alt.Color('subscribed:N', scale=alt.Scale(domain=domain, range=range_)),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
    ).interactive()
st.altair_chart(cit_vs_dl_by_cpurank, use_container_width=True)


#cpu_Rank y vs. subject, colored by subscribed
#what Altair calls a "stripplot"
cpurank_vs_subject = alt.Chart(df[filt], title='CPU_Rank by Subject', width=40).mark_circle(size=40, opacity=0.5).encode(
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
st.altair_chart(cpurank_vs_subject)#, use_container_width=True)


components.html(
'''
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2Z0VMP44J0"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-2Z0VMP44J0');
</script>
'''
)


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



