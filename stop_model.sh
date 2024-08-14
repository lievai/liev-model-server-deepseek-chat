#!/bin/bash
echo "Stopping model..."
pkill -f "python waitress_model_deepseek_chat.py"
echo "Model stopped."
