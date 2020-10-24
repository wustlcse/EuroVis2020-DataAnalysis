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
    cur['total_article_duration'] = 0
    if not cur['raw_data_list']:
        cur['total_article_duration'] = 0
        cur['total_exploration_path'] = 0
        cur['avg_time_per_article'] = 'NA'
    else:
        for r in cur['raw_data_list']:
            dur = r[duration_enum]
            if dur != 'NA':
                cur['total_article_duration'] += int(dur)
        cur['total_exploration_path'] = len(cur['raw_data_list'])
        cur['avg_time_per_article'] = cur['total_article_duration']/len(cur['raw_data_list'])

print(result)

