import csv, pprint
from collections import OrderedDict
Serial_enum = 0
Participant_enum = 1
ActionType_enum = 2
ActionParameters_enum = 3
Date_enum = 4
Time_enum = 5
Group_enum = 6
Day_enum = 7
duration_enum = 8


result = OrderedDict() # stores the data collection results
articles_info = OrderedDict() # stores article information
with open('data/eventlog.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    current_participant = ''
    previous_participant = ''
    participants = set()
    for row in reader:
        current_participant = row[Participant_enum]
        participants.add(current_participant)
        if current_participant != previous_participant:
            result[current_participant] = {}
            result[current_participant]['raw_data_list'] = []
        elif row[ActionType_enum] == 'GetDetail' and 'Article' in row[ActionParameters_enum]:
            result[current_participant]['raw_data_list'].append(row)
        previous_participant = current_participant

with open('data/article_info.csv', 'r') as file:
    reader_articles_info = csv.reader(file)
    next(reader_articles_info)
    for row in reader_articles_info:
        current_article_num = row[0]
        articles_info['Article ' + current_article_num] = {}
        articles_info['Article ' + current_article_num]['RelevantToTask'] = row[1]
        articles_info['Article ' + current_article_num]['Original'] = row[2]

for key, value in result.items():
    cur = result[key] # key --> Participant code; cur --> each participant's individual info dict

    # stats collected and default values
    cur['total_article_duration'] = 0

    cur['article_stats'] = {}

    cur['total_unique_article_read_count'] = 0

    cur['relevant_unique_article_read_count'] = 0

    cur['total_exploration_path_length'] = 0

    cur['total_article_read_count_in_path'] = 0

    cur['relevant_article_read_count_in_path'] = 0

    if len(cur['raw_data_list']) == 0:
        cur['avg_time_per_article'] = 'NA' # finish cur['avg_time_per_article']
    else:
        for r in cur['raw_data_list']:
            dur = r[duration_enum]
            article = r[ActionParameters_enum]
            if article in cur['article_stats']:
                cur['article_stats'][article] += 1
            else:
                cur['article_stats'][article] = 1 # finish cur['article_stats']
                if articles_info[article]['RelevantToTask'] == 'yes':
                    cur['relevant_unique_article_read_count'] += 1 # finish cur['relevant_unique_article_read_count']

            if dur != 'NA':
                cur['total_article_duration'] += int(dur) # finish cur['total_article_duration']

            cur['total_article_read_count_in_path'] += 1 # finish cur['total_article_read_count_in_path']

            if articles_info[article]['RelevantToTask'] == 'yes':
                cur['relevant_article_read_count_in_path'] += 1  # finish cur['relevant_article_read_count_in_path']

        cur['total_exploration_path_length'] = len(cur['raw_data_list']) # finish cur['total_exploration_path_length']
        cur['avg_time_per_article'] = cur['total_article_duration']/len(cur['raw_data_list']) # finish cur['avg_time_per_article']
        cur['total_unique_article_read_count'] = len(cur['article_stats']) # finish cur['total_unique_article_read_count']


pprint.pprint(result)

