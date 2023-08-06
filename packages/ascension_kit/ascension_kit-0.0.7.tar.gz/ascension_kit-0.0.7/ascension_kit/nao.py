# !/usr/bin/python
import urllib2
import bs4
import sys
import os
import time


def is_stale(player_name):
    file_age = time.time() - os.path.getmtime(player_name)

    if file_age > 86400:
        return True
    else:
        return False


def check_cache(player_name):
    file = player_name

    if os.path.isfile(file):
        return True
    else:
        return False


def download_file(player_name):
    url = 'http://alt.org/nethack/player-all-xlog.php?player=%s' % (os.path.basename(player_name).split('.')[0])

    response = urllib2.urlopen(url)

    html = response.read()

    with open(player_name, 'wb') as f:
        f.write(html)

    return html


def get_player_file(player_list):
    '''
    This function will save the associated player_name html file
    # TODO accept a list of player names and download in threads.
    # TODO cache files for a length of time so we aren't always hitting the server.
    '''

    for p in player_list.split(','):

        file = '/tmp/' + p + '.html'

        if check_cache(file):

            if not is_stale(file):
                print "File is still fresh. Using local cached file for %s." % (p)
            else:
                print "file is stale, downloading xlog for %s." % (p)
                download_file(file)
        else:
            print "No cache found for %s, downloading." % (p)
            download_file(file)

    return file


def process_html(player_file):
    '''
    Processes the html file(s) of the users
    :param player_file:
    :return: lists of things
    '''
    player_name, dates, scores, roles, ascension_games = [], [], [], [], []
    player_games = {}
    with open(player_file, 'r') as file:
        soup = bs4._soup(file)
    try:
        games = soup.findAll('pre')[0].string.split('\n')
    except IndexError:
        print "No games found for user %s. Maybe check spelling?" % os.path.basename(player_file).split('.')[0]
        os.remove(player_file)
        sys.exit(99)

    for i in range(0, len(games) - 1):
        keys = [t.split('=')[0] for t in games[i].split(':')]
        values = [t.split('=')[1] for t in games[i].split(':')]
        all_games = dict(zip(keys, values))

        dates.append(str(all_games['deathdate']))
        scores.append(int(all_games['points']))
        roles.append(str(all_games['role']))

        if str(all_games['death']) == 'ascended':
            ascension_games.append(all_games)

    return dates, scores, roles, ascension_games
