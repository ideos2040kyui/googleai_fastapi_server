import requests
import time
import logging
from datetime import datetime

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

HEALTH_CHECK_URL = "https://googleai-fastapi-server.onrender.com/health"
INTERVAL_SECONDS = 10 * 60  # 10分

def health_check():
    """ヘルスチェックを実行"""
    try:
        response = requests.get(HEALTH_CHECK_URL, timeout=10)
        if response.status_code == 200:
            logger.info(f"✓ Health check OK: {response.json()}")
        else:
            logger.warning(f"✗ Health check failed with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Health check error: {e}")
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    logger.info("Starting health check monitor...")
    logger.info(f"Checking {HEALTH_CHECK_URL} every {INTERVAL_SECONDS // 60} minutes")
    
    while True:
        health_check()
        logger.info(f"Next check at: {datetime.fromtimestamp(time.time() + INTERVAL_SECONDS)}")
        time.sleep(INTERVAL_SECONDS)
