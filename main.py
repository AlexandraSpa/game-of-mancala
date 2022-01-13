import pygame
import random

DEFAULT_GEM_IMAGE = "01.png"


class Gem(pygame.sprite.Sprite):
    def __init__(self, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()

    # def update(self, *args: Any, **kwargs: Any) -> None:

    def set_position(self, x, y):
        self.rect.center = [x, y]


class Hole:
    def __init__(self, x, y, w, h):
        self.gems = pygame.sprite.Group()
        self.rect = pygame.Rect((x, y), (w, h))
        self.final = False

    def is_empty(self):
        if self.count_gems() == 0:
            return True
        else:
            return False

    def count_gems(self):
        return self.gems.__len__()

    def add_gem(self, gem):
        gem.set_position(random.randrange(self.rect.centerx, self.rect.centerx + 15), random.randrange(
            self.rect.centery, self.rect.centery + 15))
        self.gems.add(gem)

    def add_gems(self, list_gem):
        for gem in list_gem:
            gem.set_position(random.randrange(self.rect.centerx, self.rect.centerx + 15), random.randrange(
                self.rect.centery, self.rect.centery + 15))
            self.gems.add(gem)

    def pop_gem(self):
        return self.gems.sprites().pop()

    def remove_gems(self):
        self.gems.empty()


class Board:
    def __init__(self):
        self.up_holes = [hole1, hole2, hole3, hole4, hole5, hole6]
        self.down_holes = [hole12, hole11, hole10, hole9, hole8, hole7]
        self.holes_for_player1 = [hole1, hole2, hole3, hole4, hole5, hole6, last_hole1, hole12, hole11, hole10, hole9,
                                  hole8, hole7]
        self.holes_for_player2 = [hole12, hole11, hole10, hole9, hole8, hole7, last_hole2, hole1, hole2, hole3, hole4,
                                  hole5, hole6]
        last_hole1.final = True
        last_hole2.final = True

    def draw_gems(self, display):
        for hole in self.holes_for_player1:
            hole.gems.draw(display)
        for hole in self.holes_for_player2:
            hole.gems.draw(display)


class Player:
    def __init__(self, holes_list, final_hole):
        self.holes = holes_list
        self.available_holes = []
        self.final_hole = final_hole

    def collect_gems(self):
        gems = self.final_hole.count_gems()
        for hole in self.holes:
            if not hole.is_empty():
                gems += hole.count_gems()
        return gems

    def out_of_moves(self):
        for hole in self.holes:
            if not hole.is_empty():
                return False
        return True


class Game:
    def __init__(self):
        pygame.init()
        self.running, self.playing = True, False
        self.DISPLAY_X, self.DISPLAY_Y = 1000, 628
        self.display = pygame.display.set_mode((self.DISPLAY_X, self.DISPLAY_Y))
        self.background = pygame.image.load("background.jpg")
        self.board = Board()
        self.turn = "up"
        self.player1 = Player(self.board.up_holes, last_hole1)
        self.player1.available_holes = self.board.holes_for_player1
        self.player2 = Player(self.board.down_holes, last_hole2)
        self.player2.available_holes = self.board.holes_for_player2
        self.current_player = self.player1
        self.current_hole = self.player1.holes[0]
        self.font = pygame.font.Font(pygame.font.get_default_font(), 30)

    def game_loop(self):
        while self.playing:
            self.check_events()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.hole_clicked() and not self.current_hole.is_empty():

                    # gem_container = Gem(DEFAULT_GEM_IMAGE)
                    # gem_container.image = hole1.pop_gem().image
                    # hole2.add_gem(gem_container)
                    # hole1.pop_gem().remove(hole1.gems)
                    self.make_the_move()
                    if self.game_is_over():
                        if self.player1.collect_gems() > self.player2.collect_gems():
                            print("Player one won!")
                        elif self.player1.collect_gems() < self.player2.collect_gems():
                            print("Player two won!")
                        else:
                            print("Equality!")
                        print("Player1 " + str(self.player1.collect_gems()) + " - " +
                              str(self.player2.collect_gems()) + " Player2 ")
                        self.running, self.playing = False, False

        pygame.display.flip()
        self.display.blit(self.background, (0, 0))
        # pygame.draw.rect(self.display, (0, 0, 0), last_hole1)
        # pygame.draw.rect(self.display, (0, 0, 0), last_hole2)
        self.board.draw_gems(self.display)
        self.display_number_of_gems()
        pygame.display.update()

    def hole_clicked(self):
        for hole in self.current_player.holes:
            if hole.rect.collidepoint(pygame.mouse.get_pos()):
                self.current_hole = hole
                return True
        return False

    def make_the_move(self):
        current_index = self.current_player.available_holes.index(self.current_hole)
        print(current_index)
        for gem in self.current_hole.gems:
            gem.rect.y -= 60
        while not self.current_hole.is_empty():
            while current_index + 1 > 12:
                current_index -= 13
            gem_container = Gem(DEFAULT_GEM_IMAGE)
            gem_container.image = self.current_hole.pop_gem().image
            self.current_player.available_holes[current_index + 1].add_gem(gem_container)
            self.current_hole.pop_gem().remove(self.current_hole.gems)
            current_index += 1
        last_hole = self.current_player.available_holes[current_index]
        # print(current_index)
        if last_hole.count_gems() == 1 and 0 <= current_index <= 5 \
                and not self.current_player.available_holes[12 - current_index].is_empty():
            print("empty hole found!")
            self.current_player.final_hole.add_gems(last_hole.gems)
            last_hole.remove_gems()
            self.current_player.final_hole.add_gems(self.current_player.available_holes[12 - current_index].gems)
            self.current_player.available_holes[12 - current_index].remove_gems()
        if last_hole != self.current_player.final_hole:
            self.switch_turns()

    def switch_turns(self):
        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1

    def display_number_of_gems(self):
        for hole in self.player1.holes:
            number_displayed = self.font.render(str(hole.count_gems()), True, (255, 250, 250))
            x = hole.rect.x + hole.rect.w / 2
            y = (hole.rect.y + hole.rect.h + 13)
            self.display.blit(number_displayed, (x, y))
        for hole in self.player2.holes:
            number_displayed = self.font.render(str(hole.count_gems()), True, (255, 250, 250))
            x = hole.rect.x + hole.rect.w / 2
            y = (hole.rect.y - hole.rect.h / 2)
            self.display.blit(number_displayed, (x, y))
        number_displayed = self.font.render(str(self.player1.final_hole.count_gems()), True, (255, 250, 250))
        x = self.player1.final_hole.rect.x + self.player1.final_hole.rect.w / 2
        y = (self.player1.final_hole.rect.y + self.player1.final_hole.rect.h + 13)
        self.display.blit(number_displayed, (x, y))
        number_displayed = self.font.render(str(self.player2.final_hole.count_gems()), True, (255, 250, 250))
        x = self.player2.final_hole.rect.x + self.player2.final_hole.rect.w / 2
        y = (self.player2.final_hole.rect.y + self.player2.final_hole.rect.h + 13)
        self.display.blit(number_displayed, (x, y))

    def game_is_over(self):
        if self.player1.out_of_moves() or self.player2.out_of_moves():
            return True
        return False


hole1 = Hole(182, 334, 71, 71)
hole2 = Hole(hole1.rect.x + 118, 334, 71, 71)
hole3 = Hole(hole2.rect.x + 118, 334, 71, 71)
hole4 = Hole(hole3.rect.x + 118, 334, 71, 71)
hole5 = Hole(hole4.rect.x + 118, 334, 71, 71)
hole6 = Hole(hole5.rect.x + 118, 334, 71, 71)
hole7 = Hole(hole1.rect.x, hole1.rect.y - 105, 71, 71)
hole8 = Hole(hole7.rect.x + 118, hole7.rect.y, 71, 71)
hole9 = Hole(hole8.rect.x + 118, hole7.rect.y, 71, 71)
hole10 = Hole(hole9.rect.x + 118, hole7.rect.y, 71, 71)
hole11 = Hole(hole10.rect.x + 118, hole7.rect.y, 71, 71)
hole12 = Hole(hole11.rect.x + 118, hole7.rect.y, 71, 71)
last_hole2 = Hole(53, 269, 110, 110)
last_hole1 = Hole(863, 268, 110, 111)

if __name__ == '__main__':
    hole1.add_gems([Gem("01.png"), Gem("02.png"), Gem("03.png"), Gem("04.png")])
    hole2.add_gems([Gem("01.png"), Gem("02.png"), Gem("03.png"), Gem("04.png")])
    hole3.add_gems([Gem("01.png"), Gem("02.png"), Gem("03.png"), Gem("04.png")])
    hole4.add_gems([Gem("01.png"), Gem("02.png"), Gem("03.png"), Gem("04.png")])
    hole5.add_gems([Gem("01.png"), Gem("02.png"), Gem("03.png"), Gem("04.png")])
    hole6.add_gems([Gem("01.png"), Gem("02.png"), Gem("03.png"), Gem("04.png")])
    hole7.add_gems([Gem("05.png"), Gem("06.png"), Gem("07.png"), Gem("08.png")])
    hole8.add_gems([Gem("05.png"), Gem("06.png"), Gem("07.png"), Gem("08.png")])
    hole9.add_gems([Gem("05.png"), Gem("06.png"), Gem("07.png"), Gem("08.png")])
    hole10.add_gems([Gem("05.png"), Gem("06.png"), Gem("07.png"), Gem("08.png")])
    hole11.add_gems([Gem("05.png"), Gem("06.png"), Gem("07.png"), Gem("08.png")])
    hole12.add_gems([Gem("05.png"), Gem("06.png"), Gem("07.png"), Gem("08.png")])

    game = Game()
    game.playing = True
    game.game_loop()
