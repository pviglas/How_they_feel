import requests
import json
import pandas as pd
# from pandas import DataFrame
import urllib
import argparse
import sys


def insert_dummy_entries(articles_df, topic_name):

    # 4 sad emotions, 2 happy -> Viewpoint = Sad
    temp_str = 'sad happy excited sad sad sad'

    # 4 sad emotions, 6 happy -> Viewpoint = Happy
    temp_str2 = 'sad happy excited sad sad sad happy happy happy excited'

    temp_df = pd.DataFrame([{'Title': 'mine1',
                             'Source_name': 'mine1',
                             'Description': 'mine1',
                             'Date': 'mine1',
                             'Content': temp_str,
                             'url': 'oeo',
                             'Topic': topic_name,
                             'Viewpoint': 'Neutral',
                             'Happy_counter': 0,
                             'Sad_counter': 0}  # Default = Neutral
                            ])

    articles_df = articles_df.append(temp_df, ignore_index=True)

    temp_df = pd.DataFrame([{'Title': 'mine2',
                             'Source_name': 'mine1',
                             'Description': 'mine1',
                             'Date': 'mine1',
                             'Content': temp_str2,
                             'url': 'oeo',
                             'Topic': topic_name,
                             'Viewpoint': 'Neutral',
                             'Happy_counter': 0,
                             'Sad_counter': 0}  # Default = Neutral
                            ])

    articles_df = articles_df.append(temp_df, ignore_index=True)

    return articles_df


def create_json_dict(topic_name):
    url = ('https://newsapi.org/v2/everything?'
           'q=' + topic_name + '&'
           # 'q=(brexit AND people AND feel)&'
           'from=2021-11-22&'
           'sortBy=popularity&'
           'apiKey=407badbfe4a44c1089a0dfa35ecf26ee')

    response = requests.get(url)
    json_dict = response.json()
    # print(json_dict)

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

    # print(topic_info_dict)
    print(json.dumps(topic_info_dict, indent=2, sort_keys=False))


def group_articles(json_dict, topic_name):
    articles_list = json_dict['articles']  # Extract articles from json_dict
    articles_df = pd.DataFrame()

    for article in articles_list:
        # print(type(article))
        # print(article)
        source_name = str(article['source']['name'])
        title = str(article['title'])
        description = str(article['description'])
        url = str(article['url'])
        publication_date = str(article['publishedAt'])
        content = str(article['content'])  # truncated to 200 chars, by the api

        temp_df = pd.DataFrame([{'Title': title,
                                 'Source_name': source_name,
                                 'Description': description,
                                 'Date': publication_date,
                                 'Content': content.lower(),
                                 # lowercase for str compare later
                                 'url': url,
                                 'Topic': topic_name,
                                 'Viewpoint': 'Neutral',
                                 'Happy_counter': 0,
                                 'Sad_counter': 0}  # Default = Neutral
                                ])

        articles_df = articles_df.append(temp_df, ignore_index=True)
        # print("\nAfter insert: \n")
        # print(article_df)

    # print("\nFinal article_df: \n")
    # print(article_df)

    return articles_df


def find_viewpoint(articles_df):

    # 2 Categories of emotions
    # Searching for them in article.content and count them
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


def display_viewpoints(articles_df):
    happy = len(articles_df[articles_df['Viewpoint'].str.match('Happy')])
    print("happy articles: ", happy)


def main():
    parser = argparse.ArgumentParser(description='Search for a topic.')
    parser.add_argument('topic', type=str, help='Topic name.')

    parser.add_argument('-f', '--feelings', action='store_true',
                        help='Searching for viewpoints, about the topic.')

    parser.add_argument('-v', '--viewpoint', type=str, choices=['happy', 'sad',
                                                                'neutral'],
                        default=False,
                        help='Shows articles that match the viewpoint.')

    parser.add_argument('-y', '--year', type=int, choices=range(2000, 2021),
                        metavar='Range: 2000-2021', default=False,
                        help='Shows articles for the given year.')

    args = parser.parse_args()

    print("args print:", args.topic)

    if args.feelings:

        if not args.viewpoint:
            print("viewpoint == false")
        if not args.year:
            print("year == false")

        print("will search for viewpoints about:", args.topic)
        dict_json = create_json_dict(args.topic)
        df_articles = group_articles(dict_json, args.topic)

        print(type(df_articles))
        print(df_articles)
        display_viewpoints(df_articles)

    else:
        print("Shows only sources, not feelings:", args.topic)
        dict_json = create_json_dict(args.topic)
        find_sources(dict_json)


if __name__ == '__main__':
    main()

