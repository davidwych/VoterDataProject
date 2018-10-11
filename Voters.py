import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('seaborn')
from polls import polls


#USEFUL FUNCTIONS:
def convert_to_percentages(array, weighted=False, sanity_check=False):
    """Converts an array of counts to percentages of the total

    Parameters
    ----------
    array : (list, numpy array)
        array of counts
        (len 1 for unweighted, len 2 for weighted)

    Args
    ----
    weights : (bool)
        True -- weighted (weighted by demographic factors)
        False -- unweighted
    sanity_check : (bool)
        True -- perform sanity check (percentages at add to 1.0)
        False -- trust the universe

    Returns
    -------
    unique_elements : (numpy array)
        unique elements from array
    percs : (numpy array)
        percentages for each element
    """
    if not weighted:
        unique_elements = list(set(array))
        counts = np.zeros(len(unique_elements))
        for ans in array:
            idx = np.where(unique_elements == ans)
            counts[idx] += 1
        total = np.sum(counts)
        percs = counts/total
    else:
        unique_elements = list(set(array[0]))
        counts = np.zeros(len(unique_elements))
        for i in range(len(array[0])):
            idx = np.where(unique_elements == array[0][i])
            counts[idx] += array[1][i]
        total = np.sum(counts)
        percs = counts/total

    def sanity_checker():
        if np.sum(percs) == 1.0:
            print("Sanity confirmed!")
        else:
            print("Sanity in question...")
    if sanity_check:
        sanity_checker()

    return np.array(unique_elements), percs

#VOTER class
class Voters:
    """Class for working with YouGov VOTER Study Group data

    Usage::
        >>> all_voters = Voters()
        >>> specific_voters = Voters().get_voters(column_label="<column_label>",
                                                selection="<answer id>")
        >>> specific_column = Voters().get_column(column_label="<column_label>")

        To get access to the dataframe itself:
        >>> voter_instance.data

    :param data: largely unecessary to worry about. Loads the entire
    YouGov dataset if initialized on its own, and copies the DataFrame
    from other instances if manipulating with the function below
    """
    def __init__(self, data='./VOTER_Survey_December16_Release1.csv'):
        if isinstance(data, str):
            self.data = pd.read_csv(data)
        else:
            self.data = data

    def __add__(self, other):
        """Concatenate the dataframes of two Voters instances"""
        return Voters(data=pd.concat([self.data, other.data], axis=1))

    def __sub__(self, other):
        """Subtracting the columns of dataframes of two Voters instances"""
        return Voters(data=self.data.drop(other.data.columns, axis=1))

    def get_column(self, column_label):
        """Get data from one specific column in the dataframe

        Parameters
        ----------
        column_label : (str)
            label for the column in the dataframe

        Returns
        -------
        Voters() instance : (class instance)

        Usage::
            To select the column for 2016 Presidential Election vote
            >>> Voters().get_column(column_label="presvote16post_2016")

        """
        column = pd.DataFrame(self.data[column_label].fillna(value=-1.0))
        return Voters(data=column)

    def get_voters(self, column_label, selection):
        """Get dataframe with voters who match an answer id in a column

        Parameters
        ----------
        column_label : (str)
            label for the column in the dataframe
        selection : (str)
            answer index for specific response

        Returns
        -------
        Voters() instance : (class instance)

        Usage::
            To get dataframe of Hillary voters in 2016 Presidential Election
            >>> Voters().get_voters(column_label="presvote16post_2016",
                                    selection=1)

        """
        voters = self.data[:][self.data[column_label] == selection].fillna(value=-1.0)
        voters = voters.drop(column_label, axis=1)
        return Voters(data=voters)

    def _extract(self, selection="", weighted=False):
        """Extracts a numpy array for input to plot_percentages()

        Args
        ----
        selection : (str) (optional)
            extract a particular column of the dataframe
            (otherwise, Voters() column instance is automatically extracted)
        weighted : (bool) (optional)
            True -- outputs both the data from the column and the weights
                    column for the voters in the dataframe
            False -- just extract the data from the column, no weighting

        Returns
        -------
        numpy.ndarray (len 1 if weighted=False, len 2 if weighted=True)

        """
        if selection == "":
            if not weighted:
                return np.array(self.data[self.data.columns[0]])
            else:
                return np.array([self.data[self.data.columns[0]], Voters().data.iloc[self.data.index]["weight"]])
        else:
            if not weighted:
                return np.array(self.data[selection])
            else:
                return np.array([self.data[selection], Voters().data.iloc[self.data.index]["weight"]])

    def plot_percentages(self, selection="", rotate_labels=True, weighted=True,
                         bar_labels=True, ft=False, show_not_sure=False):
        """Plot bar chart of percentages of answers from the column on interest
        in the dataframe

        Parameters
        ----------
        selection : (str) (optional)
            label for the column in the dataframe
            (if not specified, the column of the dataframe
            will be automatically plotted)
        rotate_labels : (bool) (optional)
            rotate the labels of the bars (if True)
        weighted : (bool) (optional)
            weight the data w.r.t demographics (if True)
        bar_labels : (bool) (optional)
            label the bars with their associated percentages
        ft : (bool) (optional)
            set to True if plotting a "Feelings Thermometer" question
        show_not_sure : (bool) (optional)
            show the percentages of voters who answered "not sure" (if True)

        Returns
        -------
        Bar chart matplotlib plot

        Usage::
            Plot 2016 Presidential Election responses for all voters, weighted
            >>> Voters().plot_percentages(column_label="presvote16post_2016",
                                          rotate_labels=True, weighted=True)

        """
        if selection == "":
            if not weighted:
                opts, percs = convert_to_percentages(self._extract())
            else:
                opts, percs = convert_to_percentages(self._extract(weighted=True), weighted=True)
            selection = self.data.columns[0]
        else:
            if not weighted:
                opts, percs = convert_to_percentages(self._extract(selection=selection))
            else:
                opts, percs = convert_to_percentages(self._extract(selection=selection, weighted=True), weighted=True)

        #Sort the answer options
        opts = np.sort(opts)

        #Empty list to collect NaN answers, and "not sure" answers
        nans = []
        not_sure = []
        if -1 in opts:
            idx = np.where(np.array(opts).astype(int) == -1)
            nans.append(opts[idx])
            nans.append(percs[idx])
            opts = np.delete(opts, idx)
            percs = np.delete(percs, idx)
        if 31 in opts:
            idx = np.where(np.array(opts).astype(int) == 31)
            nans.append(opts[idx])
            nans.append(percs[idx])
            opts = np.delete(opts, idx)
            percs = np.delete(percs, idx)
        if 97 in opts:
            idx = np.where(np.array(opts).astype(int) == 97)
            nans.append(opts[idx])
            nans.append(percs[idx])
            opts = np.delete(opts, idx)
            percs = np.delete(percs, idx)
        if 997 in opts:
            idx = np.where(np.array(opts).astype(int) == 997)
            nans.append(opts[idx])
            nans.append(percs[idx])
            opts = np.delete(opts, idx)
            percs = np.delete(percs, idx)
        if (show_not_sure == False) and (len(opts) < 8):
            idx = np.where(np.array(opts).astype(int) == 8)
            not_sure.append(opts[idx])
            not_sure.append(percs[idx])
            opts = np.delete(opts, idx)
            percs = np.delete(percs, idx)

        #Initialize plot
        f, ax = plt.subplots()

        #Normal plots
        if not ft:
            if rotate_labels:
                plt.xticks(opts, polls[selection][3], rotation=45, ha="right")
            else:
                plt.xticks(opts, polls[selection][3])
        #Feelings thermometer plots
        else:
            #Collecting feelings thermometer answers in to bins
            ft_bins = np.linspace(0,100,51)
            new_percs = np.zeros(len(ft_bins))
            i = 0
            for j in range(len(opts) - 1):
                if opts[j] < ft_bins[i+1]:
                    new_percs[i] += percs[j]
                else:
                    new_percs[i] += percs[j]
                    i += 1
            opts = ft_bins + (100/(51*2))
            percs = new_percs

            if rotate_labels:
                plt.xticks([0.0, 25.0, 50.0, 75.0, 100.0], ["Very Cold", "Cold", "None", "Warm", "Very Warm"], rotation=45, ha="right")
            else:
                plt.xticks([0.0, 25.0, 50.0, 75.0, 100.0], ["Very Cold", "Cold", "None", "Warm", "Very Warm"])

        #Bar chart
        rects = ax.bar(opts, percs)

        #Label the bars with the associated percentages
        def autolabel(rects):
            max_height = max([rect.get_height() for rect in rects])
            for rect in rects:
                height = rect.get_height()
                #Label below if large bar
                if height > max_height/4.0:
                    ax.text(rect.get_x() + rect.get_width()/2., height-(max_height/15),
                            '{:.1%}'.format(height), ha='center', va='bottom', fontweight='bold')
                #Label above if small bar
                else:
                    ax.text(rect.get_x() + rect.get_width()/2., height+(max_height/15),
                            '{:.1%}'.format(height), ha='center', va='bottom', fontweight='bold')

        if bar_labels:
            autolabel(rects)
        #Title with the question summary
        plt.suptitle(t=polls[selection][0], fontweight="bold")
        #Output the plot
        plt.show()
        #Print out the sample size and number of NaNs (if any)
        print("N = {}".format(self.data.shape[0]))
        try:
            print("NaNs (percentage): {}".format(nans[1]))
        except IndexError:
            pass
