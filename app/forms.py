# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import User
from datetime import datetime

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField(
        '确认密码', validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被注册，请选择其他用户名。')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册，请选择其他邮箱。')

class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

from wtforms import SelectField

class TaskForm(FlaskForm):
    title = StringField('任务标题', validators=[DataRequired()])
    description = TextAreaField('任务描述')
    due_date = DateTimeField('截止日期', format='%Y-%m-%d %H:%M:%S', default=datetime.utcnow)
    assigned_user = QuerySelectField(
        '分配给',
        query_factory=lambda: User.query.all(),
        allow_blank=True,
        get_label='username'
    )
    # 添加 status 字段
    status = SelectField(
        '任务状态',
        choices=[('to_do', '待办'), ('in_progress', '进行中'), ('done', '完成')]
    )
    submit = SubmitField('提交')

class EmptyForm(FlaskForm):
    pass