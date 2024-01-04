import numpy as np
import cv2
import collections
import time

import warnings
warnings.filterwarnings("ignore")

from src.ip import detect_dices, dices_bboxes_overlay
from src.gameplay import Player, get_all_dices



if __name__ == "__main__":

    nb_dices = 5
    player = Player(name="you")
    cpu = Player(name="cpu")

    round = 1
    while(True):
        print(f"\n\n----- Round {round} -----")

        player.reset()
        cpu.reset()

        cpu.roll_dices(nb_dices)

        # Player roll the dices
        cap = cv2.VideoCapture(0)
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
                            player.set_dices(dices)
                            break
                        else:
                            dices_tmp["time"] = frame_time
                            dices_tmp["values"] = dices

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cap.release()

        print("")
        player.print_roll()
        print("")
        player.bet(2 * nb_dices)

        all_dices = get_all_dices(player, cpu)
        win = player.check_bet(all_dices)

        print("")
        player.print_roll()
        cpu.print_roll()
        if win:
            print("You won!")
            player.score += 1
        else:
            print("You lost")

        cont = input("\nPlay a next round? (y/n):    ")
        if cont == "n":
            print(f"\nGame over.\nYou scored {player.score} point(s)\n")

            cv2.destroyAllWindows()

            break
        round += 1