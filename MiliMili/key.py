# 邮件信息
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'  # 腾讯QQ邮箱SMTP服务器地址
EMAIL_PORT = 25  # SMTP服务器端口号
EMAIL_HOST_USER = '3044039051@qq.com'  # 发送邮件的QQ邮箱
EMAIL_HOST_PASSWORD = 'zosulotgxochdehe'  # 授权码
EMAIL_USE_TLS = False  # 与SMTP服务器通信时，是否启动TLS链接（安全链接）默认False

# 对象存储信息
bucket_secret_id = 'AKIDNZVAYfV5NO9dqmTv5zcz4sPggPr2yc07'
bucket_secret_key = 'sTnqc7LJ0Q2NREl10h8IBn8CyTigNo31'
bucket_app_id = '-1309504341'
bucket_region = 'ap-beijing'
bucket_access = 'public-read'

# 数据库配置
db_ENGINE = 'django.db.backends.mysql'
db_NAME = 'milimili'
db_USER = 'buaa2021'
db_PASSWORD = 'buaa(2021)'
db_HOST = 'rm-wz974lh9hz3g6w0k5ko.mysql.rds.aliyuncs.com'
db_PORT = '3306'

# 查看IP地址
aliyun_appcode = '1437a6fc99dc4078bfe01338d7132c2c'  # 开通服务后 买家中心-查看AppCode

# token加密所需的密钥
TOKEN_SECRET_KEY = 'django-insecure-7_zr&s64q6sv+hnto6smvc!5$s96+cw7%)tf@fab9%lpanbr%x'
