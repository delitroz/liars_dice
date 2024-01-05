import numpy as np
import cv2
import collections
import time

from src.camera_utils import select_camera
from src.ip import detect_dices, dices_bboxes_overlay
from src.gameplay import HumanPlayer, RobotPlayer, get_all_dices


if __name__ == "__main__":

    camera = select_camera()
    cv2.destroyAllWindows()   # Necessary otherwise the window for camera selection don't go away

    nb_dices = 5
    player = HumanPlayer(name="you")
    cpu = RobotPlayer(name="cpu")

    round = 1
    while(True):
        print(f"\n\n----- Round {round} -----")

        player.reset()
        cpu.reset()

        cpu.roll_dices(nb_dices)
        player.roll_dices_camera(nb_dices, camera)
        

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