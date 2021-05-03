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
#from pandas.api.types import CategoricalDtype
#import streamlit_analytics

#streamlit_analytics.start_tracking()

#st.set_page_config(layout="wide")
st.image('unsub_extender2.png')
#st.sidebar.write("*Version 1.0*")
st.sidebar.markdown('**[About unsub extender on GitHub](https://github.com/eschares/unsub_extender/blob/main/README.md)**')


with st.beta_expander("How to use and requirements:"):
    st.write("This tool takes an **unsub** data export file .csv and automates the creation of various plots and visualizations.")
    st.write("Upload your .csv file using the button in the left sidebar, or explore the example dataset and ready-made plots to see what is available.")
    st.markdown('**More information about unsub extender [is available on the project GitHub page](https://github.com/eschares/unsub_extender/blob/main/README.md)**')

#Initialize with a hardcoded dataset
file = filename = "Unsub_export_example.csv"

uploaded_file = st.sidebar.file_uploader('Upload new .csv file to analyze:', type='csv')
if uploaded_file is not None:
    file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type,"FileSize":uploaded_file.size}
    #st.write(file_details)
    
    file = uploaded_file
    filename = uploaded_file.name


st.header('Analyzing file "' + filename + '"')


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def load_data(file):
    st.write("I ran!")
    return pd.read_csv(file, sep=',', encoding='utf-8')  #Process the data in cached way to speed up processing

df = load_data(file)

#force 'subscribed' column to be a string, not Bool and all uppercase
df['subscribed'] = df['subscribed'].astype(str)
df['subscribed'] = df['subscribed'].str.upper()

#process data to calculate IF%
total_usage = df['usage'].sum()
df['current_yr_usage'] = ((df['use_ill_percent'] + df['use_other_delayed_percent']) / 100) * df['usage']
df['IF%'] = (df['current_yr_usage'] / total_usage) * 100
df['cost_per_IF%'] = df['subscription_cost'] / df['IF%']


my_slot1 = st.empty()   #save this spot to fill in later for how many rows get selected with the filter

# Sliders and filter
price_slider = st.sidebar.slider('Price ($) between:', min_value=0, max_value=int(max(df['subscription_cost'])), value=(0,int(max(df['subscription_cost']))))
cpu_slider = st.sidebar.slider('Cost per Use Rank between:', min_value=0, max_value=int(max(df['cpu_rank'])), value=(0,int(max(df['cpu_rank']))))
downloads_slider = st.sidebar.slider('Downloads between:', min_value=0, max_value=int(max(df['downloads'])), value=(0,int(max(df['downloads']))))
citations_slider = st.sidebar.slider('Citations between:', min_value=0.0, max_value=max(df['citations']), value=(0.0,max(df['citations'])))
authorships_slider = st.sidebar.slider('Authorships between:', min_value=0.0, max_value=max(df['authorships']), value=(0.0,max(df['authorships'])))
weighted_usage_slider = st.sidebar.slider('Weighted usage (DL + x*Cit + y*Auth) between:', min_value=0, max_value=int(max(df['usage'])), value=(0,int(max(df['usage']))))
OA_percent_slider = st.sidebar.slider('OA % between:', min_value=0, max_value=int(max(df['free_instant_usage_percent'])), value=(0,int(max(df['free_instant_usage_percent']))))


filt = ( (df['free_instant_usage_percent'] >= OA_percent_slider[0]) & (df['free_instant_usage_percent'] <= OA_percent_slider[1]) &
        (df['downloads'] >= downloads_slider[0]) & (df['downloads'] <= downloads_slider[1]) &
        (df['citations'] >= citations_slider[0]) & (df['citations'] <= citations_slider[1]) &
        (df['subscription_cost'] >= price_slider[0]) & (df['subscription_cost'] <= price_slider[1]) &
        (df['authorships'] >= authorships_slider[0]) & (df['authorships'] <= authorships_slider[1]) &
        (df['cpu_rank'] >= cpu_slider[0]) & (df['cpu_rank'] <= cpu_slider[1]) &
        (df['usage'] >= weighted_usage_slider[0]) & (df['usage'] <= weighted_usage_slider[1])
        )


if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df[filt])
    
my_slot2 = st.empty()   #save this spot to fill in later with the summary table of counts and sum$ by Subscribed

#Report the summary stats of what you selected
selected_jnls = str(df[filt].shape[0])
total_jnls = str(df.shape[0])
cost_sum = df[filt]['subscription_cost'].sum()  #cost of selected journals
currency_string = "${:,.0f}".format(cost_sum)   #format with $, commas, and no decimal points
my_slot1.subheader(selected_jnls + ' rows selected out of ' + total_jnls + ' rows, costing a total of ' + currency_string)


#set up the color maps on 'subscribed'
subscribed_colorscale = alt.Scale(domain = ['TRUE', 'FALSE', 'MAYBE', ' '],
                                  range = ['blue', 'red', 'green', 'gray'])


with st.beta_expander("Modify the 'Subscribed' status of journal(s):"):
    selected_titles = st.multiselect('Journal Name (shown in order provided by the underlying datafile):', df[filt]['title'])
    #st.write(selected_titles)

    col1, col2 = st.beta_columns(2)

    radiovalue = col1.radio("'Subscribed' choices", ['TRUE', "FALSE", 'MAYBE', ' '])
    #write(radiovalue)

if col2.button('Commit change'):
    for title in selected_titles:
        title_filter = (df['title'] == title)
        df.loc[title_filter, 'subscribed'] = radiovalue

### Summary dataframe created to show count and sum$ by Subscribed status
summary_df = df[filt].groupby('subscribed')['subscription_cost'].agg(['count','sum'])
summary_df['sum'] = summary_df['sum'].apply(lambda x: "${0:,.0f}".format(x))
#now formatted as a string (f)
#leading dollar sign, add commas, round result to 0 decimal places
my_slot2.write(summary_df.sort_index(ascending=False))

########  Charts start here  ########

#blue histogram, but colored by subscribed
#filt_to_100 = df['cpu']<=100
unsub_hist = alt.Chart(df[filt].reset_index(), height=450, width=800).mark_bar().encode(
    alt.X('cpu:Q', bin=alt.Bin(maxbins=100), title="Cost per Use bins", axis=alt.Axis(format='$')),
    alt.Y('count()', axis=alt.Axis(grid=False)),
    alt.Detail('index'),
    tooltip=['title', 'cpu', 'subscription_cost', 'subscribed'],
    color=alt.Color('subscribed:N', scale=subscribed_colorscale)
    ).properties(
        title={
            "text": ["Unsub's Cost per Use Histogram, color coded by Subscribed status"],
            "subtitle": ["Graph supports pan, zoom, and live-updates from changes in filters on the left"],
            "color": "black",
            "subtitleColor": "gray"
        }
).interactive()
unsub_hist


#weighted usage in log by cost (x), colored by subscribed
#adding clickable legend to highlight subscribed categories
selection1 = alt.selection_multi(fields=['subscribed'], bind='legend')
weighted_vs_cost = alt.Chart(df[filt], title='Weighted Usage vs. Cost by Subscribed status, clickable legend').mark_circle(size=75, opacity=0.5).encode(
    alt.X('subscription_cost:Q', axis=alt.Axis(format='$,.2r')),
    alt.Y('usage:Q', scale=alt.Scale(type='log'), title='Weighted Usage (DL + Cit + Auth)'),
    color=alt.condition(selection1, alt.Color('subscribed:N', scale=subscribed_colorscale), alt.value('lightgray')),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'cpu_rank', 'subscribed'],
    ).interactive().properties(height=500).add_selection(selection1)
st.altair_chart(weighted_vs_cost, use_container_width=True)


#same chart as above but now colored by cpu_rank, and would really like buckets somehow
selection2 = alt.selection_multi(fields=['cpu_rank'], bind='legend')
weighted_vs_cost2 = alt.Chart(df[filt], title='Weighted Usage vs. Cost by CPU_Rank').mark_circle(size=75, opacity=0.5).encode(
    alt.X('subscription_cost:Q', axis=alt.Axis(format='$,.2r')),
    y=alt.Y('usage:Q', scale=alt.Scale(type='log'), title='Weighted Usage (DL + Cit + Auth)'),
    color=alt.condition(selection2, alt.Color('cpu_rank:Q', scale=alt.Scale(scheme='viridis')), alt.value('lightgray')
        #,legend = alt.Legend(type='symbol')                
        ),   #selection, if selected, if NOT selected
    #opacity=alt.condition(selection2, alt.value(1), alt.value(0.2)),
    tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'cpu_rank', 'subscribed'],
    ).interactive().properties(height=500).add_selection(selection2)
st.altair_chart(weighted_vs_cost2, use_container_width=True)


st.header("Look at Instant Fill rates")
# Instant Fill % graphs
st.subheader('Calculate and look at the Instant Fill % for each journal')
IF = alt.Chart(df[filt], height=400, width=500).mark_circle().encode(
    alt.X('IF%', title='Instant Fill %'),
    alt.Y('subscription_cost', title="Journal Cost", axis=alt.Axis(format='$,.2r')),    #grouped thousands with two significant digits
    tooltip=(['title','subscription_cost','IF%']),
    color=alt.Color('subscribed:N', scale=subscribed_colorscale)
    ).properties(
        title={
            "text": ['Instant Fill % vs. Journal Subscription Cost'],
            "subtitle": ["Which journals increase Instant Fill % the most", "(moving to the right), and what do they each cost?"],
            "color": "black",
            "subtitleColor": "gray"
        }
        ).interactive()
IF

IF2 = alt.Chart(df[filt], height=400, width=500).mark_circle().encode(
    alt.X('IF%', title="Instant Fill %"),
    alt.Y('cost_per_IF%', scale=alt.Scale(type='log'), title="log ( Price per IF% )", axis=alt.Axis(format='$,.2r')),
    tooltip=(['title','subscription_cost','IF%','cost_per_IF%']),
    color=alt.Color('subscribed:N', scale=subscribed_colorscale)
    ).properties(
        title={
            "text": ['Instant Fill % vs. Price per IF%'],
            "subtitle": ["Normalized by price, which journals are the best way", "to increase Instant Fill % (tending to lower right corner)?","Note: Y-axis shown in log to stretch and increase visibility"],
            "color": "black",
            "subtitleColor": "gray"
        }
).interactive()
IF2


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
    tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'cpu_rank', 'subscribed']    
).properties(
    width=350,
    height=250
).repeat(
    row=['usage'],#, 'downloads', 'citations', 'authorships'],
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
    tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'subscribed'],
    ).add_selection(selection)#.interactive()

#Altair scatter plot
#auth vs dl
auth_vs_dl = alt.Chart(df[filt], title='Authorships vs. Downloads').mark_circle(size=75, opacity=0.5).encode(
    x='downloads:Q',
    y='authorships:Q',
    color=alt.Color('subscribed:N', scale=subscribed_colorscale),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'subscribed'],
    ).interactive().add_selection(selection)

cit_vs_dl | cit_vs_dl.encode(y='authorships')






#Altair scatter plot
#auth vs cit, colord by subscribed
auth_vs_cit = alt.Chart(df[filt], title='Authorships vs. Citations').mark_circle(size=75, opacity=0.5).encode(
    x='citations:Q',
    y='authorships:Q',
    color=alt.Color('subscribed:N', scale=subscribed_colorscale),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'subscribed'],
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
#     tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'subscribed'],
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
    tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'subscribed'],
    ).interactive()
st.altair_chart(cpurank_vs_subject)#, use_container_width=True)

#html_string = "<h3>Hello there</h3>"
html_string = "<img src='https://www.google-analytics.com/collect?v=1&tid=G-2Z0VMP44J0&cid=555&aip=1&t=event&ec=email&ea=open&dp=%2Femail%2Fnewsletter&dt=My%20Newsletter'></img>"
st.markdown(html_string, unsafe_allow_html=True)


html_string2 = "<img src='https://www.google-analytics.com/collect?v=1&tid=UA-195227159-1&cid=555&aip=1&t=event&ec=email&ea=open&dp=%2Femail%2Fnewsletter&dt=My%20Newsletter'></img>"
st.markdown(html_string2, unsafe_allow_html=True)

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
    
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-195227159-1"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'UA-195227159-1');
</script>
'''
)

#streamlit_analytics.stop_tracking()


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



