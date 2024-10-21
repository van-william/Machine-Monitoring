---
title: Machine Monitoring
emoji: 🏭
colorTo: blue
sdk: gradio
sdk_version: 4.44.1
app_file: gradio/app.py
pinned: true
---

# Machine Monitoring Proof of Concept
This repo includes a variety of experiments with using Node-Red, Tulip (Tulip Edge MC and App Player), MQTT, InfluxDB, Gradio, and other tools to build a simple machine monitoring workflow.

## Tulip
* Edge MC is used alongside the Machine Kit to process sensor data and write to Tulip and other cloud destinations via Node-Red
* Tulip Apps such as Machine Monitoring Terminal were used as examples of extending sensor data to operators

## InfluxDB
* InfluxDB was used as a cloud time series database for storing sensor data
* This data was then queried (Either from Tulip or from Gradio web apps) and visualized

## Gradio
* A simple web app was built on Hugging Face Gradio (Hosted on Hugging Face Spaces) to showcase additional methods of simple web apps for visualizing sensor data
* Link to web app: https://huggingface.co/spaces/van-william/machine_monitoring