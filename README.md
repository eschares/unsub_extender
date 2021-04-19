![unsub extender logo](https://github.com/eschares/unsub_extender/blob/main/unsub_extender2.png)

[unsub](http://unsub.org) is a collection analysis tool that assists libraries in analyzing their journal subscriptions.
The tool provides rich data and a summary graph, but more detailed analysis tends to take place off the site in an exported .csv file that allows for filtering, notes, and additional visualization.

[**unsub extender**](https://github.com/eschares/unsub_extender) is a Python script that automates useful plots and provides standardized visualizations for a collection analysis team to explore.
The graphs are interactive through [Altair](https://altair-viz.github.io/index.html) and support zoom, pan, and hover, and filters in the sidebar help set parameters to quickly narrow in on obvious titles to KEEP or CANCEL.
Hosting is provided by [Streamlit](https://streamlit.io/).

# Requirements:
An unsub export file - in an [unsub](http://unsub.org) project, choose "Export - Download as spreadsheet".

A .csv file will be saved, which is the input to **unsub extender.**

The .csv file must have the following columns in any order, but named exactly as:
* downloads
* citations
* authorships
* usage (will be renamed to "weighted usage" during the analysis)
* subscription_cost
* subscribed

These should already be the default column names assigned by unsub in the file export.

# Usage
Hosted on Streamlit
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/eschares/unsub_extender/main/unsub_extender.py/)

Navigate to https://share.streamlit.io/eschares/unsub_extender/main/unsub_extender.py to run in browser

# License
MIT License

Copyright (c) 2021 Eric Schares

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


# Credits
* Eric Schares
* [unsub](http://unsub.org)
