from flask import Flask, Response, render_template_string
import cv2
import numpy as np
from cam import Cam

app = Flask(__name__)

# Kamera-Objekt: index=0, Bildgröße 1024x1280 Pixel
cam = Cam(0, 1024, 1280)

# Parameter für die Änderungs-Erkennung
DIFF_THRESHOLD = 40      # Schwellwert für Pixeländerung

# Referenzbild holen
reference_frame = cam.capture()
reference_frame_gray = cv2.cvtColor(reference_frame, cv2.COLOR_BGR2GRAY)


def generate_frames():
    """Generator, der kontinuierlich JPEG-Frames mit Kreisen liefert."""
    while True:
        frame = cam.capture()
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Differenz zur Referenz
        diff = cv2.absdiff(reference_frame_gray, frame_gray)
        diff_blur = cv2.GaussianBlur(diff, (5, 5), 0)
        _, thresh = cv2.threshold(diff_blur, DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)
        kernel = np.ones((2, 2), np.uint8)
        thresh_clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

        count = cv2.countNonZero(thresh_clean)
        if count > 30:
            countours, _ = cv2.findContours(thresh_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in countours:
                cv2.drawContours(frame, [c], -1, (0, 0, 255), 2)

        # Rechteck für ROI (optional, falls gewünscht)
        cv2.rectangle(frame, (520, 270), (1200, 840), (0, 255, 0), 2)

        # Frame nach JPEG encoden
        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            continue
        jpg_bytes = buffer.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + jpg_bytes + b"\r\n"
        )


@app.route("/")
def index():
    # Mini-HTML-Seite, die den Stream als <img> anzeigt
    html = """
    <!doctype html>
    <html>
      <head>
        <title>OpenCV Live Stream</title>
      </head>
      <body>
        <h1>Live Stream</h1>
        <img src="{{ url_for('video_feed') }}" />
      </body>
    </html>
    """
    return render_template_string(html)


@app.route("/video_feed")
def video_feed():
    # Dieser Endpoint ist dein eigentlicher Stream
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    finally:
        cam.quit()
        cv2.destroyAllWindows()

