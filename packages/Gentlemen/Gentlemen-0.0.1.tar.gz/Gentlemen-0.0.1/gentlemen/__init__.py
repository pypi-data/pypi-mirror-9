#!/usr/bin/env python

import random

def main():
    this_is = [
        "gentlemen",
        "actually good news",
    ]

    print('This is {}.'.format(random.choice(this_is)))

if __name__ == '__main__':
    main()
