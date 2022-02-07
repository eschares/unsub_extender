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
import os
import re
from datetime import datetime

st.set_page_config(page_title='Unsub Extender', page_icon="scissors.jpg", layout='centered', initial_sidebar_state="expanded")

#st.set_page_config(layout="wide")
st.image('unsub_extender2.png')


with st.expander("How to use:"):
    st.write("This site takes an Unsub data export .csv file and automates the creation of useful plots and interactive visualizations so you can make more informed collection decisions.")
    st.write('**Upload your specific Unsub .csv** export file using the "Browse files" button in the left sidebar, or explore the pre-loaded example dataset and plots to see what is available.')
    st.write("Graphs are interactive and support zoom, click-and-drag, and hover.  Double click a graph to reset back to the default view.")
    st.write("Filter on various criteria using the sliders on the left to narrow in on areas of interest, hover over data points to learn more about a specific journal, then use the dropdown to actually change a journal's *Subscribed* status and watch the graphs update. (Note: you may have to occasionally hit *'r'* to force a reload if you notice it's not loading right away)")
    st.markdown('This project is written in Python and deployed as a web app using the library Streamlit. **More information about unsub extender, its requirements, and the source code is available on the [project GitHub page](https://github.com/eschares/unsub_extender)**')

#==== Load Data ====
#Initialize with a hardcoded dataset
file = filename = "Unsub_export_example.csv"

st.sidebar.subheader('Upload your Unsub export file')
uploaded_file = st.sidebar.file_uploader("Must be a .csv file", type='csv')
if uploaded_file is not None:
    file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type,"FileSize":uploaded_file.size}
    #st.write(file_details)
    
    file = uploaded_file
    filename = uploaded_file.name

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def load_data(file):
    st.write("New file loaded")
    return pd.read_csv(file)#, sep=',', encoding='utf-8')  #Process the data in cached way to speed up processing

st.header('Analyzing file "' + filename + '"')

df = load_data(file)



#==== Pre-process data ====
#force 'subscribed' column to be a string, not Bool and all uppercase
df['subscribed'] = df['subscribed'].astype(str)
df['subscribed'] = df['subscribed'].str.upper()

#convert subject and era_subjects columns to strings, sometimes they are left blank and get coverted to 0/ints which screws everything up
if ('subject' in df.columns):
    df['subject'] = df['subject'].astype(str)
if ('era_subjects' in df.columns):
    df['era_subjects'] = df['era_subjects'].astype(str)

#handle cases where a '-' is in the cell, seems to happen in cpu and cpu_rank
df['cpu'] = pd.to_numeric(df['cpu'], errors='coerce')
df['cpu_rank'] = pd.to_numeric(df['cpu_rank'], errors='coerce')     #changes '-' to not a number
df = df.replace(np.nan, 0, regex=True)  #changes that to 0
df['cpu_rank'] = df['cpu_rank'].astype(int)
fix_filt = (df['cpu_rank']==0)
df.loc[fix_filt,'cpu_rank']= int(max(df['cpu_rank']))   #moves cpu_rank of 0 to max cpu_rank number

#move anything with weighted usage of 0 to 1 so log graphs work
df = df.replace({'usage':0}, 1)

#process data to calculate IF%
#check and don't redo if IF% column already exists - rerunning a file through UE
if not 'IF%' in df.columns:
    total_usage = df['usage'].sum()
    df['current_yr_usage'] = ((df['use_subscription_percent'] + df['use_ill_percent'] + df['use_other_delayed_percent']) / 100) * df['usage']  #assumes subscription comes in as 0 everywhere, set to FALSE
    df['IF%'] = (df['current_yr_usage'] / total_usage) * 100
    df['cost_per_IF%'] = df['subscription_cost'] / df['IF%']

st.sidebar.subheader("Change a journal's Subscribed status")
sidebar_modifier_slot = st.sidebar.empty()
my_slot1 = st.empty()   #save this spot to fill in later for how many rows get selected with the filter


# Sliders and filter
st.sidebar.subheader("**Filters** (arrow keys to fine-tune)")
price_slider = st.sidebar.slider('Price ($) between:', min_value=0, max_value=int(max(df['subscription_cost'])), value=(0,int(max(df['subscription_cost']))))
cpu_slider = st.sidebar.slider('Cost per Use Rank between:', min_value=int(min(df['cpu_rank'])), max_value=int(max(df['cpu_rank'])), value=(int(min(df['cpu_rank'])),int(max(df['cpu_rank']))), help='CPU Rank ranges from 1 to max number of journals in the dataset')
downloads_slider = st.sidebar.slider('Downloads between:', min_value=0, max_value=int(max(df['downloads'])), value=(0,int(max(df['downloads']))), help='Average per year over the next five years')
citations_slider = st.sidebar.slider('Citations between:', min_value=0.0, max_value=max(df['citations']), value=(0.0,max(df['citations'])), help='Average per year over the next five years')
authorships_slider = st.sidebar.slider('Authorships between:', min_value=0.0, max_value=max(df['authorships']), value=(0.0,max(df['authorships'])), help='Average per year over the next five years')
weighted_usage_slider = st.sidebar.slider('Weighted usage (DL + x*Cit + y*Auth) between:', min_value=0, max_value=int(max(df['usage'])), value=(0,int(max(df['usage']))), help='x Citation and y Authorship weights are set in the Unsub tool itself')
free_percent_slider = st.sidebar.slider('Free % (OA + backfile) between:', min_value=0, max_value=int(max(df['free_instant_usage_percent'])), value=(0,int(max(df['free_instant_usage_percent']))))
OA_percent_slider = st.sidebar.slider('OA % between:', min_value=0, max_value=int(max(df['use_oa_percent'])), value=(0,int(max(df['use_oa_percent']))))
subscribed_filter = st.sidebar.radio('Subscribed status:',['Show All', 'TRUE', 'FALSE', 'MAYBE', '(blank)'], help='Filter based on the current Subscribed status')
subscribed_filter_flag = 0
if subscribed_filter == "(blank)":
    subscribed_filter = " "
if subscribed_filter != 'Show All':
    subscribed_filter_flag = 1

#could also use between: (df['cpu_rank'].between(cpu_slider[0], cpu_slider[1]))
filt = ( (df['use_oa_percent'] >= OA_percent_slider[0]) & (df['use_oa_percent'] <= OA_percent_slider[1]) &
        (df['free_instant_usage_percent'] >= free_percent_slider[0]) & (df['free_instant_usage_percent'] <= free_percent_slider[1]) &
        (df['downloads'] >= downloads_slider[0]) & (df['downloads'] <= downloads_slider[1]) &
        (df['citations'] >= citations_slider[0]) & (df['citations'] <= citations_slider[1]) &
        (df['subscription_cost'] >= price_slider[0]) & (df['subscription_cost'] <= price_slider[1]+1) &     #subtle bug where most expensive journal doesn't show if price has cents b/c $100.10 is greater than int($100)
        (df['authorships'] >= authorships_slider[0]) & (df['authorships'] <= authorships_slider[1]) &
        (df['cpu_rank'] >= cpu_slider[0]) & (df['cpu_rank'] <= cpu_slider[1]) &
        (df['usage'] >= weighted_usage_slider[0]) & (df['usage'] <= weighted_usage_slider[1])
        )




# if st.checkbox('Show raw data'):
#     st.subheader('Raw data')
#     st.write(df[filt])
    
my_slot2 = st.empty()   #save this spot to fill in later with the summary table of counts and sum$ by Subscribed

#Report the number of journals the filter selected
selected_jnls = str(df[filt].shape[0])
total_jnls = str(df.shape[0])
cost_sum = df[filt]['subscription_cost'].sum()  #cost of selected journals
currency_string = "${:,.0f}".format(cost_sum)   #format with $, commas, and no decimal points
my_slot1.subheader(selected_jnls + ' rows selected out of ' + total_jnls + ' rows, costing a total of ' + currency_string)


#set up the color maps on 'subscribed'
subscribed_colorscale = alt.Scale(domain = ['TRUE', 'FALSE', 'MAYBE', ' '],
                                  range = ['blue', 'red', 'green', 'gray'])

subscribed_point_mapping = alt.Scale(domain=['TRUE', 'FALSE', 'MAYBE', ' '],
                                     range=["cross", "circle", "diamond", "triangle-up"]    #The scale property allow you to map a domain to a range, where the domain specifies input values, and the range specifies the visual properties to which the domain is mapped. If you want multiple domain values to map to the same range value, it can be done like this:
                                         )

# Function to remove a title from all four lists in preparation for adding back to one list
def clear_title_from_list(title):
    if title in st.session_state.to_true:
        st.session_state.to_true.remove(title)
        st.write('Removed ', title, "from st.to_true list")
    
    if title in st.session_state.to_false:
        st.session_state.to_false.remove(title)
        st.write('Removed ', title, "from st.to_false list")
        
    if title in st.session_state.to_maybe:
        st.session_state.to_maybe.remove(title)
        st.write('Removed ', title, "from st.to_maybe list")
        
    if title in st.session_state.to_blank:
        st.session_state.to_blank.remove(title)
        st.write('Removed ', title, "from st.to_blank list")

# Initialize session_state versions of to_true/false/maybe/blank lists
if 'to_true' not in st.session_state:
    st.session_state.to_true = []
if 'to_false' not in st.session_state:
    st.session_state.to_false = []
if 'to_maybe' not in st.session_state:
    st.session_state.to_maybe = []
if 'to_blank' not in st.session_state:
    st.session_state.to_blank = []


#Put Modifier down here after the filt definition so only those titles that meet the filt show up, but put into empty slot further up the sidebar for flow
with sidebar_modifier_slot:
    with st.expander("Expand to select:"):
        filtered_titles_df = df.loc[filt]['title']      #make a new df with only the valid titles
        #then give those valid titles as choices in the Modifier, was causing problems when trying to offer them through a filter, kept trying to use the index but wouldn't be there anymore
        selected_titles = st.multiselect('Journal Name:', pd.Series(filtered_titles_df.reset_index(drop=True)), help='Displayed in order provided by the underlying datafile')
        #st.write(selected_titles)
    
        col1, col2 = st.columns([2,1])
    
        with col1:
            radiovalue = st.radio("Change 'Subscribed' status to:", ['TRUE', 'MAYBE', 'FALSE', '(blank)'])
            if radiovalue == "(blank)":
                radiovalue = " "
                #write(radiovalue)
        with col2:
            st.write(" ")       #Move the Commit button down vertically
            st.write(" ")       #I'm sure there's a smarter way to do this, but oh well
            if st.button('Commit change!'):
                for title in selected_titles:
                    clear_title_from_list(title)  #remove title from all lists, so we only keep the most recent change
                                                    #note we are not clearing all 4 lists, just removing one title at a time

                if radiovalue == 'TRUE':
                    for title in selected_titles:
                        st.session_state.to_true.append(title)
                        
                if radiovalue == 'FALSE':
                    for title in selected_titles:
                        st.session_state.to_false.append(title)
                        
                if radiovalue == 'MAYBE':
                    for title in selected_titles:
                        st.session_state.to_maybe.append(title)
                        
                if radiovalue == " ":
                    for title in selected_titles:
                        st.session_state.to_blank.append(title)


# Actually do the changes in df; this runs every time the script runs but session_state lets me save the previous changes
for title in st.session_state.to_true:
    title_filter = (df['title'] == title)
    df.at[title_filter, 'subscribed'] = 'TRUE'

for title in st.session_state.to_false:
    title_filter = (df['title'] == title)
    df.at[title_filter, 'subscribed'] = 'FALSE'
    
for title in st.session_state.to_maybe:
    title_filter = (df['title'] == title)
    df.at[title_filter, 'subscribed'] = 'MAYBE'
    
for title in st.session_state.to_blank:
    title_filter = (df['title'] == title)
    df.at[title_filter, 'subscribed'] = ' '


if subscribed_filter_flag:      #add another filter part, have to do it this way so Subscribed=ALL works
    filt2 = (df['subscribed'] == subscribed_filter)
    subscribed_filter
    filt2
    filt = filt & filt2



if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df[filt])

### Summary dataframe created to show count and sum$ by Subscribed status
summary_df = df[filt].groupby('subscribed')['subscription_cost'].agg(['count','sum'])
summary_df['sum'] = summary_df['sum'].apply(lambda x: "${0:,.0f}".format(x))
#now formatted as a string (f)
#leading dollar sign, add commas, round result to 0 decimal places
my_slot2.write(summary_df.sort_index(ascending=False))  #display in order of TRUE, MAYBE, FALSE, blank




### Export the df with any changes the user made 
st.sidebar.subheader('Export spreadsheet with any changes')
sidebar_changessummary_slot = st.sidebar.empty()
with sidebar_changessummary_slot:
    with st.expander("Show the changes made"):
        if st.session_state.to_true:
            st.write("Titles you changed to TRUE ", st.session_state.to_true)
        if st.session_state.to_false:
            st.write("Titles you changed to FALSE ", st.session_state.to_false)
        if st.session_state.to_maybe:
            st.write("Titles you changed to MAYBE ", st.session_state.to_maybe)
        if st.session_state.to_blank:
            st.write("Titles you changed to (blank) ", st.session_state.to_blank)


##### Export the dataset with any changes made by user #####
@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv=convert_df(df)

date = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

st.sidebar.download_button(label="Click to download",
                      data=csv,
                      file_name='UnsubExtender_output_'+date+'.csv',
                      mime='text/csv')


########  Charts start here  ########
st.subheader('Start by looking at the overall usage')
#weighted usage in log by cost (x), colored by subscribed
#adding clickable legend to highlight subscribed categories
selection1 = alt.selection_multi(fields=['subscribed'], bind='legend')
weighted_vs_cost = alt.Chart(df[filt]).mark_point(size=75, opacity=0.5, filled=True).encode(
    alt.X('subscription_cost:Q', axis=alt.Axis(format='$,.2r'), scale=alt.Scale(clamp=True)),
    alt.Y('usage:Q', scale=alt.Scale(type='log'), title='Weighted Usage (DL + Cit + Auth)'),
    color=alt.condition(selection1, alt.Color('subscribed:N', scale=subscribed_colorscale), alt.value('lightgray')),   #Nominal data type
    shape=alt.Shape('subscribed:N', scale=subscribed_point_mapping),
    tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'use_oa_percent', 'free_instant_usage_percent', 'cpu', 'cpu_rank', 'subscribed'],
    ).interactive().properties(
        height=500,
        title={
            "text": ["Total Weighed Usage vs. Cost, color-coded by Subscribed status; clickable legend"],
            "subtitle": ["Graph supports pan, zoom, and live-updates from changes in filters on left sidebar", "Journals on the underside of this curve might be considered for cancellation"],
            "color": "black",
            "subtitleColor": "gray"
        }
        ).add_selection(selection1)
st.altair_chart(weighted_vs_cost, use_container_width=True)

#same chart as Weighted Use vs. cost but now colored by cpu_rank, and would really like buckets somehow
selection2 = alt.selection_multi(fields=['subscribed'], bind='legend')
weighted_vs_cost2 = alt.Chart(df[filt]).mark_point(size=75, opacity=0.5, filled=True).encode(
    alt.X('subscription_cost:Q', axis=alt.Axis(format='$,.2r'), scale=alt.Scale(clamp=True)),
    y=alt.Y('usage:Q', scale=alt.Scale(type='log'), title='Weighted Usage (DL + Cit + Auth)'),
    color=alt.condition(selection2, alt.Color('cpu_rank:Q', scale=alt.Scale(scheme='viridis', reverse=True)), alt.value('lightgray')),   #selection, if selected, if NOT selected,
    shape=alt.Shape(
        'subscribed:N',
        #sort=['TRUE', 'FALSE', 'MAYBE'],
        scale=subscribed_point_mapping
        ),      #circle, square, cross, diamond, triangle-up, triangle-down, triangle-right, triangle-left
    tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'cpu', 'cpu_rank', 'subscribed'],
    ).interactive().properties(
        height=500,
        title={
            "text": ['Total Weighted Usage vs. Cost, color coded by CPU_Rank gradient'],
            "subtitle": ["Same graph as above, but with different color coding", "High Cost-per-Use rank (least economical) journals show up in darker colors"],
            "color": "black",
            "subtitleColor": "gray"
        }
        ).add_selection(selection2)
st.altair_chart(weighted_vs_cost2, use_container_width=True)



st.subheader('Look into the authorships, citations, and downloads of each journal')
auth_hist = alt.Chart(df[filt].reset_index()).mark_bar(width=10).encode(
    alt.X('authorships:Q', title="Authorships (average per year over the next five years)"),
    alt.Y('count()', axis=alt.Axis(grid=False)),
    alt.Detail('index'),
    tooltip=['title', 'authorships', 'subscription_cost', 'subscribed'],
    color=alt.Color('subscribed:N', scale=subscribed_colorscale)
    ).interactive().properties(
        height=400,
        title={
            "text": ["Authorships Distribution"],
            "subtitle": ["What do the range of Authorships look like?", "Use this graph to help set the Authorships slider filter and narrow down titles of interest"],
            "color": "black",
            "subtitleColor": "gray"
        }
        )
st.altair_chart(auth_hist, use_container_width=True)

scatter_dl_vs_cit = alt.Chart(df[filt]).mark_point(size=75, opacity=0.5, filled=True).encode(
    alt.X('downloads:Q', title="Downloads"),
    alt.Y('citations:Q', title="Citations"),
    color=alt.Color('subscribed:N', scale=subscribed_colorscale),
    shape=alt.Shape('subscribed:N', scale=subscribed_point_mapping),
    tooltip=['title', 'authorships', 'subscription_cost', 'subscribed']
    #size=('authorships')
).interactive().properties(
        height=400,
        title={
            "text": ["Citations vs. Downloads"],
            "subtitle": ["What is contributing to the weighted usage?", "Hold authorships steady with a filter and consider citations and DLs within that group"],
            "color": "black",
            "subtitleColor": "gray"
        }
        )
st.altair_chart(scatter_dl_vs_cit, use_container_width=True)


#3x scatter matrix showing all metrics vs. overall usage
scatter_selection = alt.selection_multi(fields=['subscribed'], bind='legend')

linked = alt.Chart(df[filt]).mark_point(size=50, opacity=0.5, filled=True).encode(
    alt.X(alt.repeat("repeat"), type='quantitative'),
    alt.Y('usage:Q', title='Weighted Usage (DL + Cit + Auth)'),
    color=alt.condition(scatter_selection, alt.Color('subscribed:N', scale=subscribed_colorscale), alt.value('lightgray')),   #Nominal data type
    shape=alt.Shape('subscribed:N', scale=subscribed_point_mapping),
    tooltip=['title','downloads','citations','authorships','usage','use_oa_percent', 'free_instant_usage_percent', 'subscription_cost', 'cpu', 'cpu_rank', 'subscribed']    
).properties(
    width=350,
    height=250,
    title={
        "text": ["Four linked plots - Weighted usage vs. [ DL / cit / auth / Free% ]"],
        "subtitle": ["Zooming in will adjust all four"],
        'color':'black',
        'subtitleColor': 'gray'
        }
).repeat(
    repeat=['downloads', 'citations', 'authorships', 'free_instant_usage_percent'],
    columns=2
).interactive().add_selection(scatter_selection)

linked



# Instant Fill % graphs
st.subheader('Consider the Instant Fill % from each journal (paid usage / total package usage)')

IF_selection = alt.selection_single()

IF = alt.Chart(df[filt]).mark_point(opacity=0.5, filled=True).encode(
    alt.X('subscription_cost', title="Journal Cost", axis=alt.Axis(format='$,.2r')),    #grouped thousands with two significant digits
    alt.Y('IF%', title='Instant Fill %'),
    tooltip=(['title','subscription_cost','IF%']),
    color=alt.Color('subscribed:N', scale=subscribed_colorscale),
    shape=alt.Shape('subscribed:N', scale=subscribed_point_mapping),
    ).interactive().properties(
        height = 400,
        title={
            "text": ['Instant Fill % vs. Journal Subscription Cost'],
            "subtitle": ["Which journals increase Instant Fill % the most (moving up), and what do they cost?", "Could look for a less expensive journal that gets you the same IF%, generally the upper band", "Note: Must look at all journals in the package together; graphing subsets will throw the calculations off"],
            "color": "black",
            "subtitleColor": "gray"
        }
        )
st.altair_chart(IF, use_container_width=True)

IF2 = alt.Chart(df[filt]).mark_point(opacity=0.5, filled=True).encode(
    alt.X('cost_per_IF%', scale=alt.Scale(type='log'), title="log ( Price per 1 IF% point)", axis=alt.Axis(format='$,.2r')),
    alt.Y('IF%', title="Instant Fill %"),
    tooltip=(['title','subscription_cost','IF%','cost_per_IF%']),
    color=alt.Color('subscribed:N', scale=subscribed_colorscale),
    shape=alt.Shape('subscribed:N', scale=subscribed_point_mapping)
    ).interactive().properties(
        height=400,
        title={
            "text": ['Instant Fill % vs. Price per 1 IF% point'],
            "subtitle": ["Normalized by price, which journals are the best way to increase Instant Fill % (tending to upper left corner)?","Note: X-axis shown in log to stretch and increase visibility", "Note: Must look at all journals in the package together; graphing subsets will throw the calculations off"],
            "color": "black",
            "subtitleColor": "gray"
        }
)
st.altair_chart(IF2, use_container_width=True)



st.subheader('Look where journal decisions land in the Unsub histogram')
#Unsub histogram, but colored by subscribed
unsub_hist = alt.Chart(df[filt].reset_index()).mark_bar().encode(   #.reset_index() turns the indx into a column
    alt.X('cpu:Q', bin=alt.Bin(step=1), title="Cost per Use bins (data may continue beyond the chart, zoom out or scroll to see)", axis=alt.Axis(format='$'), scale=alt.Scale(domain=[-1,100])),
    alt.Y('count()', axis=alt.Axis(grid=False)),
    alt.Detail('index'),
    tooltip=['title', 'cpu', 'cpu_rank', 'subscription_cost', 'subscribed'],
    color=alt.Color('subscribed:N', scale=subscribed_colorscale)
    ).interactive().properties(
        height=400,
        title={
            "text": ["Unsub's Cost per Use Histogram, color coded by Subscribed status"],
            "subtitle": ["Note: Journals are grouped by Subscribed status, not shown in continuous order by CPU like Unsub does", "Note 2: X-axis default set to max of $100, zoom out to see data that may have even higher CPU"],
            "color": "black",
            "subtitleColor": "gray"
        }
        )
st.altair_chart(unsub_hist, use_container_width=True)



st.subheader('Consider journal subject areas')

def split_era(sentence):
    """
    Input: era_subjects column of one row
        ex. [['0608', 'Zoology'], ['0707', 'Veterinary Sciences'], ['06', 'Biological Sciences'], ['07', 'Agricultural and Veterinary Sciences']]"
    Output: a list of the broadest two digit era_subjects category; can have multiple
        ex. ['Biological Sciences', 'Agricultural and Veterinary Sciences']
    """

    two_digit_list = []
    final = []
    
    mylist = re.split(r'\]',sentence)      #breaks into [['0608', 'Zoology' (no end bracket)
    for i in mylist:
        m = re.search(r'\d+', i)    #m tells if it has digits
        if m==None:
            m = re.search(r'MD', i)
        if m!=None:             #when digit search doesn't match, it returns a NoneType and errors the group() call
            #print(m.group())    #returns the part of string where there was a match; 0608, 0707, 06, 07
            if len(m.group())==2:
                two_digit_list.append(i)
        
        
    #print(two_digit_list)     #List of two digit codes: ['06', 'Biological Sciences'
    
    for j in two_digit_list:
        comma_split = re.split(r'\',', j)
        for c in comma_split:       #either numbers or words
            d = re.search(r'[a-z]+', c)     #look for words
            if d!=None:
                final.append(c[2:-1])       #if it has words, strip off leading _' and trailing '
    
    return (final)


if ('era_subjects' in df.columns): #& (df['era_subjects'] != 0).all():
    st.write("Using column for **'era_subject'** codes by Excellence in Research for Australia (ERA).")
    st.write("**Note:** Some titles do not have an **'era_subject'** area assigned; they appear in the first (left-most) column.")
    
    #create new column called 'era_split', calling fn on each row and adding the two digit codes in list form
    df['era_split'] = df.apply(lambda x: split_era(x['era_subjects']), axis=1, result_type='reduce')
    #remove leading and ending bracket and quote mark
    df['era_split'] = df['era_split'].astype(str).str.slice(2,-2)
    #Now it looks like "Commerce, Management, Tourism and Services', 'Built Environment and Design', 'Engineering"
    
    #can't just split by comma since some subjects have multiple words so have to split by ', ' quotecommaspacequote
    df['era_split_by_quotecommaquote'] = df['era_split'].str.split('\', \'')
    df2 = df.explode('era_split_by_quotecommaquote')    #new df defined with more rows than the original, with repeated rows, names and all its data every time
    df2.reset_index(drop=True, inplace=True)
    
    #force 'subscribed' column to be a string, not Bool, and all uppercase
    df2['subscribed'] = df2['subscribed'].astype(str)
    df2['subscribed'] = df2['subscribed'].str.upper()
    df2['cpu_rank'] = df2['cpu_rank'].astype(int)
    
    subject_filtered_titles_df = df2.loc[df2['title'].isin(df[filt]['title'])]  #df2 is larger than df b/c rows repeated multiple times.
    #Want to show only titles that fit filter but can't apply it directly since index won't match. So only select titles that get returned in df[filt]
    
    cpurank_vs_subject2 = alt.Chart(subject_filtered_titles_df).mark_point(size=40, opacity=0.5, filled=True).encode(
        x=alt.X('era_split_by_quotecommaquote:N', title=None),
        y=alt.Y('cpu_rank:Q'),
        color=alt.Color('subscribed:N', scale=subscribed_colorscale),   #Nominal data type
        shape=alt.Shape('subscribed:N', scale=subscribed_point_mapping),
        tooltip=['title', 'cpu_rank', 'downloads','citations','authorships','usage','subscription_cost', 'era_split', 'subscribed'],
        
        ).interactive().properties(
            height=600,
            title={
                "text": ["Overview of cancellations by 'Subject' column"],
                "subtitle": ["Review decisions and make sure you're not penalizing one discipline too much", "Subject area classifications are probably not perfect, but gives a general idea"],
                "color": "black",
                "subtitleColor": "gray"
            }
            ).configure_axis(
    labelFontSize=15,
    #titleFontSize=20
    )
    st.altair_chart(cpurank_vs_subject2, use_container_width=True)
    
#if (df['subject'] != 0).all():
elif ('subject' in df.columns):
    st.write("Note: Your file uses the older **'subject'** column which is now deprecated by Unsub. Future export files use the **'era_subject'** codes by Excellence in Research for Australia (ERA).")
    #cpu_Rank y vs. subject, colored by subscribed
    cpurank_vs_subject = alt.Chart(df[filt]).mark_point(size=40, opacity=0.5, filled=True).encode(
        x=alt.X('subject:N', title=None),# axis=alt.Axis(values=[0], ticks=True, grid=False, labels=False), scale=alt.Scale()),
        y=alt.Y('cpu_rank:Q'),
        color=alt.Color('subscribed:N', scale=subscribed_colorscale),   #Nominal data type
        shape=alt.Shape('subscribed:N', scale=subscribed_point_mapping),
        tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'subscribed'],
        ).interactive().properties(
            height=600,
            title={
                "text": ["Overview of cancellations by 'Subject' column"],
                "subtitle": ["Review decisions and make sure you're not penalizing one discipline too much", "Subject area classifications are probably not perfect, but gives a general idea"],
                "color": "black",
                "subtitleColor": "gray"
            }
            ).configure_axis(
    labelFontSize=15,
    #titleFontSize=20
    )
    st.altair_chart(cpurank_vs_subject, use_container_width=True)
else:
    st.write("Sorry, you don't seem to have the right data in your file.")
    st.write("I need either a **subject** column (old version) or an **era_subjects** column (new version) to show these by-subject charts.")




##### Footer in sidebar #####
st.sidebar.subheader("About")
github = "[![GitHub repo stars](https://img.shields.io/github/stars/eschares/unsub_extender?logo=github&style=social)](<https://github.com/eschares/unsub_extender>)"
twitter = "[![Twitter Follow](https://img.shields.io/twitter/follow/eschares?style=social)](<https://twitter.com/eschares>)"
zenodo = "[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5167933.svg)](https://doi.org/10.5281/zenodo.5167933)"
st.sidebar.write(zenodo)
st.sidebar.write(twitter + " " + github)

html_string = "<p style=font-size:13px>v1.1, last modified 2/4/22 <br />Created by Eric Schares, Iowa State University <br /> Send any feedback, suggestions, bug reports, or success stories to <b>eschares@iastate.edu</b></p>"
st.sidebar.markdown(html_string, unsafe_allow_html=True)
#st.sidebar.write("*Version 1.0*")

# Analytics code
components.html(
    """
<html>
<body>
<script>var clicky_site_ids = clicky_site_ids || []; clicky_site_ids.push(101315881);</script>
<script async src="//static.getclicky.com/js"></script>
<noscript><p><img alt="Clicky" width="1" height="1" src="//in.getclicky.com/101315881ns.gif" /></p></noscript>
</body>
</html>
    """
)


components.html(
"""
<a title="Web Analytics" href="https://statcounter.com/" target="_blank"><img src="https://c.statcounter.com/12526873/0/c525cd17/1/" alt="Web Analytics" ></a>
"""
)
