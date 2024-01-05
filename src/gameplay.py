import numpy as np
import random
import time


def ask_player_name():
    """Asks the player for their name.

    Returns:
        str: Player's name
    """
    print("")
    return input("What's your name?   ")


def ask_nb_cpus():
    """Asks the player how many computer-controlled opponents to play against.

    Returns:
        int: Number of opponents
    """
    time.sleep(0.5)
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

    return nb_cpus


class Bid:
    def __init__(self, player_name, occurence, value, challenged_by):
        """Constructor of the bid class.

        Args:
            player_name (str): Name of the player placing the bid
            occurence (int): Occurence of a particular value on all dices
            value (int): Dice value
            challenged_by (str): Name of the player challenging this bid
        """
        self.player_name = player_name
        self.occurence = occurence
        self.value = value
        self.challenged_by = challenged_by


class Player:
    def __init__(self, name, nb_dices):
        """Constructor of the Player class.

        Args:
            name (str): Player's name
            nb_dices (int): Player's initial number of dices
        """
        self.name = name
        self.nb_dices = nb_dices
        self.dices_values = []

    def roll_dices(self):
        """Rolls the dices"""
        self.dices_values = np.random.randint(low=1, high=7, size=self.nb_dices)

    def disclose_dices(self):
        """Prints the values of the dices rolled"""
        time.sleep(0.5)
        print(f"{self.name} rolled: {self.dices_values}")

    def remove_dice(self):
        """Removes a dice from the player"""
        time.sleep(0.5)
        if self.nb_dices > 0:
            self.nb_dices -= 1
            print(f"\n{self.name} lost a dice and has now {self.nb_dices} left")
        else:
            print(f"\n{self.name} has no dices left and was eliminated!")


class HumanPlayer(Player):
    def __init__(self, name, nb_dices):
        """Constructor for the human player class

        Args:
            name (str): Player's name
            nb_dices (int): Player's initial number of dices
        """
        super().__init__(name, nb_dices)

    def challenge_last_bid(self, last_bid):
        """Asks the player if they want to challenge the last bid. If yes
        update the last bid "challenged_by" argument to the player's name.

        Args:
            last_bid (object Bid): Last bid

        Returns:
            obect Bid: Updated last bid
        """
        time.sleep(0.5)
        challenge = input("Challenge the last bid? (y/n): ")
        if challenge == "y":
            last_bid.challenged_by = self.name
        return last_bid

    def place_bid(self, last_bid):
        """Asks the player which bid they want to place. Update the last bid
        accordingly.

        Args:
            last_bid (object Bid): Last bid

        Returns:
            object Bid: Updated Bid
        """
        while True:
            time.sleep(0.5)
            s = input("Place your bid! (int:occurences int:value): ")
            parts = s.split()

            # check valid format
            if len(parts) != 2 or not all(part.isdigit() for part in parts):
                print("Error: Input bid be two integers separated by a space.")
            else:
                occurence, value = map(int, parts)
                if not 1 <= value <= 6:
                    print("Error: The value must be between 1 and 6.")
                else:
                    # check if bid raised
                    if (
                        (occurence > last_bid.occurence and value == last_bid.value)
                        or (occurence == last_bid.occurence and value > last_bid.value)
                        or (occurence > last_bid.occurence and value > last_bid.value)
                    ):
                        last_bid.player_name = self.name
                        last_bid.occurence = occurence
                        last_bid.value = value
                        break
                    else:
                        print(f"You have to raise the bid!")

        return last_bid


class CpuPlayer(Player):
    def __init__(self, name, nb_dices):
        """Constructor for the cpu player class

        Args:
            name (str): Player's name
            nb_dices (int): Player's initial number of dices
        """
        super().__init__(name, nb_dices)

    # TODO improve AI
    def challenge_last_bid(self, last_bid, total_nb_dice):
        """Potentially challenges the last bid made. If last bid is challenged,
        update the "challenged_by" argument to the player's name.

        Args:
            last_bid (object Bid): Last bid
            total_nb_dice (int): Total number of dices in the game

        Returns:
            object Bid: Updated last bid
        """

        rand = random.uniform(0, 1)
        p = 0.1
        if (rand < p) or (last_bid.occurence > total_nb_dice):
            last_bid.challenged_by = self.name

        return last_bid

    # TODO improve AI
    def place_bid(self, last_bid, total_nb_dice):
        """Places a bid

        Args:
            last_bid (object Bid): Last bid
            total_nb_dice (int): Total number of dices in the game

        Returns:
            object Bid: Updated last bid
        """
        last_bid.player_name = self.name
        if last_bid.value == 6:
            last_bid.occurence += 1
        else:
            rand = random.uniform(0, 1)
            p = 0.5
            last_bid.player_name = self.name
            if rand < p:
                last_bid.occurence += 1
            else:
                last_bid.value += 1
        time.sleep(0.5)
        print(f"{self.name} raised the bid to {last_bid.occurence} {last_bid.value}")
        return last_bid


class Game:
    def __init__(self, player_name, nb_cpus, nb_dices):
        """Constructor of the Game class

        Args:
            player_name (str): Player's name
            nb_cpus (_type_): Number of computer-controlled oponents
            nb_dices (_type_): Initial number of dices for each player
        """

        self.round = 1
        self.human_player = HumanPlayer(name=player_name, nb_dices=nb_dices)
        self.cpu_players = [
            CpuPlayer(name=f"cpu{i}", nb_dices=nb_dices) for i in range(nb_cpus)
        ]
        self.all_players = [self.human_player] + self.cpu_players
        self.nb_players = len(self.all_players)
        self.total_nb_dice = nb_dices * self.nb_players
        print(
            f"\nStarting a new game of {self.nb_players} players with {nb_dices} dices each."
        )

    def bid_round(self):
        """Plays a round of bidding.

        Returns:
            object Bid: Last bid made in the round
        """
        bid_round = 1
        last_bid = Bid(
            player_name="nobody", occurence=0, value=0, challenged_by="nobody"
        )

        while True:
            if bid_round == 1:  # no challenge allowed for first player
                last_bid = self.human_player.place_bid(last_bid)
            else:
                last_bid = self.human_player.challenge_last_bid(last_bid)
                if last_bid.challenged_by != "nobody":
                    break
                else:
                    last_bid = self.human_player.place_bid(last_bid)

            for p in self.cpu_players:
                last_bid = p.challenge_last_bid(last_bid, self.total_nb_dice)
                if last_bid.challenged_by != "nobody":
                    break
                else:
                    last_bid = p.place_bid(last_bid, self.total_nb_dice)

            if last_bid.challenged_by != "nobody":
                break

            bid_round += 1

        return last_bid

    def check_bid(self, bid):
        """Check if a bid is valid and return the the looser. If the bid
        is valid, the looser is the player that challenged it, if not, the looser
        is the player that placed that bid

        Args:
            bid (oject Bid): Last bid of the bidding round

        Returns:
            object Player: Looser of the bidding round
        """
        all_dices = np.concatenate([p.dices_values for p in self.all_players], axis=0)
        bid_value_occurences = np.count_nonzero(all_dices == bid.value)
        time.sleep(0.5)
        print("")
        print(f"There are {bid_value_occurences} {bid.value}s on the table")

        bid_valid = bid_value_occurences == bid.occurence
        if bid_valid:
            print(
                f"{bid.challenged_by} shouldn't have challenged {bid.player_name}'s bid!"
            )
        else:
            print(
                f"{bid.challenged_by} was right to challenge {bid.player_name}'s bid!"
            )

        looser_name = bid.challenged_by if bid_valid else bid.player_name

        return next((p for p in self.all_players if p.name == looser_name))

    def play_round(self):
        """Plays a full round"""
        print(f"\n\n---------- Round {self.round} ----------")
        print(f"{self.total_nb_dice} dices are still in the game.")
        for p in self.all_players:
            print(f"   {p.name} has {p.nb_dices} left.")

        # all players roll their dices
        self.human_player.roll_dices()
        for p in self.cpu_players:
            p.roll_dices()

        # player have their roll presented to them
        time.sleep(0.5)
        print("")
        self.human_player.disclose_dices()

        # bid time!
        print("")
        last_bid = self.bid_round()
        time.sleep(0.5)
        print(
            f"\n{last_bid.challenged_by} challenged {last_bid.player_name}'s last bid of {last_bid.occurence} {last_bid.value}!"
        )

        # all dices are revealed
        time.sleep(0.5)
        print("")
        self.human_player.disclose_dices()
        for p in self.cpu_players:
            p.disclose_dices()

        # get the looser of the bid round
        looser = self.check_bid(last_bid)

        # remove a dice from the looser
        looser.remove_dice()
        self.total_nb_dice -= 1
        self.round += 1

    def play(self):
        """Plays the game"""
        while True:
            self.play_round()

            # end game if player has 0 dice
            if self.human_player.nb_dices == 0:
                time.sleep(0.5)
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
                time.sleep(0.5)
                print(f"\nNo cpu players remaining.\n{self.human_player.name} won!\n")
                break
