# app/models.py

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    # 任务创建者的关系
    tasks = db.relationship(
        'Task',
        backref='author',
        foreign_keys='Task.user_id',
        lazy='dynamic'
    )

    # 被分配任务的关系
    assigned_tasks = db.relationship(
        'Task',
        backref='assigned_user',
        foreign_keys='Task.assigned_user_id',
        lazy='dynamic'
    )

    def set_password(self, password):
        """设置密码哈希值"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """检查密码是否正确"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)

    # 创建任务的用户
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', name='fk_tasks_user_id_users'),
        nullable=False
    )

    # 被分配用户
    assigned_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', name='fk_tasks_assigned_user_id_users'),
        nullable=True
    )


    def __repr__(self):
        return f'<Task {self.title}>'