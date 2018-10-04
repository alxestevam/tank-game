import pygame
import threading


class Window(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name='Game window thread')
        pygame.init()
        self.win = pygame.display.set_mode((600, 600))
        self.clock = pygame.time.Clock()
        self.isRunning = True
        t = threading.Thread(target=self.start_game)
        t.setDaemon(True)
        t.start()

        while self.isRunning:
            for event in pygame.event.get():
                dt_s = float(self.clock.tick(60)) * 1e-3
                print('yep')
                if event.type == pygame.QUIT:
                    self.isRunning = False
        pygame.quit()

    def start_game(self):
        while True:
            self.win.fill((100, 100, 100))
            pygame.display.update()


if __name__ == '__main__':
    c = Window()