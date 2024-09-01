import json
import paho.mqtt.client as mqtt
from core.Thread import EasyThread
from nanoid import generate

class MQTT(EasyThread):
  def __init__(self, option):
    super().__init__()
    self.broker = option["broke"] if "broke" in option else 'broker.emqx.io'
    self.port = option["port"] if "port" in option else 1883
    self.topic = option["topic"] if "topic" in option else "user/test/mqtt"
    self.client_id = 'mqtt_Qt_'+generate(size=6)
    self.client = None
    
  def destroy(self, param):
    print("destroy mqtt param:", param)
    self.client.disconnect()
    self.client.loop_stop()

  # 客户端连接
  def connect_mqtt(self):
    def on_connect(client, userdata, flags, rc):
      if rc == 0:
        print("Connected to MQTT Broker!")
        self.response.emit({"status": 0, "msg": "Connected to MQTT Broker!"})
      else:
        print("Failed to connect, return code %d\n", rc)
        self.response.emit({"status": -1, "msg": "Connected to MQTT Broker!"})
    # Set Connecting Client ID
    client = mqtt.Client(client_id=self.client_id)
    client.on_connect = on_connect
    client.connect(self.broker, self.port)
    self.client = client
  
  # 发布消息
  def publish(self, msg):
    payload = {"client_id":self.client_id, "payload":msg}
    result = self.client.publish(self.topic, json.dumps(payload))
    if result[0] == 0:
      print(f"Send `{msg}` to topic `{self.topic}`")
      self.response.emit({"status": 0, "msg": f"Send `{msg}` to topic `{self.topic}`"})
    else:
      print(f"Failed to send message to topic {self.topic}")
      self.response.emit({"status": -1, "msg": f"Failed to send message to topic {self.topic}"})

  # 订阅消息
  def subscribe(self):
    def on_message(client, userdata, msg):
      # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
      self.response.emit({"status": 1, "msg": msg.payload.decode(), "topic": msg.topic})
    self.client.subscribe(self.topic)
    self.client.on_message = on_message

  # 启动线程
  def run(self):
    self.connect_mqtt()
    self.subscribe()
    self.client.loop_forever()