import socket
import time
import paho.mqtt.client as mqtt
import os

TCP_HOST = os.getenv("tcp_host", "192.168.178.110")
TCP_PORT = int(os.getenv("tcp_port", 9999))
MQTT_HOST = os.getenv("mqtt_host", "192.168.178.23")
MQTT_PORT = int(os.getenv("mqtt_port", 1883))
MQTT_USER = os.getenv("mqtt_user", "")
MQTT_PASS = os.getenv("mqtt_password", "")
MQTT_TOPIC = os.getenv("mqtt_topic", "junctek/data")

def parse_r50(data_line):
    if not data_line.startswith(":r50="):
        return None
    try:
        parts = data_line.strip()[5:].split(",")
        return {
            "voltage": int(parts[0]) / 100,
            "current": int(parts[1]) / 100,
            "ah_remaining": int(parts[2]) / 1000,
            "ah_used": int(parts[3]) / 100,
            "wh_remaining": int(parts[4]) / 100,
            "runtime_s": int(parts[5]),
            "temperature": int(parts[6]) - 100,
            "watts": int(parts[7]) / 100,
            "relay": int(parts[8]),
            "direction": int(parts[9]),
            "life_mins": int(parts[10]),
            "internal_resistance": int(parts[11]) / 100,
        }
    except Exception:
        return None

def main():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
    mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
    mqtt_client.loop_start()

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((TCP_HOST, TCP_PORT))
                s.settimeout(5)
                buffer = ""
                while True:
                    chunk = s.recv(1024).decode(errors='ignore')
                    buffer += chunk
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        parsed = parse_r50(line)
                        if parsed:
                            for key, val in parsed.items():
                                mqtt_client.publish(f"{MQTT_TOPIC}/{key}", val)
                            print("Gesendet:", parsed)
        except Exception as e:
            print(f"Fehler: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
