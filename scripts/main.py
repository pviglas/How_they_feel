import requests
import json
import pandas as pd
# from pandas import DataFrame
import urllib
import argparse
import sys

""" -------------- Level 1 -------------- """


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
    happy_emotions = ['happy', '']  # y
    sad_emotions = []  # y

   # string_transformer = sk.preprocessing.FunctionTransformer(count_strings,
    #                                                          kw_args={
     #                                                       'y': happy_emotions})

    # df['count'] = string_transformer.fit_transform(X=df)


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

        print("will search for topic points of view = ", args.topic)
        json_dict = create_json_dict(args.topic)
        articles_df = group_articles(json_dict, args.topic)

        print(type(articles_df))
        print(articles_df)

    else:
        print("Shows only sources, not feelings:", args.topic)
        json_dict = create_json_dict(args.topic)
        find_sources(json_dict)


if __name__ == '__main__':
    main()
