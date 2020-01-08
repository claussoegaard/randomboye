import pygame


# class LCDScreen:
#     LCD_COLUMNS = 16
#     LCD_ROWS = 2
#     BACKGROUND_COLOR = (0, 200, 255)

#     def __init__(self):
#         pass

#     class LCDCell:
#         CELL_WIDTH = 50
#         CELL_HEIGHT = 70

#         def __init__(self, x, y, char):
#             # Location
#             self.x = x
#             self.y = y
#             # Letter to print in cell
#             self.char = char

class RaspberryPiMock:
    LCD_COLUMNS = 16
    LCD_ROWS = 2
    CELL_WIDTH = 50
    CELL_HEIGHT = 70
    SURFACE_RECT = (CELL_WIDTH * LCD_COLUMNS, CELL_HEIGHT * LCD_ROWS)
    BACKGROUND_COLOR = (0, 200, 255)
    SAMPLE_TEXT = [
        "Cløjs           ",  # Always 16 long
        "Ariel           "   # Always 16 long
    ]
    FRAME_COLOR = (0, 0, 0)

    def __init__(self):
        pygame.init()       # Prepare the pygame module for use
        self._font = pygame.font.Font(None, 90)
        print((self.CELL_HEIGHT - self._font.size("Aj")[1]) / 2.0)
        print(self._font.size("A")[1])
        self._top_offset = (self.CELL_HEIGHT - self._font.size("A")[1]) / 2.0
        # Create surface of (width, height), and its window.
        self._main_surface = pygame.display.set_mode(self.SURFACE_RECT)

    def draw_cell(self, column, row, letter):
        loc_and_size = (
            self.CELL_WIDTH * column,
            self.CELL_HEIGHT * row,
            self.CELL_WIDTH,
            self.CELL_HEIGHT
        )
        pygame.draw.rect(self._main_surface, self.FRAME_COLOR, loc_and_size, 2)
        text = self._font.render(letter, True, (0, 0, 0))
        text_size = self._font.size(letter)
        horizontal_padding = self.CELL_WIDTH - text_size[0]
        left_offset = horizontal_padding / 2.0
        self._main_surface.blit(
            text, (
                (self.CELL_WIDTH * column) + left_offset,
                (self.CELL_HEIGHT * row) + self._top_offset
            )
        )

    def draw_lcd(self, text):
        for row in range(self.LCD_ROWS):
            line_text = self.SAMPLE_TEXT[row]
            for column in range(self.LCD_COLUMNS):
                self.draw_cell(column, row, line_text[column])

    def run(self):
        """ Set up the game and run the main game loop """

        while True:
            ev = pygame.event.poll()    # Look for any event
            if ev.type == pygame.QUIT:  # Window close button clicked?
                break  # ... leave game loop

            # Update your game objects and data structures here...

            # We draw everything from scratch on each frame.
            # So first fill everything with the background color
            self._main_surface.fill(self.BACKGROUND_COLOR)
            self.draw_lcd(self.SAMPLE_TEXT)
            # for row in range(self.LCD_ROWS):
            #     line_text = self.SAMPLE_TEXT[row]
            #     for column in range(self.LCD_COLUMNS):
            #         loc_and_size = (50 * column, 70 * row, 50, 70)
            #         pygame.draw.rect(self._main_surface, self.FRAME_COLOR, loc_and_size, 2)
            #         text = self._font.render(list(line_text)[column], True, (0, 0, 0))
            #         text_size = self._font.size(line_text[column])
            #         horizontal_padding = self.CELL_WIDTH - text_size[0]
            #         left_offset = horizontal_padding / 2.0
            #         self._main_surface.blit(
            #             text,
            #             ((50 * column) + left_offset, self._top_offset + (70 * row))
            #         )

            # for i in range(self.LCD_COLUMNS):
            #     loc_and_size = (50 * i, 0, 50, 70)
            #     pygame.draw.rect(self._main_surface, self.FRAME_COLOR, loc_and_size, 2)
            #     text = self._font.render(list("Cløjs")[i], True, (0, 0, 0))

            #     text_size = self._font.size("Cløjs"[i])

            #     horizontal_padding = self.CELL_WIDTH - text_size[0]
            #     left_offset = horizontal_padding / 2.0

            #     # print(self._font.size("Cløus"[i]))
            #     self._main_surface.blit(text, ((50 * i) + left_offset, self._top_offset))
            # font = pygame.font.Font(None, 50)

            # text1 = font.render("C", True, (0, 0, 0))
            # text_rect1 = text1.get_rect(center=(50 / 2, 70 / 2))
            # self._main_surface.blit(text1, text_rect1)

            # # font = pygame.font.Font(None, 25)
            # text2 = font.render("l", True, (0, 0, 0))
            # text_rect2 = text2.get_rect(center=(100 / 2, 70 / 2))
            # self._main_surface.blit(text2, text_rect2)

            # text3 = font.render("a", True, (0, 0, 0))
            # text_rect3 = text3.get_rect(center=(150 / 2, 70 / 2))
            # self._main_surface.blit(text3, text_rect3)

            # text4 = font.render("u", True, (0, 0, 0))
            # text_rect4 = text4.get_rect(center=(200 / 2, 70 / 2))
            # self._main_surface.blit(text4, text_rect4)

            # text5 = font.render("s", True, (0, 0, 0))
            # text_rect5 = text5.get_rect(center=(250 / 2, 70 / 2))
            # self._main_surface.blit(text5, text_rect5)

            # # main_surface.draw.text("Yo", (50, 70))
            # # print(f"C:{self._font.size('C')}")
            # # myfont = pygame.font.SysFont("Courier", 90)
            # letter1 = self._font.render('C', False, (0, 0, 0))
            # # print(f"1: {letter1.get_rect()}")
            # self._main_surface.blit(letter1, (0, 0))

            # letter2 = self._font.render('l', False, (0, 0, 0))
            # # print(f"2: {letter2.get_rect()}")
            # self._main_surface.blit(letter2, (50, 0))

            # letter3 = self._font.render('a', False, (0, 0, 0))
            # # print(f"3: {letter3.get_rect()}")
            # self._main_surface.blit(letter3, (100, 0))

            # letter4 = self._font.render('u', False, (0, 0, 0))
            # # print(f"3: {letter3.get_rect()}")
            # self._main_surface.blit(letter4, (150, 0))

            # letter5 = self._font.render('s', False, (0, 0, 0))
            # # print(f"3: {letter3.get_rect()}")
            # self._main_surface.blit(letter5, (200, 0))

            # Now the surface is ready, tell pygame to display it!
            pygame.display.flip()

        pygame.quit()     # Once we leave the loop, close the window.

    # def draw_single_cell():
    #     color = (80 + (i * 10), 240 - (i * 10), 65)
    #     loc_and_size = (50 * i, 0, 50, 70)
    #     pygame.draw.rect(self._main_surface, color, loc_and_size, 2)
    #     text = self._font.render(list("Cløjs")[i], True, (0, 0, 0))

    #     text_size = self._font.size("Cløjs"[i])

    #     horizontal_padding = self.CELL_WIDTH - text_size[0]
    #     left_offset = horizontal_padding / 2.0

    #     # print(self._font.size("Cløus"[i]))
    #     self._main_surface.blit(text, ((50 * i) + left_offset, self._top_offset))
    # def draw_single_cell(self, letter, start_x, start_y):
    #     letter_size = self._font.size(letter)
    #     draw_x = (CELL_WIDTH - letter_size[0]) / 2.0
    #     cell_text = self._font.render(letter, False, (0, 0, 0))
    #     self._main_surface.blit(cell_text, (0, 0))


single_cell = RaspberryPiMock()

single_cell.run()

# def init(chars, lines):
#     global screen
#     global myfont
#     pygame.init()
#     size = [12 * chars, 20 * lines]
#     screen = pygame.display.set_mode(size)
#     pygame.display.set_caption("Mock LCD")
#     myfont = pygame.font.SysFont("monospace", 20)


# def draw(args):
#     i = 0
#     global screen
#     global myfont
#     screen.fill((0, 0, 0))  # erase screen contents
#     while(i < len(args)):
#         line = myfont.render(args[i], 2, (255, 255, 0))
#         screen.blit(line, (0, 20 * i))
#         i += 1
#     pygame.display.flip()


# while True:
#     ev = pygame.event.poll()    # Look for any event
#     if ev.type == pygame.QUIT:  # Window close button clicked?
#         break                   # ... leave game loop
#     init(16, 2)  # initialize a 16x2 display
#     # draw the three lines passed as a list
#     draw(["Hello!",
#           "     world"])
