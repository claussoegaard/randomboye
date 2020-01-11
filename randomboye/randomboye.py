# from discogs_collection import DiscogsCollection
# from signal import pause
from raspi_io_diagnoser import RaspberryPiIODiagnoser
import pygame


def main():
    pygame.init()
    print("Ran Main Randomboye")
    pi = RaspberryPiIODiagnoser()

    run = True
    while run:
        # pause()
        # pygame.time.delay(100)
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         run = False

    pygame.quit() 


if __name__ == '__main__':
    main()
