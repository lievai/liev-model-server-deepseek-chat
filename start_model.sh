#!/bin/bash
echo "Starting model..."
nohup python waitress_model_deepseek_chat.py > ./logs/waitress_model_deepseek_chat.log 2>&1 &
echo "Model started."
