import json
from sys import stdout
from .errors import *
from .utils import *

def parse_vine_json(fn):
    """Vine json pre-parser"""
    def _decorator(self, *args, **kwargs):
        self = fn(self, *args, **kwargs)

        # Vine adds classname+'Id' as an id to the object
        classname = self.__class__.__name__.lower()
        vineId = classname + 'Id'

        for key in list(self.keys()):
            value = self[key]

            if key == vineId:
                self['id'] = value
            elif key == 'userId':
                self['user'] = User.from_id(value)
            elif key == 'postId':
                self['post'] = Post.from_id(value)
            elif key == 'created':
                self[key] = strptime(value)
            elif key == 'comments':
                self[key] = CommentCollection.from_json(value)
            elif key == 'likes':
                self[key] = LikeCollection.from_json(value)
            elif key == 'reposts':
                self[key] = RepostCollection.from_json(value)
            elif key == 'tags':
                self[key] = PureTagCollection.from_json(value)
            elif key == 'entities':
                self[key] = PureEntityCollection.from_json(value)
            elif key == 'user':
                self[key] = User.from_json(value)

        name_attr = {
            'user': 'username',
            'post': 'description',
            'comment': 'comment',
            'tag': 'tag',
            'channel': 'channel',
            'notification': 'notificationTypeId',

            'like': 'postId',
            'repost': 'postId',
            'conversation': 'conversationId',
            'message': 'message'
        }.get(classname)
        self['name'] = self.get(name_attr, '<Unknown>')

        return self
    return _decorator


def ensure_ownership(fn):
    """Ensure ownership of the object, to avoid wasting a request"""

    def _decorator(self, *args, **kwargs):
        user_id = self.get('post', {}).get('user', {}).get(
            'id') or self.get('user', {}).get('id') or self.id
        if(user_id == self.api._user_id):
            return fn(self, *args, **kwargs)
        else:
            raise VineError(
                4, "You don't have permission to access that record.")
    return _decorator


def chained(fn):
    """Chain instance methods
    Can do things like user.unfollow().follow().unfollow()
    """

    def _decorator(self, *args, **kwargs):
        fn(self, *args, **kwargs)
        return self
    return _decorator


def inject_post(fn):
    """Inject Post into child model"""

    def _decorator(self, *args, **kwargs):
        obj = fn(self, *args, **kwargs)
        obj.post = self
        return obj
    return _decorator


class Model(AttrDict):
    api = None

    @classmethod
    @parse_vine_json
    def from_json(cls, data):
        self = cls()
        self._attrs = AttrDict(data)
        self.json = json.dumps(data)
        for key, value in list(self._attrs.items()):
            if key not in dir(self):
                self[key] = value
        return self

    @classmethod
    def from_id(cls, _id, **kwargs):
        self = cls()
        self['id'] = _id
        return self

    def connect_api(self, api):
        self.api = api

    def __repr__(self):
        classname = self.__class__.__name__
        name = self.get('name', '')
        if type(name) is int:
            name = str(name)
        else:
            # description, usernames and comments may contain weird chars
            # name = name.encode(stdout.encoding)
            max_chars = 10
            name = name[:max_chars] + (name[max_chars:] and '...')

        return "<%s [%s] '%s'>" % (classname, self.id, name)



class ModelCollection(list):
    model = Model

    @classmethod
    def from_json(cls, data):
        self = cls()
        for item in data:
            self.append(self.model.from_json(item))
        return self

    def connect_api(self, api):
        for item in self:
            item.connect_api(api)

    def __iter__(self):
        self._iterator = list.__iter__(self)
        return self._iterator

    def __next__(self):
        return next(self._iterator)


# Model collection with metadata
class MetaModelCollection(Model):
    model_key = 'records'
    collection_class = ModelCollection

    @classmethod
    def from_json(cls, data):
        self = cls(Model.from_json(data))
        for key, value in list(self.items()):
            if key == self.model_key:
                value = self.collection_class.from_json(value)
            self[key] = value
        return self

    def connect_api(self, api):
        for item in self.get_collection():
            item.connect_api(api)

    def __len__(self):
        return len(self.get_collection())

    def __getitem__(self, descriptor):
        # Retrieving metadata
        if type(descriptor) in [str, str]:
            return Model.__getitem__(self, descriptor)

        # Retrieving an element from the list
        else:
            return self.get_collection().__getitem__(descriptor)

    def __iter__(self):
        return self.get_collection().__iter__()

    def __repr__(self):
        return self.get_collection().__repr__()

    def __next__(self):
        return next(self.get_collection())

    def get_collection(self):
        return self.get(self.model_key, [])


class User(Model):

    def connect_api(self, api):
        self.api = api
        if('key' in list(self.keys())):
            self.api.authenticate(self)

    @chained
    def follow(self, user=None, **kwargs):
        user = user or self
        return self.api.follow(user_id=user.id, **kwargs)

    @chained
    def unfollow(self, user=None, **kwargs):
        user = user or self
        return self.api.unfollow(user_id=user.id, **kwargs)

    @chained
    def block(self, user=None, **kwargs):
        user = user or self
        return self.api.block(user_id=user.id, **kwargs)

    @chained
    def unblock(self, user=None, **kwargs):
        user = user or self

        return self.api.unblock(user_id=user.id, **kwargs)

    def followers(self, **kwargs):
        return self.api.get_followers(user_id=self.id, **kwargs)

    def following(self, **kwargs):
        return self.api.get_following(user_id=self.id, **kwargs)

    def timeline(self, **kwargs):
        return self.api.get_user_timeline(user_id=self.id, **kwargs)

    def likes(self, **kwargs):
        return self.api.get_user_likes(user_id=self.id, **kwargs)

    @ensure_ownership
    def pending_notifications_count(self, **kwargs):
        return self.api.get_pending_notifications_count(user_id=self.id, **kwargs)

    @ensure_ownership
    def notifications(self, **kwargs):
        return self.api.get_notifications(user_id=self.id, **kwargs)

    @chained
    @ensure_ownership
    def update(self, **kwargs):
        return self.api.update_profile(user_id=self.id, **kwargs)

    @chained
    @ensure_ownership
    def set_explicit(self, **kwargs):
        return self.api.set_explicit(user_id=self.id, **kwargs)

    @ensure_ownership
    def unset_explicit(self, **kwargs):
        return self.api.unset_explicit(user_id=self.id, **kwargs)

    def is_following(self):
        return bool(self._attrs.following)

    def is_private(self):
        return bool(self._attrs.private)

    def is_blocking(self):
        return bool(self._attrs.blocking)

    def is_blocked(self):
        return bool(self._attrs.blocked)


class Post(Model):

    @inject_post
    def like(self, **kwargs):
        return self.api.like(post_id=self.id, **kwargs)

    def unlike(self, **kwargs):
        return self.api.unlike(post_id=self.id, **kwargs)

    @inject_post
    def revine(self, **kwargs):
        return self.api.revine(post_id=self.id, **kwargs)

    @inject_post
    def comment(self, comment, entities=[], **kwargs):
        _comment = ''
        if type(comment) is list:
            entities = []
            for element in comment:
                if type(element) is str:
                    _comment += element
                else:
                    entity = {
                        'id': element.id,
                        'range': [len(_comment), len(_comment) + len(element.name)],
                        'type': 'mention',
                        'title': element.name
                    }
                    _comment += element.name + ' '
                    entities.append(entity)
        else:
            _comment = comment

        return self.api.comment(post_id=self.id, comment=_comment, entities=entities, **kwargs)

    @chained
    def report(self, **kwargs):
        return self.api.report(post_id=self.id, **kwargs)

    def likes(self, **kwargs):
        return self.api.get_post_likes(post_id=self.id, **kwargs)

    def comments(self, **kwargs):
        return self.api.get_post_comments(post_id=self.id, **kwargs)

    def reposts(self, **kwargs):
        return self.api.get_post_reposts(post_id=self.id, **kwargs)


class Comment(Model):

    @ensure_ownership
    def delete(self, **kwargs):
        return self.api.uncomment(post_id=self.post.id, comment_id=self.id, **kwargs)
    pass


class Like(Model):

    @ensure_ownership
    def delete(self, **kwargs):
        return self.api.unlike(post_id=self.post.id, **kwargs)
    pass


class Repost(Model):

    @ensure_ownership
    def delete(self, **kwargs):
        return self.api.unrevine(post_id=self.post.id, revine_id=self.id, **kwargs)
    pass


class Tag(Model):

    def timeline(self, **kwargs):
        return self.api.get_tag_timeline(tag_name=self.tag, **kwargs)


class Channel(Model):

    def timeline(self, **kwargs):
        return self.api.get_channel_recent_timeline(channel_id=self.id, **kwargs)

    def recent_timeline(self, **kwargs):
        return self.timeline()

    def popular_timeline(self, **kwargs):
        return self.api.get_channel_popular_timeline(channel_id=self.id, **kwargs)


class Notification(Model):
    pass


# mention, tag or post in a notification, comment or title
class Entity(Model):
    pass


class Venue(Model):
    pass


class Conversation(Model):
    pass


class Message(Model):
    pass


class PureUserCollection(ModelCollection):
    model = User


class UserCollection(MetaModelCollection):
    collection_class = PureUserCollection


class PurePostCollection(ModelCollection):
    model = Post


# Timeline
class PostCollection(MetaModelCollection):
    collection_class = PurePostCollection


class PureCommentCollection(ModelCollection):
    model = Comment


class CommentCollection(MetaModelCollection):
    collection_class = PureCommentCollection


class PureLikeCollection(ModelCollection):
    model = Like


class LikeCollection(MetaModelCollection):
    collection_class = PureLikeCollection


class PureRepostCollection(ModelCollection):
    model = Repost


class RepostCollection(MetaModelCollection):
    collection_class = PureRepostCollection


class PureTagCollection(ModelCollection):
    model = Tag


class TagCollection(MetaModelCollection):
    collection_class = PureTagCollection


class PureChannelCollection(ModelCollection):
    model = Channel


class ChannelCollection(MetaModelCollection):
    collection_class = PureChannelCollection


class PureNotificationCollection(ModelCollection):
    model = Notification


class NotificationCollection(MetaModelCollection):
    collection_class = PureNotificationCollection


class PureEntityCollection(ModelCollection):
    model = Entity


class PureConversationCollection(ModelCollection):
    model = Conversation


class ConversationCollection(MetaModelCollection):
    collection_class = PureConversationCollection


class PureMessageCollection(ModelCollection):
    model = Message


class MessageCollection(MetaModelCollection):
    collection_class = PureMessageCollection
    model_key = 'messages'
