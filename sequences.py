import pygame
import os

import entities.player
import graphics
import grid
import flicker
import constants as const


def load_story():
    with open(os.path.join("text", "story.txt"), "r") as file:
        data = file.read()
    lines = data.split("\n")
    return lines


story = load_story()

m5x7 = pygame.font.Font(os.path.join("text", "m5x7.ttf"), 32)
m3x6 = pygame.font.Font(os.path.join("text", "m3x6.ttf"), 32)

small_heart = graphics.load_image("heart_small", 2)
small_heart.set_colorkey(const.TRANSPARENT)
large_heart = graphics.load_image("heart_large", 2)
large_heart.set_colorkey(const.TRANSPARENT)

TUTORIAL_TEXT_LEVEL = 16
FIRST_CHECKPOINT_LEVEL = 25
START_MUSIC_FADE_LEVEL = 36


class Sequence:
    HEART_OFFSETS_X = [-8, -26, 14]
    HEART_OFFSETS_UP_Y = [-14, -12, -12]
    HEART_OFFSETS_DOWN_Y = [28, 28, 28]

    def __init__(self, level_names):
        self.level_names = level_names
        self._level_num = 0
        self.current = grid.Room(level_names[self._level_num])
        self.next = grid.Room(level_names[self._level_num + 1])
        self.transitioning = False
        self.done_transitioning = False
        self._frame = 0

    @property
    def level_num(self):
        return self._level_num

    @property
    def frame(self):
        return self._frame

    def next_level(self):
        self._level_num += 1
        self.current = self.next
        self.next = grid.Room(self.level_names[self._level_num + 1])

    def start_transition(self, static_level_surf):
        self._frame = 0
        self.transitioning = True

        static_level_surf.fill(const.TRANSPARENT)
        self.next.draw_silhouette(static_level_surf)

    def _end_transition(self):
        self.transitioning = False
        self.done_transitioning = True

    def update(self):
        if self._frame >= flicker.TOTAL_LENGTH:
            self._end_transition()
            self.next_level()

        self._frame += 1

    def _draw_respawn_text(self, surf, cam):
        if self.level_num == TUTORIAL_TEXT_LEVEL:
            key_name = pygame.key.name(entities.player.Player.respawn_key.list[0])
            string = "Press %s to respawn with momentum." % key_name
            text = m3x6.render(string, False, const.WHITE)
            x = self.current.text_x - text.get_width() // 2 - cam.x
            y = self.current.text_y - 80
            surf.blit(text, (x, y))

    def _draw_hard_respawn_popup(self, surf, cam, player):
        if player.dead_no_horizontal_frames >= 60 and self.level_num < FIRST_CHECKPOINT_LEVEL:
            frame = player.dead_no_horizontal_frames - 60

            c = min(255, frame * 30)
            color = (c, c, c)

            key_name = pygame.key.name(entities.player.Player.hard_respawn_key.list[0])
            text = m3x6.render(key_name, False, color, const.BLACK)
            x = player.center_x - text.get_width() // 2 - cam.x
            y = player.y - 30
            surf.blit(text, (x, y), special_flags=pygame.BLEND_ADD)

    def _draw_level_text(self, surf, cam):
        level_num = len(self.level_names) - self._level_num
        string = str(level_num) + ": " + story[self._level_num]
        text = m5x7.render(string, False, const.WHITE)

        x = self.current.text_x - text.get_width() // 2 - cam.x
        y = self.current.text_y - cam.y

        surf.blit(text, (x, y))

    def _draw_hearts(self, surf, cam, player):
        heart = large_heart
        for i in range(player.health):
            x = self.current.text_x - cam.x + self.HEART_OFFSETS_X[i]
            if self.current.heart_direction == const.UP:
                y = self.current.text_y - cam.y + self.HEART_OFFSETS_UP_Y[i]
            else:
                y = self.current.text_y - cam.y + self.HEART_OFFSETS_DOWN_Y[i]

            surf.blit(heart, (x, y))
            heart = small_heart

    def draw_ui(self, surf, cam, player):
        self._draw_level_text(surf, cam)
        self._draw_hearts(surf, cam, player)

        self._draw_respawn_text(surf, cam)
        self._draw_hard_respawn_popup(surf, cam, player)
