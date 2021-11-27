# Code owner: Viglas Panagiotis

import requests
import json
import pandas as pd
import argparse
import matplotlib.pyplot as plt
import numpy as np


def insert_dummy_entries(articles_df, topic_name):
    """
     Function for testing purposes.
     The article.Content is truncated to 200 chars by the api, so we cannot
     search the whole article and scan every word one by one.
     Because of that (usually) the article.Happy_counter(s) and
     article.Sad_counter(s) remain 0 and this has as a result all the
     article.Viewpoint(s) remain to default(=Neutral), too.

     Testing solution:
     We can insert some dummy entries, which contain synonyms of sad/happy on
     the article.Content, in order to test the code and check the results.
    """

    # 4 sad emotions, 2 happy -> Viewpoint = Sad
    temp_str = 'sad happy excited sad sad sad'

    # 4 sad emotions, 6 happy -> Viewpoint = Happy
    temp_str2 = 'sad happy excited sad sad sad happy happy happy excited'

    temp_df = pd.DataFrame([{'Title': 'dummy_1',
                             'Source_name': 'dummy_1',
                             'Description': 'dummy_1',
                             'Date': '2020',
                             'Content': temp_str,
                             'url': 'dummy_url',
                             'Topic': topic_name,
                             'Viewpoint': 'Neutral',  # Default = Neutral
                             'Happy_counter': 0,
                             'Sad_counter': 0}
                            ])

    articles_df = articles_df.append(temp_df, ignore_index=True)

    temp_df = pd.DataFrame([{'Title': 'dummy_2',
                             'Source_name': 'dummy_2',
                             'Description': 'dummy_2',
                             'Date': '2021',
                             'Content': temp_str2,
                             'url': 'dummy_url',
                             'Topic': topic_name,
                             'Viewpoint': 'Neutral',  # Default = Neutral
                             'Happy_counter': 0,
                             'Sad_counter': 0}
                            ])

    articles_df = articles_df.append(temp_df, ignore_index=True)

    return articles_df


def create_json_dict(topic_name):
    url = ('https://newsapi.org/v2/everything?'
           'q=' + topic_name + '&'
                               'from=2021-11-22&'
                               'sortBy=popularity&'
                               'apiKey=407badbfe4a44c1089a0dfa35ecf26ee')

    response = requests.get(url)
    json_dict = response.json()

    return json_dict


def find_sources(json_dict):
    article_list = json_dict['articles']  # Extract articles from json_dict
    sources_list = []

    for article in article_list:
        temp_source_name = article['source']['name']
        flag = True

        for source in sources_list:
            if temp_source_name == source['name']:
                flag = False
                source['count'] += 1
                break

        # Add current source into sources_list, if it is not already
        if flag is True:
            temp_dict = {
                'name': temp_source_name,
                'count': 1
            }

            sources_list.append(temp_dict)

    topic_info_dict = {
        'totalSources': len(sources_list),
        'totalArticles': len(article_list),
        'sources': sources_list
    }

    print(json.dumps(topic_info_dict, indent=2, sort_keys=False))


def group_articles(json_dict, topic_name):
    articles_list = json_dict['articles']  # Extract articles from json_dict
    articles_df = pd.DataFrame()

    for article in articles_list:
        source_name = str(article['source']['name'])
        title = str(article['title'])
        description = str(article['description'])
        url = str(article['url'])

        publication_date = str(article['publishedAt'])
        filter_year_only = publication_date.split("-", 1)
        publication_year_only = filter_year_only[0]

        content = str(article['content'])  # truncated to 200 chars, by the api

        temp_df = pd.DataFrame([{'Title': title,
                                 'Source_name': source_name,
                                 'Description': description,
                                 'Date': publication_year_only,
                                 'Content': content.lower(),
                                 # lowercase for string match later
                                 'url': url,
                                 'Topic': topic_name,
                                 'Viewpoint': 'Neutral',  # Default = Neutral
                                 'Happy_counter': 0,
                                 'Sad_counter': 0}
                                ])

        articles_df = articles_df.append(temp_df, ignore_index=True)

    # Uncomment the next line of code, to run the testing_function and check
    # the results
    articles_df = insert_dummy_entries(articles_df, topic_name)

    return articles_df


def find_viewpoint(articles_df):
    # 2 Categories of emotions
    # Searching for them in article.Content and count them
    happy_emotions = ['happy', 'excited', 'good', 'amazing', 'better',
                      'beneficial', 'joy']
    sad_emotions = ['sad', 'bad', 'unhappy', 'depressed', 'miserable',
                    'dejected', 'downhearted']

    happy_pattern = r'\b{}\b'.format('|'.join(happy_emotions))
    sad_pattern = r'\b{}\b'.format('|'.join(sad_emotions))

    articles_df['Happy_counter'] = articles_df.Content.str.count(happy_pattern)
    articles_df['Sad_counter'] = articles_df.Content.str.count(sad_pattern)

    # If Happy_emotions.count() > Sad_emotions.count() => Viewpoint = Happy
    # If Happy_emotions.count() < Sad_emotions.count() => Viewpoint = Sad
    # If Happy_emotions.count() = Sad_emotions.count() => Viewpoint = Neutral

    articles_df.loc[articles_df['Happy_counter'] > articles_df[
        'Sad_counter'], 'Viewpoint'] = 'Happy'

    articles_df.loc[articles_df['Happy_counter'] < articles_df[
        'Sad_counter'], 'Viewpoint'] = 'Sad'

    return articles_df


# Filter DataFrame, by given year
def return_selected_year(articles_df, given_year):
    given_year = str(given_year)
    year_df = articles_df[articles_df['Date'].str.match(given_year)]

    return year_df


def display_predominant_viewpoint(happy, sad, neutral):
    if (happy >= sad) and (happy >= neutral):
        print("- Most people are Happy, %.2f" % happy + "%")
    elif (sad >= happy) and (sad >= neutral):
        print("- Most people are Sad, %.2f" % sad + "%")
    else:
        print("- General Viewpoint is Neutral, %.2f"
              % neutral + "%")


def find_emotion_counters(articles_df):
    number_of_articles = articles_df.shape[0]
    happy_counter = len(
        articles_df[articles_df['Viewpoint'].str.match('Happy')])
    sad_counter = len(articles_df[articles_df['Viewpoint'].str.match('Sad')])
    neutral_counter = number_of_articles - (happy_counter + sad_counter)

    return [number_of_articles, happy_counter, sad_counter, neutral_counter]


def display_viewpoints(articles_df, topic_name, selected_emotion,
                       selected_year):
    emotion_counters = find_emotion_counters(articles_df)
    articles_count = emotion_counters[0]
    happy_count = emotion_counters[1]
    sad_count = emotion_counters[2]
    neutral_count = emotion_counters[3]

    happy_percentage = (happy_count / articles_count) * 100
    sad_percentage = (sad_count / articles_count) * 100
    neutral_percentage = (neutral_count / articles_count) * 100

    if selected_emotion is False and selected_year is False:
        print("Number of articles:", articles_count)
        print("Viewpoints about " + topic_name + ":")
        print("%.2f" % happy_percentage + "% Happy")
        print("%.2f" % sad_percentage + "% Sad")
        print("%.2f" % neutral_percentage + "% Neutral ")

        # Graphical representation
        y = np.array([happy_percentage, sad_percentage, neutral_percentage])

        pie_labels_percentage = [
            str("%.2f" % happy_percentage) + "% " + "Happy",
            str("%.2f" % sad_percentage) + "% " + "Sad",
            str("%.2f" % neutral_percentage) + "% " +
            "Neutral"]
        pie_explode = [0.1, 0.1, 0.1]

        plt.title("Viewpoints about " + topic_name + ":")
        plt.pie(y, labels=pie_labels_percentage, explode=pie_explode)
        plt.show()

    elif selected_emotion is True and selected_year is False:
        print("Shows the predominant viewpoint, about:", topic_name)
        display_predominant_viewpoint(happy_percentage, sad_percentage,
                                      neutral_percentage)
    elif selected_year:
        print("Shows the predominant viewpoint, filtered by year:",
              selected_year)

        articles_by_year_df = return_selected_year(articles_df, selected_year)

        emotion_by_year = find_emotion_counters(articles_by_year_df)
        articles_by_year = emotion_by_year[0]
        happy_by_year = emotion_by_year[1]
        sad_by_year = emotion_by_year[2]
        neutral_by_year = emotion_by_year[3]

        happy_percentage = (happy_by_year / articles_by_year) * 100
        sad_percentage = (sad_by_year / articles_by_year) * 100
        neutral_percentage = (neutral_by_year / articles_by_year) * 100

        display_predominant_viewpoint(happy_percentage, sad_percentage,
                                      neutral_percentage)


def main():
    parser = argparse.ArgumentParser(description='Search for a topic.')
    parser.add_argument('topic', type=str, help='Topic name.')

    parser.add_argument('-f', '--feelings', default=False, action='store_true',
                        help='Searching for viewpoints, about the topic.')

    parser.add_argument('-v', '--viewpoint', default=False,
                        action='store_true',
                        help='Shows the predominant viewpoint.')

    parser.add_argument('-y', '--year', type=int, choices=range(2020, 2022),
                        metavar='Range: 2020-2021', default=False,
                        help='Shows the predominant viewpoint, filtered by '
                             'year.')

    args = parser.parse_args()

    if args.feelings:

        print("Search for viewpoints about:", args.topic)
        dict_json = create_json_dict(args.topic)
        df_articles = group_articles(dict_json, args.topic)

        find_viewpoint(df_articles)
        display_viewpoints(df_articles, args.topic, args.viewpoint, args.year)

    else:
        dict_json = create_json_dict(args.topic)
        find_sources(dict_json)


#
if __name__ == '__main__':
    main()
