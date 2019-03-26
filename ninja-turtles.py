#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import curses
import random
import argparse


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

        ds = ('UP', 'LEFT', 'RIGHT', 'DOWN')
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
                    return [ds[e] for e in pathes[1:]+(d,)]
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
    DIRECTIONS = {'UP': UP, 'LEFT': LEFT, 'RIGHT': RIGHT, 'DOWN': DOWN}

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
        if isinstance(direction, basestring):
            direction = Maze.DIRECTIONS[direction.upper()]
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

    def print_maze(self, msg=''):
        self.window.erase()
        self.window.addstr('steps: {}\n\n'.format(self.steps))

        for i in range(3):
            self.window.addstr(' '.join(self.array[i*3:i*3+3])+'\n')

        if msg:
            self.window.addstr(msg)
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
            curses.delay_output(500)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-frame", action='store_true')
    args = parser.parse_args()

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
        msg = 'PASS\n' if r else None
        maze.print_maze(msg)


if __name__ == '__main__':
    main()
