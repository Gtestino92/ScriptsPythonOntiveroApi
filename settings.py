import os

MONGO_URI = os.getenv('MONGO_URI', '')
MYSQL_USER = os.getenv('MYSQL_USER', '')
MYSQL_DB = os.getenv('MYSQL_DB', '')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_HOST = os.getenv('MYSQL_HOST', '')
MYSQL_CURSORCLASS = 'DictCursor'

JWT_PRIVATE_KEY = os.getenv('JWT_PRIVATE_KEY', '')
JWT_PUBLIC_KEY = os.getenv('JWT_PUBLIC_KEY', '')
