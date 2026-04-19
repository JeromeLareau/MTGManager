import cv2

from scanner.card_detect import detect_card, warp_card

def camera_loop(card_queue, stop_event):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Could not open camera")

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()
        contour = detect_card(frame)

        if contour is not None:
            cv2.drawContours(display, [contour], -1, (0, 255, 0), 3)

            if card_queue.empty():
                card = warp_card(frame, contour)
                card_queue.put(card)

        cv2.imshow("Live Scan", display)

        if cv2.waitKey(1) == 27:  # ESC
            stop_event.set()
            break

    cap.release()
    cv2.destroyAllWindows()