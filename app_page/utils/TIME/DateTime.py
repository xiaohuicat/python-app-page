import time
from datetime import datetime, timedelta

def now_timestamp():
  # 获取当前时间戳（秒级）
  timestamp_seconds = time.time()
  # 将秒级时间戳转换为毫秒级时间戳
  timestamp = int(timestamp_seconds * 1000)
  return timestamp

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
    
def dateTimeString(timestamp=None, connect="_"):
  dt_object = datetime.fromtimestamp(time.time() if not timestamp else timestamp / 1000.0)
  date_string = dt_object.strftime('%Y-%m-%d')  # 将 time.struct_time 类型转换为日期字符串
  # time_string = dt_object.strftime('%H:%M:%S:%f')[:-3]  # 将 time.struct_time 类型转换为时分秒毫秒字符串
  time_string = dt_object.strftime('%H-%M-%S')  # 将 time.struct_time 类型转换为时分秒毫秒字符串
  return date_string+connect+time_string

def isToday(given_date):
  # 获取当前日期时间
  current_date = datetime.now()

  # 判断给定日期是否是今天
  if given_date.year == current_date.year and given_date.month == current_date.month and given_date.day == current_date.day:
    return True
  else:
    return False
  
def Json2String(date_string):
  # 解析日期时间字符串为datetime对象
  date_time_obj = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')

  # 创建UTC偏移量
  utc_offset = timedelta(hours=8)

  # 添加UTC偏移量以转换为东八区时区
  date_time_obj_eastern = date_time_obj + utc_offset

  # 格式化日期时间对象为所需格式
  if isToday(date_time_obj):
    formatted_date_time = date_time_obj_eastern.strftime('%H:%M:%S')
  else:
    formatted_date_time = date_time_obj_eastern.strftime('%Y-%m-%d')

  return formatted_date_time


def calculate_datetime(date_time1:str, date_time2:str):
  if date_time1 == None or date_time2 == None: return ""
  # 将字符串转换为datetime对象
  time1 = datetime.strptime(date_time1, "%Y-%m-%d %H:%M:%S")
  time2 = datetime.strptime(date_time2, "%Y-%m-%d %H:%M:%S")

  time_difference = time2 - time1

  return str(time_difference)