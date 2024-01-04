import numpy as np

class Player():

    def __init__(self, name):

        self.name = name
        self.score = 0
        self.dices = None
        self.bet_number = 0
        self.bet_value = 0


    def roll_dices(self, nb_dices):
        self.dices = np.random.randint(low=1, high=7, size=nb_dices)


    def set_dices(self, dices):
        self.dices = dices


    def print_roll(self):
        print(f"{self.name} rolled: {' '.join([str(d) for d in self.dices])}")


    def bet(self, total_nb_dice):

        while True:
            s = input("Make your bet! (int:occurences int:value):    ")
            parts = s.split()
            if len(parts) != 2 or not all(part.isdigit() for part in parts):
                print("Error: Input should be two integers separated by a space.")
            else:
                first, second = map(int, parts)
                if first > total_nb_dice:
                    print(f"Error: The first integer is greater than the amount of dices in the game ({total_nb_dice}).")
                elif not 1 <= second <= 6:
                    print("Error: The second integer is not between 1 and 6.")
                else:
                    self.bet_number = first
                    self.bet_value = second
                    break


    def check_bet(self, all_dices):
        bet_value_occurences = np.count_nonzero(all_dices == self.bet_value)
        return bet_value_occurences == self.bet_number


    def reset(self):
        self.dices = None
        self.bet_number = 0
        self.bet_values = 0


def get_all_dices(player1, player2):
    return np.concatenate([player1.dices, player2.dices], axis=0)