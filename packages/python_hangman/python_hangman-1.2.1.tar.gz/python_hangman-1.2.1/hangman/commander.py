# coding=utf-8
from . import Hangman, GameOver, GameWon
from . import Presenter


class Commander(object):
    def __init__(self, hangman=Hangman, presenter=Presenter):
        self.game = hangman()
        self.presenter = presenter()

    @classmethod
    def run(cls, hangman=Hangman, presenter=Presenter):
        self = cls(hangman=hangman, presenter=presenter)
        flash = None
        play_again = False
        while True:
            self.presenter.write(self.game, message=flash)
            flash = None
            guess = self.presenter.prompt()
            try:
                self.game.guess(guess)
            except GameOver:
                self.presenter.write(self.game, game_over=True)
                play_again = self.presenter.play_again_prompt()
                break
            except GameWon:

                self.presenter.write(self.game, game_won=True)
                play_again = self.presenter.play_again_prompt()
                break
            except ValueError as e:
                flash = e.message
                continue
        if play_again:
            del self
            cls.run(hangman=hangman, presenter=presenter)
        else:
            self.presenter.goodbye()
            return self