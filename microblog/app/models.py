from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from datetime import datetime
from hashlib import md5

followers = db.Table( 'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user_model.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user_model.id'))
)

class UserModel(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(256))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('PostModel', backref='author', lazy='dynamic')
    followed = db.relationship(
        'UserModel', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def check_password(self, password):
        return check_password_hash(pwhash=self.password_hash, password=password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        default_gravatar_style = 'robohash'
        return 'https://www.gravatar.com/avatar/{}?d={}&s={}'.format(digest, default_gravatar_style, size)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def followed_posts(self):
        followed = PostModel.query.join(
            followers, followers.c.followed_id == PostModel.user_id).filter(
                followers.c.follower_id == self.id).order_by(
                    PostModel.timestamp.desc())
        own = PostModel.query.filter_by(user_id = self.id)

        return followed.union(own).order_by(PostModel.timestamp.desc())

    def __repr__(self):
        return '<User {}>'.format(self.username)

class PostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(768))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))

    def __repr__(self) -> str:
        return '<Post {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))
