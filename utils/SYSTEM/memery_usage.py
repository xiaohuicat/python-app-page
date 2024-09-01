import psutil

def memery_usage():
  # 获取当前进程的内存占用情况
  process = psutil.Process()
  memory_usage = process.memory_info().rss

  # 转换为MB
  memory_usage_mb = memory_usage / (1024 * 1024)

  return memory_usage_mb