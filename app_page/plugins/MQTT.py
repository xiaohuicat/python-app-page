import json
import logging
import time
from typing import Optional, Dict, Any
import paho.mqtt.client as mqtt
from nanoid import generate
from ..core.Thread import EasyThread

logger = logging.getLogger(__name__)

class MQTT(EasyThread):
    """
    MQTT客户端封装类，继承自EasyThread
    支持自动重连、心跳检测、消息回调等功能
    """
    
    def __init__(self, option: Dict[str, Any]):
        super().__init__()
        self.broker = option.get("broker", "broker.emqx.io")
        self.port = option.get("port", 1883)
        self.topic = option.get("topic", "user/test/mqtt")
        self.username = option.get("username", None)
        self.password = option.get("password", None)
        self.keepalive = option.get("keepalive", 60)
        self.reconnect_delay = option.get("reconnect_delay", 5)
        self.callback = option.get("callback", None)

        self.client_id = f'mqtt_Qt_{generate(size=6)}'
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        self._connection_count = 0

        if callable(self.callback):
            self.response.connect(self.callback)
        
    def _on_connect(self, client: mqtt.Client, userdata, flags, rc: int):
        """连接回调函数"""
        self.is_connected = True
        self._connection_count += 1
        if rc == 0:
            logger.info(f"Connected to MQTT Broker! (Connection #{self._connection_count})")
            self._emit({"status": 0, "msg": "Connected to MQTT Broker!", "connection_count": self._connection_count})
        else:
            logger.error(f"Failed to connect, return code {rc}")
            self._emit({"status": -1, "msg": f"Connection failed with code {rc}"})
            self.is_connected = False
            # 尝试重连
            time.sleep(self.reconnect_delay)
            try:
                self.client.reconnect()
            except Exception as e:
                logger.error(f"Reconnect failed: {e}")

    def _on_message(self, client: mqtt.Client, userdata, msg):
        """消息接收回调函数"""
        try:
            payload = msg.payload.decode('utf-8')
            logger.debug(f"Received message from {msg.topic}: {payload[:100]}...")
            self._emit({
                "status": 1,
                "msg": payload,
                "topic": msg.topic,
                "qos": msg.qos
            })
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _emit(self, data: Dict[str, Any]) -> None:
        """发送响应"""
        self.response.emit(data)

    def connect_mqtt(self) -> bool:
        """建立MQTT连接"""
        try:
            client = mqtt.Client(
                client_id=self.client_id,
                protocol=mqtt.MQTTv5,
                transport="tcp"
            )
            
            # 设置认证信息
            if self.username and self.password:
                client.username_pw_set(self.username, self.password)
            
            # 设置回调
            client.on_connect = self._on_connect
            client.on_message = self._on_message
            
            # 设置连接选项
            client.connect(self.broker, self.port, keepalive=self.keepalive)
            
            self.client = client
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MQTT client: {e}")
            self._emit({"status": -1, "msg": f"Client initialization failed: {str(e)}"})
            return False

    def publish(self, msg: str, topic: str = None, qos: int = 0) -> bool:
        """发布消息到指定主题"""
        if not self.client or not self.is_connected:
            logger.warning("Cannot publish: Not connected to MQTT broker")
            self._emit({"status": -1, "msg": "Not connected to MQTT broker"})
            return False
            
        try:
            target_topic = topic or self.topic
            payload_data = {
                "client_id": self.client_id,
                "timestamp": time.time(),
                "payload": msg
            }
            result = self.client.publish(target_topic, json.dumps(payload_data), qos=qos)
            
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published message to {target_topic}")
                self._emit({"status": 0, "msg": f"Sent to {target_topic}"})
                return True
            else:
                logger.error(f"Failed to publish to {target_topic}, error code: {result[0]}")
                self._emit({"status": -1, "msg": f"Publish failed with code {result[0]}"})
                return False
                
        except Exception as e:
            logger.error(f"Publish exception: {e}")
            self._emit({"status": -1, "msg": f"Exception: {str(e)}"})
            return False

    def subscribe(self) -> bool:
        """订阅主题"""
        if not self.client or not self.is_connected:
            logger.warning("Cannot subscribe: Not connected to MQTT broker")
            return False
            
        try:
            result, mid = self.client.subscribe(self.topic, qos=1)
            if result == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Subscribed to topic: {self.topic}")
                return True
            else:
                logger.error(f"Failed to subscribe, error code: {result}")
                return False
        except Exception as e:
            logger.error(f"Subscribe exception: {e}")
            return False

    def reconnect(self) -> bool:
        """手动重连"""
        if self.client:
            try:
                self.client.reconnect()
                return True
            except Exception as e:
                logger.error(f"Reconnect failed: {e}")
                return False
        return False

    def destroy(self, param=None) -> None:
        """清理资源"""
        logger.info("Destroying MQTT instance")
        if self.client:
            try:
                self.client.disconnect()
                self.client.loop_stop()
                self.client = None
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
        self.is_connected = False
        self.callback = None
        logger.info(f"MQTT instance destroyed. Param: {param}")

    def run(self) -> None:
        """线程启动入口"""
        logger.info(f"Starting MQTT thread for {self.client_id}")
        
        if not self.connect_mqtt():
            logger.error("Failed to start MQTT connection")
            return
            
        # 等待连接确认
        time.sleep(1)
        
        if self.is_connected:
            self.subscribe()
            
        try:
            self.client.loop_start()  # 使用loop_start异步运行
            while self.is_alive():
                time.sleep(1)
            self.destroy()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.destroy()
        except Exception as e:
            logger.error(f"Run loop error: {e}")
            self.destroy()
        finally:
            logger.info("MQTT thread stopped")
