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
                             'Date': '2021',
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
           # 'q=(brexit AND people AND feel)&'
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
        content = str(article['content'])  # truncated to 200 chars, by the api

        temp_df = pd.DataFrame([{'Title': title,
                                 'Source_name': source_name,
                                 'Description': description,
                                 'Date': publication_date,
                                 'Content': content.lower(),  # lowercase for string match later
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


def display_viewpoints(articles_df, topic_name):

    number_of_articles = articles_df.shape[0]
    happy_counter = len(articles_df[articles_df['Viewpoint'].str.match('Happy')])
    sad_counter = len(articles_df[articles_df['Viewpoint'].str.match('Sad')])
    neutral_counter = number_of_articles - (happy_counter+sad_counter)

    happy_percentage = (happy_counter/number_of_articles)*100
    sad_percentage = (sad_counter/number_of_articles)*100
    neutral_percentage = (neutral_counter / number_of_articles) * 100

    print("Number of articles:", number_of_articles)
    print("Viewpoints about " + topic_name + ":")
    print("%.2f" % happy_percentage + "% Happy")
    print("%.2f" % sad_percentage + "% Sad")
    print("%.2f" % neutral_percentage + "% Neutral ")

    # Graphic representation
    y = np.array([happy_percentage, sad_percentage, neutral_percentage])
    pie_labels = ["Happy", "Sad", "Neutral"]
    pie_explode = [0.2, 0, 0]

    plt.pie(y, labels=pie_labels, explode=pie_explode)
    plt.show()


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

        find_viewpoint(df_articles)
        print(df_articles)
        display_viewpoints(df_articles, args.topic)

    else:
        print("Shows only sources, not feelings:", args.topic)
        dict_json = create_json_dict(args.topic)
        find_sources(dict_json)


if __name__ == '__main__':
    main()

