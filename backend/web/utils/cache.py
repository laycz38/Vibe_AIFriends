import functools

from django.core.cache import cache


CACHE_TTL_NOTE_LIST = 120       # 首页列表 2 分钟
CACHE_TTL_NOTE_DETAIL = 300     # 笔记详情 5 分钟
CACHE_TTL_USER_STATS = 300      # 用户统计 5 分钟
CACHE_TTL_COMMENTS = 120        # 评论列表 2 分钟


def cache_note_list(page, page_size, user_id, query=''):
    """首页笔记列表缓存 key"""
    q = query.strip()
    suffix = f':auth:{user_id}' if user_id else ':public'
    return f'notes:list:{page}:{page_size}:{hash(q)}{suffix}'


def cache_note_detail(note_id):
    return f'notes:detail:{note_id}'


def cache_user_stats(user_id):
    return f'user:stats:{user_id}'


def cache_comments(note_id):
    return f'comments:{note_id}'


def invalidate_note_list():
    """笔记增删改时清除所有列表缓存（简单粗暴，数据量小）"""
    try:
        keys = cache.keys('notes:list:*')
        if keys:
            cache.delete_many(keys)
    except Exception:
        # redis.keys 性能差，改用 iter
        try:
            for key in cache.iter_keys('notes:list:*'):
                cache.delete(key)
        except Exception:
            pass


def invalidate_note(note_id):
    cache.delete(cache_note_detail(note_id))
    cache.delete(cache_comments(note_id))
    invalidate_note_list()


def invalidate_user_stats(user_id):
    cache.delete(cache_user_stats(user_id))


def cached(key_func, ttl):
    """装饰器：把函数返回值存入 Redis，下次直接返回缓存"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = key_func(*args, **kwargs)
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout=ttl)
            return result

        return wrapper

    return decorator
