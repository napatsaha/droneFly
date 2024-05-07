import threading
import time
import logging
import sys, os
import signal
from _thread import interrupt_main



class MainTimer:
    def __init__(self, duration):
        self.duration = duration

    def start(self):
        self.initial = time.time()

    def is_valid(self) -> bool:
        valid = time.time() - self.initial < self.duration
        return valid

class ExitCommand(Exception):
    pass

def threadf():
    logging.info("Thread start")
    time.sleep(THREAD_DURATION)
    logging.info("Thread Finished")

    signal.raise_signal(signal.SIGTERM)
    # interrupt_main()


def signal_handler(signalnum, frame):
    logging.info("Signal Called")

    raise ExitCommand()

MAIN_DURATION = 10
MAIN_FPS = 20
THREAD_DURATION = 5

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s -- %(threadName)s -- %(msg)s",
                    datefmt="%H-%M-%S")


signal.signal(signal.SIGTERM, signal_handler)
break_thread = threading.Thread(target=threadf, daemon=False)
main_timer = MainTimer(duration=MAIN_DURATION)


try:
    logging.info("Main Start")
    main_timer.start()
    break_thread.start()

    while main_timer.is_valid():
        time.sleep(1/MAIN_FPS)

    logging.info("Main Finished")

except ExitCommand:
    logging.info("Main Interrupted")
except KeyboardInterrupt:
    logging.info("Keyboard Interrupted")

finally:

    logging.info("END")