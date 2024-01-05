from src.gameplay import ask_player_name, ask_nb_cpus, Game


if __name__ == "__main__":

    # player_name = ask_player_name()
    player_name = "Player"

    # nb_cpus = ask_nb_cpus()
    nb_cpus = 4

    nb_dices = 3

    game = Game(player_name, nb_cpus, nb_dices)
    game.play()
