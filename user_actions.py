from kivy.uix.relativelayout import RelativeLayout


def keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self.on_key_pressed)
    self._keyboard.unbind(on_key_down=self.on_key_release)
    self._keyboard = None


def on_key_pressed(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'left':
        self.current_speed_x = self.Speed_x
    elif keycode[1] == 'right':
        self.current_speed_x = - self.Speed_x
    return True


def on_key_release(self, keyboard, keycode):
    self.current_speed_x = 0
    return True


def on_finger_touch(self, touch):
    if not self.state_game_over and self.start:
        if touch.x < self.width / 2:
            # print('<-')
            self.current_speed_x = self.Speed_x
        else:
            # print('->')
            self.current_speed_x = - self.Speed_x

    return super(RelativeLayout, self).on_touch_down(touch)


def on_finger_release(self, touch):
    # print('UP')
    self.current_speed_x = 0
