from django.shortcuts import render


# 重定向 404 界面
def page_not_found(request, exception, template_name='404/404.html'):
    return render(request, template_name)
