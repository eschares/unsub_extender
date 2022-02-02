# Unsub Extender - Versioning Record and Changelog

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