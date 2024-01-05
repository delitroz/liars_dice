from src.gameplay import ask_player_name, ask_nb_cpus, Game


if __name__ == "__main__":

    player_name = ask_player_name()
    nb_cpus = ask_nb_cpus()
    nb_dices = 5

    game = Game(player_name, nb_cpus, nb_dices)
    game.play()