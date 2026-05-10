from datetime import datetime
import httpx
from openai import OpenAI
from config import Config


def _load_ai_config():
    """优先从 system_config 数据库表读取 AI 配置，回退到 Config 默认值。"""
    try:
        from video.models import SystemConfig
        rows = {c.config_key: c.config_value
                for c in SystemConfig.objects.filter(
                    config_key__in=['ai_api_key', 'ai_base_url', 'ai_appid', 'ai_model'])}
        return {
            'api_key':  rows.get('ai_api_key')  or Config.api_key,
            'base_url': rows.get('ai_base_url') or 'https://qianfan.baidubce.com/v2',
            'appid':    rows.get('ai_appid')    or Config.appid,
            'model':    rows.get('ai_model')    or 'ernie-3.5-8k',
        }
    except Exception:
        return {
            'api_key':  Config.api_key,
            'base_url': 'https://qianfan.baidubce.com/v2',
            'appid':    Config.appid,
            'model':    'ernie-3.5-8k',
        }


def test_ai_connection(ai_config=None):
    """用一条 hello 消息验证 AI 配置是否可用。"""
    ai = ai_config or _load_ai_config()
    http_client = httpx.Client(timeout=20.0)
    client = OpenAI(
        api_key=ai['api_key'],
        base_url=ai['base_url'],
        http_client=http_client,
        default_headers={"appid": ai['appid']}
    )
    try:
        response = client.chat.completions.create(
            model=ai['model'],
            messages=[{"role": "user", "content": "hello"}],
            temperature=0,
        )
        return (response.choices[0].message.content or '').strip()
    finally:
        http_client.close()


def analyze_single_viedo(video_data, analysis_focus=None):
    ai = _load_ai_config()

    # 手动传入 httpx.Client 实例，绕过 openai 旧版与 httpx>=0.28 的 proxies 参数不兼容问题
    client = OpenAI(
        api_key=ai['api_key'],
        base_url=ai['base_url'],
        http_client=httpx.Client(),
        default_headers={"appid": ai['appid']}
    )
    try:
        publish_date = datetime.strptime(video_data['发表时间'], "%Y.%m.%d")
        days_since_publish = (datetime.now() - publish_date).days
        days_info = f"已发布{days_since_publish}天"
    except:
        days_info = '发布时间数据异常'

    try:
        dur = video_data['视频时长']
        if isinstance(dur, (int, float)):
            video_duration = int(dur)
        elif isinstance(dur, str) and ':' in dur:
            parts = dur.split(':')
            video_duration = int(parts[0]) * 60 + int(parts[1])
        else:
            video_duration = int(dur) if str(dur).strip().isdigit() else 0
        interaction_rate = ((video_data['点赞数量'] + video_data['评论数量'] + video_data['分享数量']) / video_data[
            '粉丝数量']) * 100 if \
            video_data['粉丝数量'] > 0 else 0
        like_rate = (video_data['点赞数量'] / video_data['粉丝数量']) * 100 if video_data['粉丝数量'] > 0 else 0
    except Exception as e:
        print('指标异常')
        print(e)
        return str(e)
    prompt = f"""
    你是一个短视频内容策略专家，请分析以下视频信息数据，并提供优化建议。

    === 视频基础信息 ===
    - 粉丝数量: {video_data['粉丝数量']}
    - 发表时间: {days_info}
    - 视频描述: {video_data['视频描述']}
    - 视频时长: {video_duration}秒
    - 点赞数量: {video_data['点赞数量']}
    - 收藏数量: {video_data['收藏数量']}
    - 评论数量: {video_data['评论数量']}
    - 分享数量: {video_data['分享数量']}

    === 关键指标 ===
    - 点赞率: {like_rate:.2f}%
    - 互动率: {interaction_rate:.2f}%

    === 分析重点 ===
    {analysis_focus if analysis_focus else "1. 找出该视频表现优异/不足的指标. 提供内容优化建议. 建议发布时间调整（如有数据）"}

    请按照以下结构返回分析结果：
    === 表现评估 ===
    [分析点赞/评论/分享等指标的优劣]

    === 优化建议 ===
    1. [内容方向调整建议]
    2. [互动设计建议（如提问、投票等）]
    3. [标签/话题优化建议]
    """
    try:
        messages = [
            {
                "role": 'system',
                "content": "你是一个专业的短视频数据分析师，擅长从数据中发现优化机会。"
            },
            {
                "role": "user",
                "content": prompt
            }

        ]

        response = client.chat.completions.create(
            model=ai['model'],
            messages=messages,
            temperature=0.7,
            top_p=0.8,
        )

        return {
            "analysis": response.choices[0].message.content,
            "metrics": {
                "like_rate": like_rate,
                "interaction_rate": interaction_rate,
                "duration": video_duration,
                "days_since_publish": days_since_publish if "days_since_publish" in locals() else None,

            }
        }
    except Exception as e:
        print(e)
        return {"error": "AI分析失败"}
