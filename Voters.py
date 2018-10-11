import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('seaborn')
from polls import polls


#USEFUL FUNCTIONS:
def convert_to_percentages(array, weighted=False, sanity_check=False):
    """
    Converts an array of counts to percentages of the total

    ### inputs ###
    array (list, numpy array) -- array of counts

    ### outputs ###
    unique_elements (list) -- unique elements from array
    percs (numpy array) -- percentages for each element
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

    #Sanity checking
    def sanity_checker():
        if np.sum(percs) == 1.0:
            print("Sanity confirmed!")
        else:
            print("Sanity in question...")
    if sanity_check:
        sanity_checker()

    return unique_elements, percs

#VOTER class
class Voters:
    """Class for working with YouGov VOTER Study poll"""
    def __init__(self, data='./VOTER_Survey_December16_Release1.csv'):
        if isinstance(data, str):
            self.data = pd.read_csv(data)
        else:
            self.data = data

    def __add__(self, other):
        return Voters(data=pd.concat([self.data, other.data], axis=1))

    def __sub__(self, other):
        return Voters(data=self.data.drop(other.data.columns, axis=1))

    def get_column(self, column_label):
        column = pd.DataFrame(self.data[column_label].fillna(value=-1.0))
        return Voters(data=column)

    def get_voters(self, column_label, selection):
        voters = self.data[:][self.data[column_label] == selection].fillna(value=-1.0)
        voters = voters.drop(column_label, axis=1)
        return Voters(data=voters)

    def extract(self, selection="", weighted=False):
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

        if selection == "":
            if not weighted:
                opts, percs = convert_to_percentages(self.extract())
            else:
                opts, percs = convert_to_percentages(self.extract(weighted=True), weighted=True)
            selection = self.data.columns[0]
        else:
            if not weighted:
                opts, percs = convert_to_percentages(self.extract(selection=selection))
            else:
                opts, percs = convert_to_percentages(self.extract(selection=selection, weighted=True), weighted=True)

        opts = np.array(opts)
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

        f, ax = plt.subplots()
        opts = np.sort(opts)
        if not ft:
            if rotate_labels:
                plt.xticks(opts, polls[selection][3], rotation=45, ha="right")
            else:
                plt.xticks(opts, polls[selection][3])
        else:
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

        rects = ax.bar(opts, percs)

        def autolabel(rects):
            max_height = max([rect.get_height() for rect in rects])
            for rect in rects:
                height = rect.get_height()
                if height > max_height/4.0:
                    ax.text(rect.get_x() + rect.get_width()/2., height-(max_height/15),
                            '{:.1%}'.format(height), ha='center', va='bottom', fontweight='bold')
                else:
                    ax.text(rect.get_x() + rect.get_width()/2., height+(max_height/15),
                            '{:.1%}'.format(height), ha='center', va='bottom', fontweight='bold')

        if bar_labels:
            autolabel(rects)

        plt.suptitle(t=polls[selection][0], fontweight="bold")
        plt.show()
        print("N = {}".format(self.data.shape[0]))
        try:
            print("NaNs (percentage): {}".format(nans[1]))
        except IndexError:
            pass
