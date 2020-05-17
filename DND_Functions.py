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
        An array where each element is the result of the dice roll
    """
    n = int(n)
    if type(roll) == int:
        return np.ones(n) * roll
    elif len(roll) == 1:
        return np.ones(n) * int(roll)
    else:
        roll = roll.upper()
        (die, val) = list(map(int, roll.split('D')))
        return sum(np.random.randint(1, val + 1, size=(die, n)))


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
    n = int(n)
    hit_success_damage = np.zeros(n)
    hit_critical_damage = np.zeros(n)

    # Calculate Damage Assuming All Hits
    for action, roll in actions.items():

        # Don't include the hit modifier
        if action == 'hit':
            continue

        hit_success_damage += GetRollValue(roll, n)

        # Don't include the proficiency bonus for a critical
        if action == 'prof':
            continue

        # Roll again for a critical hit
        hit_critical_damage += GetRollValue(roll, n)

    # Check for Hit
    hit = GetRollValue('1D20', n)
    hit_success = hit + actions['hit'] >= ac
    hit_critical = hit == 20
    hit_absolute_miss = hit != 0

    # Tally up final damage
    hit_success_damage_final = hit_success_damage * hit_success
    hit_critical_damage_final = hit_critical_damage * hit_critical
    final_damage = hit_success_damage_final + hit_critical_damage_final
    final_damage *= hit_absolute_miss

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


def PlotAcDistribution(actions_list, acs, n, ignore_miss=True):
    """Plots the Monte Carlo distribution results versus armor class

    args:
        actions_list: list of dictionaries, or a single dictionary. A dictionary
            of all supplements for a given attack. Each key corresponds with
            the name of an effect to stack (ie hunter's mark, longbow...). Each
            value corresponds with the dice roll associated with the attack
            (ie 1D6, 1D8, ...). One of the key-value pairs should be "hit" to
            take into account your hit modifier.
        acs: list of ints. Various armor classes to calculate the distributions
            to.
        n: int. Number of simulations to run.
        ignore_miss: Bool. True if all attacks that result in a miss should be
            ignored.
    """
    if isinstance(actions_list, dict):
        actions_list = [actions_list]

    for ac in acs:

        sim_damage_results = 0

        for actions in actions_list:
            sim_damage_results += MonteCarloAttack(actions, ac, n=n)

        if ignore_miss:
            sim_damage_results = sim_damage_results[sim_damage_results > 0]

        frequency_dict = ReturnFrequencies(sim_damage_results)

        PlotFrequencies(frequency_dict, label=ac, markersize=3)

        plt.legend(loc='best', title='Armour Class')
        plt.grid(True)