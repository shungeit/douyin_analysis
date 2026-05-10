import os


class Config:
    DB_HOST = os.environ.get('DB_HOST', '192.168.1.249')
    DB_NAME = os.environ.get('DB_NAME', 'dy_django_analysis')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '123456')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    api_key = os.environ.get('QIANFAN_API_KEY', 'bce-v3/ALTAK-yQLltbngT9EgqvDeiRU3j/37fd5a4a016d9f15b02c5834033c2f92509c679e')
    appid = os.environ.get('QIANFAN_APPID', 'app-JXFImPgB')