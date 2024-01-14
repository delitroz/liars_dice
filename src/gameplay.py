import numpy as np
import random
import time

from scipy.stats import binom


def ask_player_name():
    """Asks the player for their name.

    Returns
    -------
    str
        Player's name
    """
    print("")
    player_name = input("What's your name? ")
    time.sleep(0.5)
    return player_name

def ask_nb_cpus():
    """Asks the player how many computer-controlled opponents to plaz against.

    Returns
    -------
    int
        Number of opponents
    """
    print("")
    while True:
        try:
            nb_cpus = int(input("How many opponents do you want (1-4)?   "))
            if 1 <= nb_cpus <= 4:
                break
            else:
                print("Invalid input. Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    time.sleep(0.5)
    return nb_cpus

class Bid:
    """Class implementing a bid."""

    def __init__(self, player_name, count, value, challenged_by):
        """
        Parameters
        ----------
        player_name : str
            Name of the player placing the bid
        count : int
            Cont of a particular value on all dices
        value : int
            Dice value
        challenged_by : str
            Name of the plaxer challenging this bid
        """
        self.player_name = player_name
        self.count = count
        self.value = value
        self.challenged_by = challenged_by


class Player:
    """Class implementing a player."""

    def __init__(self, name, nb_dices):
        """
        Parameters
        ----------
        name : str
            Player's name
        nb_dices : int
            Player's initial number of dices
        """
        self.name = name
        self.nb_dices = nb_dices
        self.dices_values = []

    def roll_dices(self):
        """Rolls the dices"""
        self.dices_values = np.random.randint(low=1, high=7, size=self.nb_dices)

    def disclose_dices(self):
        """Prints the values of the dices rolled"""
        print(f"{self.name} rolled: {self.dices_values}")
        time.sleep(0.5)

    def remove_dice(self):
        """Removes a dice from the player"""
        if self.nb_dices > 0:
            self.nb_dices -= 1
            print(f"\n{self.name} lost a dice and has now {self.nb_dices} left")
        else:
            print(f"\n{self.name} has no dices left and was eliminated!")
        time.sleep(0.5)


class HumanPlayer(Player):
    
    def __init__(self, name, nb_dices):
        """
        Parameters
        ----------
        name : str
            Player's name
        nb_dices : int
            Player's initial number of dices
        """
        super().__init__(name, nb_dices)

    def challenge_last_bid(self, last_bid, total_nb_dices):
        """Asks the player if they want to challenge the last bid. If yes, update
        the last bid "challenged_by" argument to the player's name.

        Parameters
        ----------
        last_bid : Bid
            Last bid
        total_nb_dices : int
            Always unused. Only for consistency with CpuPlayer counterpart.

        Returns
        -------
        Bid
            Updated last bid
        """
        while True:
            challenge = input("Challenge the last bid? (y/n): ")
            if challenge == "y":
                last_bid.challenged_by = self.name
                break
            elif challenge == "n":
                break
            else:
                print(f"   Invalid input: should be 'y' or 'n'")
        time.sleep(0.5)
        return last_bid 

    def place_bid(self, last_bid, total_nb_dices):
        """Asks the player which bid they want to place.

        Parameters
        ----------
        last_bid : Bid
            Last Bid
        total_nb_dices : int
            Always unused. Only for consistency with CpuPlayer counterpart.

        Returns
        -------
        _type_
            _description_

        Raises
        ------
        the
            _description_
        """
        bid = Bid(player_name=self.name, count=0, value=0, challenged_by=None)

        while True:
            s = input("Place your bid! (count value): ")
            parts = s.split()
            # check valid format
            if len(parts) != 2 or not all(part.isdigit() for part in parts):
                print("   Invalid input: should be two integers separated by a space.")
            else:
                count, value = map(int, parts)
                if (
                    (count > last_bid.count and value == last_bid.value)
                    or (count == last_bid.count and value > last_bid.value)
                    or (count > last_bid.count and value > last_bid.value)
                ):
                    bid.count = count
                    bid.value = value
                    break
                else:
                    print(f"   Invalid input: You have to raise the bid!")
        time.sleep(0.5)
        return bid


class CpuPlayer(Player):
    """Class implementing a computer-controlled player"""

    def __init__(self, name, nb_dices):
        """
        Parameters
        ----------
        name : str
            Player's name
        nb_dices : int
            Player's initial number of dices
        """
        super().__init__(name, nb_dices)

    def compute_bid_proba(self, bid, total_nb_dices):
        """Compute the probility that a bid is valid.

        Parameters
        ----------
        bid : Bid
            Bid
        total_nb_dices : int
            Total number of dices in the game

        Returns
        -------
        float
            Probability that the bid is valid
        """
        bid_value_own_count = np.count_nonzero(self.dices_values == bid.value)
        bid_value_count_left = bid.count - bid_value_own_count
        nb_opponents_dices = total_nb_dices - self.nb_dices

        p_bid_valid = sum(
            binom.pmf(k, nb_opponents_dices, 1 / 6)
            for k in range(bid_value_count_left, nb_opponents_dices + 1)
        )

        return p_bid_valid

    def challenge_last_bid(self, last_bid, total_nb_dices):
        """Potentially challenges the last bid made. If last bid is challenged,
        update the "challenged_by" argument to the player's name.

        Parameters
        ----------
        last_bid : Bid
            Last bid
        total_nb_dices : int
            Total number of dices in the game

        Returns
        -------
        Bid
            Updated last bid
        """
        challenge_reason = None

        # always challenge aberrant bids
        if (last_bid.count > total_nb_dices) or not (1 <= last_bid.value <= 6):
            last_bid.challenged_by = self.name
            challenge_reason = "abberrant bid"

        # challenge when probability that last bid is valid is low
        p_bid_valid = self.compute_bid_proba(last_bid, total_nb_dices)
        if p_bid_valid < 0.3:
            last_bid.challenged_by = self.name
            challenge_reason = "low proba"

        # small probability of bluffing
        if p_bid_valid < 0.5:
            p_bluff = 0.1
            if random.uniform(0, 1) < p_bluff:
                last_bid.challenged_by = self.name
                challenge_reason = "bluff"

        # # Debugging logs
        # print(f"\n[DEBUG] {self.name} challenge decision")
        # print(f"[DEBUG]    last bid: {last_bid.count} {last_bid.value}")
        # print(f"[DEBUG]    rolled {self.dices_values}")
        # print(f"[DEBUG]    last bid proba: {p_bid_valid:.6f}")
        # if challenge_reason:
        #     print(f"[DEBUG]    challenge: {challenge_reason}")
        # else:
        #     print("[DEBUG]    no challenge")

        return last_bid

    def generate_k_random_bid(self, k, last_bid, total_nb_dices):
        """Given the last bid, generates k pseudo-random new bids that satisfy the game rules.

        Parameters
        ----------
        k : int
            Number of bids to generate
        last_bid : Bid
            Last Bid
        total_nb_dices : int
            Total number of dices in the game

        Returns
        -------
        List[Bid]
            List of random valid bids      
        """

        bids = []
        for i in range(k):

            if last_bid.value == 6:
                count_i = random.randint(
                    last_bid.count + 1, min(last_bid.count + 3, total_nb_dices)
                )
                value_i = last_bid.value

            elif last_bid.value == total_nb_dices:
                count_i = last_bid.count
                value_i = random.randint(last_bid.value + 1, 6)

            else:
                count_i = random.randint(
                    last_bid.count, min(last_bid.count + 3, total_nb_dices)
                )
                if count_i == last_bid.count:
                    value_i = random.randint(last_bid.value + 1, 6)
                else:
                    p = random.uniform(0, 1)
                    if p < 0.75:
                        value_i = last_bid.value
                    else:
                        value_i = random.randint(last_bid.value + 1, 6)

            bid_i = Bid(
                player_name=self.name,
                count=count_i,
                value=value_i,
                challenged_by=None,
            )

            bids.append(bid_i)

        return bids

    def place_bid(self, last_bid, total_nb_dices):
        """Places a bid

        Parameters
        ----------
        last_bid : Bid
            Last bid
        total_nb_dices : int
            Total number of dices in the game

        Returns
        -------
        Bid
            Bid
        """
        first_bid = False
        if last_bid.player_name is None:  # First bid
            first_bid = True
            value = random.choice(self.dices_values)
            own_count = np.count_nonzero(self.dices_values == value)
            count = own_count + random.randint(0, 2)
            bid = Bid(
                player_name=self.name, count=count, value=value, challenged_by=None
            )
        else:
            random_bids = self.generate_k_random_bid(10, last_bid, total_nb_dices)
            random_bids_probas = [
                self.compute_bid_proba(b, total_nb_dices) for b in random_bids
            ]
            most_probable_idx = max((v, i) for i, v in enumerate(random_bids_probas))[1]
            bid = random_bids[most_probable_idx]

        # # Debugging logs
        # print(f"\n[DEBUG] {self.name} bidding decision")
        # if first_bid:
        #     print(f"[DEBUG]    plays first")
        #     print(f"[DEBUG]    rolled {self.dices_values}")
        # else:
        #     print("[DEBUG]    raises bid")
        #     print(f"[DEBUG]    last bid: {last_bid.count} {last_bid.value}")
        #     print(f"[DEBUG]    rolled {self.dices_values}")
        #     for i in range(len(random_bids)):
        #         print(
        #             f"[DEBUG]       random_bid_{i}: count={random_bids[i].count}, value={random_bids[i].value}, proba={random_bids_probas[i]:.4f}"
        #         )

        if first_bid:
            print(f"{self.name} placed a first bid of {bid.count} {bid.value}")
        else:
            print(f"{self.name} raised the bid to {bid.count} {bid.value}")

        time.sleep(0.5)

        return bid


class Game:
    """Class implementing a game"""

    def __init__(self, player_name, nb_cpus, nb_dices):
        """
        Parameters
        ----------
        player_name : str
            Player's name
        nb_cpus : int
            Number of computer-controlled opponents
        nb_dices : int
            Initial number of dices for each player
        """
        self.round = 1
        self.human_player = HumanPlayer(name=player_name, nb_dices=nb_dices)
        self.cpu_players = [
            CpuPlayer(name=f"cpu{i}", nb_dices=nb_dices) for i in range(nb_cpus)
        ]
        self.all_players = [self.human_player] + self.cpu_players
        self.nb_players = len(self.all_players)
        self.total_nb_dices = nb_dices * self.nb_players
        print(
            f"\nStarting a new game of {self.nb_players} players with {nb_dices} dices each."
        )
        time.sleep(0.5)

    def play_bid_round(self):
        """Plays a round of bidding.

        Returns
        -------
        Bid
            Last bid made in the round
        """
        bid_round = 0
        last_bid = Bid(player_name=None, count=0, value=0, challenged_by=None)

        while True:
            for i, p in enumerate(self.all_players):
                if (i == 0) and (bid_round == 0):
                    last_bid = p.place_bid(last_bid, self.total_nb_dices)
                else:
                    last_bid = p.challenge_last_bid(last_bid, self.total_nb_dices)
                    if last_bid.challenged_by is not None:
                        break
                    else:
                        last_bid = p.place_bid(last_bid, self.total_nb_dices)

            if last_bid.challenged_by is not None:
                break

            bid_round += 1

        return last_bid

    def check_bid(self, bid):
        """Check if a bid is valid and return the the looser. If the bid
        is valid, the looser is the player that challenged it, if not, the looser
        is the player that placed that bid

        Parameters
        ----------
        bid : Bid
            Last bid of the bidding round

        Returns
        -------
        Player
            Looser of the bidding round
        """
        all_dices = np.concatenate([p.dices_values for p in self.all_players], axis=0)
        true_count = np.count_nonzero(all_dices == bid.value)
        bid_valid = true_count >= bid.count

        print("")
        print(f"There are {true_count} {bid.value}s on the table")
        time.sleep(0.25)
        if bid_valid:
            print(
                f"{bid.challenged_by} shouldn't have challenged {bid.player_name}'s bid!"
            )
        else:
            print(
                f"{bid.challenged_by} was right to challenge {bid.player_name}'s bid!"
            )
        time.sleep(0.5)

        looser_name = bid.challenged_by if bid_valid else bid.player_name
        looser = next((p for p in self.all_players if p.name == looser_name))

        return looser

    def play_round(self):
        """Plays a full round"""
        print(f"\n\n---------- Round {self.round} ----------")
        print(f"\n{self.total_nb_dices} dices are still in the game.")
        for p in self.all_players:
            print(f"   {p.name} has {p.nb_dices} left.")
        time.sleep(0.5)

        # all players roll their dices
        self.human_player.roll_dices()
        for p in self.cpu_players:
            p.roll_dices()

        # player have their roll presented to them
        print("")
        self.human_player.disclose_dices()

        # bid time!
        print("")
        last_bid = self.play_bid_round()
        print(
            f"\n{last_bid.challenged_by} challenged {last_bid.player_name}'s last bid of {last_bid.count} {last_bid.value}!"
        )
        time.sleep(0.5)

        # all dices are revealed
        print("")
        self.human_player.disclose_dices()
        for p in self.cpu_players:
            p.disclose_dices()
        time.sleep(0.5)

        # get the looser of the bid round
        looser = self.check_bid(last_bid)

        self.round += 1

        return looser

    def play(self):
        """Plays the game"""
        while True:
            looser = self.play_round()

            # reorder players for next round (looser starts first)
            looser_idx = self.all_players.index(looser)
            self.all_players = (
                self.all_players[looser_idx:] + self.all_players[:looser_idx]
            )

            # remove a dice from the looser
            looser.remove_dice()
            self.total_nb_dices -= 1

            # end game if player has 0 dice
            if self.human_player.nb_dices == 0:
                print(f"\n{self.human_player.name} has no dice left.\nGame over\n")
                break

            # remove cpus players with no dices left
            for p in self.cpu_players:
                if p.nb_dices == 0:
                    self.cpu_players.remove(p)
                    self.all_players.remove(p)
                    self.nb_players = len(self.all_players)

            # end game if no cpu players remaining
            if len(self.cpu_players) == 0:
                print(f"\nNo cpu players remaining.\n{self.human_player.name} won!\n")
                break

            time.sleep(0.5)
            while True:
                if input(f"\nPress Enter to continue   ") is not None:
                    break
