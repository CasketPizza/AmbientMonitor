import win32gui
import win32ui
import win32con
import cv2
import numpy as np

def capture_screen(hwnd):
    left, top, right, bot = win32gui.GetClientRect(hwnd)
    width = right - left
    height = bot - top

    hwindc = win32gui.GetWindowDC(hwnd)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bitmap)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)

    bmpinfo = bitmap.GetInfo()
    bmpstr = bitmap.GetBitmapBits(True)
    img = np.frombuffer(bmpstr, dtype='uint8')
    img = img.reshape((height, width, 4))

    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwindc)
    win32gui.DeleteObject(bitmap.GetHandle())

    return img

def main():
    hwnd = win32gui.GetDesktopWindow()

    cv2.namedWindow("Display", cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)  # Create resizable window

    cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    is_fullscreen = False

    while True:
        screenshot = capture_screen(hwnd)
        flipped_screenshot = cv2.flip(screenshot, 1)

        if flipped_screenshot is not None:
            cv2.imshow("Display", flipped_screenshot)

        key = cv2.waitKey(1)

        if cv2.getWindowProperty("Display", cv2.WND_PROP_ASPECT_RATIO) != -1:
            if key == 27:  # Escape key
                break
            elif key == ord(' '):  # Toggle fullscreen on spacebar
                if not is_fullscreen:
                    cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                is_fullscreen = not is_fullscreen

        if key == 27 or cv2.getWindowProperty("Display", cv2.WND_PROP_ASPECT_RATIO) == -1:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
