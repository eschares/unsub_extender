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
import streamlit_analytics

st.set_page_config(page_title='Unsub Extender', page_icon="scissors.jpg", layout='centered', initial_sidebar_state="expanded")

streamlit_analytics.start_tracking()

#st.set_page_config(layout="wide")
st.image('unsub_extender2.png')
#st.sidebar.write("*Version 1.0*")
st.sidebar.markdown('**[About unsub extender](https://github.com/eschares/unsub_extender/blob/main/README.md)**')


with st.beta_expander("How to use:"):
    st.write("This site takes an Unsub data export .csv file and automates the creation of useful plots and interactive visualizations so you can make more informed collection decisions.")
    st.write('**Upload your specific Unsub .csv** export file using the "Browse files" button in the left sidebar, or explore the pre-loaded example dataset and plots to see what is available.')
    st.write("Graphs are interactive and support zoom, click-and-drag, and hover.  Double click a graph to reset it back to default view.")
    st.write("Filter on various criteria using the sliders on the left to narrow in on areas of interest, hover over data points to learn more about a specific journal, then use the dropdown to actually change a journal's *Subscribed* status and watch the graphs update. (Note: you may have to occasionally hit *'r'* to force a reload if you notice it's not loading right away)")
    st.markdown('This project is written in Python and deployed as a web app using the library Streamlit. **More information about unsub extender, its requirements, and the source code is available on the [project GitHub page](https://github.com/eschares/unsub_extender)**')

#Initialize with a hardcoded dataset
file = filename = "Unsub_export_example.csv"

uploaded_file = st.sidebar.file_uploader('Analyze your Unsub export file .csv :', type='csv')
if uploaded_file is not None:
    file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type,"FileSize":uploaded_file.size}
    #st.write(file_details)
    
    file = uploaded_file
    filename = uploaded_file.name


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def load_data(file):
    st.write("New file loaded")
    return pd.read_csv(file, sep=',', encoding='utf-8')  #Process the data in cached way to speed up processing

st.header('Analyzing file "' + filename + '"')

df = load_data(file)

#force 'subscribed' column to be a string, not Bool and all uppercase
df['subscribed'] = df['subscribed'].astype(str)
df['subscribed'] = df['subscribed'].str.upper()

#process data to calculate IF%
total_usage = df['usage'].sum()
df['current_yr_usage'] = ((df['use_ill_percent'] + df['use_other_delayed_percent']) / 100) * df['usage']
df['IF%'] = (df['current_yr_usage'] / total_usage) * 100
df['cost_per_IF%'] = df['subscription_cost'] / df['IF%']

sidebar_modifier_slot = st.sidebar.empty()
my_slot1 = st.empty()   #save this spot to fill in later for how many rows get selected with the filter


# Sliders and filter
st.sidebar.subheader("**Filters**")
price_slider = st.sidebar.slider('Price ($) between:', min_value=0, max_value=int(max(df['subscription_cost'])), value=(0,int(max(df['subscription_cost']))))
cpu_slider = st.sidebar.slider('Cost per Use Rank between:', min_value=0, max_value=int(max(df['cpu_rank'])), value=(0,int(max(df['cpu_rank']))), help='CPU Rank ranges from 0 to max number of journals in the dataset')
downloads_slider = st.sidebar.slider('Downloads between:', min_value=0, max_value=int(max(df['downloads'])), value=(0,int(max(df['downloads']))), help='Average per year over the next five years')
citations_slider = st.sidebar.slider('Citations between:', min_value=0.0, max_value=max(df['citations']), value=(0.0,max(df['citations'])), help='Average per year over the next five years')
authorships_slider = st.sidebar.slider('Authorships between:', min_value=0.0, max_value=max(df['authorships']), value=(0.0,max(df['authorships'])), help='Average per year over the next five years')
weighted_usage_slider = st.sidebar.slider('Weighted usage (DL + x*Cit + y*Auth) between:', min_value=0, max_value=int(max(df['usage'])), value=(0,int(max(df['usage']))), help='x Citation and y Authorship weights are set in the Unsub tool itself')
OA_percent_slider = st.sidebar.slider('OA % between:', min_value=0, max_value=int(max(df['free_instant_usage_percent'])), value=(0,int(max(df['free_instant_usage_percent']))))
subscribed_filter = st.sidebar.radio('Subscribed status:',['Show All', 'TRUE', 'FALSE', 'MAYBE', '(blank)'], help='Filter based on the current Subscribed status')
subscribed_filter_flag = 0
if subscribed_filter == "(blank)":
    subscribed_filter = " "
if subscribed_filter != 'Show All':
    subscribed_filter_flag = 1

#could also use between: (df['cpu_rank'].between(cpu_slider[0], cpu_slider[1]))
filt = ( (df['free_instant_usage_percent'] >= OA_percent_slider[0]) & (df['free_instant_usage_percent'] <= OA_percent_slider[1]) &
        (df['downloads'] >= downloads_slider[0]) & (df['downloads'] <= downloads_slider[1]) &
        (df['citations'] >= citations_slider[0]) & (df['citations'] <= citations_slider[1]) &
        (df['subscription_cost'] >= price_slider[0]) & (df['subscription_cost'] <= price_slider[1]) &
        (df['authorships'] >= authorships_slider[0]) & (df['authorships'] <= authorships_slider[1]) &
        (df['cpu_rank'] >= cpu_slider[0]) & (df['cpu_rank'] <= cpu_slider[1]) &
        (df['usage'] >= weighted_usage_slider[0]) & (df['usage'] <= weighted_usage_slider[1])
        )


if subscribed_filter_flag:      #add another filter part, have to do it this way so Subscribed=ALL works
    filt2 = (df['subscribed'] == subscribed_filter)
    filt = filt & filt2

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df[filt])
    
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


#Put Modifier down here after the filt definition so only those titles that meet the filt show up, but put into empty slot further up the sidebar for flow
with sidebar_modifier_slot:
    with st.beta_expander("Change a journal's Subscribed status:"):
        filtered_titles_df = df.loc[filt]['title']      #make a new df with only the valid titles
        #then give those valid titles as choices in the Modifier, was causing problems when trying to offer them through a filter, kept trying to use the index but wouldn't be there anymore
        selected_titles = st.multiselect('Journal Name:', pd.Series(filtered_titles_df.reset_index(drop=True)), help='Displayed in order provided by the underlying datafile')
        #st.write(selected_titles)
    
        col1, col2 = st.beta_columns([2,1])
    
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
                    title_filter = (df['title'] == title)
                    df.loc[title_filter, 'subscribed'] = radiovalue



### Summary dataframe created to show count and sum$ by Subscribed status
summary_df = df[filt].groupby('subscribed')['subscription_cost'].agg(['count','sum'])
summary_df['sum'] = summary_df['sum'].apply(lambda x: "${0:,.0f}".format(x))
#now formatted as a string (f)
#leading dollar sign, add commas, round result to 0 decimal places
my_slot2.write(summary_df.sort_index(ascending=False))  #display in order of TRUE, MAYBE, FALSE, blank




########  Charts start here  ########
#st.header('Charts created automatically')
#weighted usage in log by cost (x), colored by subscribed
#adding clickable legend to highlight subscribed categories
selection1 = alt.selection_multi(fields=['subscribed'], bind='legend')
weighted_vs_cost = alt.Chart(df[filt]).mark_circle(size=75, opacity=0.5).encode(
    alt.X('subscription_cost:Q', axis=alt.Axis(format='$,.2r'), scale=alt.Scale(clamp=True)),
    alt.Y('usage:Q', scale=alt.Scale(type='log'), title='Weighted Usage (DL + Cit + Auth)'),
    color=alt.condition(selection1, alt.Color('subscribed:N', scale=subscribed_colorscale), alt.value('lightgray')),   #Nominal data type
    tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'cpu_rank', 'subscribed'],
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
selection2 = alt.selection_multi(fields=['cpu_rank'], bind='legend')
weighted_vs_cost2 = alt.Chart(df[filt]).mark_circle(size=75, opacity=0.5).encode(
    alt.X('subscription_cost:Q', axis=alt.Axis(format='$,.2r'), scale=alt.Scale(clamp=True)),
    y=alt.Y('usage:Q', scale=alt.Scale(type='log'), title='Weighted Usage (DL + Cit + Auth)'),
    color=alt.condition(selection2, alt.Color('cpu_rank:Q', scale=alt.Scale(scheme='viridis')), alt.value('lightgray')),   #selection, if selected, if NOT selected
    #opacity=alt.condition(selection2, alt.value(1), alt.value(0.2)),
    tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'cpu_rank', 'subscribed'],
    ).interactive().properties(
        height=500,
        title={
            "text": ['Total Weighted Usage vs. Cost, color coded by CPU_Rank gradient'],
            "subtitle": ["Same graph as above, but with different color coding", "High Cost-per-Use rank (least economical) journals show up in light yellow"],
            "color": "black",
            "subtitleColor": "gray"
        }
        ).add_selection(selection2)
st.altair_chart(weighted_vs_cost2, use_container_width=True)


#Unsub histogram, but colored by subscribed    bin=alt.Bin(step=1)
#hist_filt = filt & (df['cpu']<=100)
#hist_df = df[hist_filt]
unsub_hist = alt.Chart(df[filt].reset_index()).mark_bar().encode(   #.reset_index() turns the indx into a column
    alt.X('cpu:Q', bin=alt.Bin(step=1), title="Cost per Use bins (data may continue beyond the chart, zoom out or scroll to see)", axis=alt.Axis(format='$'), scale=alt.Scale(domain=[-1,100])),
    alt.Y('count()', axis=alt.Axis(grid=False)),
    alt.Detail('index'),
    tooltip=['title', 'cpu', 'subscription_cost', 'subscribed'],
    color=alt.Color('subscribed:N', scale=subscribed_colorscale)
    ).interactive().properties(
        height=400,
        #width=800,
        title={
            "text": ["Unsub's Cost per Use Histogram, color coded by Subscribed status"],
            "subtitle": ["Journals grouped by Subscribed status, not shown in continuous order by CPU", "Note: X-axis default set to max of $100, zoom out to see data that may have even higher CPU"],
            "color": "black",
            "subtitleColor": "gray"
        }
        )
st.altair_chart(unsub_hist, use_container_width=True)
#st.write("Journals with cpu>100: ")

auth_hist = alt.Chart(df[filt].reset_index()).mark_bar(width=10).encode(
    alt.X('authorships:Q', title="Authorships (average per year over the next five years)"),
    alt.Y('count()', axis=alt.Axis(grid=False)),
    alt.Detail('index'),
    tooltip=['title', 'authorships', 'subscription_cost', 'subscribed'],
    color=alt.Color('subscribed:N', scale=subscribed_colorscale)
    ).interactive().properties(
        height=400,
        #width=800,
        title={
            "text": ["Authorships Distribution"],
            "subtitle": ["What do the range of Authorships look like?", "Use this graph to help set the Authorships slider filter and narrow down titles of interest"],
            "color": "black",
            "subtitleColor": "gray"
        }
        )
st.altair_chart(auth_hist, use_container_width=True)

scatter_dl_vs_cit = alt.Chart(df[filt]).mark_circle(size=75, opacity=0.5).encode(
    alt.X('downloads:Q', title="Downloads"),
    alt.Y('citations:Q', title="Citations"),
    color=alt.Color('subscribed:N', scale=subscribed_colorscale),
    tooltip=['title', 'authorships', 'subscription_cost', 'subscribed'],
    size=('authorships')
).interactive().properties(
        height=400,
        #width=800,
        title={
            "text": ["Citations vs. Downloads"],
            "subtitle": ["Where is the usage coming from?"],
            "color": "black",
            "subtitleColor": "gray"
        }
        )
st.altair_chart(scatter_dl_vs_cit, use_container_width=True)


# Instant Fill % graphs
st.subheader('Consider the Instant Fill % from each journal')

IF_selection = alt.selection_single()

IF = alt.Chart(df[filt]).mark_circle().encode(
    alt.X('subscription_cost', title="Journal Cost", axis=alt.Axis(format='$,.2r')),    #grouped thousands with two significant digits
    alt.Y('IF%', title='Instant Fill %'),
    tooltip=(['title','subscription_cost','IF%']),
    color=alt.Color('subscribed:N', scale=subscribed_colorscale)
    ).interactive().properties(
        height = 400,
        title={
            "text": ['Instant Fill % vs. Journal Subscription Cost'],
            "subtitle": ["Which journals increase Instant Fill % the most (moving up), and what do they cost?", "Look for a less expensive journal that gets you the same IF%, generally the upper band"],
            "color": "black",
            "subtitleColor": "gray"
        }
        )
st.altair_chart(IF, use_container_width=True)

IF2 = alt.Chart(df[filt]).mark_circle().encode(
    alt.X('cost_per_IF%', scale=alt.Scale(type='log'), title="log ( Price per IF% point)", axis=alt.Axis(format='$,.2r')),
    alt.Y('IF%', title="Instant Fill %"),
    tooltip=(['title','subscription_cost','IF%','cost_per_IF%']),
    color=alt.Color('subscribed:N', scale=subscribed_colorscale)
    ).interactive().properties(
        height=400,
        title={
            "text": ['Instant Fill % vs. Price per IF% point'],
            "subtitle": ["Normalized by price, which journals are the best way to increase Instant Fill % (tending to upper left corner)?","Note: X-axis shown in log to stretch and increase visibility"],
            "color": "black",
            "subtitleColor": "gray"
        }
)
st.altair_chart(IF2, use_container_width=True)


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
cpurank_vs_subject = alt.Chart(df[filt]).mark_circle(size=40, opacity=0.5).encode(
    x=alt.X('subject:N', title=None),# axis=alt.Axis(values=[0], ticks=True, grid=False, labels=False), scale=alt.Scale()),
    y=alt.Y('cpu_rank:Q'),
    color=alt.Color('subscribed:N', scale=subscribed_colorscale),   #Nominal data type
    # column=alt.Column(
    #     'subscribed:N',
    #     header=alt.Header(
    #         labelAngle=-90,
    #         titleOrient='top',
    #         labelOrient='bottom',
    #         labelAlign='right',
    #         labelPadding=3,
    #         ),
    #     ),
    tooltip=['title','downloads','citations','authorships','usage','subscription_cost', 'subscribed'],
    ).interactive().properties(
        height=600,
        #width=800,
        title={
            "text": ["Overview of cancellations by 'Subject' column"],
            "subtitle": ["Review decisions and make sure you're not penalizing one discipline too much", "Subject area classifications are probably not perfect, but gives a general idea"],
            "color": "black",
            "subtitleColor": "gray"
        }
        )
st.altair_chart(cpurank_vs_subject, use_container_width=True)




##### Footer in sidebar #####
html_string = "<p style=font-size:13px>Created by Eric Schares, Iowa State University <br />If you found this useful, or have suggestions or other feedback, please email eschares@iastate.edu</p>"
st.sidebar.markdown(html_string, unsafe_allow_html=True)

streamlit_analytics.stop_tracking(unsafe_password="testtesttest")

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
