import requests
import json
import pandas as pd
import urllib
import argparse
import sys

""" -------------- Level 1 -------------- """


def find_sources(topic_name):

    url = ('https://newsapi.org/v2/everything?'
           'q='+topic_name+'&'
           # 'q=(brexit AND people AND feel)&'
           'from=2021-11-22&'
           'sortBy=popularity&'
           'apiKey=407badbfe4a44c1089a0dfa35ecf26ee')

    response = requests.get(url)
    json_dict = response.json()
    # print(json_dict)

    article_list = json_dict['articles']    # Extract articles from json_dict
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


def main():

    given_topic = None

    parser = argparse.ArgumentParser(description='Search for a topic.')
    parser.add_argument('topic', type=str, help='Given topic name.')
    parser.add_argument('-f', '--feelings', action='store_true',
                        help='Searching for points of view, about the topic.')
    args = parser.parse_args()

    print("args print", args.topic)
    if args.feelings:
        print("will search for topic points of view = ", args.topic)
    else:
        print("Shows only sources, not feelings:",args.topic)
        find_sources(args.topic)


if __name__ == '__main__':
    main()

