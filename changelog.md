# Unsub Extender - Versioning Record and Changelog

## 3/24/2022, v.1.2
- add RUSA/ETS BETA award information
- add live demo webinar links
- 'perpetual_access_years' and '_text' conversions
- Support blank Subscribed status
- Logic for 'subject' and 'era_subjects' str convert

## 2/2/2022
- removed streamlit-analytics, was not compatible with Streamlit 1.3.1
- latest pandas (1.4) was causing AssertionError, downgraded to 1.3.5
- fixed trailing underscore in exported dataset filename
- added dropdown to show user what they changed before exporting new data

## 1/25/2022, v.1.1
- upgraded Streamlit from v.0.84.1 to v.1.3.1 for less memory usage (current version is v1.4, but upgraded caused error "no module named 'streamlit.report_thread'")
- streamlit.media_file_manager deprecated, move to st.download_button to export dataset
- st.beta_columns move to st.columns
- st.beta_expander move to st.expander
- add 'era_subjects' to example data file
- convert subjects and era_subjects columns to strings
- used Streamlit states to get decisions to persist across runs
- changed marker shape to vary by Subscribed status

## 8/6/2021, v.1.0
- first stable version released
- get DOI
