"""Pump Monitor Constants"""

# Redis keys
NEW_TOKEN_QUEUE_KEY = "new_tokens"
PROCESSING_QUEUE_KEY = "processing_tokens"  # 处理中的消息队列
FAILED_TOKEN_QUEUE_KEY = "failed_tokens"

# Control signals
STOP_SIGNAL = "STOP"
