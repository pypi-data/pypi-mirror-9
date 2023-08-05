import os
import sys
import argparse
import datetime
import pytz
from twinkerer import Twinkerer, post
from twinkerer import twitterapi


class DateStringAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        formats_ = [
            '%Y-%m-%d',
            '%Y/%m/%d',
        ]
        for format_ in formats_:
            try:
                dt_ = datetime.datetime.strptime(values, format_).date()
                setattr(namespace, self.dest, dt_)
                return
            except:
                continue
        parser.error('"%s" must be string to parse as datetime.' % self.dest)


class UnsignedIntegerAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        value = int(values)
        if value > 0:
            setattr(namespace, self.dest, value)
            return
        else:
            parser.error('"%s" must be plus integer.' % self.dest)


def build_args(args, conf):
    if hasattr(conf, 'twinkerer_timezone'):
        tz_ = pytz.timezone(conf.twinkerer_timezone)
    else:
        tz_ = pytz.utc
    args.from_date = args.post_date - datetime.timedelta(days=args.days)
    args.from_datetime = datetime.datetime(
        args.from_date.year,
        args.from_date.month,
        args.from_date.day,
        tzinfo=tz_,
    )
    args.to_date = args.post_date - datetime.timedelta(days=1)
    args.to_datetime = datetime.datetime(
        args.post_date.year,
        args.post_date.month,
        args.post_date.day,
        tzinfo=tz_,
    )
    if args.command is None:
        args.command = 'fetch'


def fetch(twinkerer, args):
    user_id = twinkerer.me['id']
    for tweet in twinkerer.fetch_timeline(user_id, args.from_datetime, args.to_datetime):
        print('========')
        if isinstance(tweet, twitterapi.ReTweet):
            print(u'ReTweet>\n' + tweet.text)
        else:
            print(u'Tweet>\n' + tweet.text)
        print(u'from '+tweet.user.name)
        print(u'at '+tweet.created_at.isoformat())


ArgParser = argparse.ArgumentParser()
group_ = ArgParser.add_mutually_exclusive_group()
group_.add_argument(
    '-f', '--fetch', dest='command',
    action='store_const', const='fetch',
)
group_.add_argument(
    '-p', '--post', dest='command',
    action='store_const', const='post',
)
ArgParser.add_argument(
    '--date', dest='post_date',
    action=DateStringAction,
    default=datetime.date.today(),
)
ArgParser.add_argument(
    '--to', dest='to_date',
    action=DateStringAction,
    default=(datetime.date.today() - datetime.timedelta(days=1)),
)
ArgParser.add_argument(
    '--days', dest='days',
    action=UnsignedIntegerAction,
    default=7,
)
ArgParser.add_argument(
    '--conf', dest='config_path', nargs='?',
)


def main(argv=None):
    """console script
    """
    if not argv:
        argv = sys.argv[1:]

    args = ArgParser.parse_args(argv)
    cwd_ = os.getcwd()
    if args.config_path is None:
        sys.path.append(cwd_)
        import conf
        tw = Twinkerer.from_module(conf)

    build_args(args, conf)
    if args.command == 'fetch':
        return fetch(tw, args)
    elif args.command == 'post':
        new_post = post(tw, args)
        print("New post created as '%s'" % new_post.path)
