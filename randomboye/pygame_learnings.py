import pygame


def main():
    """ Set up the game and run the main game loop """
    pygame.init()      # Prepare the pygame module for use
    surface_sz = 480   # Desired physical surface size, in pixels.

    # Create surface of (width, height), and its window.
    surface = pygame.display.set_mode((surface_sz, surface_sz))
    pygame.display.set_caption("Learnings")

    # Set up some data to describe a small rectangle and its color
    # small_rect = (300, 200, 150, 90)
    # some_color = (255, 0, 0)        # A color is a mix of (Red, Green, Blue)
    run = True
    while run:
        pygame.time.delay(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.draw.rect(surface, (255, 0, 0), (50, 50, 40, 60))

        pygame.display.update()

        # ev = pygame.event.poll()    # Look for any event
        # if ev.type == pygame.QUIT:  # Window close button clicked?
        #     break  # ... leave game loop

        # Update your game objects and data structures here...

        # We draw everything from scratch on each frame.
        # So first fill everything with the background color
        # main_surface.fill((0, 200, 255))

        # Overpaint a smaller rectangle on the main surface
        # main_surface.fill(some_color, small_rect)

        # Now the surface is ready, tell pygame to display it!
        # pygame.display.flip()

    pygame.quit()     # Once we leave the loop, close the window.


if __name__ == '__main__':
    main()
