import sys
import os
import argparse

import mkpassphrase as M


def main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(description='Generate a passphrase.')
    parser.add_argument('-n', '--num-words', type=int, metavar='NUM_WORDS',
                        help='Number of words in passphrase', default=M.WORDS)
    parser.add_argument('--min', type=int, metavar='MIN',
                        help='Minimum word length', default=M.MIN)
    parser.add_argument('--max', type=int, metavar='MAX',
                        help='Maximum word length', default=M.MAX)
    parser.add_argument('-f', '--word-file', type=str, metavar='WORD_FILE',
                        help='Word file path (one word per line)',
                        default=M.WORD_FILE)
    parser.add_argument('--lowercase', action='store_true', dest='lowercase',
                        help='Make each word entirely lowercase, rather than'
                             ' the default behavior of choosing Titlecase or'
                             ' lowercase for each word (with probability 0.5)')
    parser.add_argument('--non-ascii', action='store_false', dest='ascii',
                        help='Whether to allow words with non-ascii letters')
    parser.add_argument('-p', '--pad', metavar='PAD', default='',
                        help='Pad passphrase using PAD as prefix and suffix')
    parser.add_argument('-d', '--delimiter', dest='delimiter', default=' ',
                        metavar='DELIM',
                        help='Use DELIM to separate words in passphrase')
    parser.add_argument('-t', '--items', dest='times', type=int, default=1,
                        metavar='TIMES', help="Generate TIMES different "
                        "passphrases")
    parser.add_argument('-V', '--version', action='store_true',
                        help="Show version")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Print just the passphrase')

    args = parser.parse_args()
    if args.version:
        print("%s %s" % (M.__name__, M.__version__))
        sys.exit(0)
    if args.min > args.max:
        parser.exit("--max must be equal to or greater than --min")
    if args.min < 1 or args.max < 1:
        parser.exit('--min and --max must be positive')
    if args.num_words < 1:
        parser.exit('--num-words must be positive')
    if args.times < 1:
        parser.exit('--times must be positive')
    if not os.access(args.word_file, os.R_OK):
        parser.exit("word file does not exist or is not readable: %s" %
                    args.word_file)

    for i in range(args.times):
        passphrase, num_candidates = M.mkpassphrase(
            path=args.word_file,
            min=args.min,
            max=args.max,
            num_words=args.num_words,
            lowercase=args.lowercase,
            delim=args.delimiter,
            pad=args.pad,
            ascii=args.ascii
        )
        print(passphrase)

    possibilities = M.num_possible(num_candidates, args.num_words)

    if not args.quiet:
        print("{0:,g} unique candidate words".format(num_candidates))
        print("{0:,g} possible passphrases".format(possibilities))


if __name__ == '__main__':
    main()
