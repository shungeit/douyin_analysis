from django.urls import path

from video import api

urlpatterns = [
    # 认证
    path('auth/login/', api.LoginView.as_view()),
    path('auth/register/', api.RegisterView.as_view()),
    path('auth/logout/', api.LogoutView.as_view()),
    path('auth/me/', api.MeView.as_view()),
    path('auth/change-password/', api.ChangePasswordView.as_view()),

    # 数据
    path('dashboard/', api.DashboardView.as_view()),
    path('videos/', api.VideoListView.as_view()),
    path('comments/', api.CommentListView.as_view()),

    # 图表
    path('charts/ip-distribution/', api.IPDistributionView.as_view()),
    path('charts/fans-distribution/', api.FansDistributionView.as_view()),
    path('charts/engagement/', api.EngagementView.as_view()),
    path('charts/sentiment/', api.SentimentView.as_view()),
    path('charts/wordcloud/video/', api.WordcloudVideoView.as_view()),
    path('charts/wordcloud/comment/', api.WordcloudCommentView.as_view()),

    # 功能
    path('predict/', api.PredictView.as_view()),
    path('ai/analyze/', api.AIAnalyzeView.as_view()),

    # 系统配置
    path('config/', api.SystemConfigView.as_view()),

    # 数据管理操作
    path('ops/test-connection/', api.TestConnectionView.as_view()),
    path('ops/migrate/', api.MigrateDataView.as_view()),
    path('ops/refresh-stats/', api.RefreshStatsView.as_view()),
    path('ops/nlp/', api.RunNLPView.as_view()),
    path('ops/wordcloud/', api.GenerateWordcloudView.as_view()),
]
