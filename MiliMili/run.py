import os
import platform

os.system("python manage.py makemigrations")
os.system("python manage.py migrate")

if platform.system() != "Linux":
    os.system("python manage.py runserver")
    # 本地环境，直接运行
else:
    os.system("python manage.py runserver 0.0.0.0:8000 > log.txt & \n")
    print("The backend is running!")
    # 服务器环境，后台运行
