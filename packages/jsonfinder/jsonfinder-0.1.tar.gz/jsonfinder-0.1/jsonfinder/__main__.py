from itertools import imap
from sys import argv, stdout, stdin
from jsonfinder import jsonfinder
from json import dumps


def main():
    args = argv[1:]
    for line in stdin:
        for item in jsonfinder(line, other=str, json=(tuple, object)):
            if isinstance(item, tuple):
                pos, obj = item
                item_str = line[pos[0]:pos[1]]
                if all(imap(item_str.__contains__, args)):
                    item = dumps(item[1], indent=4, sort_keys=True)
                else:
                    item = item_str
            stdout.write(item)
        stdout.flush()
    print


if __name__ == "__main__":
    main()