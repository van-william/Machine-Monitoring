import streamlit as st
import paho.mqtt.client as mqtt
import pandas as pd
import plotly.graph_objs as go
from influxdb_client_3 import InfluxDBClient3
import os
import time
import threading

# InfluxDB configuration
INFLUXDB_URL = "https://us-east-1-1.aws.cloud2.influxdata.com/"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = "dd7895c825a7c36a"
INFLUXDB_BUCKET = "machine_monitoring"

# MQTT configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "test_fan"

# Global variables
data_points = []
MAX_DATA_POINTS = 100

# Initialize InfluxDB client
influx_client = InfluxDBClient3(host=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)


def query_influxdb(query):
    table = influx_client.query(query=query, database="machine_monitoring", language="sql")
    df = table.to_pandas().sort_values(by="time")
    return df

def main():
    st.title("Data Visualization Dashboard")

    # InfluxDB Query and Visualization
    st.header("Historical Data from InfluxDB")
    query = '''
    SELECT *
    FROM "fan"
    WHERE time >= now() - interval '2 week'
    '''
    df = query_influxdb(query)
    if not df.empty:
        st.line_chart(data=df, x='time', y='current')
    else:
        st.write("No historical data available for the past week.")

if __name__ == "__main__":
    main()