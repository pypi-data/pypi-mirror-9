import sys
import utils
from prettytable import PrettyTable

table = PrettyTable(['Player', 'Total Games', 'Ascensions', 'Pct', 'Avg. Turns', 'Fastest',
                     'Slowest', 'Total Turns', 'Total Points', 'Avg. Points', 'Time Spent'])


def process_ascensions(player_dict):
    for p in player_dict:
        if len(player_dict[p]['ascension_games']) == 0:
            print "No ascensions for %s. Total games: %s" % (p, len(player_dict[p]['dates']))
            sys.exit(99)

        roles = [str(g['role']) for g in player_dict[p]['ascension_games']]
        race = [str(g['race']) for g in player_dict[p]['ascension_games']]
        gender0 = [str(g['gender0']) for g in player_dict[p]['ascension_games']]
        gender = [str(g['gender']) for g in player_dict[p]['ascension_games']]
        align0 = [str(g['align0']) for g in player_dict[p]['ascension_games']]
        align = [str(g['align']) for g in player_dict[p]['ascension_games']]
        points = [int(g['points']) for g in player_dict[p]['ascension_games']]
        turns = [int(g['turns']) if g['turns'] else 0 for g in player_dict[p]['ascension_games']]
        dates = [str(g['deathdate']) for g in player_dict[p]['ascension_games']]
        maxlvl = [int(g['maxlvl']) for g in player_dict[p]['ascension_games']]
        realtime = [int(g['realtime']) if g['realtime'] else 0 for g in player_dict[p]['ascension_games']]
        total_games = len(player_dict[p]['dates'])
        dhm = utils.seconds_to_days_hours_mins(sum(realtime))

        if len(player_dict) == 1:
            print ''
            print '{:^40}'.format('[ Ascensions ]')
            print ''
            print '{:40} {:,}'.format('Total Games', total_games)
            print '{:40} {:,} ({:.2%})'.format('Ascensions', len(points), float(len(points)) / float(total_games))
            print '{:40} {:,}'.format('Average turns/ascension', (sum(turns)) / len(turns))
            print '{:40} {:,}'.format('Fastest Ascension', min(turns))
            print '{:40} {:,}'.format('Slowest Ascension', max(turns))
            print ''
            print '{:40} {:,}'.format('Total Ascension Turns', sum(turns))
            print ''
            print '{:40} {:,}'.format('Total Points', sum(points))
            print '{:40} {:,}'.format('Average Points/Ascension', (sum(points)) / (len(points)))
            print '{:40} {} days {} hours {} minutes'.format('Time Spent Ascending', dhm[0], dhm[1], dhm[2])
            sys.exit(0)

        table.add_row([p, len(player_dict[p]['dates']),
                       int(len(points)),
                       str(round((float(len(points)) / float(len(player_dict[p]['dates']))), 5) * 100) + ' %',
                       sum(turns) / len(turns), min(turns), max(turns), sum(turns),
                       sum(points), (sum(points)) / (len(points)),
                       str(dhm[0]) + 'd ' + str(dhm[1]) + 'h ' + str(dhm[2]) + 'm '])

        table.align = 'r'

    table.sortby = 'Avg. Turns'
    print table
