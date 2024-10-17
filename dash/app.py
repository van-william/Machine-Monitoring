import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from influxdb_client_3 import InfluxDBClient3
from datetime import datetime
import os
import paho.mqtt.client as mqtt
import threading
import json

# Global variables
MAX_DATA_POINTS = 100  # Increased for better visibility
MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPIC = "test_fan/current"
mqtt_data = []  # Global list to store incoming MQTT messages

# InfluxDB configuration
INFLUXDB_URL = "https://us-east-1-1.aws.cloud2.influxdata.com/"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = "dd7895c825a7c36a"
INFLUXDB_BUCKET = "machine_monitoring"
influx_client = InfluxDBClient3(host=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG, database="machine_monitoring")

# MQTT Client setup
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    global mqtt_data
    try:
        # Parse the message payload
        payload = float(msg.payload.decode('utf-8'))
        new_point = {
            "timestamp": msg.timestamp,
            "current": payload,
            "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        mqtt_data.append(new_point)
        if len(mqtt_data) > MAX_DATA_POINTS:
            mqtt_data = mqtt_data[-MAX_DATA_POINTS:]
        print(f"Received MQTT data: {new_point}")
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def start_mqtt_client():
    try:
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_BROKER, 1883, 60)
        client.loop_start()  # Start the MQTT client in a separate thread
    except Exception as e:
        print(f"Error starting MQTT client: {e}")

# Start MQTT client in a separate thread
mqtt_thread = threading.Thread(target=start_mqtt_client)
mqtt_thread.daemon = True
mqtt_thread.start()

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("MQTT and InfluxDB Data Visualization"),
    html.Div([
        html.H2("MQTT Data Visualization"),
        html.P(f"Listening to MQTT topic: {MQTT_TOPIC}"),
        dcc.Graph(id='mqtt-chart'),
        html.Div(id='mqtt-debug'),  # Add a debug div
        dcc.Interval(id='mqtt-interval', interval=1000, n_intervals=0)  # Add interval for regular updates
    ]),
    html.Div([
        html.H2("InfluxDB Data Visualization"),
        dcc.Graph(id='influxdb-chart'),
        dcc.Interval(id='influxdb-interval', interval=300000, n_intervals=0)  # Update every 5 minutes
    ])
])

# Callback for MQTT chart and debug info
@app.callback(
    [Output('mqtt-chart', 'figure'),
     Output('mqtt-debug', 'children')],
    [Input('mqtt-interval', 'n_intervals')]
)
def update_mqtt_chart(n):
    global mqtt_data
    if not mqtt_data:
        return dash.no_update, "No MQTT data received yet."
    
    df = pd.DataFrame(mqtt_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['current'],
        mode='lines+markers'
    ))
    fig.update_layout(
        title="MQTT Data Visualization",
        xaxis_title="Timestamp",
        yaxis_title="Current"
    )
    
    debug_info = f"Last MQTT data point: {mqtt_data[-1]}"
    return fig, debug_info

# Callback for InfluxDB chart
@app.callback(
    Output('influxdb-chart', 'figure'),
    Input('influxdb-interval', 'n_intervals')
)
def update_influxdb_chart(n):
    try:
        df = query_influxdb()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['time'],
            y=df['current'],
            mode='lines+markers'
        ))
        fig.update_layout(
            title="InfluxDB Data Visualization",
            xaxis_title="Time",
            yaxis_title="Current"
        )
        return fig
    except Exception as e:
        print(f"Error querying InfluxDB: {e}")
        return dash.no_update

def query_influxdb():
    try:
        query = '''
        SELECT *
        FROM "fan"
        WHERE time >= now() - interval '2 week'
        '''
        table = influx_client.query(query=query, language="sql")
        df = table.to_pandas().sort_values(by="time")
        return df
    except Exception as e:
        print(f"Error querying InfluxDB: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

if __name__ == '__main__':
    app.run_server(debug=True)
