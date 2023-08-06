# coding=utf-8

"""Generate words that sound like characters from Game of Thrones.

Usage:
  name-of-thrones [--quantity=<number>] [--min=<length>] [--max=<length>]
                  [--json] [--nocolour] [--alphabetical] [--length] [--reverse]
  name-of-thrones (-h | --help | --version)

Options:
  --version                show program's version number and exit.
  -h, --help               show this help message and exit.
  -q, --quantity=<number>  the quantity of words to generate [default: 10].
  --min=<length>           the minimum length of each word [default: 4].
  --max=<length>           the maximum length of each word [default: 10].
  -j, --json               output the words in JSON format.
  -n, --nocolour           output the words without colourization.
  -a, --alphabetical       output the words in alphabetical order.
  -l, --length             output the words in order of their length.
  -r, --reverse            reverse the order of the words.
"""
import json
from itertools import islice

from colorama import Fore, init, Style
from docopt import docopt

from game_of_thrones import __version__, MarkovChain, sort_words


def main():
    arguments = docopt(__doc__, version=__version__)

    quantity = int(arguments['--quantity'])

    chain = MarkovChain(
        min_length=int(arguments['--min']),
        max_length=int(arguments['--max']),
    )

    words = sort_words(arguments, list(islice(chain.unique_word(), quantity)))

    if arguments['--json']:
        output = {'quantity': quantity}
        output['names'] = words
        print(json.dumps(output))
    else:
        init(autoreset=True)

        for i, word in enumerate(words):
            if i == quantity:
                break

            line = '{:>3}. {:<12}'.format(i + 1, word)

            if arguments['--nocolour']:
                print(line)
            else:
                # alternate row colours
                colour = Fore.BLUE if i % 2 == 0 else Fore.CYAN
                print(Style.BRIGHT + colour + line)

if __name__ == '__main__':
    main()
