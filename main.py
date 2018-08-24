import pyautogui
import time
import numpy as np
# from multiprocessing import Queue
# from threading import Thread
# import click

import gtk.gdk
import pygame
from sys import argv
from pygame.locals import *
from pymouse import PyMouseEvent
from os import remove

DISPLAY = True


def get_initial_position_step():
    return np.array([p // 2 for p in pyautogui.size()], dtype=int), \
           np.array([p//4 for p in pyautogui.size()], dtype=int)


def get_moves(position, step):
    moves = {
        "h": position + step * [-1, 0],
        "j": position + step * [0, 1],
        "k": position + step * [0, -1],
        "l": position + step * [1, 0]
    }
    return moves


def get_max_reachable(step):
    reachable = {
        "h": step * np.array([-2, 0]),
        "j": step * np.array([0, 2]),
        "k": step * np.array([0, -2]),
        "l": step * np.array([2, 0])
    }
    return reachable


def reduce_step(key, step):
    if key in "hl":
        if step[0] > 1:
            step[0] /= 2
    else:
        if step[1] > 1:
            step[1] /= 2

    return step


def draw_moves(position, moves, step, display):
    reachable = get_max_reachable(step)

    # myfont = pygame.font.SysFont("monospace", 30)
    # label = myfont.render("Some text!", 1, (255,255,0))
    # display.blit(label, (100, 100))
    # screen = display.get_surface()

    for r in reachable.values():
        pygame.draw.line(display, (0, 255, 0), tuple(position), tuple(position + r), 2)

    for k, m in moves.items():
        distance = np.abs(position - m).sum()
        if (distance > 40) and k in ["h", "j", "k", "l"]:
            diam = 16
        else:
            diam = 0

        if diam > 0:
            pygame.draw.circle(display, (0, 25, 0), m, diam + 2)
            pygame.draw.circle(display, (0, 255, 0), m, diam)

            myfont = pygame.font.SysFont("monospace", 2 * diam, bold=True)
            label = myfont.render(k, 1, (0, 0, 0))
            text_rect = label.get_rect(center=m)
            display.blit(label, text_rect)


def get_screenshot(fname):
    # Uses Python Image Library
    import Image
    w = gtk.gdk.get_default_root_window()
    sz = w.get_size()
    pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, sz[0], sz[1])
    pb = pb.get_from_drawable(w, w.get_colormap(), 0, 0, 0, 0, sz[0], sz[1])
    pb.save(fname, "png")


def load_shot(fname):
    surface = pygame.image.load(fname)
    surface.convert()  # Makes blitting a bit faster
    return surface


def save_data_point(fname, position):
    with open("/home/swolf/local/src/zenos_mouse/data/labels_{}_{}.txt".
              format(*pyautogui.size()), "a") as label_file:
        label_file.write("{},{},{}\n".format(fname, position[0], position[1]))


class MouseClickCapture(PyMouseEvent):

    def __init__(self):
        super(MouseClickCapture, self).__init__()

    def click(self, x, y, button, press):
        if press:
            fname = "/home/swolf/local/src/zenos_mouse/data/capture_{}.png".format(time.time())
            get_screenshot(fname)
            save_data_point(fname, (x, y))
            time.sleep(2000)


def draw_current_data_points(display):
    with open("/home/swolf/local/src/zenos_mouse/data/labels.txt", "r") as label_file:
        lines = label_file.readlines()
        for l in lines:
            x, y = l.strip().split(",")[1:3]
            pygame.draw.circle(display, (0, 100, 250), (int(x), int(y)), 4)


def display_screenshot(display):
    fname = "/home/swolf/local/src/zenos_mouse/data/screenshot_{}.png".format(time.time())
    get_screenshot(fname)
    capture = load_shot(fname)
    display.blit(capture, (0, 0))
    return fname, capture


def move_mouse():
    # Set up PyGame
    pygame.init()

    display = pygame.display.set_mode(pyautogui.size(), pygame.FULLSCREEN)
    fname, capture = display_screenshot(display)

    position, step = get_initial_position_step()
    moves = get_moves(position, step)
    draw_moves(position, moves, step, display)

    history = []

    try:
        draw_current_data_points(display)
    except:
        pass

    key_to_gamekey = {"h": pygame.K_h, "j": pygame.K_j, "k": pygame.K_k, "l": pygame.K_l}

    while True:
        pygame.display.update()
        # Deal with QUIT events
        for e in pygame.event.get():
            if e.type == QUIT:
                return
            if e.type == pygame.MOUSEBUTTONDOWN:
                # if mouse is used save training data
                pos = pygame.mouse.get_pos()
                pygame.display.quit()
                pyautogui.click(*position)
                save_data_point(fname, pos)
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_f:
                    # click and exit
                    pygame.display.quit()
                    pyautogui.click(*position)
                    save_data_point(fname, position)
                    return
                if e.key == pygame.K_q:
                    # quit
                    remove(fname)
                    pygame.display.quit()
                    return

                if e.key == pygame.K_u:
                    # undo last move
                    if history:
                        position, step = history.pop()
                        moves = get_moves(position, step)
                        display.blit(capture, (0, 0))
                        draw_moves(position, moves, step, display)

                for c, key in key_to_gamekey.items():
                    # make move
                    if e.key == key:
                        history.append((position.copy(), step.copy()))
                        position = moves[c]

                        # reduce movement speed by two
                        step = reduce_step(c, step)

                        # update display
                        moves = get_moves(position, step)
                        display.blit(capture, (0, 0))
                        draw_moves(position, moves, step, display)

if __name__ == '__main__':
    if len(argv) > 1 and argv[1] == 'learn':
        print("starting learning capture mode")
        MouseClickCapture().run()
        exit()
    else:
        move_mouse()
