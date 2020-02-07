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


WORD_ORIENTATIONS = ["horizontal", "vertical", "diagonal"]


def initialize(wordset, debug=False):
    total_chars = sum([len(x) for x in wordset])
    longest = max([len(x) for x in wordset])

    # smallest grid size is 8x8
    width = max([8, longest])

    # want payload to be just less than 50% of all chars
    while total_chars > width ** 2 / 2:
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


def format_output(grid):
    for row in grid:
        for char in row:
            if char:
                sys.stdout.write("{} ".format(char))
            else:
                sys.stdout.write("  ")
        sys.stdout.write('\n')


def main(args):
    grid = initialize(args.words, debug=args.debug)
    # easier to fit the big words first
    args.words.sort(key = lambda x: len(x), reverse=True)
    for word in [x.upper() for x in args.words]:
        grid = place(word, grid, debug=args.debug)

    #TODO: take a pass to make sure there is exactly one of each word
    for x in range(len(grid)):
        for y in range(len(grid)):
            if grid[x][y] is None:
                grid[x][y] = random.choice(string.ascii_uppercase)

    format_output(grid)


if __name__ == "__main__":
    a = argparse.ArgumentParser(__doc__)
    a.add_argument("--debug", required=False, action="store_true")
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
