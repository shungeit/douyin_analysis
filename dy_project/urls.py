from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('video.api_urls')),
    # 保留旧模板路由（Django Admin 的 SimpleUI 仍需要它）
    path('home/', include('video.urls')),
]
