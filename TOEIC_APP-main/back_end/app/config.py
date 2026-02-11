import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'votre-clé-secrète'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://root:@localhost/toeic_app'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 299


    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'elalamisafa2003@gmail.com' 
    MAIL_PASSWORD = 'aojz nien jciv ymvh'   
    MAIL_DEFAULT_SENDER = 'elalamisafa2003@gmail.com' 

