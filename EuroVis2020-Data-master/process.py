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

with open('data/eventlog.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    current_participant = ''
    previous_participant = ''
    participants = set()
    result = OrderedDict()
    for row in reader:
        current_participant = row[Participant_enum]
        participants.add(current_participant)
        if current_participant != previous_participant:
            result[current_participant] = {}
            result[current_participant]['raw_data_list'] = []
        elif row[ActionType_enum] == 'GetDetail' and 'Article' in row[ActionParameters_enum]:
            result[current_participant]['raw_data_list'].append(row)
        previous_participant = current_participant

for key, value in result.items():
    cur = result[key]
    cur['total_article_duration'] = 0
    if not cur['raw_data_list']:
        cur['total_article_duration'] = 0
        cur['total_exploration_path'] = 0
    else:
        for r in cur['raw_data_list']:
            dur = r[duration_enum]
            if dur != 'NA':
                cur['total_article_duration'] += int(dur)
        cur['total_exploration_path'] = len(cur['raw_data_list'])

print(result)

