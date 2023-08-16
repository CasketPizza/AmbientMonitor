import win32gui
import win32ui
import win32con
import cv2
import numpy as np

# Global variable to store contrast level
contrast_level = 1.0
brightness_level = 0
adjustment_step =0.1

key_states = {ord('1'): False, ord('2'): False, ord('3'): False, ord('4'): False}

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
    global contrast_level, brightness_level  # Use the global contrast_level and brightness_level variables
    global key_states

    hwnd = win32gui.GetDesktopWindow()

    cv2.namedWindow("Display", cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)
    cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    is_fullscreen = False

    while True:
        screenshot = capture_screen(hwnd)
        flipped_screenshot = cv2.flip(screenshot, 1)

        if flipped_screenshot is not None:
            resized_screenshot = cv2.resize(flipped_screenshot, None, fx=0.1, fy=0.1)  # Reduce image size
            blurred_screenshot = cv2.GaussianBlur(resized_screenshot, (99, 99), 0)
            
            # Adjust contrast using the current contrast_level
            contrasted_screenshot = cv2.convertScaleAbs(blurred_screenshot, alpha=contrast_level, beta=brightness_level)
            
            cv2.imshow("Display", contrasted_screenshot)

        key = cv2.waitKey(1)

        if key == 27:
            break
        elif key == ord(' '):
            if not is_fullscreen:
                cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            is_fullscreen = not is_fullscreen

        for adjust_key in [ord('1'), ord('2'), ord('3'), ord('4')]:
            if key_states[adjust_key] and key != adjust_key:
                key_states[adjust_key] = False

        if key in key_states:
            if not key_states[key]:
                key_states[key] = True
                if key == ord('4'):
                    contrast_level += adjustment_step
                elif key == ord('3'):
                    contrast_level -= adjustment_step
                elif key == ord('1'):
                    brightness_level -= 10
                elif key == ord('2'):
                    brightness_level += 10

        if cv2.getWindowProperty("Display", cv2.WND_PROP_ASPECT_RATIO) == -1:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()