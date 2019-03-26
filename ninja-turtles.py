#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import curses
import random
import argparse
import logging
import logging.config


def initlog(level='', log="-", disable_existing_loggers=True):
    level = getattr(logging, level.upper())
    log_format = '[%(asctime)s] %(levelname)s %(name)s %(pathname)s %(lineno)d [%(funcName)s] %(message)s'

    config = {
        "version": 1,
        "disable_existing_loggers": disable_existing_loggers,
        "formatters": {
            "custom": {
                "format": log_format
            }
        },
        "handlers": {
        },
        'root': {
            'level': level,
            'handlers': ['console']
        }
    }
    console = {
        "class": "logging.StreamHandler",
        "level": "DEBUG",
        "formatter": 'custom',
        "stream": "ext://sys.stderr"
    }
    file_handler = {
        "class": "logging.handlers.RotatingFileHandler",
        "level": "DEBUG",
        "formatter": 'custom',
        "filename": log,
        "maxBytes": 10*1000**2,  # 10M
        "backupCount": 5,
        "encoding": "utf8"
    }
    if log == "-":
        config["handlers"]["console"] = console
        config["root"]["handlers"] = ["console"]
    else:
        config["handlers"]["file_handler"] = file_handler
        config["root"]["handlers"] = ["file_handler"]
    logging.config.dictConfig(config)
# end initlog


class MazeSolution(object):

    def __init__(self, array, anchor):
        self.array = tuple(array)
        self.anchor = anchor
        self.target = tuple([str(i) for i in range(1, len(array))]) + (' ',)

    def up(self, array, anchor):
        if anchor <= 2:
            return None, None

        dest = anchor - 3
        new_array = list(array)
        new_array[dest], new_array[anchor] = new_array[anchor], new_array[dest]
        return tuple(new_array), dest

    def down(self, array, anchor):
        if anchor + 3 >= 9:
            return None, None

        dest = anchor + 3
        new_array = list(array)
        new_array[dest], new_array[anchor] = new_array[anchor], new_array[dest]
        return tuple(new_array), dest

    def left(self, array, anchor):
        if anchor % 3 == 0:
            return None, None

        dest = anchor - 1
        new_array = list(array)
        new_array[dest], new_array[anchor] = new_array[anchor], new_array[dest]
        return tuple(new_array), dest

    def right(self, array, anchor):
        if anchor % 3 == 2:
            return None, None

        dest = anchor + 1
        new_array = list(array)
        new_array[dest], new_array[anchor] = new_array[anchor], new_array[dest]
        return tuple(new_array), dest

    def find_solution(self):
        if self.array == self.target:
            return tuple()

        stack = []
        visited = set()
        last_direction = -1
        pathes = (last_direction, )
        step = 0

        stack.append((self.array[:], self.anchor, pathes))
        visited.add(tuple(self.array[:]))

        directions = (self.up,  self.left, self.right, self.down)

        count = 0
        while stack:
            count += 1
            array, anchor, pathes = stack.pop()
            last_direction = pathes[-1]
            for d in range(4):
                if last_direction == 3-d:
                    continue
                new_array, new_anchor = directions[d](array, anchor)
                if new_array is None:
                    continue
                if new_array == self.target:
                    return pathes[1:]+(d,)
                if new_array in visited:
                    continue
                stack.insert(0, (new_array, new_anchor, pathes+(d,)))
                visited.add(new_array)


class Maze(object):
    """docstring for Maze"""
    UP = 0
    LEFT = 1
    RIGHT = 2
    DOWN = 3

    def __init__(self, print_frame=True):
        self.target = list('12345678 ')
        self.array = list('12345678 ')
        self.anchor = 8
        self.steps = 0
        self.last_direction = 0
        self.print_frame = print_frame

        self.window = curses.initscr()
        self.window.keypad(True)
        # curses.noecho()
        # curses.cbreak()

        self.init()
        self.steps = 0

    def move(self, direction):
        dest = None
        if direction == Maze.UP:
            dest = self.up()
        elif direction == Maze.DOWN:
            dest = self.down()
        elif direction == Maze.LEFT:
            dest = self.left()
        elif direction == Maze.RIGHT:
            dest = self.right()

        if dest is not None:
            self.array[dest], self.array[self.anchor] = self.array[self.anchor], self.array[dest]
            self.anchor = dest
            return True
        return False

    def up(self):
        if self.anchor <= 2:
            return None
        return self.anchor - 3

    def down(self):
        if self.anchor + 3 >= 9:
            return None
        return self.anchor + 3

    def left(self):
        if self.anchor % 3 == 0:
            return None
        return self.anchor - 1

    def right(self):
        if self.anchor % 3 == 2:
            return None
        return self.anchor + 1

    def init(self, count=100):
        random.seed(time.time())
        directions = [Maze.UP, Maze.DOWN, Maze.LEFT, Maze.RIGHT]
        i = 1
        while i <= count:
            if self.print_frame:
                self.print_maze()
            direction = random.choice(directions)
            if self.last_direction == 3 - direction:
                continue
            if self.move(direction):
                self.last_direction = direction
                i += 1
                if self.print_frame:
                    curses.delay_output(100)
        self.print_maze()

    def resolved(self):
        return self.array == self.target

    def print_maze(self):
        self.window.erase()
        self.window.addstr('steps: {}\n\n'.format(self.steps))

        for i in range(3):
            self.window.addstr(' '.join(self.array[i*3:i*3+3])+'\n')

        self.window.refresh()

    def run(self):
        while True:
            self.print_maze()

            ch = self.window.getch()
            # print(ch)
            r = False
            if ch == curses.KEY_UP:
                r = self.move(Maze.UP)
            elif ch == curses.KEY_DOWN:
                r = self.move(Maze.DOWN)
            elif ch == curses.KEY_LEFT:
                r = self.move(Maze.LEFT)
            elif ch == curses.KEY_RIGHT:
                r = self.move(Maze.RIGHT)
            elif ch == ord('q'):
                return False
            elif ch == ord('f'):
                ms = MazeSolution(self.array, self.anchor)
                pathes = ms.find_solution()
                self.go_to_target(pathes)

            if self.resolved():
                return True
            if r:
                self.steps += 1

    def go_to_target(self, pathes):
        for p in pathes:
            self.move(p)
            self.steps += 1
            self.print_maze()
            curses.delay_output(100)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", default="-", help="log file")
    parser.add_argument("--level", default="info")
    parser.add_argument("--disable-existing-loggers", dest='feature', action='store_true')
    parser.add_argument("--print-frame", action='store_true')
    parser.set_defaults(disable_existing_loggers=True)
    args = parser.parse_args()

    initlog(level=args.level, log=args.l, disable_existing_loggers=args.disable_existing_loggers)

    # ms = MazeSolution('1234567 8', 7)
    # print(ms.find_solution())
    # return

    maze = Maze(args.print_frame)
    r = False
    try:
        r = maze.run()
    except KeyboardInterrupt:
        pass
    finally:
        maze.print_maze()
        pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
