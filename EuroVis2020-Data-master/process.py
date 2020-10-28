import csv, pprint, statistics
from collections import OrderedDict
from datetime import datetime
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
            result[current_participant]['raw_any_data_list'] = []

            result[current_participant]['raw_any_data_list'].append(row)
            if row[ActionType_enum] == 'GetDetail' and 'Article' in row[ActionParameters_enum]:
                result[current_participant]['raw_data_list'].append(row)
        else:
            result[current_participant]['raw_any_data_list'].append(row)
            if row[ActionType_enum] == 'GetDetail' and 'Article' in row[ActionParameters_enum]:
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
    cur['relevant_article_duration'] = 0
    cur['irrelevant_article_duration'] = 0


    cur['article_stats'] = {}


    cur['total_unique_article_read_count'] = 0
    cur['relevant_unique_article_read_count'] = 0
    cur['irrelevant_unique_article_read_count'] = 0


    cur['total_exploration_path_length'] = 0


    cur['total_article_read_count_in_path'] = 0
    cur['relevant_article_read_count_in_path'] = 0
    cur['irrelevant_article_read_count_in_path'] = 0

    cur['avg_revisitation_rate_total_articles'] = 0
    cur['avg_revisitation_rate_relevant_articles'] = 0
    cur['avg_revisitation_rate_irrelevant_articles'] = 0

    cur['avg_time_gap_between_relevant_articles'] = 'NA'

    # print(key,"------")

    if len(cur['raw_any_data_list']) == 0:
        cur['how_long_it_takes_to_read_first_relevant_article'] = 'NA'
        cur['avg_time_gap_between_relevant_articles'] = 'NA'
    else:
        for any_data_row in cur['raw_any_data_list']:
            if any_data_row[ActionType_enum] == 'GetDetail' and 'Article' in any_data_row[ActionParameters_enum] and articles_info[any_data_row[ActionParameters_enum]]['RelevantToTask'] == 'yes':
                first_relevant_article_encounter_time = any_data_row[Time_enum]
                first_relevant_article_encounter_time_object = datetime.strptime(first_relevant_article_encounter_time, '%HH %MM %SS')
                first_any_data_encounter_time = cur['raw_any_data_list'][0][Time_enum]
                first_any_data_encounter_time_object = datetime.strptime(first_any_data_encounter_time, '%HH %MM %SS')
                diff = first_relevant_article_encounter_time_object - first_any_data_encounter_time_object
                print(first_any_data_encounter_time_object, first_relevant_article_encounter_time_object, diff, diff.total_seconds())
                cur['how_long_it_takes_to_read_first_relevant_article'] = diff.total_seconds() # finish cur['avg_time_gap_between_relevant_articles']
                break

        relevant_article_time_gaps_list = []

        actions_by_day_dict = {}
        for any_data_row in cur['raw_any_data_list']:
            temp_day = any_data_row[Day_enum]
            if temp_day in actions_by_day_dict:
                if any_data_row[ActionType_enum] == 'GetDetail' and 'Article' in any_data_row[ActionParameters_enum] and articles_info[any_data_row[ActionParameters_enum]]['RelevantToTask'] == 'yes':
                    current_relevant_article_encounter_time = any_data_row[Time_enum]
                    current_relevant_article_encounter_time_object = datetime.strptime(current_relevant_article_encounter_time, '%HH %MM %SS')
                    actions_by_day_dict[temp_day]['relevant_article_time_dots_list'].append(current_relevant_article_encounter_time_object)
            else:
                actions_by_day_dict[temp_day] = {}
                actions_by_day_dict[temp_day]['relevant_article_time_dots_list'] = []
                actions_by_day_dict[temp_day]['relevant_article_time_gaps_list'] = []
                if any_data_row[ActionType_enum] == 'GetDetail' and 'Article' in any_data_row[ActionParameters_enum] and articles_info[any_data_row[ActionParameters_enum]]['RelevantToTask'] == 'yes':
                    current_relevant_article_encounter_time = any_data_row[Time_enum]
                    current_relevant_article_encounter_time_object = datetime.strptime(current_relevant_article_encounter_time, '%HH %MM %SS')
                    actions_by_day_dict[temp_day]['relevant_article_time_dots_list'].append(current_relevant_article_encounter_time_object)

        for day,daily_dict in actions_by_day_dict.items():
            for i in range(len(daily_dict['relevant_article_time_dots_list'])-1):
                temp_gap = (daily_dict['relevant_article_time_dots_list'][i+1] - daily_dict['relevant_article_time_dots_list'][i]).total_seconds()
                daily_dict['relevant_article_time_gaps_list'].append(temp_gap)
                relevant_article_time_gaps_list.append(temp_gap)

        if len(relevant_article_time_gaps_list) != 0:
            cur['avg_time_gap_between_relevant_articles'] = statistics.mean(relevant_article_time_gaps_list) # finish cur['avg_time_gap_between_relevant_articles']

    if len(cur['raw_data_list']) == 0:
        cur['avg_time_per_article'] = 'NA'
        cur['avg_time_per_relevant_article'] = 'NA'
        cur['avg_time_per_irrelevant_article'] = 'NA'

        cur['avg_revisitation_rate_total_articles'] = 'NA'
        cur['avg_revisitation_rate_relevant_articles'] = 'NA'
        cur['avg_revisitation_rate_irrelevant_articles'] = 'NA'

        cur['avg_time_gap_between_relevant_articles'] = 'NA'
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
                else:
                    cur['irrelevant_unique_article_read_count'] += 1 # finish cur['irrelevant_unique_article_read_count']
            if dur != 'NA':
                cur['total_article_duration'] += int(dur) # finish cur['total_article_duration']

            cur['total_article_read_count_in_path'] += 1 # finish cur['total_article_read_count_in_path']

            if articles_info[article]['RelevantToTask'] == 'yes':
                cur['relevant_article_read_count_in_path'] += 1  # finish cur['relevant_article_read_count_in_path']
                if dur != 'NA':
                    cur['relevant_article_duration'] += int(dur)  # finish cur['relevant_article_duration']
            else:
                cur['irrelevant_article_read_count_in_path'] += 1  # finish cur['irrelevant_article_read_count_in_path']
                if dur != 'NA':
                    cur['irrelevant_article_duration'] += int(dur)  # finish cur['irrelevant_article_duration']

        cur['total_exploration_path_length'] = len(cur['raw_data_list']) # finish cur['total_exploration_path_length']

        cur['avg_time_per_article'] = cur['total_article_duration']/len(cur['raw_data_list']) # finish cur['avg_time_per_article']

        cur['total_unique_article_read_count'] = len(cur['article_stats']) # finish cur['total_unique_article_read_count']

        if cur['relevant_article_read_count_in_path'] != 0:
            cur['avg_time_per_relevant_article'] = cur['relevant_article_duration']/cur['relevant_article_read_count_in_path'] # finish cur['avg_time_per_relevant_article']
        else:
            cur['avg_time_per_relevant_article'] = 'NA'

        if cur['irrelevant_article_read_count_in_path'] != 0:
            cur['avg_time_per_irrelevant_article'] = cur['irrelevant_article_duration']/cur['irrelevant_article_read_count_in_path'] # finish cur['avg_time_per_irrelevant_article']
        else:
            cur['avg_time_per_irrelevant_article'] = 'NA'

        for article_name, article_name_count in cur['article_stats'].items():
            cur['avg_revisitation_rate_total_articles'] += article_name_count
            if articles_info[article_name]['RelevantToTask'] == 'yes':
                cur['avg_revisitation_rate_relevant_articles'] += article_name_count
            else:
                cur['avg_revisitation_rate_irrelevant_articles'] += article_name_count

        cur['avg_revisitation_rate_total_articles'] /= cur['total_unique_article_read_count'] # finish cur['avg_revisitation_rate_total_articles']

        if cur['relevant_unique_article_read_count'] != 0:
            cur['avg_revisitation_rate_relevant_articles'] /= cur['relevant_unique_article_read_count'] # finish cur['avg_revisitation_rate_relevant_articles']
        else:
            cur['avg_revisitation_rate_relevant_articles'] = 'NA' # finish cur['avg_revisitation_rate_relevant_articles']

        if cur['irrelevant_unique_article_read_count'] != 0:
            cur['avg_revisitation_rate_irrelevant_articles'] /= cur['irrelevant_unique_article_read_count']  # finish cur['avg_revisitation_rate_irrelevant_articles']
        else:
            cur['avg_revisitation_rate_irrelevant_articles'] = 'NA' # finish cur['avg_revisitation_rate_irrelevant_articles']

for key, value in result.items():
    print(key)
    for k, v in value.items():
        if k != 'raw_data_list' and k != 'raw_any_data_list':
            print(k,v)

            



