import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('seaborn-muted')
from polls import polls

#VOTER class
class Voters:
    """Class for working with YouGov VOTER Study Group data

    Usage::
        >>> all_voters = Voters()
        >>> specific_voters = Voters().get_voters(column_label="<column_label>",
                                                selection="<answer id>")
        >>> specific_column = Voters().get_column(column_label="<column_label>")

        - To get access to the dataframe itself:
        >>> voter_instance.data

    :param data: largely unecessary to worry about. Loads the entire
    YouGov dataset if initialized on its own, and copies the DataFrame
    from other instances if manipulating with the function below
    """
    def __init__(self, data='./VOTER_Survey_December16_Release1.csv',
                       voter_label="All Voters"):
        if isinstance(data, str):
            self.data = pd.read_csv(data)
            self.voter_label = voter_label
        else:
            self.data = data
            self.voter_label = voter_label

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
            - To select the column for 2016 Presidential Election vote
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
            - To get dataframe of Hillary voters in 2016 Presidential Election
            >>> Voters().get_voters(column_label="presvote16post_2016",
                                    selection=1)

        """
        voters = self.data[:][self.data[column_label] == selection].fillna(value=-1.0)
        voters = voters.drop(column_label, axis=1)

        answer_idx = np.where(np.array(polls[column_label][2]) == selection)
        _voter_label = polls[column_label][3][int(answer_idx[0])]

        return Voters(data=voters, voter_label=_voter_label)

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

    def _convert_to_percentages(self, array, sanity_check=False):
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
        if len(array) == 1:
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

    def _collect_unsure(self, opts, percs, show_not_sure):
        """Collects info on miscelaneous options we don't care about and
        deletes them from the opts array, so they're not plotted

        Parameters
        ----------
        opts : (numpy array)
            Array of response option identifiers
        percs : (numpy array)
            Array of percentages for each response
        show_not_sure : (bool)
            Show answers "not sure" on plot (if True)

        Returns
        -------
        opts : (numpy array)
            updated answer identifier array
        percs : (numpy array)
            updated percentages array
        nans : (list)
            updated array of NaN answers
        not_sure : (list)
            updates array of "not sure" answers

        """
        nans = []
        not_sure = []
        nan_opts = [-1, 31, 97, 997]
        for opt in nan_opts:
            if opt in opts:
                idx = np.where(np.array(opts).astype(int) == opt)
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
        return opts, percs, nans, not_sure

    def _autolabel(self, rects, ax, max_p=""):
        if max_p == "":
            max_p = max([rect.get_height() for rect in rects])
        else:
            max_p = max_p
        for rect in rects:
            height = rect.get_height()
            #Label below if large bar
            if height > max_p/4.0:
                ax.text(rect.get_x() + rect.get_width()/2., height-(max_p/15),
                        '{:.1%}'.format(height), ha='center', va='bottom', fontweight='bold')
            #Label above if small bar
            else:
                ax.text(rect.get_x() + rect.get_width()/2., height+(max_p/15),
                        '{:.1%}'.format(height), ha='center', va='bottom', fontweight='bold')


    def plot_percentages(self, selection="", rotate_labels=True, weighted=True,
                         bar_labels=True, ft=False, show_not_sure=False):
        """Plot bar chart of percentages of answers from the column on interest
        in the dataframe

        Args
        ----
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
            - Plot 2016 Presidential Election responses for all voters, weighted
            >>> Voters().plot_percentages(column_label="presvote16post_2016",
                                          rotate_labels=True, weighted=True)

        """
        #For single-column dataframe, no selection necessary
        if selection == "":
            if not weighted:
                opts, percs = self._convert_to_percentages(self._extract())
            else:
                opts, percs = self._convert_to_percentages(self._extract(weighted=True))
            selection = self.data.columns[0]
        else:
            if not weighted:
                opts, percs = self._convert_to_percentages(self._extract(selection=selection))
            else:
                opts, percs = self._convert_to_percentages(self._extract(selection=selection, weighted=True))

        opts, percs, nans, not_sure = self._collect_unsure(opts, percs, show_not_sure)

        #Sort the answer options
        order = np.argsort(opts)
        opts = opts[order]
        percs = percs[order]

        #Initialize plot
        f, ax = plt.subplots()

        #Normal plots
        if not ft:
            if rotate_labels:
                plt.xticks(opts, polls[selection][3], rotation=45, ha="right")
            else:
                plt.xticks(opts, polls[selection][3])
            #Bar chart
            rects = ax.bar(opts, percs)

        #Feelings Thermometer plots
        else:
            #Collecting feelings thermometer answers in to bins
            ft_bins = np.linspace(0,100,11)
            new_percs = np.zeros(len(ft_bins))
            i = 0
            for j in range(len(opts)):
                if opts[j] < ft_bins[i+1]:
                    new_percs[i] += percs[j]
                else:
                    new_percs[i+1] += percs[j]
                    i += 1
            opts = ft_bins
            bar_width = 0.8*(100/11)
            percs = new_percs

            #Bar chart
            rects = ax.bar(opts, percs, bar_width)

            if rotate_labels:
                plt.xticks([0.0, 25.0, 50.0, 75.0, 100.0],
                           ["Very Cold", "Cold", "None", "Warm", "Very Warm"],
                           rotation=45, ha="right")
            else:
                plt.xticks([0.0, 25.0, 50.0, 75.0, 100.0],
                           ["Very Cold", "Cold", "None", "Warm", "Very Warm"])

        if bar_labels:
            self._autolabel(rects, ax)
        #Title with the question summary
        plt.suptitle(t=polls[selection][0], fontweight="bold")
        #Output the plot
        plt.show()
        #Print out the sample size and number of NaNs (if any)
        print("N = {}".format(self.data.shape[0]))
        try:
            print("NaNs (percentage): {:.1%}".format(nans[1][0]))
        except IndexError:
            pass
        def save(title="voter_data_plot.png"):
            plt.savefig(title, format="png")

    def plot_comparison(self, other, selection="", rotate_labels=True,
                        weighted=True, bar_labels=True, ft=False,
                        show_not_sure=False):
        """Plot bar chart of percentages of answers from the column on interest
        in the dataframe

        Args
        ----
        other : (class/Voters() instance)
            Voters() instance for another dataframe
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
            - Plot 2016 Presidential Election responses for all voters, weighted
            >>> Voters().plot_percentages(column_label="presvote16post_2016",
                                          rotate_labels=True, weighted=True)

        """
        ### WORKING ON THIS ###
        # opts = np.array([None]*(len(other)+1))
        # percs = np.array([None]*(len(other)+1))
        # opts[0], percs[0] = self._convert_to_percentages(self._extract())
        # if not weighted:
        #     for i in range(len(other)):
        #         opts[i+1], percs[i+1] = self._convert_to_percentages(other[i]._extract())
        # else:
        #     for i in range(len(other)):
        #         opts[i+1], percs[i+1] = self._convert_to_percentages(other[i]._extract(weighted=True))
        # nans = np.array([None]*(len(other)+1))
        # not_sure = np.array([None]*(len(other)+1))
        # for i in range(len(other) + 1):
        #     opts[i], percs[i], nans[i], not_sure[i] = self._collect_unsure(opts[i], percs[i], show_not_sure)
        #
        # max_p = max(percs)
        # order = np.array([None]*len(other)+1)
        # for i in range(len(other)+1):
        #     order[i] = np.argsort(opts[i])
        #     opts[i] = opts[i][order[i]]
        #     percs[i] = percs[order[i]]
        #
        # f, ax = plt.subplots()
        # if not ft:
        #     bar_width = 1/(len(order)+1)
        #     offsets = np.arange(1,len(opts))-(opts/2)
        #     for i in range(len(opts)):
        #         opts[i] = opts[i] + bar_width*offsets[i]
        #     if rotate_labels:
        #         plt.xticks(np.arange(1,(len(opts[i])+1)), polls[selection][3],
        #                    rotation=45, ha="right")
        #     else:
        #         plt.xticks(opts[i] + 0.5*bar_width, polls[selection][3])
        #
        #     rects = [None]*len(opts)
        #     for i in range(len(opts)):
        #         rects[i] = ax.bar(opts[i], percs[i], bar_width)
        # else:
        #     print("not working yet")
        #
        # #Title with the question summary
        # plt.suptitle(t=polls[selection][0], fontweight="bold")
        # #Legend
        # ax.legend((rects_1[0], rects_2[0]), (self.voter_label, other.voter_label))
        # #Output the plot
        # plt.show()
        # #Print out the sample size and number of NaNs (if any)
        # print("N_{} = {}".format(self.voter_label, self.data.shape[0]))
        # print("N_{} = {}".format(other.voter_label, other.data.shape[0]))
        # try:
        #     print("NaNs_{} (percentage): {:.1%}".format(self.voter_label, nans_1[1][0]))
        #     print("NaNs_{} (percentage): {:.1%}".format(other.voter_label, nans_2[1][0]))
        # except IndexError:
        #     pass
        # def save(title="voter_data_plot.png"):
        #     plt.savefig(title, format="png")

        #For single-column dataframe, no selection necessary
        if selection == "":
            if not weighted:
                opts_1, percs_1 = self._convert_to_percentages(self._extract())
                opts_2, percs_2 = self._convert_to_percentages(other._extract())
            else:
                opts_1, percs_1 = self._convert_to_percentages(self._extract(weighted=True))
                opts_2, percs_2 = self._convert_to_percentages(other._extract(weighted=True))
            if self.data.columns[0] == other.data.columns[0]:
                selection = self.data.columns[0]
            else:
                raise TypeError("Voters() instances must have the same column to compare")
        else:
            if not weighted:
                opts_1, percs_1 = self._convert_to_percentages(self._extract(selection=selection))
                opts_2, percs_2 = self._convert_to_percentages(other._extract(selection=selection))
            else:
                opts_1, percs_1 = self._convert_to_percentages(self._extract(selection=selection, weighted=True))
                opts_2, percs_2 = self._convert_to_percentages(other._extract(selection=selection, weighted=True))

        opts_1, percs_1, nans_1, not_sure_1 = self._collect_unsure(opts_1, percs_1, show_not_sure)
        opts_2, percs_2, nans_2, not_sure_2 = self._collect_unsure(opts_2, percs_2, show_not_sure)

        max_p = max(max(percs_1), max(percs_2))

        #Sort the answer options
        opts_1 = np.sort(opts_1)
        opts_2 = np.sort(opts_2)

        #Initialize plot
        f, ax = plt.subplots()

        #Normal plots
        if not ft:
            bar_width = 0.4
            opts_2 = opts_1 + bar_width
            if rotate_labels:
                plt.xticks(opts_1 + 0.5*bar_width , polls[selection][3],
                           rotation=45, ha="right")
            else:
                plt.xticks(opts_1 + 0.5*bar_width, polls[selection][3])

            #Bar chart
            rects_1 = ax.bar(opts_1, percs_1, bar_width)
            rects_2 = ax.bar(opts_2, percs_2, bar_width)
        #Feelings Thermometer plots
        else:
            #Collecting feelings thermometer answers in to bins
            def _collect(_opts, _percs, num_bins=11, side="left"):
                """Collecting FT percentage bars in to bins"""
                ft_bins = np.linspace(0,100,num_bins)
                new_percs = np.zeros(len(ft_bins))
                bar_width = 0.45*(100/num_bins)
                i = 0
                for j in range(len(_opts)):
                    if _opts[j] < ft_bins[i+1]:
                        new_percs[i] += _percs[j]
                    else:
                        new_percs[i+1] += _percs[j]
                        i += 1
                if side == "left":
                    opts = ft_bins
                else:
                    opts = ft_bins + bar_width
                percs = new_percs
                return opts, percs, bar_width

            opts_1, percs_1, bar_width_1 = _collect(opts_1, percs_1, side="left")
            opts_2, percs_2, bar_width_2 = _collect(opts_2, percs_2, side="right")

            #Bar chart
            rects_1 = ax.bar(opts_1, percs_1, bar_width_1, color="Blue")
            rects_2 = ax.bar(opts_2, percs_2, bar_width_2, color="Red")

            ft_ticks = np.array([0.0, 25.0, 50.0, 75.0, 100.0]) + (bar_width_1/2)
            if rotate_labels:
                plt.xticks(ft_ticks, ["Very Cold", "Cold", "None", "Warm", "Very Warm"],
                           rotation=45, ha="right")
            else:
                plt.xticks(ft_ticks, ["Very Cold", "Cold", "None", "Warm", "Very Warm"])

        if bar_labels:
            self._autolabel(rects_1, ax, max_p = max_p)
            self._autolabel(rects_2, ax, max_p = max_p)

        #Title with the question summary
        plt.suptitle(t=polls[selection][0], fontweight="bold")
        #Legend
        ax.legend((rects_1[0], rects_2[0]), (self.voter_label, other.voter_label))
        #Output the plot
        plt.show()
        #Print out the sample size and number of NaNs (if any)
        print("N_{} = {}".format(self.voter_label, self.data.shape[0]))
        print("N_{} = {}".format(other.voter_label, other.data.shape[0]))
        try:
            print("NaNs_{} (percentage): {:.1%}".format(self.voter_label, nans_1[1][0]))
            print("NaNs_{} (percentage): {:.1%}".format(other.voter_label, nans_2[1][0]))
        except IndexError:
            pass
        def save(title="voter_data_plot.png"):
            plt.savefig(title, format="png")
