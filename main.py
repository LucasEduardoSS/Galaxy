from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from time import sleep

Config.set('graphics', 'width', '1600')
Config.set('graphics', 'height', '800')

from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.widget import Widget
import random

''' !!! ATTENTION !!!

All the logic behind the algorithms below is make using the grid layout in 2D perspective
and then, at the end, transformed to 3D.
'''

Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import on_key_release, on_key_pressed, keyboard_closed, on_finger_touch, on_finger_release

    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)  # origin x for the perspective view
    perspective_point_y = NumericProperty(0)  # origin y for the perspective view

    V_NB_LINES = 8  # Number of vertical lines
    V_LINES_SPACING = .3  # Percentage in screen width
    vertical_lines = []  # List of vertical lines

    H_NB_LINES = 15  # Number of horizontal lines
    H_LINES_SPACING = .2  # Percentage in screen height
    horizontal_lines = []  # List of horizontal lines

    Speed = .8
    current_offset_y = 0
    current_y_loop = 0

    Speed_x = 2
    current_speed_x = 0  # Variable used set the speed which the grid moves as the ship moves
    current_offset_x = 0  # Variable used to move the grid as the ship moves

    NB_TILES = 16
    tiles = []
    tiles_coordinates = []

    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    state_game_over = False
    start = False

    menu_title = StringProperty('G   A   L   A   X   Y')
    menu_button_title = StringProperty('START')

    score_txt = StringProperty(f'Score: {str(current_y_loop)}')

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None

    deaths = 0

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print("INIT W:" + str(self.width) + " H:" + str(self.height))
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_key_pressed)
            self._keyboard.bind(on_key_up=self.on_key_release)

        Clock.schedule_interval(self.update, 1/60)  # Call the function "update" 60 times per second
        Clock.schedule_interval(self.update_speed, 1)

    def reset_game(self):
        # Reset x and y offset position, back to the initial grid position
        self.current_offset_y = 0
        self.current_offset_x = 0

        # Reset the ship travel progress
        self.current_y_loop = 0

        # Reset score
        self.score_txt = 'Score:  ' + str(self.current_y_loop)

        # Reset ship forward speed
        self.current_speed_x = 0

        self.tiles_coordinates = []
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.state_game_over = False

    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        else:
            return False

    def init_audio(self):
        # Game begin audio
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_begin.volume = .25

        # Game main theme
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_galaxy.volume = .25

        # Game over impact sound
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_impact.volume = .25

        # Game over impact voice sound
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_gameover_voice.volume = .25

        # Game Music1 sound
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_music1.volume = 1

        # Restart sound
        self.sound_restart = SoundLoader.load("audio/restart.wav")
        self.sound_restart.volume = .25

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_speed(self, dt):
        return self.current_y_loop**1.001 - self.current_y_loop + self.Speed

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2

        self.ship_coordinates[0] = (center_x - ship_half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + self.height * self.SHIP_HEIGHT)
        self.ship_coordinates[2] = (center_x + ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])

        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision(self):
        """

        :return:
        """
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]

            if ti_y > self.current_y_loop + 1:
                # Ship collided
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                # Ship did not collide
                return True

        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        """
        Check if the ship colides if
        :param ti_x:
        :param ti_y:
        :return:
        """
        x_min, y_min = self.get_tile_coordinates(ti_x, ti_y)
        x_max, y_max = self.get_tile_coordinates(ti_x + 1, ti_y + 1)

        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if x_min <= px <= x_max and y_min <= py <= y_max:
                return True
        return False

    def init_tiles(self):
        """
        Initialize the tiles, without specific coordinates
        :return:
        """
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                # Append to the tiles list a Quad widget
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinates(self):
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        last_y = 0
        last_x = 0

        # Clean the coordinates that are out of the screen: ti_y < self.current_y_loop
        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        # Get the last x and y from the last tile created, if the tiles list is not empty
        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_x = last_coordinates[0]
            last_y = last_coordinates[1] + 1

        # Generate the tiles
        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            # Randomly choose a type of tile, straight, left or right
            r = random.randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            self.tiles_coordinates.append((last_x, last_y))

            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1

            if last_x <= start_index:
                r = random.randint(0, 1)

            elif last_x >= end_index - 1:
                r = random.choice([0, 2])

            # Turn to right
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            # Turn to left
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y += 1

    def init_vertical_lines(self):
        with self.canvas:
            Color(.5, .5, .5)
            # self.line = Line(points=[100, 0, 100, 100])

            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x  #
        spacing = self.V_LINES_SPACING * self.width  # Space between lines
        offset = index - 0.5  # Central line offset
        line_x = central_line_x + offset * spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]  # Auxiliar variable which holds the tile i
            tile_coordinates = self.tiles_coordinates[i]  # Auxiliar variable which holds the tile i coordinates

            x_min, y_min = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            x_max, y_max = self.get_tile_coordinates(tile_coordinates[0] + 1, tile_coordinates[1] + 1)

            x1, y1 = self.transform(x_min, y_min)
            x2, y2 = self.transform(x_min, y_max)
            x3, y3 = self.transform(x_max, y_max)
            x4, y4 = self.transform(x_max, y_min)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES/2)+1
        for i in range(start_index, start_index + self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)

            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def init_horizontal_lines(self):
        """
        Initialize the horizontal lines and store then in a list
        :return: None
        """

        with self.canvas:
            Color(.5, .5, .5, 1)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1

        x_min = self.get_line_x_from_index(start_index)  # First line position, from left to right # Minimum line x point (starting point)
        x_max = self.get_line_x_from_index(end_index)  # Maximum line x point (ending point)

        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)  # Lines point y (Line height)

            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)

            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update(self, dt):
        # print(f'update: {dt*60}')
        time_factor = dt*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        # Calculate the speed y based in the height of the game viewport
        if not self.state_game_over and self.start:
            speed_y = self.update_speed(dt) * self.height / 100
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            # Create the illusion of movement in the axis y
            if self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_txt = 'Score:  ' + str(self.current_y_loop)
                self.generate_tiles_coordinates()
                # print("loop : " + str(self.current_y_loop))  # Shows the current loop

            # Update the frame for the ship movement
            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        # Show game over if the check_ship_collision return False
        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            self.menu_title = 'G  A  M  E    O  V  E  R'
            self.menu_button_title = 'RESTART'
            self.menu_widget.opacity = 1  # Turns back menu background opacity
            self.deaths += 1

            # Sounds for game over
            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            sleep(1)
            self.sound_gameover_voice.play()

    def on_start_button_pressed(self):
        self.reset_game()  # Restart the game
        self.start = True

        if self.deaths == 0:
            # Plays begin sound when first start the game
            self.sound_begin.play()

        else:
            # Plays restart sound when restart the game
            self.sound_restart.play()

        # Loop the music
        self.sound_music1.loop = True
        self.sound_music1.play()

        # Hides menu background
        self.menu_widget.opacity = 0


class GalaxyApp(App):
    pass


if __name__ == "__main__":
    GalaxyApp().run()
