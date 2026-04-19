import os
from queue import Queue
import threading

from constant import TEMP_DIR
from scanner.camera_capture import camera_loop
from scanner.processing import process_cards

os.makedirs(TEMP_DIR, exist_ok=True)

if __name__ == "__main__":
    card_queue = Queue(maxsize=1)
    stop_event = threading.Event()

    camera_thread = threading.Thread(
        target=camera_loop,
        args=(card_queue, stop_event),
        daemon=True
    )

    processing_thread = threading.Thread(
        target=process_cards,
        args=(card_queue, stop_event),
        daemon=True
    )

    camera_thread.start()
    processing_thread.start()

    camera_thread.join()
    stop_event.set()
