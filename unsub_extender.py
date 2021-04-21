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


st.image('unsub_extender2.png')

file = st.selectbox('Choose file to analyze', ["Unsub_Elsevier_2021_cancellations.csv", "test2.csv"])

#uploaded_file = st.sidebar.file_uploader('Upload new .csv file:', type='csv')
#if uploaded_file is not None:
#    file = uploaded_file

df = pd.read_csv(file)  #Process the data
#change column name 'usage' to 'weighted usage', how we refer to it interally since it contains DL + xCit + yAuth
if 'usage' in df.columns:
    df.rename(columns = {'usage': 'weighted usage'}, inplace=True)

#force 'subscribed' column to be a string, not Bool and all uppercase
df['subscribed'] = df['subscribed'].astype(str)
df['subscribed'] = df['subscribed'].str.upper()


my_slot1 = st.empty()   #save this spot to fill in later for how many rows get selected

# Sliders and filter
st.sidebar.markdown('**[About unsub extender](https://github.com/eschares/unsub_extender/blob/main/README.md)**')
price_slider = st.sidebar.slider('Price ($) between:', min_value=0, max_value=int(max(df['subscription_cost'])), value=(0,int(max(df['subscription_cost']))))
cpu_slider = st.sidebar.slider('Cost per Use Rank between:', min_value=0, max_value=int(max(df['cpu_rank'])), value=(0,int(max(df['cpu_rank']))))
downloads_slider = st.sidebar.slider('Downloads between:', min_value=0, max_value=int(max(df['downloads'])), value=(0,int(max(df['downloads']))))
citations_slider = st.sidebar.slider('Citations between:', min_value=0.0, max_value=max(df['citations']), value=(0.0,max(df['citations'])))
authorships_slider = st.sidebar.slider('Authorships between:', min_value=0.0, max_value=max(df['authorships']), value=(0.0,max(df['authorships'])))
weighted_usage_slider = st.sidebar.slider('Weighted usage (DL + x*Cit + y*Auth) between:', min_value=0, max_value=int(max(df['weighted usage'])), value=(0,int(max(df['weighted usage']))))
OA_percent_slider = st.sidebar.slider('OA % between:', min_value=0, max_value=int(max(df['free_instant_usage_percent'])), value=(0,int(max(df['free_instant_usage_percent']))))


filt = ( (df['free_instant_usage_percent'] >= OA_percent_slider[0]) & (df['free_instant_usage_percent'] <= OA_percent_slider[1]) &
        (df['downloads'] >= downloads_slider[0]) & (df['downloads'] <= downloads_slider[1]) &
        (df['citations'] >= citations_slider[0]) & (df['citations'] <= citations_slider[1]) &
        (df['subscription_cost'] >= price_slider[0]) & (df['subscription_cost'] <= price_slider[1]) &
        (df['authorships'] >= authorships_slider[0]) & (df['authorships'] <= authorships_slider[1]) &
        (df['cpu_rank'] >= cpu_slider[0]) & (df['cpu_rank'] <= cpu_slider[1]) &
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


#set up the color maps on 'subscribed'
subscribed_colorscale = alt.Scale(domain = ['TRUE', 'FALSE', 'MAYBE', ' '],
                                  range = ['blue', 'red', 'green', 'gray'])
# domain = ['TRUE', 'FALSE', 'MAYBE', ' ']
# range_ = ['blue', 'red', 'green', 'gray']

#weighted usage in log by cost (x), colored by subscribed
#adding clickable legend to highlight subscribed categories
selection1 = alt.selection_multi(fields=['subscribed'], bind='legend')
weighted_vs_cost = alt.Chart(df[filt], title='Weighted Usage vs. Cost by Subscribed status, clickable legend').mark_circle(size=75, opacity=0.5).encode(
    x='subscription_cost:Q',
    y=alt.Y('weighted usage:Q', scale=alt.Scale(type='log'), title='Weighted Usage (DL + Cit + Auth)'),
    color=alt.condition(selection1, alt.Color('subscribed:N', scale=subscribed_colorscale), alt.value('lightgray')),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'cpu_rank', 'subscribed'],
    ).interactive().properties(height=500).add_selection(selection1)
st.altair_chart(weighted_vs_cost, use_container_width=True)


#same chart as above but now colored by cpu_rank, and would really like buckets somehow
selection2 = alt.selection_multi(fields=['cpu_rank'], bind='legend')
weighted_vs_cost2 = alt.Chart(df[filt], title='Weighted Usage vs. Cost by CPU_Rank, clickable legend').mark_circle(size=75, opacity=0.5).encode(
    x='subscription_cost:Q',
    y=alt.Y('weighted usage:Q', scale=alt.Scale(type='log'), title='Weighted Usage (DL + Cit + Auth)'),
    color=alt.condition(selection2, alt.Color('cpu_rank:Q', scale=alt.Scale(scheme='viridis')), alt.value('lightgray')
        #,legend = alt.Legend(type='symbol')                
                        ),   #selection, if selected, if NOT selected
    
    #color=alt.Color('cpu_rank:Q',scale=alt.Scale(scheme='category20b')),
    #opacity=alt.condition(selection2, alt.value(1), alt.value(0.2)),
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'cpu_rank', 'subscribed'],
    ).interactive().properties(height=500).add_selection(selection2)
st.altair_chart(weighted_vs_cost2, use_container_width=True)



#click the bar chart to filter the scatter plot
click = alt.selection_multi(encodings=['color'])
scatter = alt.Chart(df[filt], title="Citations vs. Downloads, with clickable bar graph linked underneath").mark_point().encode(
    x='downloads',
    y='citations',
    color='subscribed'
).transform_filter(click).interactive()

hist = alt.Chart(df[filt]).mark_bar().encode(
    x='count()',
    y='subscribed',
    color = alt.condition(click, alt.Color('subscribed:N', scale=subscribed_colorscale), alt.value('lightgray'))
).add_selection(click)

scatter & hist

#scatter matrix
scatter_selection = alt.selection_multi(fields=['subscribed'], bind='legend')

eric = alt.Chart(df).mark_circle().encode(
    alt.X(alt.repeat("column"), type='quantitative'),
    alt.Y(alt.repeat("row"), type='quantitative'),
    #color=alt.Color('subscribed:N', scale=subscribed_colorscale)
    color=alt.condition(scatter_selection, alt.Color('subscribed:N', scale=subscribed_colorscale), alt.value('lightgray')),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'cpu_rank', 'subscribed']    
).properties(
    width=350,
    height=250
).repeat(
    row=['weighted usage'],#, 'downloads', 'citations', 'authorships'],
    column=['downloads', 'citations', 'authorships']
).interactive().add_selection(scatter_selection)

eric




#cit vs dl
selection = alt.selection_interval()
cit_vs_dl = alt.Chart(df[filt], title='Citations vs. Downloads, linked selection').mark_circle(size=75, opacity=0.5).encode(
    x='downloads:Q',
    y='citations:Q',
    color=alt.condition(selection, alt.Color('subscribed:N', legend=None, scale=subscribed_colorscale),
                        alt.value('gray')),   #alt.condition takes selection object, values for points inside selection, value for points OUTSIDE selection
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
    ).add_selection(selection)#.interactive()

#Altair scatter plot
#auth vs dl
auth_vs_dl = alt.Chart(df[filt], title='Authorships vs. Downloads').mark_circle(size=75, opacity=0.5).encode(
    x='downloads:Q',
    y='authorships:Q',
    color=alt.Color('subscribed:N', scale=subscribed_colorscale),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
    ).interactive().add_selection(selection)

cit_vs_dl | cit_vs_dl.encode(y='authorships')






#Altair scatter plot
#auth vs cit, colord by subscribed
auth_vs_cit = alt.Chart(df[filt], title='Authorships vs. Citations').mark_circle(size=75, opacity=0.5).encode(
    x='citations:Q',
    y='authorships:Q',
    color=alt.Color('subscribed:N', scale=subscribed_colorscale),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
    ).interactive()
st.altair_chart(auth_vs_cit, use_container_width=True)

#cit vs dl, by cpu_rank 5 buckets, colred by subscribed
#NOT DONE
#break it into 5 or 6 chunks based on number of rows
#seemed to break everything??
#into_5 = int(df.shape[0]/5)

# #cpu_bucket_selector = st.slider('Filter by CPU_Ranks', 1, df.shape[0], 1, into_5)
# cit_vs_dl_by_cpurank = alt.Chart(df[filt], title='====NOT DONE, WILL HAVE SELECTOR BY CPU_RANK BUCKETS====').mark_circle(size=75, opacity=0.5).encode(
#     x='downloads:Q',
#     y='citations:Q',
#     color=alt.Color('subscribed:N', scale=subscribed_colorscale),   #Nominal data type
#     tooltip=['title','downloads','citations','authorships','weighted usage','subscription_cost', 'subscribed'],
#     ).interactive()
# st.altair_chart(cit_vs_dl_by_cpurank, use_container_width=True)


#cpu_Rank y vs. subject, colored by subscribed
#what Altair calls a "stripplot"
cpurank_vs_subject = alt.Chart(df[filt], title='CPU_Rank by Subject ===NOT DONE===', width=40).mark_circle(size=40, opacity=0.5).encode(
    x=alt.X('subject:N', title=None, #axis=alt.Axis(values=[0], ticks=True, grid=False, labels=False), scale=alt.Scale(),
            ),
    y=alt.Y('cpu_rank:Q'),
    color=alt.Color('subscribed:N', scale=subscribed_colorscale),   #Nominal data type
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



