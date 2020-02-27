#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docstring"""

#TODO: difficulty knob
#       easy normal difficult
#               backwards  word fragments    limit rare chars, no q w/o u

import argparse
import random
import string
import sys
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


WORD_ORIENTATIONS = ["horizontal", "vertical", "diagonal"]

# 0,0 is lower left, max,max is upper right
CANVAS_X_MAX = 215.9 * mm * 0.95 # = 612 (us-letter) at 95%
CANVAS_Y_MAX = 279.4 * mm # = 792

TITLE_FONT_NAME = "Helvetica-Bold"
TITLE_FONT_SIZE = 32
TITLE_Y = 276 * mm
PUZZLE_FONT_NAME = "Courier-Bold"
PUZZLE_FONT_SIZE = 16
KEY_FONT_NAME = "Courier"
KEY_FONT_SIZE = 10


def initialize(wordset, debug=False):
    total_chars = sum([len(x) for x in wordset])
    longest = max([len(x) for x in wordset])

    # smallest grid size is 8x8
    width = max([8, longest])

    # want payload to be just less than 80% of all chars
    while total_chars > width ** 2 * .80:
        width += 1
    # largest is 16x16
    if width > 16:
        raise RuntimeError("too many characters, try fewer words")

    if debug:
        garbage = width ** 2 - total_chars
        print("{} of {} chars are garbage ({}%)".format(garbage, width ** 2,
            garbage * 100 / width ** 2))

    grid = []
    for x in range(width):
        grid.append([])
        for y in range(width):
            grid[x].append(None)
    return grid


def get_start(orientation, grid_width, word_length):
    if orientation == "horizontal":
        if grid_width == word_length:
            x = 0
        else:
            x = random.choice(range(grid_width - word_length))
        y = random.choice(range(grid_width))
    elif orientation == "vertical":
        x = random.choice(range(grid_width))
        if grid_width == word_length:
            y = 0
        else:
            y = random.choice(range(grid_width - word_length))
    elif orientation == "diagonal":
        if grid_width == word_length:
            x = 0
        else:
            x = random.choice(range(grid_width - word_length))
        if grid_width == word_length:
            y = 0
        else:
            y = random.choice(range(grid_width - word_length))
    return (x, y)


def fits(word, grid, start, orientation, debug=False):
    x, y = start
    collide = False
    for char in word:
        if grid[x][y] is None:
            pass
        elif grid[x][y] == char:
            collide = True
            pass
        else:
            return False
        if orientation == "horizontal":
            x += 1
        elif orientation == "vertical":
            y += 1
        elif orientation == "diagonal":
            x += 1
            y += 1
    if debug and collide:
        print("collide")
    return True


def place(word, grid, debug=False):
    word_fits = False
    while not word_fits:
        orientation = random.choice(WORD_ORIENTATIONS)
        start = get_start(orientation, len(grid), len(word))
        if debug:
            print(word, start, orientation)
        if fits(word, grid, start, orientation, debug=debug):
            x, y = start
            for char in word:
                grid[x][y] = char
                if orientation == "horizontal":
                    x += 1
                elif orientation == "vertical":
                    y += 1
                elif orientation == "diagonal":
                    x += 1
                    y += 1
            word_fits = True

    return grid


def format_output(title, grid, wordlist, output_fn, debug=False):
    if debug:
        for row in grid:
            for char in row:
                if char:
                    sys.stdout.write("{} ".format(char))
                else:
                    sys.stdout.write("  ")
            sys.stdout.write('\n')

    c = canvas.Canvas(output_fn)

    # title line
    x_margin = 32
    if title:
        c.setFont(TITLE_FONT_NAME, TITLE_FONT_SIZE)
        title_x = (CANVAS_X_MAX - x_margin - c.stringWidth(title,
                                                TITLE_FONT_NAME,
                                                TITLE_FONT_SIZE)) / 2
        c.drawString(title_x, TITLE_Y, title)

    # puzzle grid
    c.setFont(PUZZLE_FONT_NAME, PUZZLE_FONT_SIZE)

    x_margin = 40
    grid_max_pts = CANVAS_X_MAX - 80
    grid_max_cells = 16
    cell_pts = grid_max_pts / grid_max_cells

    x_min = x_margin + cell_pts * (grid_max_cells - len(grid)) / 2
    x_max = CANVAS_X_MAX - x_margin - cell_pts * (grid_max_cells - len(grid)) / 2
    x_delta = (x_max - x_min) / len(grid)

    y = 256 * mm
    y -= (16 - len(grid)) * 8 # adjust down for smaller puzzles

    for row in grid:
        x = x_min
        for char in row:
            c.drawString(x, y, char)
            x += x_delta
        y -= 9.2 * mm

    # the <hr /> between puzzle and key
    c.line(32, CANVAS_Y_MAX / 3, CANVAS_X_MAX - 48, CANVAS_Y_MAX / 3)

    # key list
    random.shuffle(wordlist)
    listchunks = []

    if len(wordlist) <= 16:
        listchunks.append(wordlist[:int(len(wordlist)/2)])
        listchunks.append(wordlist[int(len(wordlist)/2):])
        x = 200
    else:
        idx = 0
        while idx < len(wordlist):
            listchunks.append(wordlist[idx:idx+8])
            idx += 8
        x = (CANVAS_X_MAX - 80) / 2 - 96 * len(listchunks) / 2

    c.setFont(KEY_FONT_NAME, KEY_FONT_SIZE)
    for chunk in listchunks:
        y = 80 * mm
        for word in chunk:
            c.drawString(x, y, word)
            y -= 9.2 * mm
        x += 128

    # write the PDF
    c.showPage()
    c.save()


def main(args):
    grid = initialize(args.words, debug=args.debug)
    # easier to fit the big words first
    args.words.sort(key = lambda x: len(x), reverse=True)

    wordlist = [x.upper() for x in args.words]
    for word in wordlist:
        grid = place(word, grid, debug=args.debug)

    #TODO: take a pass to make sure there is exactly one of each word
    for x in range(len(grid)):
        for y in range(len(grid)):
            if grid[x][y] is None:
                grid[x][y] = random.choice(string.ascii_uppercase)

    format_output(args.title, grid, wordlist, args.output, debug=args.debug)


if __name__ == "__main__":
    a = argparse.ArgumentParser(__doc__)
    a.add_argument("--debug", required=False, action="store_true")
    a.add_argument("--title", "-t", required=False)
    a.add_argument("--output", "-o", required=True)
    a.add_argument("--words", action="append", nargs='+')
    args = a.parse_args()

    # consolidate all usages of --words
    words = list(set([y for x in args.words for y in x]))
    args.words = words

    # limit to only words > 3 chars
    words = []
    for word in args.words:
        if len(word) >= 3:
            words.append(word)
        else:
            print("Omitting short word '{}'".format(word))
    args.words = words

    random.seed()
    main(args)

#TODO: check printable margins
