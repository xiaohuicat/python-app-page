from datetime import datetime


def timestamp_to_str(timestamp):
    # 将毫秒数转换为日期对象
    date = datetime.fromtimestamp(timestamp / 1000)

    # 获取日期对象的年月日
    year, month, day = date.year, date.month, date.day

    # 判断是否是今天
    if year == datetime.now().year and month == datetime.now().month and day == datetime.now().day:
        # 是今天，返回18:35:44格式
        time_str = date.strftime("%H:%M:%S")
        return time_str
    else:
        # 不是今天，返回2023/03/28格式
        date_str = date.strftime("%Y/%m/%d")
        return date_str


def isToday(given_date):
    # 获取当前日期时间
    current_date = datetime.now()

    # 判断给定日期是否是今天
    if given_date.year == current_date.year and given_date.month == current_date.month and given_date.day == current_date.day:
        return True
    else:
        return False


def format_milliseconds(ms: int) -> str:
    """
    将毫秒时间戳转换为易读的时长字符串。
    
    示例:
        1000         -> "0:01"
        60000        -> "1:00"
        7234500      -> "2:0:34"   (2小时0分34秒)
        3661000      -> "1:1:01"   (1小时1分1秒)
    
    参数:
        ms (int): 毫秒数（非负整数）
    
    返回:
        str: 格式化后的时间字符串
    """
    if ms < 0:
        raise ValueError("毫秒数不能为负数")
    
    total_seconds = ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours == 0:
        # 小于1小时：M:SS
        return f"{minutes}:{seconds:02d}"
    else:
        # 大于等于1小时：H:M:SS（分钟和秒不补零，只有秒固定两位）
        return f"{hours}:{minutes}:{seconds:02d}"