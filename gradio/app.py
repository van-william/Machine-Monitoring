import gradio as gr
import paho.mqtt.client as mqtt
import pandas as pd
import time
from influxdb_client_3 import InfluxDBClient3
import threading
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import os

# Global variables
data_points = []
MAX_DATA_POINTS = 10

# InfluxDB configuration
INFLUXDB_URL = "https://us-east-1-1.aws.cloud2.influxdata.com/"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = "dd7895c825a7c36a"
INFLUXDB_BUCKET = "machine_monitoring"
influx_client = InfluxDBClient3(host=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG,database="machine_monitoring")

query = '''
    SELECT *
    FROM "fan"
    WHERE time >= now() - interval '2 week'
    '''

# MQTT setup
MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPIC = "test_fan/current"

def query_influxdb(query):
    table = influx_client.query(query=query, language="sql")
    df = table.to_pandas().sort_values(by="time")
    return df

def query_influxdb_gr():
    query = '''
    SELECT *
    FROM "fan"
    WHERE time >= now() - interval '2 week'
    '''
    table = influx_client.query(query=query, language="sql")
    df = table.to_pandas().sort_values(by="time")
    return df



# Callback when a message is received from the server
def on_message(client, userdata, message):
    global data_points
    try:
        payload = message.payload.decode()
        value = float(payload)  # Assume the payload is a single float value
        data_points.append({"timestamp": time.time(), "current": value, "datetime": datetime.now().strftime('%H:%M:%S')})
        # Keep only the last MAX_DATA_POINTS
        
        if len(data_points) > MAX_DATA_POINTS:
            data_points.pop(0)  # Remove the oldest data point
    except ValueError:
        print(f"Received invalid payload: {payload}")

# Set up MQTT client
client = mqtt.Client(client_id="gradio_client", protocol=mqtt.MQTTv311)
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.subscribe(MQTT_TOPIC)

# Start MQTT loop in a separate thread
mqtt_thread = threading.Thread(target=client.loop_start)
mqtt_thread.start()

# Gradio components
def update_mqtt_live_data():
    # Convert timestamps to formatted time strings
    df = pd.DataFrame(data_points)
    return df

# Gradio components
def update_chart():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[point["timestamp"] for point in data_points],
        y=[point["value"] for point in data_points],
        mode='lines+markers'
    ))
    fig.update_layout(
        title="MQTT Data Visualization",
        xaxis_title="Timestamp",
        yaxis_title="Value"
    )
    return fig

with gr.Blocks() as app:
    gr.Markdown("# MQTT Data Visualization")
    gr.Markdown(f"Listening to MQTT topic: {MQTT_TOPIC}")

    line_plot = gr.LinePlot(update_mqtt_live_data, label="MQTT", x="datetime", y="current", every=1)



    #plotly_plot = gr.Plot(make_figure(update_data), label="Plotly Chart", every=1)

    gr.Markdown("# InfluxDB Data Visualization")
    line_plot = gr.LinePlot(query_influxdb_gr, label="InfluxDB", x="time", y="current", every=300)

    gr.Markdown("# Plotly Data Visualization")
    plot = gr.Plot(update_chart, every=1)
    app.load(update_chart, None, plot)
    

# Launch the app
app.launch()
