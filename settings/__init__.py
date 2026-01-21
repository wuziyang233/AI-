from datetime import timedelta

DB_URI = "mysql+aiomysql://root:Wzy822894180@127.0.0.1:3306/ai_name?charset=utf8mb4"


# 邮箱相关配置
MAIL_USERNAME = "1827074175@qq.com"
MAIL_PASSWORD = "vmvyhwqjvgcwbech"
MAIL_FROM = "1827074175@qq.com"
MAIL_PORT = 587
MAIL_SERVER = "smtp.qq.com"
MAIL_FROM_NAME = "wzy"
MAIL_STARTTLS = True
MAIL_SSL_TLS = False

JWT_SECRET_KEY = "sdafdsvcqwd12"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=15)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)


