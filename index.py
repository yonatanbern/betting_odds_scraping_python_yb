
print('Scraping project: \n')
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import time
from datetime import datetime
import itertools
from decimal import Decimal

# file to contain results data
f = open("res_data.txt", "a")
f.write("My project:\n")

def convert_to_float(frac_str):
    try:
        return float(frac_str)
    except ValueError:
        try:
            num, denom = frac_str.split('/')
        except ValueError:
            return None
        try:
            leading, num = num.split(' ')
        except ValueError:
            return float(num) / float(denom)
        if float(leading) < 0:
            sign_mult = -1
        else:
            sign_mult = 1
        return float(leading) + sign_mult * (float(num) / float(denom))


def Average(lst):
    return sum(lst) / len(lst)


""" Scrapping Data from oddschecker.com using bs4 & requests module """

res = requests.get('https://www.oddschecker.com/football')
soup = BeautifulSoup(res.text, 'html.parser')


# "*************************** SEC 1+2 START *******************************


football_games_odds_table_tag = soup.select('#outer-container')[0].select('#page-centre-container')[0].find_all('table')[0]
football_games_odds_table = football_games_odds_table_tag.find_all('a')

games_links_dic = {}

for game in football_games_odds_table:
    if game.has_attr('data-event-name'):
        games_links_dic[game.get('data-event-name')] = 'https://www.oddschecker.com' + game.get('href')


# Choose Number of games to be analyzed later by the Algorithm
N_games = 10

# Analyzing the first N-games from website
first_N_games = dict(itertools.islice(games_links_dic.items(), N_games))
# choose number of time you wish to run the algorithm
Num_for_iteration_User_input = 5


num_of_times = 0
while num_of_times < Num_for_iteration_User_input:

    # Dictionary of every game's odds from website
    games_odds_per_match_DB = {}

    # creating the dic explained above
    for g_name, g_link in first_N_games.items():

        games_odds_per_match_DB[g_name] = {}

        time.sleep(1)
        res = requests.get(g_link)
        soup = BeautifulSoup(res.text, 'html.parser')
        time.sleep(1)

        bk_names_table = soup.select('.eventTableHeader')[0].find_all('td')
        booking_agencies_list = []
        for td in bk_names_table:
            if td.has_attr('data-bk'):
                bk_name = td.find('aside').find('a').find('picture').find('img').get('alt')
                booking_agencies_list.append(bk_name)

        game_rows_odds = soup.find_all('tbody')[0].find_all('tr')
        for row in game_rows_odds:
            # print(row.find_all('td'))
            row_per_booking = row.find_all('td')
            i = 0
            for col in row_per_booking:

                if col.has_attr('data-o'):
                    games_odds_per_match_DB[g_name][option_to_bet][booking_agencies_list[i]] = convert_to_float(col.get('data-o'))
                    i += 1

                elif col.get('class')[0] == "sel":
                    a = col.find('a')
                    option_to_bet = a.text
                    games_odds_per_match_DB[g_name][option_to_bet] = {}


    # *************************** SEC 1+2 END *******************************

    #s = '3/4'
    #print(s, convert_to_float(s))
    #print(booking_agencies_list)

    print('****Ans Sec 1+2*****')
    print('DB:', games_odds_per_match_DB)
    f.write('\nDB:' + '\n')
    f.write(str(games_odds_per_match_DB) + '\n')

    # "*************************** SEC 3 START *******************************

    # Algorithm Alerts important Changes in the odds

    if num_of_times == 0:
        Game_avg_per_option = {}

    num_of_iteration = 0

    for match in games_odds_per_match_DB:
        #print('Game: ', match)
        if num_of_times == 0:
            Game_avg_per_option[match] = {}

        for option in games_odds_per_match_DB[match].keys():
            #print(option)
            if num_of_times == 0:
                Game_avg_per_option[match][option] = {}
            list_of_odds_nums = []

            for bk_key in games_odds_per_match_DB[match][option].keys():
                odd_game = games_odds_per_match_DB[match][option][bk_key]
                if odd_game is not None:
                    #print(odd_game, end=' ')
                    list_of_odds_nums.append(odd_game)

            curr_odd_avg = Average(list_of_odds_nums)

            if num_of_times == 0:

                Game_avg_per_option[match][option] = [curr_odd_avg, curr_odd_avg, curr_odd_avg]

            else:

                #print('this is herere')
                #print(Game_avg_per_option[match][option][1])
                if curr_odd_avg > Game_avg_per_option[match][option][1]:

                    Game_avg_per_option[match][option][1] = curr_odd_avg
                elif curr_odd_avg < Game_avg_per_option[match][option][2]:
                    Game_avg_per_option[match][option][2] = curr_odd_avg

                Game_avg_per_option[match][option][0] = curr_odd_avg
                #print('in elseee')


    print(f'this is the {num_of_times} iteration!')
    num_of_times += 1
    print(time.time())
    f.write('Time stamp:: ' + str(time.time()) + '\n')
    if num_of_times != Num_for_iteration_User_input:
        print('sleep 30 sec')
        time.sleep(30)


print('\nAverage table per Match: ', Game_avg_per_option)
f.write('\n\nAverage table per Match - Format: Game, bet-option -> [latest-avg-score odd, Max-avg-score odd, '
        'Min-avg-score ''odd]:\n')
f.write(str(Game_avg_per_option))

# Decide the threshold to get alarms: the more higher more sensitive and less alerts
score_threshold = 1.2

for match in Game_avg_per_option:
    # print(match)
    # print(Game_avg_per_option[match])
    for opt in Game_avg_per_option[match].keys():
        max_score_odd = Game_avg_per_option[match][opt][1]
        min_score_odd = Game_avg_per_option[match][opt][2]
        # condition for alerts
        if max_score_odd - min_score_odd > score_threshold:
            print("ALERT:")
            f.write("\nALERT:\n")
            print(match, opt, Game_avg_per_option[match][opt])
            f.write(str(match) + ' ')
            f.write(str(opt) + ' ')
            f.write(str(Game_avg_per_option[match][opt]) + '\n')

# print(Game_avg_per_option)
f.close()
print('\nFINISH')
