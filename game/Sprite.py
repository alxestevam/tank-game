from abc import abstractmethod


class Sprite(object):

    @abstractmethod
    def show(self, win):
        pass
