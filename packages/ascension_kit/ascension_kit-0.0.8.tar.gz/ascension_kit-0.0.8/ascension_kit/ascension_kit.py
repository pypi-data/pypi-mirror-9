#!/usr/bin/env python
import nao
import format
import argparse
import os


def main():
    # TODO make saving the file optional
    # TODO make a pretty table
    """ Fetches a users NAO data"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', '-l', help='NAO user list')
    cmd_args = parser.parse_args()

    if not cmd_args.list:
        parser.print_help()
    elif cmd_args.list:
        player_list = [p.strip() for p in cmd_args.list.split(',')]
    print "Fetching games for user(s) %s" % cmd_args.list.split(',')

    players = [nao.get_player_file(p) for p in player_list]

    player_dict = {}
    for p in players:
        dates, scores, roles, ascension_games = nao.process_html(p)
        player_data = dict()
        player_data['dates'] = dates
        player_data['scores'] = scores
        player_data['roles'] = roles
        player_data['ascension_games'] = ascension_games
        player_dict[os.path.basename(p).split('.')[0]] = player_data

    format.process_ascensions(player_dict)


if __name__ == '__main__':
    main()
