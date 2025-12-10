import cv2
from flask import Flask, Response, render_template_string

app = Flask(__name__)

# Kamera öffnen (0 = erste Webcam, kann je nach System anders sein)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Kamera konnte nicht geöffnet werden")


def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Hier kannst du das Bild noch bearbeiten (z.B. cv2.cvtColor, Zeichnungen, etc.)

        # Frame in JPEG encoden
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        jpg_bytes = buffer.tobytes()

        # MJPEG-Chunk erzeugen
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + jpg_bytes + b'\r\n'
        )

        

@app.route("/")
def index():
    # einfache HTML-Seite mit dem Stream
    html = """
    <!doctype html>
    <title>OpenCV Stream</title>
    <h1>Live Stream</h1>
    <img src="{{ url_for('video_feed') }}" />
    """
    return render_template_string(html)


@app.route("/video_feed")
def video_feed():
    # Endpoint, den du überall als <img src="..."> einbinden kannst
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    try:
        # unter Windows aufpassen: threaded=True ist meistens ok
        app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
    finally:
        cap.release()
