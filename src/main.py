from cam import Cam
import time
import cv2
import numpy as np

# Kamera-Objekt: index=0, Bildgröße 500x500 Pixel
cam = Cam(0, 1024, 1280)

# Parameter für die Änderungs-Erkennung
DIFF_THRESHOLD = 40      # Schwellwert für Pixeländerung

if __name__ == "__main__":

    # --- 1. REFERENZBILD HOLEN ---

    reference_frame = cam.capture()
    reference_frame_gray = cv2.cvtColor(reference_frame, cv2.COLOR_BGR2GRAY)

    print("Referenz gesetzt")


    # --- 2. HAUPTSCHLEIFE ---

    while True:
        frame = cam.capture()
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 2.1 Differenz zur Referenz
        diff = cv2.absdiff(reference_frame_gray, frame_gray)

        # 2.2 leicht glätten -> weniger Rauschen, aber nicht zu viel Detailverlust
        diff_blur = cv2.GaussianBlur(diff, (5, 5), 0)

        # 2.3 Threshold -> stark veränderte Pixel = weiß
        _, thresh = cv2.threshold(diff_blur, DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)

        # 2.4 leichte Morphology, um vereinzelte Pixelpunkte zu entfernen
        kernel = np.ones((2, 2), np.uint8)
        thresh_clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

        roi = thresh_clean[520:270, 1200:840]
        count = cv2.countNonZero(thresh_clean)
        print(count)
        if count > 30:
            countours, _ = cv2.findContours(thresh_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in countours:
                cv2.drawContours(frame, [c], -1, (0, 0, 255), 2)
            print("hit!")

        # --- 4. DEBUG-ANZEIGE ---

        cv2.rectangle(frame, (520, 270), (1200, 840), (0, 255, 0), 2)

        cv2.imshow("Live", frame)
        # cv2.imshow("Diff", diff)
        # cv2.imshow("Diff Blurred", diff_blur)
        # cv2.imshow("Threshold RAW", thresh)
        cv2.imshow("Threshold Clean", thresh_clean)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        time.sleep(.5)

