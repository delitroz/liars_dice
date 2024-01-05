import cv2
import numpy as np
import time
import collections

from .ip import detect_dices, dices_bboxes_overlay

class Player():

    def __init__(self, name):

        self.name = name
        self.score = 0
        self.dices_values = None
        self.bet_occurence = 0
        self.bet_value = 0


    def roll_dices(self, nb_dices):
        self.dices_values = np.random.randint(low=1, high=7, size=nb_dices)


    def set_dices_values(self, dices_values):
        self.dices_values = dices_values


    def print_roll(self):
        print(f"{self.name} rolled: {' '.join([str(d) for d in self.dices_values])}")


    def check_bet(self, all_dices):
        bet_value_occurences = np.count_nonzero(all_dices == self.bet_value)
        return bet_value_occurences == self.bet_occurence


    def reset(self):
        self.dices = None
        self.bet_number = 0
        self.bet_values = 0


class HumanPlayer(Player):

    def __init__(self, name):
        super().__init__(name)

    
    def roll_dices_camera(self, nb_dices, camera):

        print("\nRoll the dices!")
        cap = cv2.VideoCapture(camera)
        dices_tmp = {
            "time": time.time(),
            "values": [],
        }
        while(True):
            ret, frame = cap.read()
            obj_lst = detect_dices(frame)
            overlay = dices_bboxes_overlay(frame, obj_lst)
            cv2.imshow("", overlay)

            dices = [o.value for o in obj_lst]
            nb_played_dices = len(dices)

            if (nb_played_dices != 0) & (nb_played_dices == nb_dices):
                frame_time = time.time()

                if dices_tmp["values"] == []:
                    dices_tmp["time"] = frame_time
                    dices_tmp["values"] = dices

                # validate the throw when values are stable for 1 second
                else:
                    if frame_time - dices_tmp["time"] >= 1:
                        if (
                            collections.Counter(dices) == collections.Counter(dices_tmp["values"])
                        ):
                            self.set_dices_values(dices)
                            break
                            

                        else:
                            dices_tmp["time"] = frame_time
                            dices_tmp["values"] = dices

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

    
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
                    self.bet_occurence = first
                    self.bet_value = second
                    break


class RobotPlayer(Player):

    def __init__(self, name):
        super().__init__(name)


def get_all_dices(player1, player2):
    return np.concatenate([player1.dices_values, player2.dices_values], axis=0)