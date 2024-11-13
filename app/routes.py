# app/routes.py

from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from app import db
from app.forms import RegistrationForm, LoginForm, TaskForm, EmptyForm
from app.models import User, Task
from flask_login import login_user, logout_user, login_required, current_user
from app.email import send_email
import logging

bp = Blueprint('main', __name__)

# 配置日志
logging.basicConfig(level=logging.DEBUG)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        logging.debug(f"Registering user: {form.username.data}")
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('恭喜您，注册成功！', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='注册', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        logging.debug(f"Attempting to log in user with email: {form.email.data}")
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            logging.debug("User logged in successfully.")
            flash('登录成功！', 'success')
            return redirect(url_for('main.index'))
        else:
            logging.debug("Login failed: Incorrect email or password.")
            flash('登录失败，请检查邮箱和密码。', 'danger')
    return render_template('login.html', title='登录', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出登录。', 'info')
    return redirect(url_for('main.index'))

@bp.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    if form.validate_on_submit():
        logging.debug(f"Creating task: {form.title.data}")
        assigned_user = form.assigned_user.data
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            user_id=current_user.id,
            assigned_user_id=assigned_user.id if assigned_user else None
        )
        db.session.add(task)
        db.session.commit()

        # 如果任务被分配给其他用户，发送邮件通知
        if assigned_user and assigned_user != current_user:
            send_email(
                subject='新任务分配给您',
                recipients=[assigned_user.email],
                text_body=render_template('emails/task_assigned.txt', user=assigned_user, task=task, assigner=current_user),
                html_body=render_template('emails/task_assigned.html', user=assigned_user, task=task, assigner=current_user)
            )

        flash('任务已创建。', 'success')
        return redirect(url_for('main.tasks'))
    return render_template('create_task.html', title='创建任务', form=form)

@bp.route('/tasks')
@login_required
def tasks():
    tasks = Task.query.filter(
        (Task.user_id == current_user.id) | (Task.assigned_user_id == current_user.id)
    ).all()
    form = EmptyForm()
    return render_template('tasks.html', title='我的任务', tasks=tasks, form=form)

@bp.route('/task/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.get_or_404(id)
    if task.author != current_user:
        abort(403)  # 禁止访问

    form = TaskForm()
    if form.validate_on_submit():
        assigned_user = form.assigned_user.data
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.assigned_user_id = assigned_user.id if assigned_user else None
        db.session.commit()

        # 如果任务被重新分配给其他用户，发送邮件通知
        if assigned_user and assigned_user != current_user:
            send_email(
                subject='任务已重新分配给您',
                recipients=[assigned_user.email],
                text_body=render_template('emails/task_assigned.txt', user=assigned_user, task=task, assigner=current_user),
                html_body=render_template('emails/task_assigned.html', user=assigned_user, task=task, assigner=current_user)
            )

        flash('任务已更新。', 'success')
        return redirect(url_for('main.tasks'))
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
        form.due_date.data = task.due_date
        form.assigned_user.data = task.assigned_user
    return render_template('edit_task.html', title='编辑任务', form=form, task=task)

@bp.route('/task/<int:id>/delete', methods=['POST'])
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:  # 检查 user_id
        abort(403)  # 禁止访问

    form = EmptyForm()
    if form.validate_on_submit():
        db.session.delete(task)
        db.session.commit()
        flash('任务已删除。', 'success')
        return redirect(url_for('main.tasks'))
    else:
        abort(400)  # 错误的请求

# 错误处理程序
@bp.app_errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

@bp.app_errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@bp.app_errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500