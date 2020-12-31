from background_task import background


@background()
def demo_task():
    print("Starting process_tick")
