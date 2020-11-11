import csv, pprint, statistics
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

keywords_list = ['Henk','Brodogi','Carmine','Osvaldo','Yanick','Cato','Loreto','Katell','Ale','Loreto','Hanne',
                 'Jeroen','Karel','Valentine','Mies','Elian','Silvia','Marek','Vann','Ferro','Rocha','Stefano']


result = OrderedDict() # stores the data collection results
articles_info = OrderedDict() # stores article information
participants_info = OrderedDict() # stores participant info


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

with open('data/survey.csv', 'r') as file:
    reader_participants_info = csv.reader(file)
    next(reader_participants_info)
    for row in reader_participants_info:
        current_participant_id = row[8]
        participants_info[current_participant_id] = {}
        participants_info[current_participant_id]['LOC'] = row[len(row)-1]

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

            if any_data_row[ActionType_enum] == 'EditNotes':
                cur['total_editnotes_count'] += 1

            if any_data_row[ActionType_enum] == 'Search':
                cur['total_search_count'] += 1
                if any(ext in any_data_row[ActionParameters_enum] for ext in keywords_list):
                    cur['total_relevant_search_count'] += 1

            if any_data_row[ActionType_enum] == 'AddElement':
                cur['total_addelement_count'] += 1
                if any(ext in any_data_row[ActionParameters_enum] for ext in keywords_list):
                    cur['total_relevant_addelement_count'] += 1

            if any_data_row[ActionType_enum] == 'AddConnection':
                cur['total_addconnection_count'] += 1
                if any(ext in any_data_row[ActionParameters_enum] for ext in keywords_list):
                    cur['total_relevant_addconnection_count'] += 1

            if any_data_row[ActionType_enum] == 'GetDetail' and 'Resume' in any_data_row[ActionParameters_enum]:
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

no_NA_result_dict = {}
NA_flag = 0
for key, value in result.items():
    # print(key)
    for k, v in value.items():
        # if k != 'raw_data_list' and k != 'raw_any_data_list':
        #     print(k,v)
        if v == 'NA':
            NA_flag = 1
    if NA_flag == 0:
        no_NA_result_dict[key] = value
    NA_flag = 0

# print(len(no_NA_result_dict))
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

#plt.show()










