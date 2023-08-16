import win32gui
import win32ui
import win32con
import win32api
import cv2
import numpy as np

def capture_screen(hwnd, left, top, right, bot):
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
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    half_width = screen_width // 2

    cv2.namedWindow("Display", cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)  # Create resizable window

    cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    is_fullscreen = False
    is_left_side = True

    while True:
        if is_left_side:
            screenshot = capture_screen(hwnd, 0, 0, half_width, screen_height)
        else:
            screenshot = capture_screen(hwnd, half_width, 0, screen_width, screen_height)
        
        flipped_screenshot = cv2.flip(screenshot, 1)

        if flipped_screenshot is not None:
            blurred_screenshot = flipped_screenshot.copy()  # Make a copy of the original image
            for _ in range(9):  # Apply blur three times (you can adjust the number)
                blurred_screenshot = cv2.GaussianBlur(blurred_screenshot, (99, 99), 0)
            
            gradient = np.zeros_like(blurred_screenshot)
            gradient[:, :gradient.shape[1]//2] = [0, 0, 0, 0]
            gradient[:, gradient.shape[1]//2:] = [0, 0, 0, 255]
            
            blended_image = cv2.addWeighted(blurred_screenshot, 0.5, gradient, 0.5, 0)
            
            cv2.imshow("Display", blended_image)

        key = cv2.waitKey(1)

        if key == 27:  # Escape key
            break
        elif key == 13:  # Enter key
            is_left_side = not is_left_side
        elif key == ord(' '):  # Toggle fullscreen on spacebar
            if not is_fullscreen:
                cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            is_fullscreen = not is_fullscreen

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
