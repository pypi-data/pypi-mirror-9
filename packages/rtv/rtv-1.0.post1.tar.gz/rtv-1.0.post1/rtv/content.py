import textwrap
from datetime import datetime
from contextlib import contextmanager

import praw
import six
import requests

from .errors import SubmissionURLError, SubredditNameError

def split_text(big_text, width):
    return [
        text for line in big_text.splitlines()
        # wrap returns an empty list when "line" is a newline. In order to
        # consider newlines we need a list containing an empty string.
        for text in (textwrap.wrap(line, width=width) or [''])]

def strip_subreddit_url(permalink):
    """
    Grab the subreddit from the permalink because submission.subreddit.url
    makes a seperate call to the API.
    """

    subreddit = permalink.split('/')[4]
    return '/r/{}'.format(subreddit)

def humanize_timestamp(utc_timestamp, verbose=False):
    """
    Convert a utc timestamp into a human readable relative-time.
    """

    timedelta = datetime.utcnow() - datetime.utcfromtimestamp(utc_timestamp)

    seconds = int(timedelta.total_seconds())
    if seconds < 60:
        return 'moments ago' if verbose else '0min'
    minutes = seconds // 60
    if minutes < 60:
        return ('%d minutes ago' % minutes) if verbose else ('%dmin' % minutes)
    hours = minutes // 60
    if hours < 24:
        return ('%d hours ago' % hours) if verbose else ('%dhr' % hours)
    days = hours // 24
    if days < 30:
        return ('%d days ago' % days) if verbose else ('%dday' % days)
    months = days // 30.4
    if months < 12:
        return ('%d months ago' % months) if verbose else ('%dmonth' % months)
    years = months // 12
    return ('%d years ago' % years) if verbose else ('%dyr' % years)

@contextmanager
def default_loader(self):
    yield

class BaseContent(object):

    def get(self, index, n_cols):
        raise NotImplementedError

    def iterate(self, index, step, n_cols):

        while True:
            if step < 0 and index < 0:
                # Hack to prevent displaying negative indicies if iterating in
                # the negative direction.
                break
            try:
                yield self.get(index, n_cols=n_cols)
            except IndexError:
                break
            index += step

    @staticmethod
    def flatten_comments(comments, root_level=0):
        """
        Flatten a PRAW comment tree while preserving the nested level of each
        comment via the `nested_level` attribute.
        """

        stack = comments[:]
        for item in stack:
            item.nested_level = root_level

        retval = []
        while stack:
            item = stack.pop(0)
            nested = getattr(item, 'replies', None)
            if nested:
                for n in nested:
                    n.nested_level = item.nested_level + 1
                stack[0:0] = nested
            retval.append(item)
        return retval

    @staticmethod
    def strip_praw_comment(comment):
        """
        Parse through a submission comment and return a dict with data ready to
        be displayed through the terminal.
        """

        data = {}
        data['object'] = comment
        data['level'] = comment.nested_level

        if getattr(comment.submission, 'author'):
            sub_author = comment.submission.author.name
        else:
            sub_author = '[deleted]'

        if isinstance(comment, praw.objects.MoreComments):
            data['type'] = 'MoreComments'
            data['count'] = comment.count
            data['body'] = 'More comments'.format(comment.count)
        else:
            data['type'] = 'Comment'
            data['body'] = comment.body
            data['created'] = humanize_timestamp(comment.created_utc)
            data['score'] = '{} pts'.format(comment.score)
            data['author'] = (comment.author.name if getattr(comment, 'author') else '[deleted]')
            data['is_author'] = (data['author'] == sub_author)
            data['flair'] = (comment.author_flair_text if comment.author_flair_text else '')
            data['likes'] = comment.likes

        return data

    @staticmethod
    def strip_praw_submission(sub):
        """
        Parse through a submission and return a dict with data ready to be
        displayed through the terminal.
        """

        is_selfpost = lambda s: s.startswith('http://www.reddit.com/r/')

        data = {}
        data['object'] = sub
        data['type'] = 'Submission'
        data['title'] = sub.title
        data['text'] = sub.selftext
        data['created'] = humanize_timestamp(sub.created_utc)
        data['comments'] = '{} comments'.format(sub.num_comments)
        data['score'] = '{} pts'.format(sub.score)
        data['author'] = (sub.author.name if getattr(sub, 'author') else '[deleted]')
        data['permalink'] = sub.permalink
        data['subreddit'] = strip_subreddit_url(sub.permalink)
        data['flair'] = (sub.link_flair_text if sub.link_flair_text else '')
        data['url_full'] = sub.url
        data['url'] = ('selfpost' if is_selfpost(sub.url) else sub.url)
        data['likes'] = sub.likes

        return data


class SubmissionContent(BaseContent):
    """
    Grab a submission from PRAW and lazily store comments to an internal
    list for repeat access.
    """

    def __init__(
            self,
            submission,
            loader=default_loader,
            indent_size=2,
            max_indent_level=4):

        self.indent_size = indent_size
        self.max_indent_level = max_indent_level
        self._loader = loader
        self._submission = submission
        self._submission_data = None
        self._comment_data = None
        self.name = None

        self.reset()

    @classmethod
    def from_url(
            cls,
            reddit,
            url,
            loader=default_loader,
            indent_size=2,
            max_indent_level=4):

        try:
            with loader():
                submission = reddit.get_submission(url)

        except praw.errors.APIException:
            raise SubmissionURLError(url)

        return cls(submission, loader, indent_size, max_indent_level)

    def reset(self):

        with self._loader():
            self._submission.refresh()
            self._submission_data = self.strip_praw_submission(self._submission)
            self.name = self._submission_data['permalink']
            comments = self.flatten_comments(self._submission.comments)
            self._comment_data = [self.strip_praw_comment(c) for c in comments]

    def get(self, index, n_cols=70):
        """
        Grab the `i`th submission, with the title field formatted to fit inside
        of a window of width `n`
        """

        if index < -1:
            raise IndexError

        elif index == -1:
            data = self._submission_data
            data['split_title'] = textwrap.wrap(data['title'], width=n_cols-2)
            data['split_text'] = split_text(data['text'], width=n_cols-2)
            data['n_rows'] = (len(data['split_title']) + len(data['split_text']) + 5)
            data['offset'] = 0

        else:
            data = self._comment_data[index]
            indent_level = min(data['level'], self.max_indent_level)
            data['offset'] = indent_level * self.indent_size

            if data['type'] == 'Comment':
                data['split_body'] = split_text(data['body'], width=n_cols-data['offset'])
                data['n_rows'] = len(data['split_body']) + 1
            else:
                data['n_rows'] = 1

        return data

    def toggle(self, index, n_cols=70):
        """
        Toggle the state of the object at the given index.

        If it is a comment, pack it into a hidden comment.
        If it is a hidden comment, unpack it.
        If it is more comments, load the comments.
        """
        data = self.get(index)

        if data['type'] == 'Submission':
            # Can't hide the submission!
            pass

        elif data['type'] == 'Comment':
            cache = [data]
            count = 1
            for d in self.iterate(index+1, 1, n_cols):
                if d['level'] <= data['level']:
                    break

                count += d.get('count', 1)
                cache.append(d)

            comment = {}
            comment['type'] = 'HiddenComment'
            comment['cache'] = cache
            comment['count'] = count
            comment['level'] = data['level']
            comment['body'] = 'Hidden'.format(count)
            self._comment_data[index:index+len(cache)] = [comment]

        elif data['type'] == 'HiddenComment':
            self._comment_data[index:index+1] = data['cache']

        elif data['type'] == 'MoreComments':
            with self._loader():
                comments = data['object'].comments()
                comments = self.flatten_comments(comments, root_level=data['level'])
                comment_data = [self.strip_praw_comment(c) for c in comments]
                self._comment_data[index:index+1] = comment_data

        else:
            raise ValueError('% type not recognized' % data['type'])


class SubredditContent(BaseContent):
    """
    Grabs a subreddit from PRAW and lazily stores submissions to an internal
    list for repeat access.
    """

    def __init__(self, name, submissions, loader):

        self.name = name
        self._loader = loader
        self._submissions = submissions
        self._submission_data = []

    @classmethod
    def from_name(cls, reddit, name, loader, order='hot'):

        name = name.strip(' /')  # Strip leading and trailing backslashes
        if name.startswith('r/'):
            name = name[2:]

        # Grab the display type e.g. "python/new"
        if '/' in name:
            name, order = name.split('/')

        if order == 'hot':
            display_name = '/r/{}'.format(name)
        else:
            display_name = '/r/{}/{}'.format(name, order)

        if name == 'front':
            if order == 'hot':
                submissions = reddit.get_front_page(limit=None)
            elif order == 'top':
                submissions = reddit.get_top(limit=None)
            elif order == 'rising':
                submissions = reddit.get_rising(limit=None)
            elif order == 'new':
                submissions = reddit.get_new(limit=None)
            elif order == 'controversial':
                submissions = reddit.get_controversial(limit=None)
            else:
                raise SubredditNameError(display_name)

        else:
            subreddit = reddit.get_subreddit(name)
            if order == 'hot':
                submissions = subreddit.get_hot(limit=None)
            elif order == 'top':
                submissions = subreddit.get_top(limit=None)
            elif order == 'rising':
                submissions = subreddit.get_rising(limit=None)
            elif order == 'new':
                submissions = subreddit.get_new(limit=None)
            elif order == 'controversial':
                submissions = subreddit.get_controversial(limit=None)
            else:
                raise SubredditNameError(display_name)

        # Verify that content exists for the given submission generator.
        # This is necessary because PRAW loads submissions lazily, and
        # there is is no other way to check things like multireddits that
        # don't have a real corresponding subreddit object.
        content = cls(display_name, submissions, loader)
        try:
            content.get(0)
        except (praw.errors.APIException, requests.HTTPError):
            raise SubredditNameError(display_name)

        return content

    def get(self, index, n_cols=70):
        """
        Grab the `i`th submission, with the title field formatted to fit inside
        of a window of width `n`
        """

        if index < 0:
            raise IndexError

        while index >= len(self._submission_data):

            try:
                with self._loader():
                    submission = next(self._submissions)
            except StopIteration:
                raise IndexError
            else:
                data = self.strip_praw_submission(submission)
                self._submission_data.append(data)

        # Modifies the original dict, faster than copying
        data = self._submission_data[index]
        data['split_title'] = textwrap.wrap(data['title'], width=n_cols)
        data['n_rows'] = len(data['split_title']) + 3
        data['offset'] = 0

        return data
