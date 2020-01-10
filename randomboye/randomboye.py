# from discogs_collection import DiscogsCollection
# from signal import pause
from raspi_io_diagnoser import RaspberryPiIODiagnoser
import pygame


def main():
    pygame.init()
    print("Ran Main Randomboye")
    pi = RaspberryPiIODiagnoser()


if __name__ == '__main__':
    main()
