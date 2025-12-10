import cv2

class Cam:
  def __init__(self, cam: int, width: int, height: int):
    self.frame = None
    # Use CAP_DSHOW for Windows compatibility
    self.cap = cv2.VideoCapture(cam, cv2.CAP_DSHOW)
    if not self.cap.isOpened():
      raise RuntimeError("error opening cam")
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    self.warmup()

  def quit(self) -> None:
    self.cap.release()

  def warmup(self) -> None:
    for _ in range(5):
      self.cap.read()

  def capture(self):
    ret, self.frame = self.cap.read()
    return self.frame

  def save(self, path: str) -> None:
    cv2.imwrite(path, self.frame)