"""python-twitter wrapper functions.
"""
try:
    from ConfigParser import ConfigParser
except:
    from configparser import ConfigParser
import twitter
from tinkerer import master
from tinkerer.post import Post
from twinkerer import utils
from twinkerer.twitterapi import parse_tweet, Tweet, ReTweet


DEFAULT_SECTION = 'twitter'

DEFAULT_CONFIGS = {
    'twinkerer_filename': 'tweet_log',
    'twinkerer_title_oneday': 'tweets at {from_date}',
    'twinkerer_title_between': 'tweets from {from_date} to {to_date}',
}


class Twinkerer(object):
    def __init__(self, api, config={}):
        self._api = api
        self._me = None
        self._config = utils.update_dict(DEFAULT_CONFIGS, config)

    @classmethod
    def from_config(cls, config, section=None):
        if section is None:
            section = DEFAULT_SECTION
        else:
            section = str(section)
        if not isinstance(config, ConfigParser):
            raise ValueError()
        elif not config.has_section(section):
            raise ValueError("Argument-config don't have section 'twitter'")
        api_ = twitter.Twitter(
            auth=twitter.OAuth(
                config.get(section, 'access_token_key'),
                config.get(section, 'access_token_secret'),
                config.get(section, 'consumer_key'),
                config.get(section, 'consumer_secret'),
                )
        )
        return cls(api_)

    @classmethod
    def from_module(cls, module):
        api_ = twitter.Twitter(
            auth=twitter.OAuth(
                module.twitter_access_token_key,
                module.twitter_access_token_secret,
                module.twitter_consumer_key,
                module.twitter_consumer_secret,
                )
        )
        config_ = {k: v for k, v in module.__dict__.items() if k.startswith('twinkerer_')}
        return cls(api_, config_)

    @property
    def me(self):
        if not self._me:
            user_settings = self._api.account.settings(_method='GET')
            user = self._api.users.show(screen_name=user_settings['screen_name'])
            user['_settings'] = user_settings
            self._me = user
        return self._me

    def get_my_timeline(self):
        user_id_ = self.me['id']
        tweets_ = self._api.statuses.user_timeline(user_id=user_id_)
        return tweets_

    def fetch_timeline(self, user_id, from_date, to_date):
        tl_list = []
        done_fetch_ = False
        current_id_ = None
        for _ in range(10):
            if current_id_ is None:
                tweets_ = self._api.statuses.user_timeline(user_id=user_id)
            else:
                tweets_ = self._api.statuses.user_timeline(user_id=user_id, max_id=current_id_)
            for tweet in tweets_:
                tw = Tweet(tweet)
                current_id_ = tw.id - 1
                if to_date <= tw.created_at:
                    continue
                if tw.created_at < from_date:
                    done_fetch_ = True
                    break
                tl_list.append(parse_tweet(tweet))
            if done_fetch_:
                break
        return tl_list

    def build_title(self, from_date, to_date, template=None):
        if template is None:
            if from_date == to_date:
                template = self._config['twinkerer_title_oneday']
            else:
                template = self._config['twinkerer_title_between']
        return template.format(from_date=from_date, to_date=to_date)

    def create_post(self, raw_title=None, post_date=None):
        post_ = Post(
            title=self._config['twinkerer_filename'],
            date=post_date,
        )
        if raw_title is not None:
            post_.title = raw_title
        return post_


def post(twinkerer, cmd_args):
    user_id_ = twinkerer.me['id']
    title_ = twinkerer.build_title(cmd_args.from_date, cmd_args.to_date)
    post_ = twinkerer.create_post(title_, cmd_args.post_date)
    post_content = ''
    timeline_ = twinkerer.fetch_timeline(
        user_id_,
        cmd_args.from_datetime,
        cmd_args.to_datetime,
    )
    post_content = ''.join([tl.as_html() for tl in timeline_])
    result_ = post_.write(post_content, author="default",
              categories="none", tags="none",
              template=None)
    if not master.exists_doc(post_.docname):
        master.prepend_doc(post_.docname)
    return post_
