# The Voter Data Project

## Making it easier to work with large databases of voter responses

## YouGov Data

YouGov and Democracy Fund teamed up to produce the Voter Study Group data set, a longitudinal poll of 8000 individuals initially interviewed in 2012, with a follow-up poll in 2016.

## The Voters module

The `Voters` module is a python module created to easily work with and analyze the YouGov data.

It is a class initialized with the call `Voters()`. If initialized on its own, it loads the entire YouGov data set as a pandas data frame that can be accessed and tinkered with `Voters().data` as you would a normal `pandas` data frame. 

All of the information necessary to work with the data set is in the `polls` in the file `polls.py` (for anyone looking to do similar work, fair warning, the creation of this dictionary was *by far* the most labor-intensive part of this project). The `polls` dictionary has the column labels for the specific quesitons asked as keys. You can view all of the available column labels, and the associated question summaries by calling:

> keys = polls.keys()
> for key in keys:
>   print(polls[key][0] + " -- " + key)

To see the full information for each question (the summary, the specific question asked, the identifiers for the answers, and the answers they correspond to) call:

> polls[<key>]

The main functions for working with the class are `get_voters()`, `get_column()` and `plot_percentages()`

`get_column()` accesses a particular column in the data frame, and resets the object's data frame to consist of only that column. The columns are indexed by the dataset's column labels. The sole argument for this function is `column_label="<column_label>"`.

`get_voters()` is more complex. It takes in a column label and a selection. One you know what column you want to work with, you can find the response indicators with `polls[<column_lable>]`, which will output all the information for that question. Once you know what indicator you would like to sort by, you can access the voters who match that indicator, in that column, by calling `<voter_object>.get_voters(column_label="<column_label">, selection=<identifier>)`. This function outputs a new `Voter` instance, with `<instance>.data` set a data frame with all columns, but consisting of only voters that matched the identifier in the column you specified.

`plot_percentages()` takes a column as input, and plots the percentages for each response indicator, indexed by the response, as a bar chart, for the `Voters()` instance. It has a few other odds and ends as well:

`rotate_labels` can be set to `True` or `False` depending on if you want the index labels rotated or not. (default is `False`)
`weighted` can be set to `True` if you'd like to weight the response indicators by demographic scaling weights. (default is `False`)
`bar_labels` can be set to `True` or `False` depending on whether or not you want the bars in the bar chart to be labeled with their exact percentages. (default is `True`)
`ft` can be set to `True` if you are plotting "Feeling Thermometer" data (default is `False`)
`not_sure` can be set to `True` if you'd like to show the percentages of people who answered "Not Sure" for each question. (default is `True`)
