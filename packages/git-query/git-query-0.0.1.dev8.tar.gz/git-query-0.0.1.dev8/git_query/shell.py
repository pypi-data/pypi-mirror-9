#!/usr/bin/python
import sys

from git_query import query


def main():
    app = query.App()
    if len(sys.argv) == 2 and \
            (sys.argv[1] == '--all' or sys.argv[1] == '-a'):
        app.show_all()

    # user passes in Gerrit ID
    elif len(sys.argv) == 2 and sys.argv[1].isdigit():
        app.show_id(sys.argv[1])

    # list all Gerrit reviews
    else:
        app.show_current()

if __name__ == '__main__':
    main()
