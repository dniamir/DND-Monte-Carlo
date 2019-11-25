from matplotlib import pyplot as plt
import numpy as np
from collections import OrderedDict
from collections import Counter


def GetRollValue(roll, n):
    """Return a 2D numpy array of random rolls

    args:
        roll: string. The type of dice that needs to be rolled. ie 1D6, 2D8, ect
            If an int is given, this will assume that it is a flat damage
            modifier.
        n: The number of times to repeat the simulation

    returns:
        A 2D numpy array where rows correspond to the results of each dice roll,
        and the columns corresond with a different simulation
    """
    if type(roll) == int:
        return np.ones((1, n)) * roll
    elif len(roll) == 1:
        return np.ones((1, n)) * int(roll)
    else:
        roll = roll.upper()
        (die, val) = list(map(int, roll.split('D')))
        return np.random.randint(1, val + 1, size=(die, n))


def MonteCarloAttack(actions, ac=14, n=1e3):
    """Returns damage done to a target with the specified AC

    args:
        actions: Dict. A dictionary of all supplements for a given attack. Each
            key corresponds with the name of an effect to stack (ie hunter's
            mark, longbow...). Each value corresponds with the dice roll
            associated with the attack (ie 1D6, 1D8, ...). One of the key-value
            pairs should be "hit" to take into account your hit modifier.
        ac: int. The armor class of the target. Used to determine if an attack
            is successful.
        n: int. The number of Monte Carlo simulations to run.

    returns:
        final_damage: list of ints. The final damage done for each simulation
            iteration
    """
    results = {}
    n = int(n)
    final_val = np.zeros(n)

    # Calculate Damage Assuming All Hits
    for action, roll in actions.items():
        if action != 'hit':
            results[action] = GetRollValue(roll, n)
            for array in results[action]:
                final_val = final_val + array

    # Check for Hit
    hit = np.random.randint(1, 21, size=n) + actions['hit']
    hit = hit > ac
    final_damage = final_val * hit

    return final_damage


def ReturnFrequencies(list_of_values):
    """Gives the frequency (%) of each value in a list

    args:
        list_of_values: list of ints. A list of integers to count

    returns:
        frequency_dict: Dict. A dictionary where key corresponds with value
            int the original list and value corresponds with frequency of
            that value.
    """
    frequency_dict = OrderedDict()
    value_counts = Counter(list_of_values)
    total_counts = sum(value_counts.values())
    for key, value in sorted(value_counts.items()):
        frequency_dict[key] = float(value) / total_counts * 100

    return frequency_dict


def PlotFrequencies(frequency_dict, label=None, **kwargs):
    """Plots the frequency of a value vs. the value itself

    args:
        list_of_values: list of ints. A list of integers to count
    """
    values = []
    frequencies = []

    for value, frequency in frequency_dict.items():
        values += [value]
        frequencies += [frequency]

    plt.plot(values, frequencies, marker='o', markeredgecolor='black',
             label=label, **kwargs)
