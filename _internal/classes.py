import pygame as pg
import random as rand


class Cell(pg.sprite.Sprite):
    def __init__(self, x, y, cl_cell_png, flag_png, board):
        pg.sprite.Sprite.__init__(self)
        self.image = cl_cell_png
        self.board = board
        self.rect = self.image.get_rect()
        self.rect.topleft = (board.x + board.scale * x, board.y + board.scale * y)
        self.x = x
        self.y = y
        self.bomb = False
        self.opened = False
        self.can_click = True
        self.closed_cell = cl_cell_png
        self.flag = False
        self.flag_png = flag_png


    def open(self):
        self.image = self.opened_cell
        self.opened = True
        if self.flag:
            self.flag = False

    def update(self):
        # проверка нажатия
        clicked = pg.mouse.get_pressed(3)
        if clicked[0]:
            mouse_pos = pg.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos) and not self.opened and self.board.can_click\
                    and not self.board.on_interface(mouse_pos):
                if self.bomb:
                    if self.board.f_click:
                        self.board.to_destroy = True
                        self.board.cell_to_click = (self.x, self.y)
                    else:
                        self.open()
                        self.board.state = 'gameover'
                        self.board.boom.play()
                else:
                    self.board.f_click = False
                    self.board.op_start = (self.x, self.y)
                    self.open_all_empty()
                    self.board.cell_s.play()
                self.board.can_click = False
        elif clicked[2]:
            mouse_pos = pg.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos) and not self.opened and self.board.can_click\
                    and not self.board.on_interface(mouse_pos):
                if not self.flag:
                    self.image = self.flag_png
                    self.flag = True
                    self.board.flag_s.play()
                    self.board.bombs_count_t -= 1
                else:
                    self.flag = False
                    self.image = self.closed_cell
                    self.board.flag_s.play()
                    self.board.bombs_count_t += 1
                self.board.can_click = False
        else:
            self.board.can_click = True

    def open_all_empty(self):
        self.open()
        self.board.op_cell_count += 1
        pos_nums = (-1, 0, 1)
        map = self.board.map
        if self.count == 0:
            for i in pos_nums:
                for j in pos_nums:
                    if not self.board.out_of_range(self.x + i, self.y + j) and abs(i) != abs(j):
                        cell = map[(self.x + i, self.y + j)]
                        if not cell.bomb and not cell.opened:
                            cell.open_all_empty()


    def bombs_around(self):
        pos_nums = (-1, 0, 1)
        map = self.board.map
        count = 0
        for i in pos_nums:
            for j in pos_nums:
                if not self.board.out_of_range(self.x + i, self.y + j):
                    if map[(self.x + i, self.y + j)].bomb:
                        count += 1
        return count

    def fill(self):
        if self.bomb:
            self.opened_cell = pg.transform.scale(self.board.bomb_png, (self.board.scale, self.board.scale))
        else:
            count = self.bombs_around()
            self.count = count
            if count == 0:
                self.opened_cell = pg.transform.scale(self.board.op_cell_png, (self.board.scale, self.board.scale))
            else:
                self.opened_cell = pg.transform.scale(self.board.numbers[count - 1], (self.board.scale, self.board.scale))


class Board:
    def __init__(self, height, width, bombs_count, cell_count, theme):
        self.x = 560
        self.y = 150
        self.height = height
        self.width = width


        self.pictures()
        self.sounds()
        self.windows()

        self.state = 'game'
        self.can_click = True
        self.scale = 800 / self.width
        self.zoom = []
        self.to_destroy = False
        self.f_click = True
        self.bombs_count = bombs_count
        self.bombs_count_t = bombs_count
        self.cell_count = cell_count
        self.op_cell_count = 0
        self.play_win = True
        self.play_gameover = True
        self.p_m_pos = pg.mouse.get_pos()
        self.timer = 0
        self.op_start = None
        self.theme = theme

        self.group = pg.sprite.Group()
        self.generate_map()
        self.generate_bomb()
        for cell in self.group:
            cell.fill()

    def generate_bomb(self):     
        bombs_count = self.bombs_count
        while bombs_count > 0:
            cell = self.map[(rand.randint(0, self.width - 1), rand.randint(0, self.height - 1))]
            if not cell.bomb:
                cell.bomb = True
                bombs_count -= 1

    def generate_map(self):
        self.map = {}
        cl_cell_png = pg.transform.scale(self.cl_cell_png, (self.scale, self.scale))
        flag_png = pg.transform.scale(self.flag_png, (self.scale, self.scale))
        for i in range(self.height):
            for j in range(self.width):
                cell = Cell(j, i, cl_cell_png, flag_png, self)
                self.group.add(cell)
                self.map[(j, i)] = cell

    def pictures(self):
        self.op_cell_png = pg.image.load('_internal\клетка_открытая.png')
        self.cl_cell_png = pg.image.load('_internal\клетка.png')
        self.bomb_png = pg.image.load('_internal\мина.png')
        self.flag_png = pg.image.load('_internal\флаг.png')
        self.background = pg.image.load('_internal\фон.png')
        self.background_ussr = pg.image.load('_internal\фон_ссср.png')
        self.background_japan = pg.image.load('_internal\фон_япония.png')
        self.win = pg.image.load('_internal\победа_партии.png')
        self.win_ussr = pg.image.load('_internal\герой_советского_союза.png')
        self.win_japan = pg.image.load('_internal\хирохито_гордится_тобой.png')
        self.gameover = pg.image.load('_internal\ты_огорчил_партию.png')
        self.gameover_ussr = pg.image.load('_internal\расстрел.png')
        self.gameover_japan = pg.image.load('_internal\отсутствие_боеприпасов.png')
        self.numbers = []
        for i in range(1, 9):
            num = pg.image.load('_internal\цифра_{}.png'.format(i))
            self.numbers.append(num)

    def sounds(self):
        pg.mixer.init()
        self.boom = pg.mixer.Sound('_internal\бомба_с.mp3')
        self.cell_s = pg.mixer.Sound('_internal\клетка.mp3')
        self.flag_s = pg.mixer.Sound('_internal\флаг.mp3')
        self.win_s = pg.mixer.Sound('_internal\победа_партии.mp3')
        self.gameover_s = pg.mixer.Sound('_internal\ты_огорчил_партию.mp3')
        self.win_ussr_s = pg.mixer.Sound('_internal\гимн_ссср.mp3')
        self.gameover_ussr_s = pg.mixer.Sound('_internal\расстрел_звук.mp3')
        self.win_japan_s = pg.mixer.Sound('_internal\гимн_япония.mp3')
        self.gameover_japan_s = pg.mixer.Sound('_internal\АЙ!.mp3')

    def windows(self):
        self.interface = pg.image.load('_internal\интерфейс.png')
        self.interface_ussr = pg.image.load('_internal\интерфейс_ссср.png')
        self.interface_japan = pg.image.load('_internal\интерфейс_япония.png')
        self.interface_top = pg.rect.Rect(0, 0, 1920, 137)
        self.interface_bot = pg.rect.Rect(0, 996, 1920, 84)
        self.window = pg.image.load('_internal\диалог_окно.png')
        self.window_japan = pg.image.load('_internal\диалог_окно_япония.png')
        self.apply_window_ussr = pg.image.load('_internal\диалог_окно_2_ссср.png')
        self.apply_window_japan = pg.image.load('_internal\диалог_окно_2_япония.png')
        self.apply_window = pg.image.load('_internal\диалог_окно_2.png')

    def on_interface(self, m_pos):
        return self.interface_top.collidepoint(m_pos) or self.interface_bot.collidepoint(m_pos)

    def mouse_on_board(self):
        m_pos = pg.mouse.get_pos()
        if self.x <= m_pos[0] <= self.x + self.scale * self.width and \
                self.y <= m_pos[1] <= self.y + self.scale * self.height:
            return True
        else:
            return False

    def centering(self):
        # найти центр поля
        self.x = 960 - (self.width * self.scale) / 2
        self.y = 555 - (self.height * self.scale) / 2
        self.cell_moving()

    def cell_moving(self):
        for key in self.map:
            cell = self.map[key]
            cell.rect.topleft = (self.x + self.scale * cell.x, self.y + self.scale * cell.y)

    # передвижение
    def moving(self):
        clicked = pg.mouse.get_pressed()
        m_pos = pg.mouse.get_pos()
        if clicked[1]:
            self.x += m_pos[0] - self.p_m_pos[0]
            self.y += m_pos[1] - self.p_m_pos[1]
            self.cell_moving()
        self.p_m_pos = pg.mouse.get_pos()

    # def zoom_in(self):
    #     # # m_pos = pg.mouse.get_pos()
    #     # # delta_x = m_pos[0] - 960
    #     # # delta_y = m_pos[1] - 540
    #     # self.scale += 50
    #     # # self.x -= self.width / 2 * 50 + delta_x / 2
    #     # # self.y -= self.height / 2 * 50 + delta_y / 2
    #     # # self.zoom.append((self.width / 2 + delta_x / 2, self.width / 2 + delta_y / 2))
    #     # self.rescale()
    #
    # def zoom_out(self):
    #     # self.scale -= 50
    #     # # reverse = self.zoom.pop()
    #     # # self.x += reverse[0]
    #     # # self.y += reverse[1]
    #     # self.rescale()

    def render(self):
        new_cl_cell_png = pg.transform.scale(self.cl_cell_png, (self.scale, self.scale))
        new_op_cell_png = pg.transform.scale(self.op_cell_png, (self.scale, self.scale))
        new_bomb_png = pg.transform.scale(self.bomb_png, (self.scale, self.scale))
        new_flag_png = pg.transform.scale(self.flag_png, (self.scale, self.scale))
        new_numbers = [pg.transform.scale(number, (self.scale, self.scale)) for number in self.numbers]
        return [new_cl_cell_png, new_op_cell_png, new_bomb_png, new_flag_png, new_numbers]

    def rescale(self):
        render = self.render()
        for key in self.map:
            cell = self.map[key]
            cell.closed_cell = render[0]
            cell.flag_png = render[3]
            if cell.bomb:
                cell.opened_cell = render[2]
            else:
                if cell.count > 0:
                    cell.opened_cell = render[4][cell.count - 1]
                else:
                    cell.opened_cell = render[1]
            if cell.opened:
                cell.image = cell.opened_cell
            elif cell.flag:
                cell.image = cell.flag_png
            else:
                cell.image = cell.closed_cell
            cell.rect = cell.image.get_rect()
            cell.rect.topleft = (self.x + self.scale * cell.x, self.y + self.scale * cell.y)


    def out_of_range(self, x, y):
        if x > self.width - 1 or y > self.height - 1 or x < 0 or y < 0:
            return True
        else:
            return False
