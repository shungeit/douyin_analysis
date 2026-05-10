import os
import re
from collections import Counter
from datetime import datetime

import pandas as pd
import pymysql
from django.conf import settings
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from sqlalchemy import create_engine

import util
from config import Config
from Get_Qianfan import analyze_single_viedo, test_ai_connection
from forecast import predict_likes
from video.authentication import SessionAuthentication
from video.models import CommentData, SystemConfig, User, VideoData
from video.serializers import CommentDataSerializer, UserSerializer, VideoDataSerializer


# ── 认证 ───────────────────────────────────────────────────────────────────────

class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        try:
            user = User.objects.get(username=username, password=password)
            request.session['uid'] = user.id
            request.session['username'] = username
            return Response({'id': user.id, 'username': user.username})
        except User.DoesNotExist:
            return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        if not username or not password:
            return Response({'error': '用户名和密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': '用户已存在'}, status=status.HTTP_400_BAD_REQUEST)
        User.objects.create(username=username, password=password)
        return Response({'message': '注册成功'}, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        request.session.clear()
        return Response({'message': '已退出'})


class MeView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')
        user = request.user

        if old_password != user.password:
            return Response({'error': '原始密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password:
            return Response({'error': '新密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != confirm_password:
            return Response({'error': '两次输入密码不一致'}, status=status.HTTP_400_BAD_REQUEST)

        user.password = new_password
        user.save()
        return Response({'message': '密码修改成功'})


# ── 数据接口 ───────────────────────────────────────────────────────────────────

class DashboardView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Sum
        agg = VideoData.objects.aggregate(
            total_like=Sum('likeCount'),
            total_comment=Sum('commentCount'),
            total_collect=Sum('collectCount'),
        )
        stats = {
            'total': VideoData.objects.count(),
            'total_like': agg['total_like'] or 0,
            'total_comment': agg['total_comment'] or 0,
            'total_collect': agg['total_collect'] or 0,
        }

        rows = util.query('SELECT * FROM part2 ORDER BY likeCount DESC LIMIT 10')
        top_videos = {
            'like_counts': [r[0] for r in rows],
            'collect_counts': [r[1] for r in rows],
            'descriptions': [r[2] for r in rows],
            'ratios': [r[3] for r in rows],
        }

        return Response({'stats': stats, 'top_videos': top_videos})


class VideoListView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page     = request.GET.get('page', 1)
        per_page = int(request.GET.get('per_page', 10))
        sort_map = {
            'likeCount':    '-likeCount',
            'commentCount': '-commentCount',
            'shareCount':   '-shareCount',
            'publishTime':  '-publishTime',
        }
        sort_field = sort_map.get(request.GET.get('sort', 'likeCount'), '-likeCount')
        paginator = Paginator(VideoData.objects.all().order_by(sort_field, '-id'), per_page)
        page_obj = paginator.get_page(page)
        return Response({
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'results': VideoDataSerializer(page_obj, many=True).data,
        })


class CommentListView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Q
        page     = request.GET.get('page', 1)
        per_page = int(request.GET.get('per_page', 10))
        search   = request.GET.get('search', '').strip()
        qs = CommentData.objects.all()
        if search:
            qs = qs.filter(Q(content__icontains=search) | Q(username__icontains=search))
        paginator = Paginator(qs.order_by('-id'), per_page)
        page_obj  = paginator.get_page(page)
        return Response({
            'count':        paginator.count,
            'num_pages':    paginator.num_pages,
            'current_page': page_obj.number,
            'results':      CommentDataSerializer(page_obj, many=True).data,
        })


# ── 图表数据接口 ───────────────────────────────────────────────────────────────

class IPDistributionView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = util.query('SELECT userIP, `count` FROM part1 ORDER BY `count` DESC LIMIT 15')
        return Response({'data': [{'name': r[0], 'value': r[1]} for r in rows]})


class FansDistributionView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows3 = util.query('SELECT * FROM part3')
        rows4 = util.query('SELECT username, fansCount FROM part4 ORDER BY fansCount DESC LIMIT 10')
        return Response({
            'fans_range': [{'name': r[0], 'value': r[1]} for r in rows3],
            'top10': {
                'names': [r[0] for r in rows4],
                'values': [r[1] for r in rows4],
            },
        })


class EngagementView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = util.query('SELECT * FROM part5 ORDER BY (commentCount + shareCount) DESC LIMIT 10')
        top10 = {
            'comment_list': [r[0] for r in rows],
            'share_list': [r[1] for r in rows],
            'name_list': [r[2] for r in rows],
        }

        try:
            df = pd.read_csv('./data/nlp_result.csv')
            sw = _load_stopwords()
            # 只保留 2+ 汉字组成的词，且不在停用词表中
            cn_word = re.compile(r'^[一-鿿]{2,}$')
            all_words = []
            for text in df['segmented']:
                if isinstance(text, str):
                    all_words.extend(
                        w for w in text.strip().split()
                        if cn_word.fullmatch(w) and w not in sw
                    )
            word_counts = [{'name': w, 'value': c} for w, c in Counter(all_words).most_common(100)]
        except Exception:
            word_counts = []

        return Response({'top10': top10, 'word_counts': word_counts})


class SentimentView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            df = pd.read_csv('./data/nlp_result.csv')
            bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            labels = ['0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5',
                      '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0']
            df['score_group'] = pd.cut(df['scores'].astype(float), bins=bins, labels=labels)
            counts = df['score_group'].value_counts()

            distribution = {
                'names': [str(k) for k in counts.index.tolist()],
                'values': [int(v) for v in counts.values.tolist()],
            }

            pie_raw = {'积极': 0, '消极': 0, '中性': 0}
            for s in df['scores']:
                v = float(s)
                if v < 0.5:
                    pie_raw['消极'] += 1
                elif v == 0.5:
                    pie_raw['中性'] += 1
                else:
                    pie_raw['积极'] += 1
            pie_data = [{'name': k, 'value': v} for k, v in pie_raw.items()]
        except Exception:
            distribution = {'names': [], 'values': []}
            pie_data = []

        return Response({'pie_data': pie_data, 'distribution': distribution})


def _img_url(filename):
    """返回带文件修改时间戳的静态图片 URL，强制浏览器在文件更新后重新加载。"""
    path = os.path.join(settings.BASE_DIR, 'static', 'img', filename)
    ts = int(os.path.getmtime(path)) if os.path.exists(path) else 0
    return f'/static/img/{filename}?v={ts}'


class WordcloudVideoView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'url': _img_url('title_wordcloud.jpg')})


class WordcloudCommentView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'url': _img_url('comment_wordcloud.jpg')})


# ── 功能接口 ───────────────────────────────────────────────────────────────────

class PredictView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            input_data = {
                'duration': float(request.data['duration']),
                'collect': float(request.data['collect']),
                'comment': float(request.data['comment']),
                'share': float(request.data['share']),
                'fans': float(request.data['fans']),
                'interaction_rate': float(request.data['interaction_rate']),
                'hour': int(request.data['hour']),
            }
            prediction = predict_likes(input_data)
            return Response({'prediction': prediction, 'input': input_data})
        except Exception as e:
            return Response({'error': f'预测失败：{e}'}, status=status.HTTP_400_BAD_REQUEST)


def _load_stopwords():
    """加载停用词：stopwords.txt + 内置无意义助词/语气词/空白符。"""
    builtin = {
        # 结构助词
        '的', '地', '得', '了', '过', '着', '啊', '吧', '呢', '吗',
        '呀', '嘛', '哦', '哟', '哇', '哈', '嗯', '呵', '嘿', '哼',
        '嗨', '哎', '唉', '喂', '噢', '喔', '哈哈', '哈哈哈', '嘻嘻',
        '嗯嗯', '哈哈哈哈',
        # 高频代词/副词
        '我', '你', '他', '她', '它', '们', '我们', '你们', '他们',
        '这', '那', '都', '也', '就', '但', '还', '有', '很', '和',
        '与', '或', '所', '于', '以', '为', '被', '把', '让', '使',
        '到', '从', '由', '对', '是', '在', '不', '没',
        # 常见口语无实义词
        '什么', '这个', '那个', '一个', '一下', '一样', '一些',
        '可以', '真的', '感觉', '觉得', '已经', '还是', '因为',
        '所以', '但是', '然后', '如果', '虽然', '不是', '应该',
        '自己', '知道', '现在', '时候', '一种', '这种', '那种',
        '没有', '就是', '而且', '这样', '那样', '怎么', '为什么',
        # 换行/空白（jieba 偶尔切出）
        '\n', '\r', '\t', '\r\n', ' ', '',
    }
    try:
        sw_path = os.path.join(settings.BASE_DIR, 'data', 'stopwords.txt')
        with open(sw_path, encoding='utf-8') as f:
            builtin.update(line.strip() for line in f if line.strip())
    except Exception:
        pass
    return builtin


def _filter_tokens(tokens, stopwords):
    """过滤停用词、单字符、纯数字、纯空白。保留 2+ 汉字组成的词。"""
    result = []
    for w in tokens:
        w = w.strip()
        if not w:
            continue
        if w in stopwords:
            continue
        if len(w) == 1:          # 单字无实义
            continue
        if re.match(r'^\d+$', w):  # 纯数字
            continue
        result.append(w)
    return result


def _get_config(keys):
    """从 system_config 表批量读配置，缺失时回退到空字符串。"""
    rows = SystemConfig.objects.filter(config_key__in=keys)
    return {r.config_key: r.config_value or '' for r in rows}


AI_CONFIG_KEYS = {'ai_api_key', 'ai_base_url', 'ai_appid', 'ai_model'}


def _ai_config_from_payload(data):
    saved = _get_config(AI_CONFIG_KEYS)

    def pick(key, default):
        value = data.get(key)
        return value if value not in (None, '') else (saved.get(key) or default)

    return {
        'api_key': pick('ai_api_key', Config.api_key),
        'base_url': pick('ai_base_url', 'https://qianfan.baidubce.com/v2'),
        'appid': pick('ai_appid', Config.appid),
        'model': pick('ai_model', 'ernie-3.5-8k'),
    }


class SystemConfigView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        configs = {c.config_key: c.config_value for c in SystemConfig.objects.all()}
        return Response(configs)

    def post(self, request):
        should_test_ai = any(key in request.data for key in AI_CONFIG_KEYS)
        if should_test_ai:
            try:
                test_ai_connection(_ai_config_from_payload(request.data))
            except Exception as e:
                return Response(
                    {'success': False, 'message': f'AI 配置测试失败：{e}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        for key, value in request.data.items():
            SystemConfig.objects.update_or_create(
                config_key=key,
                defaults={'config_value': value},
            )

        message = '配置已保存，AI 测试通过' if should_test_ai else '配置已保存'
        return Response({'success': True, 'message': message})


class AIAnalyzeView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        result = analyze_single_viedo({
            '粉丝数量': int(data.get('fans', 0)),
            '发表时间': data.get('publish_date', ''),
            '视频描述': data.get('description', ''),
            '视频时长': data.get('duration', ''),
            '点赞数量': int(data.get('likes', 0)),
            '收藏数量': int(data.get('favorites', 0)),
            '评论数量': int(data.get('comments', 0)),
            '分享数量': int(data.get('shares', 0)),
        }, data.get('analysis_focus'))
        return Response(result)


# ── 数据管理操作 ───────────────────────────────────────────────────────────────

def _ts_to_date(ts):
    """Unix 时间戳 → 'YYYY.MM.DD'"""
    try:
        return datetime.fromtimestamp(int(ts)).strftime('%Y.%m.%d') if ts else ''
    except (ValueError, OSError):
        return ''


def _ts_to_str(ts):
    """Unix 时间戳 → 'YYYY-MM-DD HH:MM:SS'"""
    try:
        return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S') if ts else ''
    except (ValueError, OSError):
        return ''


def _safe_int(val):
    try:
        return int(str(val).strip())
    except (TypeError, ValueError):
        return 0


class TestConnectionView(APIView):
    """测试源数据库连接"""
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        host = request.data.get('host', '').strip()
        port = int(request.data.get('port', 3306) or 3306)
        db_name = request.data.get('db_name', '').strip() or 'media_crawler'
        user = request.data.get('user', '').strip()
        password = request.data.get('password', '')
        if not host or not user:
            return Response({'success': False, 'message': 'host 和账号不能为空'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            con = pymysql.connect(host=host, port=port, user=user, password=password,
                                  db=db_name, charset='utf8mb4', connect_timeout=5)
            con.close()
            return Response({'success': True, 'message': f'连接成功，{db_name} 数据库可访问'})
        except Exception as e:
            return Response({'success': False, 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class MigrateDataView(APIView):
    """从源数据库全量迁移到 dy_django_analysis（支持指定源数据库连接）"""
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        clear = bool(request.data.get('clear', False))

        # 从 system_config 读已保存的源库配置作为默认值
        saved = _get_config(['src_db_host', 'src_db_port', 'src_db_name', 'src_db_user', 'src_db_password'])
        src_host = request.data.get('src_host', '').strip() or saved.get('src_db_host') or Config.DB_HOST
        src_port = int(request.data.get('src_port', 0) or saved.get('src_db_port') or Config.DB_PORT)
        src_db_name = request.data.get('src_db_name', '').strip() or saved.get('src_db_name') or 'media_crawler'
        src_user = request.data.get('src_user', '').strip() or saved.get('src_db_user') or Config.DB_USER
        src_password = request.data.get('src_password') if request.data.get('src_password') else (saved.get('src_db_password') or Config.DB_PASSWORD)

        src_conf = dict(host=src_host, port=src_port, user=src_user,
                        password=src_password, db=src_db_name,
                        charset='utf8mb4', connect_timeout=10)
        dst_conf = dict(host=Config.DB_HOST, port=Config.DB_PORT,
                        user=Config.DB_USER, password=Config.DB_PASSWORD,
                        db=Config.DB_NAME, charset='utf8mb4', autocommit=False)
        try:
            # 读取源库数据
            src_con = pymysql.connect(**src_conf)
            src_cur = src_con.cursor()
            # douyin_aweme 自带 author_follower_count（粉丝数）和 video_duration（时长秒）
            # 联表 dy_creator 需通过 a.sec_uid = c.user_id（原代码用 a.user_id 类型不匹配）
            src_cur.execute("""
                SELECT a.nickname,
                       a.author_follower_count,
                       a.`desc`,
                       CAST(a.aweme_id AS CHAR),
                       a.create_time,
                       a.liked_count,
                       a.collected_count,
                       a.comment_count,
                       a.share_count,
                       a.video_duration
                FROM douyin_aweme a
            """)
            video_rows = src_cur.fetchall()

            src_cur.execute("""
                SELECT nickname, create_time, ip_location, content, like_count, aweme_id
                FROM douyin_aweme_comment WHERE content IS NOT NULL
            """)
            comment_rows = src_cur.fetchall()
            src_cur.close()
            src_con.close()

            # 写入目标库
            dst_con = pymysql.connect(**dst_conf)
            dst_cur = dst_con.cursor()
            try:
                if clear:
                    dst_cur.execute('DELETE FROM videodata')
                    dst_cur.execute('DELETE FROM commentdata')
                    dst_con.commit()

                v_sql = ("INSERT INTO videodata "
                         "(username,fansCount,description,aweme_id,publishTime,duration,"
                         "likeCount,collectCount,commentCount,shareCount,downloadCount) "
                         "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NULL)")
                for row in video_rows:
                    nickname, fans, desc, aweme_id, ct, liked, collected, cmt, share, dur = row
                    dst_cur.execute(v_sql, (
                        nickname,
                        _safe_int(fans) if fans else None,
                        desc,
                        aweme_id,
                        _ts_to_date(ct),
                        _safe_int(dur) if dur else None,
                        _safe_int(liked),
                        _safe_int(collected),
                        _safe_int(cmt),
                        _safe_int(share),
                    ))

                c_sql = ("INSERT INTO commentdata "
                         "(userid,username,commentTime,userIP,content,likeCount,aweme_id) "
                         "VALUES (0,%s,%s,%s,%s,%s,%s)")
                for row in comment_rows:
                    nickname, ct, ip, content, like, aweme_id = row
                    dst_cur.execute(c_sql, (nickname, _ts_to_str(ct), ip, content, _safe_int(like), aweme_id))

                dst_con.commit()
                return Response({
                    'success': True,
                    'message': f'从 {src_db_name} 迁移完成：{len(video_rows)} 条视频，{len(comment_rows)} 条评论',
                    'videos': len(video_rows),
                    'comments': len(comment_rows),
                })
            except Exception:
                dst_con.rollback()
                raise
            finally:
                dst_cur.close()
                dst_con.close()
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RefreshStatsView(APIView):
    """刷新 part1~part5 预计算统计表"""
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            engine = create_engine(
                f'mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}'
                f'@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}?charset=utf8mb4'
            )
            vdf = pd.read_sql_table('videodata', engine)
            cdf = pd.read_sql_table('commentdata', engine)

            # part1: IP 分布
            r1 = cdf['userIP'].value_counts().reset_index()
            r1.columns = ['userIP', 'count']
            r1.to_sql('part1', engine, if_exists='replace', index=False)

            # 将所有数值列统一转为 float（None/NaN → 0），避免排序时 NoneType 比较报错
            for col in ['likeCount', 'collectCount', 'commentCount', 'shareCount', 'fansCount']:
                if col in vdf.columns:
                    vdf[col] = pd.to_numeric(vdf[col], errors='coerce').fillna(0)

            # part2: 点赞/收藏 TOP10
            r2 = vdf[['likeCount', 'collectCount', 'description']].sort_values('likeCount', ascending=False).head(10).copy()
            r2['ratio'] = r2['collectCount'] / r2['likeCount'].replace(0, 1)
            r2.to_sql('part2', engine, if_exists='replace', index=False)

            # part3: 粉丝区间
            bins = [0, 100, 1000, 10000, 100000, float('inf')]
            labels = ['小于100', '小于1000', '小于10000', '小于100000', '大于100000']
            vdf['fansRange'] = pd.cut(vdf['fansCount'], bins=bins, labels=labels)
            r3 = vdf['fansRange'].value_counts().reset_index()
            r3.columns = ['fansRange', 'count']
            r3.to_sql('part3', engine, if_exists='replace', index=False)

            # part4: 粉丝排行 TOP10
            r4 = (vdf[['username', 'fansCount']].drop_duplicates('username')
                  .sort_values('fansCount', ascending=False).head(10))
            r4.to_sql('part4', engine, if_exists='replace', index=False)

            # part5: 评论/分享 TOP10
            r5 = vdf[['commentCount', 'shareCount', 'description']].sort_values('commentCount', ascending=False).head(10)
            r5.to_sql('part5', engine, if_exists='replace', index=False)

            engine.dispose()
            return Response({'success': True, 'message': 'part1~part5 统计表已刷新'})
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RunNLPView(APIView):
    """对 commentdata 重跑情感分析，输出 data/nlp_result.csv"""
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            import jieba
            from snownlp import SnowNLP

            stopwords_path = os.path.join(settings.BASE_DIR, 'data', 'stopwords.txt')
            with open(stopwords_path, encoding='utf-8') as f:
                stopwords = {line.strip() for line in f}

            contents = list(CommentData.objects.values_list('content', flat=True))
            scores, segmented = [], []

            for text in contents:
                text = str(text) if text else ''
                words = list(jieba.cut(text))
                filtered = [w for w in words if w not in stopwords or w in {'不', '没', '非常', '特别'}]
                filtered_text = ''.join(filtered)
                segmented.append(' '.join(filtered))
                scores.append(SnowNLP(filtered_text).sentiments if filtered_text.strip() else 0.5)

            df = pd.DataFrame({'评论内容': contents, 'scores': scores, 'segmented': segmented})
            df.to_csv(os.path.join(settings.BASE_DIR, 'data', 'nlp_result.csv'), index=False)

            pos = sum(1 for s in scores if s > 0.5)
            neg = sum(1 for s in scores if s < 0.5)
            neu = len(scores) - pos - neg
            return Response({
                'success': True,
                'message': f'NLP 分析完成，共处理 {len(scores)} 条评论',
                'positive': pos, 'negative': neg, 'neutral': neu,
            })
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateWordcloudView(APIView):
    """重新生成视频标题与评论词云图"""
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from wordcloud import WordCloud
            import jieba

            # 中文字体：优先用户放在 data/ 的 STHUPO.TTF，回退到系统 wqy 字体
            font_candidates = [
                os.path.join(settings.BASE_DIR, 'data', 'STHUPO.TTF'),
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            ]
            font_path = next((p for p in font_candidates if os.path.exists(p)), None)
            if not font_path:
                return Response({'success': False, 'message': '未找到中文字体，请将 STHUPO.TTF 放入 data/ 目录'},
                                status=status.HTTP_400_BAD_REQUEST)

            img_dir = os.path.join(settings.BASE_DIR, 'static', 'img')
            os.makedirs(img_dir, exist_ok=True)

            def make_wc(text, path):
                wc = WordCloud(width=800, height=800, background_color='white',
                               font_path=font_path, max_words=300,
                               max_font_size=100, min_font_size=10, collocations=False)
                wc.generate(text)
                plt.figure(figsize=(12, 10))
                plt.imshow(wc, interpolation='bilinear')
                plt.axis('off')
                plt.savefig(path, bbox_inches='tight')
                plt.close()

            sw = _load_stopwords()

            raw_video = ' '.join(filter(None, VideoData.objects.values_list('description', flat=True)))
            video_text = ' '.join(_filter_tokens(jieba.cut(raw_video), sw))
            make_wc(video_text, os.path.join(img_dir, 'title_wordcloud.jpg'))

            raw_comment = ' '.join(filter(None, CommentData.objects.values_list('content', flat=True)))
            comment_text = ' '.join(_filter_tokens(jieba.cut(raw_comment), sw))
            make_wc(comment_text, os.path.join(img_dir, 'comment_wordcloud.jpg'))

            return Response({'success': True, 'message': '视频词云和评论词云已重新生成'})
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
