# unsub_extender

[unsub](http://unsub.org) is a collection analysis tool that assists libraries in analyzing their journal subscriptions.
The tool is very useful, but most detailed analysis tends to take place off the site and in an exported .csv file that allows for filtering, notes, and graphing.

**unsub extender** was created to automate useful plots and provide standardized visualizations for a collection analysis team to explore.
The graphs are interactive (zoom, pan, hover), and filters in the sidebar help set parameters to zero in on obvious titles to KEEP or CANCEL.


Requirements:
In unsub, choose "Export - Download as spreadsheet".  A .csv file will be saved, which you run through **unsub extender.**

The .csv file must have the following columns in any order, but must be exactly as:
* downloads
* citations
* authorships
* usage (will be renamed to "weighted usage" during the analysis)
* subscription_cost
* subscribed

These should already be the default column names assigned by unsub in the file export.
