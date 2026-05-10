from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from video.models import User


class SessionAuthentication(BaseAuthentication):
    """
    通过 Django session 验证自定义 User 模型。
    前端 Axios 需设置 withCredentials: true 以携带 session cookie。
    """

    def authenticate(self, request):
        uid = request.session.get('uid')
        if not uid:
            return None
        try:
            user = User.objects.get(id=uid)
            return (user, None)
        except User.DoesNotExist:
            raise AuthenticationFailed('用户不存在')

    def authenticate_header(self, request):
        return 'Session'
