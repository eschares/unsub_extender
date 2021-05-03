![unsub extender logo](https://github.com/eschares/unsub_extender/blob/main/unsub_extender2.png)

# About
[unsub](http://unsub.org) is a collection analysis tool that assists libraries in analyzing their journal subscriptions.
The tool provides rich data and a summary graph, but more detailed analysis tends to take place off the site in an exported .csv file that allows for filtering, notes, and additional visualization.

[**unsub extender**](https://github.com/eschares/unsub_extender) is a Python script that takes an unsub data export file and automates useful plots and visualizations for a collection analysis team to explore.
The graphs are interactive through [Altair](https://altair-viz.github.io/index.html) and support zoom, pan, and hover, and filters in the left sidebar help set parameters to quickly narrow in on obvious titles to KEEP or CANCEL.

Hosting is provided by [Streamlit](https://streamlit.io/).

![unsub extender screenshot demo](https://github.com/eschares/unsub_extender/blob/main/demo.gif)

# Requirements
An unsub export .csv file - from an [unsub](http://unsub.org) project, choose "Export - Download as spreadsheet".

A .csv file will be saved, which is the input to **unsub extender.**

The .csv file must have the following columns in any order, but named exactly as:
* title
* downloads
* citations
* authorships
* usage
* subscription_cost
* subscribed
* cpu
* cpu_rank
* use_ill_percent
* use_other_delayed_percent

These should already be the default column names assigned by unsub in the file export.

### subscribed column
The **subscribed** column is especially important as it determines the color-coding of data points in several of the graphs. The column accepts the following values:

(TRUE and FALSE are conventions carried over from unsub, MAYBE is supported as a third option for future consideration, and leaving the cell blank will color that journal data point grey):
* TRUE
  * A title to keep, displayed in blue
* FALSE
  * A title to cancel, displayed in red
* MAYBE
  * A title to think more about, displayed in green
* (blank)
  * A title with no decision yet, displayed in grey

# Usage
Hosted on Streamlit
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/eschares/unsub_extender/main/unsub_extender.py/)

Navigate to https://share.streamlit.io/eschares/unsub_extender/main/unsub_extender.py to run in browser

# License
MIT License, Copyright (c) 2021 Eric Schares

See LICENSE file

# Credits
* Eric Schares
* [unsub](http://unsub.org)
