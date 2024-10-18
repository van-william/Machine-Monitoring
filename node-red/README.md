---
title: Machine Monitoring
emoji: 📈
colorTo: gray
sdk: gradio
sdk_version: 4.44.1
app_file: gradio/app.py
pinned: true
---
## Node Red Integrations

## MQTT
- Here, I used the native MQTT connector to publish messages to my MQTT broker (In this case, HiveMQ)

## InfluxDB
- For InfluxDB integrations, you can integrate via Telegraf and stream the MQTT messages in via Telegraf and parse to InfluxDB (This does not require anything on the Node Red side)
- You can also write data from Node-Red to InfluxDB via the REST API or via the InfluxDB Node-Red Modules. linked below:
https://flows.nodered.org/node/node-red-contrib-influxdb

