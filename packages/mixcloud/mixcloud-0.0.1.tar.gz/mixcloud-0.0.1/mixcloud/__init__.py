import collections
import dateutil.parser
import re
import requests
import unidecode
import yaml


def setup_yaml():
    def construct_yaml_str(self, node):
        # Override the default string handling function
        # to always return unicode objects
        return self.construct_scalar(node)
    tag = u'tag:yaml.org,2002:str'
    yaml.Loader.add_constructor(tag, construct_yaml_str)
    yaml.SafeLoader.add_constructor(tag, construct_yaml_str)


class Mixcloud(object):

    def __init__(self, api_root='https://api.mixcloud.com', access_token=None):
        self.api_root = api_root
        self.access_token = access_token

    def artist(self, key):
        url = '{root}/artist/{key}'.format(root=self.api_root, key=key)
        r = requests.get(url)
        return Artist.from_json(r.json())

    def user(self, key):
        url = '{root}/{user}'.format(root=self.api_root, user=key)
        r = requests.get(url)
        return User.from_json(r.json(), m=self)

    def me(self):
        url = '{root}/me/'.format(root=self.api_root)
        r = requests.get(url)
        return User.from_json(r.json(), m=self)

    def upload(self, cloudcast, mp3file):
        url = '{root}/upload/'.format(root=self.api_root)
        payload = {'name': cloudcast.name,
                   'percentage_music': 100,
                   'description': cloudcast.description(),
                   }
        for num, sec in enumerate(cloudcast.sections()):
            payload['sections-%d-artist' % num] = sec.track.artist.name
            payload['sections-%d-song' % num] = sec.track.name
            payload['sections-%d-start_time' % num] = sec.start_time

        for num, tag in enumerate(cloudcast.tags):
            payload['tags-%s-tag' % num] = tag

        r = requests.post(url,
                          data=payload,
                          params={'access_token': self.access_token},
                          files={'mp3': mp3file},
                          )
        return r

    def upload_yml_file(self, ymlfile, mp3file):
        user = self.me()
        cloudcast = Cloudcast.from_yml(ymlfile, user)
        r = self.upload(cloudcast, mp3file)


class Artist(collections.namedtuple('_Artist', 'key name')):

    @staticmethod
    def from_json(data):
        return Artist(data['slug'], data['name'])

    @staticmethod
    def from_yml(artist):
        return Artist(slugify(artist), artist)


class User(object):

    def __init__(self, key, name, m=None):
        self.m = m
        self.key = key
        self.name = name

    @staticmethod
    def from_json(data, m=None):
        return User(data['username'], data['name'], m=m)

    def cloudcast(self, key):
        url = '{root}/{user}/{cc}'.format(root=self.m.api_root,
                                          user=self.key,
                                          cc=key)
        r = requests.get(url)
        data = r.json()
        return Cloudcast.from_json(data)

    def cloudcasts(self, limit=None, offset=None):
        url = '{root}/{user}/cloudcasts/'.format(root=self.m.api_root,
                                                 user=self.key)
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        r = requests.get(url, params=params)
        data = r.json()
        return [Cloudcast.from_json(d, m=self.m) for d in data['data']]


class Cloudcast(object):

    def __init__(self, key, name, sections, tags,
                 description, user, created_time, m=None):
        self.key = key
        self.name = name
        self.tags = tags
        self._description = description
        self._sections = sections
        self.user = user
        self.created_time = created_time
        self.m = m

    @staticmethod
    def from_json(d, m=None):
        if 'sections' in d:
            sections = Section.list_from_json(d['sections'])
        else:
            sections = None
        desc = d.get('description')
        tags = [t['name'] for t in d['tags']]
        user = User.from_json(d['user'])
        created_time = dateutil.parser.parse(d['created_time'])
        return Cloudcast(d['slug'],
                         d['name'],
                         sections,
                         tags,
                         desc,
                         user,
                         created_time,
                         m=m,
                         )

    def _load(self):
        url = '{root}/{user}/{cc}'.format(root=self.m.api_root,
                                          user=self.user.key,
                                          cc=self.key)
        r = requests.get(url)
        d = r.json()
        self._sections = Section.list_from_json(d['sections'])
        self._description = d['description']

    def sections(self):
        """
        Depending on the data available when the instance was created,
        it may be necessary to fetch data.
        """
        if self._sections is None:
            self._load()
        return self._sections

    def description(self):
        """
        May hit server. See Cloudcast.sections
        """
        if self._description is None:
            self._load()
        return self._description

    @staticmethod
    def from_yml(f, user):
        setup_yaml()
        d = yaml.load(f)
        name = d['title']
        sections = [Section.from_yml(s) for s in d['tracks']]
        key = slugify(name)
        tags = d['tags']
        description = d['desc']
        created_time = None
        c = Cloudcast(key, name, sections, tags, description,
                      user, created_time)
        return c


class Section(collections.namedtuple('_Section', 'start_time track')):

    @staticmethod
    def from_json(d):
        return Section(d['start_time'], Track.from_json(d['track']))

    @staticmethod
    def list_from_json(d):
        return [Section.from_json(s) for s in d]

    @staticmethod
    def from_yml(d):
        artist = Artist.from_yml(d['artist'])
        track = d['track']
        return Section(d['start'], Track(track, artist))


class Track(collections.namedtuple('_Track', 'name artist')):

    @staticmethod
    def from_json(d):
        return Track(d['name'], Artist.from_json(d['artist']))


def slugify(s):
    s = unidecode.unidecode(s).lower()
    return re.sub(r'\W+', '-', s)
