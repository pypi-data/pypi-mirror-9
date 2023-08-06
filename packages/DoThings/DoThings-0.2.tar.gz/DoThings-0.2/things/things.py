#!/usr/bin/env python
#coding=utf8

"""Usage:
         things.py
         things.py all
         things.py clear
         things.py <thing>
         things.py done <num>
         things.py undo <num>
         things.py rm <num>
"""

import pickle
import sys
from os import path
from docopt import docopt

class TermColor:
    RED = "\033[91m"
    GREEN = "\033[92m"
    BOLD = "\033[1m"
    END = "\033[0m"

class TermSign:
    CHECK = u"\u2714".encode("utf8")
    START = u"\u2731".encode("utf8")
    BALLOTBOXWITHCHECK = u"\u2611".encode("utf8")
    BALLOTBOX = u"\u2610".encode("utf8")


class Thing(object):
    def __init__(self, name, undo=True):
        self.name = name
        self.undo = undo

class ToDo(object):
    def __init__(self, saved_file=".todo"):
        self.saved_file = saved_file
        self.todos = []

        if path.exists(saved_file):
            with open(saved_file) as fp:
                self.todos = pickle.load(fp)


    def add(self, thing):
        self.todos.append(thing)
        self._save()

    def update(self, index, updated_thing):
        self.todos[index-1] = updated_thing
        self._save()

    def done(self, index):
        self.todos[index-1].undo = False
        self._save()

    def undo(self, index):
        self.todos[index-1].undo = True
        self._save()

    def remove(self, index):
        del self.todos[index-1]
        self._save()

    def clear(self):
        del self.todos[:]
        self._save()

    def _save(self):
        with open(self.saved_file, "w+") as fp:
            pickle.dump(self.todos, fp)

    def print_todo(self):
        print
        # print "{0}  TO-DO-List  {0}".format("*"*32)
        for index, thing in enumerate(self.todos):
            if thing.undo:
                print TermColor.RED + TermSign.START + TermColor.END,
                print " {0}. {1}".format(index+1, thing.name)
        print

    def print_all(self):
        print
        # print "{0}  Archieve-List  {0}".format("*"*32)
        for index, thing in enumerate(self.todos):
            if thing.undo:
                print TermColor.RED + TermSign.START + TermColor.END,
            else:
                print TermColor.GREEN + TermSign.CHECK + TermColor.END,
            print " {0}. {1}".format(index+1, thing.name)
        print

def main():
    parser = docopt(__doc__)
    td = ToDo()
    try:
        if parser["rm"]:
            td.remove(int(parser["<num>"]))
        elif parser["clear"]:
            td.clear()
        elif parser["done"]:
            td.done(int(parser["<num>"]))
        elif parser["undo"]:
            td.undo(int(parser["<num>"]))
        elif parser["<thing>"]:
            thing = Thing(parser["<thing>"])
            td.add(thing)

        if parser["all"]:
            td.print_all()
        else:
            td.print_todo()
    except IndexError:
        sys.stderr.write("Index is out of range, please retry...\n")

if __name__ == "__main__":
    # print TermColor.RED + TermColor.BOLD + TermSign.START + TermColor.END
    # print TermColor.GREEN + TermColor.BOLD +TermSign.CHECK + TermColor.END
    main()