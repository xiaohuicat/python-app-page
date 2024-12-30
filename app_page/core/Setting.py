from app_page import LocalStore

# 本地存储
class Setting(object):
  def __init__(self) -> None:
    self.local_storage = LocalStore("./assets/data/setting.json")
    self.data = self.local_storage.getAll()

  def load(self):
    self.data = self.local_storage.getAll()
    return self.data

  def get(self, key, default=None):
    if self.data and key in self.data.keys():
      return self.data[key]
    else:
      default
  
  def save(self):
    self.local_storage.save(self.data)