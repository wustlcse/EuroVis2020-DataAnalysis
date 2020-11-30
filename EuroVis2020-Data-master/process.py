import csv, pprint, statistics,collections
from collections import OrderedDict
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
import seaborn as sns
import chart_studio.plotly as py
import plotly.figure_factory as ff
import chart_studio
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import statsmodels.api as sm
pio.renderers.default = "browser"
chart_studio.tools.set_credentials_file(username='ZLLIU', api_key='6LoZSiPvYPEmQgTSugzh')


Serial_enum = 0
Participant_enum = 1
ActionType_enum = 2
ActionParameters_enum = 3
Date_enum = 4
Time_enum = 5
Group_enum = 6
Day_enum = 7
duration_enum = 8

keywords_list = ['Henk','Brodogi','Carmine','Osvaldo','Yanick','Cato','Loreto','Katell','Ale','Hanne',
                 'Jeroen','Karel','Valentine','Mies','Elian','Silvia','Marek','Lucio','Jakab','Joachim',
                 'Jirair','Mandor','Isia','Vann','Ferro',
                 'Rocha','Stefano','Hennie','Inga','Ruscella','Haber','Bodrogi','Carla','Forluniau',
                 'Cornelia','Lais','Minke']


result = OrderedDict() # stores the data collection results
articles_info = OrderedDict() # stores article information
participants_info = OrderedDict() # stores participant info

employee_record_relevant_dict = OrderedDict()
email_header_relevant_dict = OrderedDict()
edit_notes_relevant_dict = OrderedDict()


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
            result[current_participant] = OrderedDict()
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

names_in_survey_csv_set = set()
with open('data/survey.csv', 'r') as file:
    reader_participants_info = csv.reader(file)
    next(reader_participants_info)
    for row in reader_participants_info:
        current_participant_id = row[8]
        names_in_survey_csv_set.add(current_participant_id)
        participants_info[current_participant_id] = {}
        participants_info[current_participant_id]['LOC'] = row[len(row)-1]
        participants_info[current_participant_id]['LOC-score'] = int(row[len(row)-2])
        participants_info[current_participant_id]['Extraversion-score'] = int(row[153])

with open('Assignment1 Data/Assignment1 Data/EmployeeRecords.csv', 'r') as file:
    reader_employee_record_relevant = csv.reader(file)
    next(reader_employee_record_relevant)
    count_employee_record_relevant = 1
    for row in reader_employee_record_relevant:
        current_lastname = row[0]
        if any(ext.lower() in current_lastname.lower() for ext in keywords_list):
            employee_record_relevant_dict['Employee Record ' + str(count_employee_record_relevant)] = 'yes'
        else:
            employee_record_relevant_dict['Employee Record ' + str(count_employee_record_relevant)] = 'no'
        count_employee_record_relevant += 1

with open('Assignment1 Data/Assignment1 Data/email headers.csv', 'r') as file:
    reader_email_header_relevant = csv.reader(file)
    next(reader_email_header_relevant)
    count_email_header_relevant = 1
    for row in reader_email_header_relevant:
        email_from = row[0]
        if any(ext.lower() in email_from.lower() for ext in keywords_list):
            email_header_relevant_dict['Email Header ' + str(count_email_header_relevant)] = 'yes'
        else:
            email_header_relevant_dict['Email Header ' + str(count_email_header_relevant)] = 'no'
        count_email_header_relevant += 1


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

    cur['total_resume_read_count_in_path'] = 0
    cur['total_employeerecord_read_count_in_path'] = 0
    cur['total_emailheaders_read_count_in_path'] = 0

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

        articles_actions_info = OrderedDict()  # stores actions that follow each article read
        current_article_block = ''
        previous_article_block = ''
        current_article_block_temp_name = ''
        previous_article_block_temp_name = ''
        articles_actions_info['article_counts'] = OrderedDict()
        articles_actions_info['article_actions'] = OrderedDict()

        cur['total_editnotes_count'] = 0
        cur['total_search_count'] = 0
        cur['total_getdetail_nonarticle_count'] = 0
        cur['total_addelement_count'] = 0
        cur['total_addconnection_count'] = 0

        cur['total_relevant_editnotes_count'] = 0
        cur['total_relevant_search_count'] = 0
        cur['total_relevant_getdetail_nonarticle_count'] = 0
        cur['total_relevant_addelement_count'] = 0
        cur['total_relevant_addconnection_count'] = 0

        cur['avg_editnotes_count_per_article'] = 'NA'
        cur['avg_search_count_per_article'] = 'NA'
        cur['avg_getdetail_nonarticle_count_per_article'] = 'NA'
        cur['avg_addelement_count_per_article'] = 'NA'
        # cur['avg_total_addconnection_count_per_article'] = 'NA'
        #
        # cur['avg_editnotes_count_per_relevant_article'] = 'NA'
        # cur['avg_search_count_per_relevant_article'] = 'NA'
        # cur['avg_total_getdetail_nonarticle_count_per_relevant_article'] = 'NA'
        # cur['avg_total_addelement_count_per_relevant_article'] = 'NA'
        # cur['avg_total_addconnection_count_per_relevant_article'] = 'NA'
        #
        # cur['avg_editnotes_count_per_irrelevant_article'] = 'NA'
        # cur['avg_search_count_per_irrelevant_article'] = 'NA'
        # cur['avg_total_getdetail_nonarticle_count_per_irrelevant_article'] = 'NA'
        # cur['avg_total_addelement_count_per_irrelevant_article'] = 'NA'
        # cur['avg_total_addconnection_count_per_irrelevant_article'] = 'NA'

        for any_data_row in cur['raw_any_data_list']:
            if any_data_row[ActionType_enum] == 'GetDetail' and 'Article' not in any_data_row[ActionParameters_enum]:
                cur['total_getdetail_nonarticle_count'] += 1
                if any(ext.lower() in any_data_row[ActionParameters_enum].lower() for ext in keywords_list):
                    cur['total_relevant_getdetail_nonarticle_count'] += 1

            if any_data_row[ActionType_enum] == 'EditNotes':
                cur['total_editnotes_count'] += 1

            if any_data_row[ActionType_enum] == 'Search':
                cur['total_search_count'] += 1
                if any(ext.lower() in any_data_row[ActionParameters_enum].lower() for ext in keywords_list):
                    cur['total_relevant_search_count'] += 1

            if any_data_row[ActionType_enum] == 'AddElement':
                cur['total_addelement_count'] += 1
                if any(ext.lower() in any_data_row[ActionParameters_enum].lower() for ext in keywords_list):
                    cur['total_relevant_addelement_count'] += 1

            if any_data_row[ActionType_enum] == 'AddConnection':
                cur['total_addconnection_count'] += 1
                if any(ext.lower() in any_data_row[ActionParameters_enum].lower() for ext in keywords_list):
                    cur['total_relevant_addconnection_count'] += 1

            if any_data_row[ActionType_enum] == 'GetDetail' \
                    and ('Resume' in any_data_row[ActionParameters_enum] or 'Bio' in any_data_row[ActionParameters_enum]):
                cur['total_resume_read_count_in_path'] += 1 # finish cur['total_resume_read_count_in_path']

            if any_data_row[ActionType_enum] == 'GetDetail' and 'Record' in any_data_row[ActionParameters_enum]:
                cur['total_employeerecord_read_count_in_path'] += 1 # finish cur['total_employeerecord_read_count_in_path']

            if any_data_row[ActionType_enum] == 'GetDetail' and 'Header' in any_data_row[ActionParameters_enum]:
                cur['total_emailheaders_read_count_in_path'] += 1 # finish cur['total_emailheaders_read_count_in_path']

            if any_data_row[ActionType_enum] == 'GetDetail' and 'Article' in any_data_row[ActionParameters_enum]:
                current_article_block = any_data_row[ActionParameters_enum]
                # print(current_article_block, any_data_row)
                if current_article_block in articles_actions_info['article_counts']:
                    articles_actions_info['article_counts'][current_article_block] += 1
                else:
                    if len(current_article_block) != 0:
                        articles_actions_info['article_counts'][current_article_block] = 1

            if len(current_article_block) != 0:
                temp_name = current_article_block + '_' + str(articles_actions_info['article_counts'][current_article_block])
                current_article_block_temp_name = temp_name
                if current_article_block != previous_article_block or current_article_block_temp_name != previous_article_block_temp_name:
                    # print(temp_name + " is created")
                    articles_actions_info['article_actions'][temp_name] = []
                    articles_actions_info['article_actions'][temp_name].append(any_data_row)
                else:
                    articles_actions_info['article_actions'][temp_name].append(any_data_row)
            previous_article_block = current_article_block
            previous_article_block_temp_name = current_article_block_temp_name
        cur['articles_actions_info_dict'] = articles_actions_info

        cur['percentage_editnotes_count'] = cur['total_editnotes_count'] / (cur['total_editnotes_count'] + cur['total_search_count'] + cur['total_getdetail_nonarticle_count'] + cur['total_addelement_count'] + cur['total_addconnection_count'])
        cur['percentage_search_count'] = cur['total_search_count'] / (cur['total_editnotes_count'] + cur['total_search_count'] + cur['total_getdetail_nonarticle_count'] + cur['total_addelement_count'] + cur['total_addconnection_count'])
        cur['percentage_getdetail_nonarticle_count'] = cur['total_getdetail_nonarticle_count'] / (cur['total_editnotes_count'] + cur['total_search_count'] + cur['total_getdetail_nonarticle_count'] + cur['total_addelement_count'] + cur['total_addconnection_count'])
        cur['percentage_addelement_count'] = cur['total_addelement_count'] / (cur['total_editnotes_count'] + cur['total_search_count'] + cur['total_getdetail_nonarticle_count'] + cur['total_addelement_count'] + cur['total_addconnection_count'])
        cur['percentage_addconnection_count'] = cur['total_addconnection_count'] / (cur['total_editnotes_count'] + cur['total_search_count'] + cur['total_getdetail_nonarticle_count'] + cur['total_addelement_count'] + cur['total_addconnection_count'])
        cur['percentage_releveant_search'] = 'NA'
        if cur['total_search_count'] != 0:
            cur['percentage_releveant_search'] = cur['total_relevant_search_count']/cur['total_search_count']






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

        cur['avg_editnotes_count_per_article'] = cur['total_editnotes_count'] / len(cur['raw_data_list'])
        cur['avg_search_count_per_article'] = cur['total_search_count'] / len(cur['raw_data_list'])
        cur['avg_getdetail_nonarticle_count_per_article'] = cur['total_getdetail_nonarticle_count'] / len(cur['raw_data_list'])
        cur['avg_addelement_count_per_article'] = cur['total_addelement_count'] / len(cur['raw_data_list'])

        cur['total_unique_article_read_count'] = len(cur['article_stats']) # finish cur['total_unique_article_read_count']

        if cur['relevant_article_read_count_in_path'] != 0:
            cur['avg_time_per_relevant_article'] = cur['relevant_article_duration']/cur['relevant_article_read_count_in_path'] # finish cur['avg_time_per_relevant_article']
        else:
            cur['avg_time_per_relevant_article'] = 'NA'

        if cur['irrelevant_article_read_count_in_path'] != 0:
            cur['avg_time_per_irrelevant_article'] = cur['irrelevant_article_duration']/cur['irrelevant_article_read_count_in_path'] # finish cur['avg_time_per_irrelevant_article']
        else:
            cur['avg_time_per_irrelevant_article'] = 'NA'

        if cur['relevant_article_read_count_in_path'] != 0 or cur['irrelevant_article_read_count_in_path'] != 0:
            cur['percentage_relevant_read_count_in_path'] = cur['relevant_article_read_count_in_path']/cur['total_exploration_path_length']
            cur['percentage_irrelevant_read_count_in_path'] = cur['irrelevant_article_read_count_in_path']/cur['total_exploration_path_length']
        else:
            cur['percentage_relevant_read_count_in_path'] = 'NA'
            cur['percentage_irrelevant_read_count_in_path'] = 'NA'


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

    cur['LOC'] = 'NA'
    if key in participants_info:
        cur['LOC'] = participants_info[key]['LOC']
        cur['LOC-score'] = participants_info[key]['LOC-score']
        cur['Extraversion-score'] = participants_info[key]['Extraversion-score']

    cur['percentage_editnotes_count'] = cur['total_editnotes_count'] / (
                cur['total_editnotes_count'] + cur['total_search_count'] + cur['total_getdetail_nonarticle_count'] +
                cur['total_addelement_count'] + cur['total_addconnection_count'] + cur['total_exploration_path_length'])

    cur['percentage_search_count'] = cur['total_search_count'] / (
                cur['total_editnotes_count'] + cur['total_search_count'] + cur['total_getdetail_nonarticle_count'] +
                cur['total_addelement_count'] + cur['total_addconnection_count'] + cur['total_exploration_path_length'])

    cur['percentage_getdetail_nonarticle_count'] = cur['total_getdetail_nonarticle_count'] / (
                cur['total_editnotes_count'] + cur['total_search_count'] + cur['total_getdetail_nonarticle_count'] +
                cur['total_addelement_count'] + cur['total_addconnection_count'] + cur['total_exploration_path_length'])

    cur['percentage_addelement_count'] = cur['total_addelement_count'] / (
                cur['total_editnotes_count'] + cur['total_search_count'] + cur['total_getdetail_nonarticle_count'] +
                cur['total_addelement_count'] + cur['total_addconnection_count'] + cur['total_exploration_path_length'])

    cur['percentage_addconnection_count'] = cur['total_addconnection_count'] / (
                cur['total_editnotes_count'] + cur['total_search_count'] + cur['total_getdetail_nonarticle_count'] +
                cur['total_addelement_count'] + cur['total_addconnection_count'] + cur['total_exploration_path_length'])

    cur['percentage_article_read_count'] = cur['total_exploration_path_length'] / (
                cur['total_editnotes_count'] + cur['total_search_count'] + cur['total_getdetail_nonarticle_count'] +
                cur['total_addelement_count'] + cur['total_addconnection_count'] + cur['total_exploration_path_length'])

no_NA_result_dict = {}
NA_flag = 0
all_names = []
all_good_names = []
all_good_names_locscores = []
all_good_names_set = set()
has_NA_names = []
has_NA_names_set = set()
no_loc_names = []

has_loc_names = []
has_loc_has_some_NA_names = []
for key, value in result.items():
    # print(key)
    all_names.append(key)
    for k, v in value.items():
        # if k != 'raw_data_list' and k != 'raw_any_data_list' and k != 'article_stats' and k != 'articles_actions_info_dict':
        #     print(k,v)
        if k == 'LOC' and v == 'NA':
            print(key, 'no LOC')
            no_loc_names.append(key)
        if v == 'NA':
            NA_flag = 1
            has_NA_names_set.add(key)
            if key not in has_NA_names:
                has_NA_names.append(key)
    if NA_flag == 0:
        no_NA_result_dict[key] = value
        all_good_names.append(key)
        all_good_names_locscores.append(int(no_NA_result_dict[key]['LOC-score']))
        all_good_names_set.add(key)

    NA_flag = 0

for name in has_NA_names:
    if result[name]['LOC'] != 'NA':
        has_loc_has_some_NA_names.append(name)

compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
print(compare(has_NA_names, no_loc_names))
print(has_NA_names_set)
print(no_loc_names)

print('all_names',len(all_names))
print('all_good_names', len(all_good_names))
print('has_NA_names', len(has_NA_names))
print('has_loc_has_some_NA_names',len(has_loc_has_some_NA_names))
print('no_loc_names',len(no_loc_names))

internal_names = []
external_names = []
intermediate_names = []
for name in all_good_names:
    if result[name]['LOC'] == 'Internal':
        internal_names.append(name)
    elif result[name]['LOC'] == 'External':
        external_names.append(name)
    elif result[name]['LOC'] == 'Intermediate':
        intermediate_names.append(name)
print('internals', len(internal_names))
print('externals', len(external_names))
print('intermediates', len(intermediate_names))

print(names_in_survey_csv_set.difference(set(all_names)))



df_formatted_dict = {}
df_formatted_dict['names'] = []
df_columns=[]
df_columns.append('names')
for key, value in no_NA_result_dict.items():
    #print(key,'\n')
    df_formatted_dict['names'].append(key)
    for k, v in value.items():
        if k != 'raw_data_list' and k != 'raw_any_data_list' and k != 'article_stats' and k != 'articles_actions_info_dict':
            #print(k,v)
            if k in df_formatted_dict:
                df_formatted_dict[k].append(v)
            else:
                df_formatted_dict[k] = []
                df_columns.append(k)
                df_formatted_dict[k].append(v)




# print(df_formatted_dict)
# print(df_columns)
# raw_data = {'first_name': ['Jason', 'Molly', 'Tina', 'Jake', 'Amy'],
#         'last_name': ['Miller', 'Jacobson', ".", 'Milner', 'Cooze'],
#         'age': [42, 52, 36, 24, 73],
#         'preTestScore': [4, 24, 31, ".", "."],
#         'postTestScore': ["25,000", "94,000", 57, 62, 70]}
# df = pd.DataFrame(raw_data, columns = ['first_name', 'last_name', 'age', 'preTestScore', 'postTestScore'])
df = pd.DataFrame(df_formatted_dict, columns = df_columns)
small_df = df[df.columns[-5:]]
# print(df)
# print(small_df)
# y_target = df[df.columns[-1]]
#
# fig = ff.create_scatterplotmatrix(small_df, diag='box', index='LOC',
#                                   height=1000, width=1000)
# py.iplot(fig, filename='Box plots along Diagonal Subplots')
#
# pd.set_option('display.max_columns', None)


# print(df.groupby('LOC', as_index=False).mean())
#
html = df.groupby('LOC', as_index=False).mean().to_html(classes='table table-striped')

#write html to file
text_file = open("ind2.html", "w")
text_file.write(html)
text_file.close()

df.groupby('LOC', as_index=False).mean().to_csv(r'mean_results.csv', index = False)

# fig = px.scatter(df, x="LOC-score", y="total_article_duration",color="LOC", trendline="ols")
#
#
# results = px.get_trendline_results(fig)
# print(results)

fig = px.scatter(
    df,
    x="Extraversion-score",
    y="total_article_duration",
trendline="ols",color='LOC'
)

# linear regression
regline = sm.OLS(df['total_article_duration'],sm.add_constant(df['Extraversion-score'])).fit().fittedvalues

# add linear regression line for whole sample
fig.add_traces(go.Scatter(x=df['Extraversion-score'], y=regline,
                          mode = 'lines',
                          marker_color='blue',
                          name='trend all')
                          )

fig.write_html("plot.html")

participant_searchlist_dict = OrderedDict()
participant_actionlist_dict = OrderedDict()
participant_articleread_dict = OrderedDict()
participant_editnotes_dict = OrderedDict()

all_search_list = []
all_search_actors_list = []
all_search_day_list = []
all_search_time_list = []
all_search_relevancy_list = []
all_search_actors_locscore_list = []
all_search_actors_loc_list = []
all_search_content_list = []
all_search_tag_list = []
for key, value in no_NA_result_dict.items():
    print("name: ", key)
    count_search = 0
    for k, v in value.items():
        if k == 'raw_any_data_list':
            for action_row in v:
                if action_row[ActionType_enum] == 'Search':

                    all_search_list.append(key + 'search' + str(count_search))
                    all_search_tag_list.append("search")
                    all_search_actors_list.append(key)
                    all_search_day_list.append(action_row[Day_enum])
                    all_search_time_list.append(datetime.strptime(action_row[Time_enum], '%HH %MM %SS'))
                    all_search_actors_locscore_list.append(no_NA_result_dict[key]['LOC-score'])
                    all_search_actors_loc_list.append(no_NA_result_dict[key]['LOC'])
                    all_search_content_list.append(action_row[ActionParameters_enum])
                    if any(ext.lower() in action_row[ActionParameters_enum].lower()
                            for ext in keywords_list):
                        all_search_relevancy_list.append('relevant')
                    else:
                        all_search_relevancy_list.append('irrelevant')
                    count_search += 1

all_search_df = pd.DataFrame(
    {'search_action_names': all_search_list,
     'search_actors': all_search_actors_list,
     'search_days': all_search_day_list,
     'search_times': all_search_time_list,

     'search_relevancies':all_search_relevancy_list,
     'search_actors_locscore':all_search_actors_locscore_list,
     'search_actors_loc':all_search_actors_loc_list,
     'search_content':all_search_content_list,
     'tag':all_search_tag_list,
    })


print(all_search_df)
all_good_names_sorted_by_locscore = [x for _,x in sorted(zip(all_good_names_locscores,all_good_names))]

search_scatter_fig = px.scatter(all_search_df, x="search_times", y="search_actors",
                                labels={
                                    "search_actors": "search_actors",
                                },
                                color_discrete_map={
                                    "irrelevant": "purple",
                                    "relevant": "red"
                                },
                                facet_col="search_days", color="search_relevancies", hover_data=all_search_df.columns)
search_scatter_fig.update_yaxes(categoryorder='array', categoryarray= all_good_names_sorted_by_locscore)
search_scatter_fig.update_layout(margin=dict(l=300))
search_scatter_fig.update_xaxes(tickformat='%H:%M')

search_scatter_fig.add_annotation(xref='paper', x=-0.15, yref='paper', y=0.1,
            text="<--- More Internal      |      More External --->",
            showarrow=False,
            textangle=-90,
            font_size= 18
            )
search_scatter_fig.add_hrect(y0=22.5, y1=24.5, line_width=0, fillcolor="red", opacity=0.2,annotation_text="Externals")
search_scatter_fig.add_hrect(y0=12.5, y1=22.5, line_width=0, fillcolor="blue", opacity=0.2,annotation_text="Intermediates")
search_scatter_fig.add_hrect(y0=-0.5, y1=12.5, line_width=0, fillcolor="green", opacity=0.2,annotation_text="Internals")

search_scatter_fig.write_html("search_scatter.html")

all_resumeread_list = []
all_resumeread_actors_list = []
all_resumeread_day_list = []
all_resumeread_time_list = []
all_resumeread_relevancy_list = []
all_resumeread_actors_locscore_list = []
all_resumeread_actors_loc_list = []
all_resumeread_content_list = []
all_resumeread_tag_list = []
for key, value in no_NA_result_dict.items():
    # print("name: ", key)
    count_resumeread = 0
    for k, v in value.items():
        if k == 'raw_any_data_list':
            for action_row in v:
                if action_row[ActionType_enum] == 'GetDetail' and \
                        ('Resume' in action_row[ActionParameters_enum] or 'Bio' in action_row[ActionParameters_enum]):

                    all_resumeread_list.append(key + 'resume' + str(count_resumeread))
                    all_resumeread_tag_list.append("resumeread")
                    all_resumeread_actors_list.append(key)
                    all_resumeread_day_list.append(action_row[Day_enum])
                    all_resumeread_time_list.append(datetime.strptime(action_row[Time_enum], '%HH %MM %SS'))
                    all_resumeread_actors_locscore_list.append(no_NA_result_dict[key]['LOC-score'])
                    all_resumeread_actors_loc_list.append(no_NA_result_dict[key]['LOC'])
                    all_resumeread_content_list.append(action_row[ActionParameters_enum])
                    if any(ext.lower() in action_row[ActionParameters_enum].lower() for ext in keywords_list):
                        all_resumeread_relevancy_list.append('relevant')
                    else:
                        all_resumeread_relevancy_list.append('irrelevant')
                    count_resumeread += 1

all_resumeread_df = pd.DataFrame(
    {'resumeread_action_names': all_resumeread_list,
     'resumeread_actors': all_resumeread_actors_list,
     'resumeread_days': all_resumeread_day_list,
     'resumeread_times': all_resumeread_time_list,

     'resumeread_relevancies':all_resumeread_relevancy_list,
     'resumeread_actors_locscore':all_resumeread_actors_locscore_list,
     'resumeread_actors_loc':all_resumeread_actors_loc_list,
     'resumeread_content':all_resumeread_content_list,
     'tag':all_resumeread_tag_list
    })

resumeread_scatter_fig = px.scatter(all_resumeread_df, x="resumeread_times", y="resumeread_actors",
                                labels={
                                    "resumeread_actors": "resumeread_actors",
                                },
                                color_discrete_map={
                                    "irrelevant": "purple",
                                    "relevant": "red"
                                },
                                facet_col="resumeread_days", color="resumeread_relevancies", hover_data=all_resumeread_df.columns)
resumeread_scatter_fig.update_yaxes(categoryorder='array', categoryarray= all_good_names_sorted_by_locscore)
resumeread_scatter_fig.update_layout(margin=dict(l=300))
resumeread_scatter_fig.update_xaxes(tickformat='%H:%M')

resumeread_scatter_fig.add_annotation(xref='paper', x=-0.15, yref='paper', y=0.1,
            text="<--- More Internal      |      More External --->",
            showarrow=False,
            textangle=-90,
            font_size= 18
            )
resumeread_scatter_fig.add_hrect(y0=22.5, y1=24.5, line_width=0, fillcolor="red", opacity=0.2,annotation_text="Externals")
resumeread_scatter_fig.add_hrect(y0=12.5, y1=22.5, line_width=0, fillcolor="blue", opacity=0.2,annotation_text="Intermediates")
resumeread_scatter_fig.add_hrect(y0=-0.5, y1=12.5, line_width=0, fillcolor="green", opacity=0.2,annotation_text="Internals")

resumeread_scatter_fig.write_html("resumeread_scatter.html")

print(employee_record_relevant_dict)
print(email_header_relevant_dict)




def sequence_plot(action,yaxis_ticks_order):
    all_action_list = []
    all_action_actors_list = []
    all_action_day_list = []
    all_action_time_list = []
    all_action_relevancy_list = []
    all_action_actors_locscore_list = []
    all_action_actors_loc_list = []
    all_action_content_list = []
    all_action_tag_list = []
    condition_for_bin = False
    condition_for_relevancy = False
    for key, value in no_NA_result_dict.items():
        # print("name: ", key)
        count_action = 0
        for k, v in value.items():
            if k == 'raw_any_data_list':
                for action_row in v:
                    if action == 'search':
                        condition_for_bin = action_row[ActionType_enum] == 'Search'
                        # condition_for_relevancy = any(ext.lower() in action_row[ActionParameters_enum].lower()
                        #                               or action_row[ActionParameters_enum].lower()[:3] == ext.lower()[
                        #                                                                                   :3]
                        #                               for ext in keywords_list)
                    elif action == 'readresume':
                        condition_for_bin = action_row[ActionType_enum] == 'GetDetail' \
                                            and ('Resume' in action_row[ActionParameters_enum]
                                                 or 'Bio' in action_row[ActionParameters_enum])
                        # condition_for_relevancy = any(ext.lower() in
                        #                               action_row[ActionParameters_enum].lower() for ext in
                        #                               keywords_list)
                    elif action == 'read_employee_record':
                        condition_for_bin = action_row[ActionType_enum] == 'GetDetail' \
                                            and 'Record' in action_row[ActionParameters_enum]
                        # condition_for_relevancy = False
                    elif action == 'read_email_header':
                        condition_for_bin = action_row[ActionType_enum] == 'GetDetail' \
                                            and 'Header' in action_row[ActionParameters_enum]
                        # condition_for_relevancy = False
                    elif action == 'read_article':
                        condition_for_bin = action_row[ActionType_enum] == 'GetDetail' and 'Article' in action_row[
                            ActionParameters_enum]
                        # print(action_row)
                        # condition_for_relevancy = articles_info[action_row[ActionParameters_enum]]['RelevantToTask'] == 'yes'
                    elif action == 'add_element':
                        condition_for_bin = action_row[ActionType_enum] == 'AddElement'
                        # condition_for_relevancy = any(ext.lower() in
                        #                               action_row[ActionParameters_enum].lower() for ext in
                        #                               keywords_list)
                    elif action == 'add_connection':
                        condition_for_bin = action_row[ActionType_enum] == 'AddConnection'
                        # condition_for_relevancy = any(ext.lower() in
                        #                               action_row[ActionParameters_enum].lower() for ext in
                        #                               keywords_list)
                    elif action == 'edit_notes':
                        condition_for_bin = action_row[ActionType_enum] == 'EditNotes'
                        # condition_for_relevancy = False
                    if condition_for_bin:
                        if action == 'search':
                            condition_for_relevancy = any(ext.lower() in action_row[ActionParameters_enum].lower()
                                                          or action_row[ActionParameters_enum].lower()[
                                                             :3] == ext.lower()[
                                                                    :3]
                                                          for ext in keywords_list)
                        elif action == 'readresume':
                            condition_for_relevancy = any(ext.lower() in
                                                          action_row[ActionParameters_enum].lower() for ext in
                                                          keywords_list)
                        elif action == 'read_employee_record':
                            condition_for_relevancy = employee_record_relevant_dict[action_row[ActionParameters_enum]] == 'yes'
                        elif action == 'read_email_header':
                            condition_for_relevancy = email_header_relevant_dict[action_row[ActionParameters_enum]] == 'yes'
                        elif action == 'read_article':
                            condition_for_relevancy = articles_info[action_row[ActionParameters_enum]][
                                                          'RelevantToTask'] == 'yes'
                        elif action == 'add_element':
                            condition_for_relevancy = any(ext.lower() in
                                                          action_row[ActionParameters_enum].lower() for ext in
                                                          keywords_list)
                        elif action == 'add_connection':
                            condition_for_relevancy = any(ext.lower() in
                                                          action_row[ActionParameters_enum].lower() for ext in
                                                          keywords_list)
                        elif action == 'edit_notes':
                            condition_for_relevancy = False
                        all_action_list.append(key + action + str(count_action))
                        all_action_tag_list.append(action)
                        all_action_actors_list.append(key)
                        all_action_day_list.append(action_row[Day_enum])
                        all_action_time_list.append(datetime.strptime(action_row[Time_enum], '%HH %MM %SS'))
                        all_action_actors_locscore_list.append(no_NA_result_dict[key]['LOC-score'])
                        all_action_actors_loc_list.append(no_NA_result_dict[key]['LOC'])
                        all_action_content_list.append(action_row[ActionParameters_enum])
                        if condition_for_relevancy:
                            all_action_relevancy_list.append('relevant')
                        else:
                            all_action_relevancy_list.append('irrelevant')
                        count_action += 1


    all_action_df = pd.DataFrame(
        {action + '_action_names': all_action_list,
         action + '_actors': all_action_actors_list,
         action + '_days': all_action_day_list,
         action + '_times': all_action_time_list,

         action + '_relevancies': all_action_relevancy_list,
         action + '_actors_locscore': all_action_actors_locscore_list,
         action + '_actors_loc': all_action_actors_loc_list,
         action + '_content': all_action_content_list,
         'tag': all_action_tag_list
         })
    action_scatter_fig = px.scatter(all_action_df, x=action + "_times", y=action + "_actors",
                                    labels={
                                        action + "_actors": action + "_actors",
                                    },
                                    color_discrete_map={
                                        "irrelevant": "purple",
                                        "relevant": "red"
                                    },
                                    facet_col=action + "_days", color=action + "_relevancies",
                                    hover_data=all_action_df.columns)
    action_scatter_fig.update_yaxes(categoryorder='array', categoryarray=yaxis_ticks_order)
    action_scatter_fig.update_layout(margin=dict(l=300))
    action_scatter_fig.update_xaxes(tickformat='%H:%M')

    action_scatter_fig.add_annotation(xref='paper', x=-0.15, yref='paper', y=0.1,
                                      text="<--- More Internal      |      More External --->",
                                      showarrow=False,
                                      textangle=-90,
                                      font_size=18
                                      )
    # action_scatter_fig.add_hrect(y0=22.5, y1=24.5, line_width=0, fillcolor="red", opacity=0.2,
    #                              annotation_text="Externals")
    # action_scatter_fig.add_hrect(y0=12.5, y1=22.5, line_width=0, fillcolor="blue", opacity=0.2,
    #                              annotation_text="Intermediates")
    # action_scatter_fig.add_hrect(y0=-0.5, y1=12.5, line_width=0, fillcolor="green", opacity=0.2,
    #                              annotation_text="Internals")
    action_scatter_fig.write_html(action+"_scatter.html")
    # return all_action_list, all_action_actors_list, all_action_day_list, all_action_time_list,\
    #        all_action_relevancy_list, all_action_actors_locscore_list, all_action_actors_loc_list, all_action_content_list
    return all_action_df



all_read_employee_record_df = sequence_plot("read_employee_record",all_good_names_sorted_by_locscore)
all_read_email_header_df = sequence_plot("read_email_header", all_good_names_sorted_by_locscore)
all_add_element_df = sequence_plot("add_element",all_good_names_sorted_by_locscore)
all_add_connection_df = sequence_plot("add_connection",all_good_names_sorted_by_locscore)
all_read_article_df = sequence_plot("read_article", all_good_names_sorted_by_locscore)
all_edit_notes_df = sequence_plot("edit_notes",all_good_names_sorted_by_locscore)

all_df = pd.DataFrame( np.concatenate( (all_search_df.values,
                                        all_resumeread_df.values,
                                        all_read_employee_record_df.values,
                                        all_read_email_header_df.values,
                                        all_add_element_df.values,
                                        all_add_connection_df.values,
                                        all_read_article_df.values,
                                        all_edit_notes_df.values), axis=0 ) )
all_df.columns = ['_action_names','_actors','_days','_times','_relevancies','_actors_locscore', '_actors_loc','_content','_tag']
print(all_df)

action_scatter_fig = px.scatter(all_df, x="_times", y="_actors",
                                labels={
                                    "_actors": "_actors",
                                },
                                color_discrete_map={
                                    "irrelevant": "purple",
                                    "relevant": "red"
                                },
                                symbol_map={
                                    "irrelevant": "circle",
                                    "relevant": "cross-open"
                                },
                                facet_col="_days", color="_tag",
                                symbol='_relevancies',
                                hover_data=all_df.columns)
action_scatter_fig.update_yaxes(categoryorder='array', categoryarray=all_good_names_sorted_by_locscore)
action_scatter_fig.update_layout(margin=dict(l=300))
action_scatter_fig.update_xaxes(tickformat='%H:%M')

action_scatter_fig.add_annotation(xref='paper', x=-0.15, yref='paper', y=0.1,
                                  text="<--- More Internal      |      More External --->",
                                  showarrow=False,
                                  textangle=-90,
                                  font_size=18
                                  )
# action_scatter_fig.add_hrect(y0=22.5, y1=24.5, line_width=0, fillcolor="red", opacity=0.2,
#                              annotation_text="Externals")
# action_scatter_fig.add_hrect(y0=12.5, y1=22.5, line_width=0, fillcolor="blue", opacity=0.2,
#                              annotation_text="Intermediates")
# action_scatter_fig.add_hrect(y0=-0.5, y1=12.5, line_width=0, fillcolor="green", opacity=0.2,
#                              annotation_text="Internals")
action_scatter_fig.write_html("_scatter.html")

















#plt.show()










