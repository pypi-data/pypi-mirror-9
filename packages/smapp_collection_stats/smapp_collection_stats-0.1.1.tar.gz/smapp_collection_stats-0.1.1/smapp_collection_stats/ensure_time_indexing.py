"""
Script ensures time indexes on the stats collection in mongo.

@jonathanronen 2015/1
"""

import argparse
from smapp_toolkit.twitter import MongoTweetCollection

def ensure_time_indexing(server, port, database, username, password):
    toolkit_collection = MongoTweetCollection(
        address=server,
        port=port,
        dbname=database,
        username=username,
        password=password
        )

    keywordstats_collection = toolkit_collection._mongo_database[toolkit_collection.collection_metadata.get('keywordstats_collection', 'tweets_keywordstats')]

    keywordstats_collection.ensure_index("start_time", name="index_start", background=True)
    keywordstats_collection.ensure_index("end_time", name="index_end", background=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", default="smapp-data.bio.nyu.edu", help="MongoDB host. [smapp-data.bio.nyu.edu]")
    parser.add_argument("-p", "--port", type=int, default=27011, help="MongoDB port. [27011]")
    parser.add_argument("-u", "--username", default="smapp_readWrite", help="username for MongoDB. [smapp_readWrite]")
    parser.add_argument("-w", "--password", default=None, help="password for MongoDB. [None]")
    parser.add_argument("-d", "--database", required=True , help="MongoDB database name")

    args = parser.parse_args()

    ensure_time_indexing(
        args.server,
        args.port,
        args.database,
        args.username,
        args.password)

if __name__ == '__main__':
    main()