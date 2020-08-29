from background_task import background
import datetime
from django.utils.timezone import make_aware


@background()
def demo_task():
    print("Starting process_tick")
