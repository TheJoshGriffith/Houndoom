from rotom import Rotom


class Watchdog:
    def __init__(self):
        self.rotom = Rotom()
        pass

    def loop(self):
        self.rotom.iterate_atvs()
        self.rotom.iterate_workers()
        pass