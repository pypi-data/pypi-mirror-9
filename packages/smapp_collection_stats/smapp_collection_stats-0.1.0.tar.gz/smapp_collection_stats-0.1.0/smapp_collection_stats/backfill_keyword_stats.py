"""
Script to go back in time and generate keyword stats for a certain period of time in a collection

@jonathanronen 2015/1
"""
import sys
import argparse
import gen_keyword_stats
from dateutil import parser
from datetime import timedelta

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-s", "--server", default="smapp-data.bio.nyu.edu", help="MongoDB host. [smapp-data.bio.nyu.edu]")
    arg_parser.add_argument("-p", "--port", type=int, default=27011, help="MongoDB port. [27011]")
    arg_parser.add_argument("-u", "--username", default="smapp_readWrite", help="username for MongoDB. [smapp_readWrite]")
    arg_parser.add_argument("-w", "--password", default=None, help="password for MongoDB. [None]")
    arg_parser.add_argument("-d", "--databases", nargs='+', required=True , help="MongoDB database names. Takes multiple arguments for more than one DB.")

    arg_parser.add_argument("-st", "--starting-time", required=True, help="Time to start from. Required.")
    arg_parser.add_argument("-ts", "--time-step", default=60, type=int, help="Time step size for calculations, in minutes. [60]")
    arg_parser.add_argument("-ns", "--num-steps", default=1, type=int, help="Number of time steps to calculate stats for. [1]")

    arg_parser.add_argument("-c", "--cap", type=float, default=10000.0, help="Cap of how many tweets to consider. If there are more, sample to reduce. [10,000]")

    args = arg_parser.parse_args()


    starting_time = parser.parse(args.starting_time)
    delta = timedelta(minutes=args.time_step)

    print("""Backfilling stats for ({dbs}).
Starting: {start}
Time step: {ts}
Num steps: {ns}
Cap: {cap}
        """.format(dbs=', '.join(args.databases),
            start=starting_time,
            ts=args.time_step,
            ns=args.num_steps,
            cap=args.cap))

    for dbname in args.databases:
        sys.stdout.write(dbname)
        for k in range(args.num_steps):
            sys.stdout.write('.')
            sys.stdout.flush()
            since = starting_time + k * delta
            until = starting_time + (k+1) * delta
            gen_keyword_stats.calculate_and_save(
                args.server,
                args.port,
                dbname,
                args.username,
                args.password,
                since,
                until,
                args.cap)
        sys.stdout.write("\n")


if __name__ == '__main__':
    main()