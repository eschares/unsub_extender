![unsub extender logo](https://github.com/eschares/unsub_extender/blob/main/unsub_extender2.png)

## [https://unsubextender.lib.iastate.edu/](https://unsubextender.lib.iastate.edu/)

[![DOI](https://zenodo.org/badge/358961619.svg)](https://zenodo.org/badge/latestdoi/358961619)

### :books: Paper on Unsub Extender published in [*Quantitative Science Studies*](https://doi.org/10.1162/qss_a_00200) :books:

### Learn about Unsub Extender by watching a recent [live demo](https://vimeo.com/680578098).

### ❓ Need more? Hire [Schares Data Science](https://www.scharesdatascience.com/) to help interpret your Unsub results.

# About
[Unsub](http://unsub.org) is a collection analysis tool that assists libraries in analyzing their journal subscriptions.
The tool provides rich data and a summary graph, but more detailed analysis tends to take place off the site in an exported .csv file that allows for filtering, notes, and additional visualization.

This project, [**Unsub Extender**](https://unsubextender.lib.iastate.edu), is a Python script that takes an Unsub data export file and automates useful plots and visualizations for a collection analysis team to explore.
The graphs are interactive through [Altair](https://altair-viz.github.io/index.html) and support zoom, pan, and hover, and filters in the left sidebar help set parameters to quickly narrow in on obvious titles to KEEP or CANCEL. The Python code is turned into a web app using [Streamlit](https://streamlit.io/).

Hosting provided by Iowa State University.

![unsub extender screenshot demo](https://github.com/eschares/unsub_extender/blob/main/demo.gif)

# Requirements
An export .csv file - from an [Unsub](http://unsub.org) project, choose "Export - Download as spreadsheet".

A .csv file will be saved, which is the input to **Unsub Extender.**

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
* use_oa_percent
* use_other_delayed_percent
* era_subjects

These should already be the default column names assigned by Unsub in the file export.

### subscribed column
The **subscribed** column is especially important as it determines the color-coding of data points in several of the graphs. The column accepts the following values:

(TRUE and FALSE are conventions carried over from Unsub, MAYBE is supported as a third option for future consideration, and leaving the cell blank will color that journal data point grey):
* TRUE
  * A title to keep, displayed in blue
* FALSE
  * A title to cancel, displayed in red
* MAYBE
  * A title to think more about, displayed in green
* (blank)
  * A title with no decision yet, displayed in grey

# Usage
Hosted by Iowa State University

Navigate to https://unsubextender.lib.iastate.edu to run in browser

# Awards 🎉
- 2022 RUSA ETS [Best Emerging Technology Application](https://rusaupdate.org/2022/03/2022-ets-best-emerging-technology-application-award/) (BETA) Award
- 2022 ASEE ELD [Innovation in Access to Engineering Information](https://sites.asee.org/eld/about-the-eld/awards/#innovation) Award

# License
GNU AGPLv3, Copyright (c) 2021 Eric Schares

See LICENSE file

# Credits
* Eric Schares
* Nick Booher
* [unsub](http://unsub.org)

# Recommended Citation
Eric Schares (2021). Unsub Extender. https://doi.org/10.5281/zenodo.5167933
