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

def get_moves(position, step):
    moves = {
        "h": position+step*[-1,0],
        "j": position+step*[0,1],
        "k": position+step*[0,-1],
        "l": position+step*[1,0]
        }
    return moves
    
def draw_moves(position, moves, display):
    for end_pos in moves.values():
        pygame.draw.line(display, (0,255,0), tuple(position), tuple(end_pos), 2)

def get_screenshot(fname):
    # Uses Python Image Library
    import Image
    w = gtk.gdk.get_default_root_window()
    sz = w.get_size()
    pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
    pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
    pb.save(fname,"png")
    

def load_shot(fname):
    surface = pygame.image.load(fname)
    surface.convert() # Makes blitting a bit faster
    return surface

def save_data_point(fname, position):
    with open("/home/swolf/local/src/zenos_mouse/data/labels.txt", "a") as label_file:
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

def move_mouse():
    # Set up PyGame
    pygame.init()
    fname = "/home/swolf/local/src/zenos_mouse/data/screenshot_{}.png".format(time.time())
    get_screenshot(fname)
    display = pygame.display.set_mode(pyautogui.size(), pygame.FULLSCREEN)
    capture = load_shot(fname)
    display.blit(capture, (0,0))

    position = np.array([p//2 for p in pyautogui.size()], dtype=int)
    step = np.array([p//4 for p in pyautogui.size()], dtype=int)
    moves = get_moves(position, step)

    draw_moves(position, moves, display)

    try:
        draw_current_data_points(display)
    except:
        pass

    key_to_gamekey = {"h":pygame.K_h, "j":pygame.K_j, "k":pygame.K_k, "l":pygame.K_l}

    while True:
        pygame.display.update()
        # Deal with QUIT events
        for e in pygame.event.get():
            if e.type == QUIT:
                return
            if e.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                pygame.display.quit()
                pyautogui.click(*position)
                save_data_point(fname, pos)
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_f:
                    pygame.display.quit()
                    pyautogui.click(*position)
                    save_data_point(fname, position)
                    return
                if e.key == pygame.K_q:
                    remove(fname)
                    pygame.display.quit()
                    return

                for c, key in key_to_gamekey.items():
                    if e.key == key:
                        position = moves[c]
                        if c in "hl":
                            step[0] /= 2
                        else:
                            step[1] /= 2
                        moves = get_moves(position, step)
                        display.blit(capture, (0,0))
                        draw_moves(position, moves, display)
                


if __name__ == '__main__':
    if len(argv) > 1 and argv[1] == 'learn':
        print("starting learning capture mode")
        MouseClickCapture().run()
        exit()
    else:
        move_mouse()