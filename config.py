import os

class Config:
    # 之前的配置项
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 邮件服务器配置
    MAIL_SERVER = 'mail.hygon.cn'           # 邮件服务器地址，例如 'smtp.gmail.com'
    MAIL_PORT = 587                            # 邮件服务器端口，通常为 587（TLS）或 465（SSL）
    MAIL_USE_TLS = True                        # 启用 TLS
    MAIL_USE_SSL = False                       # 如果使用 SSL，设置为 True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')   # 邮件服务器用户名
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')   # 邮件服务器密码
    MAIL_DEFAULT_SENDER = MAIL_USERNAME        # 默认发件人