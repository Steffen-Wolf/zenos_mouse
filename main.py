import pyautogui
import time
import numpy as np
# from multiprocessing import Queue
# from threading import Thread
# import click

import gtk.gdk
import pygame
from pygame.locals import *


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

def get_screenshot(fname='/home/swolf/local/src/zeno_mouse/data/screenshot_.png'):
    # Uses Python Image Library
    import Image
    w = gtk.gdk.get_default_root_window()
    sz = w.get_size()
    print "The size of the window is %d x %d" % sz
    pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
    pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
    pb.save(fname,"png")
    

def load_shot(fname='/home/swolf/tmp/screenshot.png'):
    surface = pygame.image.load(fname)
    surface.convert() # Makes blitting a bit faster
    return surface


def screenie():
    # Set up PyGame
    pygame.init()
    get_screenshot()
    display = pygame.display.set_mode(pyautogui.size(), pygame.FULLSCREEN)
    capture = load_shot()
    display.blit(capture, (0,0))

    position = np.array([p//2 for p in pyautogui.size()], dtype=int)
    step = np.array([p//4 for p in pyautogui.size()], dtype=int)
    moves = get_moves(position, step)

    draw_moves(position, moves, display)

    key_to_gamekey = {"h":pygame.K_h, "j":pygame.K_j, "k":pygame.K_k, "l":pygame.K_l}

    while True:

        pygame.display.update()
        # Deal with QUIT events
        for e in pygame.event.get():
            if e.type == QUIT:
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_f:
                    pygame.display.quit()
                    pyautogui.click(*position)
                    return
                if e.key == pygame.K_q:
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
    screenie()