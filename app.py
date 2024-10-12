import streamlit as st
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import threading
import json

# InfluxDB configuration
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "your_influxdb_token"
INFLUXDB_ORG = "your_org"
INFLUXDB_BUCKET = "your_bucket"

# MQTT configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "your/mqtt/topic"

# Initialize InfluxDB client
influxdb_client = influxdb_client.InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)

# Initialize MQTT client
mqtt_client = mqtt.Client()

# Streamlit app
def main():
    st.title("Data Visualization Dashboard")

    # InfluxDB Query and Visualization
    st.header("Historical Data from InfluxDB")
    query = '''
    from(bucket:"your_bucket")
      |> range(start: -1h)
      |> filter(fn: (r) => r._measurement == "your_measurement")
      |> aggregateWindow(every: 1m, fn: mean)
    '''
    result = query_influxdb(query)
    if result:
        st.line_chart(result)

    # MQTT Streaming Data Visualization
    st.header("Live Streaming Data from MQTT")
    mqtt_data = st.empty()

    # Start MQTT client in a separate thread
    threading.Thread(target=start_mqtt_client, daemon=True).start()

    # Update MQTT data periodically
    while True:
        mqtt_data.line_chart(get_mqtt_data())
        st.experimental_rerun()

def query_influxdb(query):
    query_api = influxdb_client.query_api()
    result = query_api.query_data_frame(query)
    if not result.empty:
        result.set_index('_time', inplace=True)
        return result[['_value']]
    return None

def on_message(client, userdata, message):
    payload = json.loads(message.payload.decode())
    # Process and store MQTT data as needed
    # For simplicity, we'll just append it to a global list
    global mqtt_data_list
    mqtt_data_list.append(payload)

def start_mqtt_client():
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.subscribe(MQTT_TOPIC)
    mqtt_client.loop_forever()

def get_mqtt_data():
    global mqtt_data_list
    df = pd.DataFrame(mqtt_data_list)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    return df

if __name__ == "__main__":
    mqtt_data_list = []
    main()