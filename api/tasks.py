from celery import shared_task
from api.utils.report_utils import ReportUtils
import logging

logger = logging.getLogger(__name__)


@shared_task(name="api.tasks.scheduled_auto_expire")
def scheduled_auto_expire():
    result = ReportUtils.auto_expire_items()
    logger.info(
        f"[AutoExpire] executed_at={result['executed_at']} "
        f"expired_count={result['expired_count']}"
    )
    return result