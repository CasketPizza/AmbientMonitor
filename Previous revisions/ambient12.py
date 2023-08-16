import win32gui
import win32ui
import win32con
import cv2
import numpy as np
import configparser

# Initial settings
initial_contrast = 1.0
initial_brightness = 0
initial_image_scale_factor = 0.1
initial_blur_amount = 99

# Global variables for contrast level, brightness level, step, image scale factor, blur amount
contrast_level = initial_contrast
brightness_level = initial_brightness
adjustment_step = 0.1
image_scale_factor = initial_image_scale_factor
blur_amount = initial_blur_amount

key_states = {ord('1'): False, ord('2'): False, ord('3'): False, ord('4'): False, ord('5'): False, ord('6'): False, ord('7'): False, ord('8'): False, ord('9'): False, ord('0'): False}

# Load saved settings from config file
config = configparser.ConfigParser()
config.read('settings.ini')

if 'Settings' in config:
    contrast_level = config.getfloat('Settings', 'contrast')
    brightness_level = config.getfloat('Settings', 'brightness')
    image_scale_factor = config.getfloat('Settings', 'scale_factor')
    blur_amount = config.getint('Settings', 'blur_amount')

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

# Restores initial settings
def reset_settings():
    global contrast_level, brightness_level, image_scale_factor, blur_amount
    contrast_level = initial_contrast
    brightness_level = initial_brightness
    image_scale_factor = initial_image_scale_factor
    blur_amount = initial_blur_amount

def cycle_capture_mode(mode):
    if mode == 'full':
        return 'left'
    elif mode == 'left':
        return 'right'
    elif mode == 'right':
        return 'full'
    else:
        return 'full'

capture_mode = 'full'

def adjust_contrast(image, contrast_value):
    # Adjust contrast using the current contrast_level
    adjusted_image = cv2.convertScaleAbs(image, alpha=contrast_value, beta=0)
    return adjusted_image

def adjust_brightness(image, brightness_value):
    # Convert image to HLS color space
    hls_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    
    # Adjust brightness in HLS color space
    hls_image[:,:,1] = np.clip(hls_image[:,:,1] + brightness_value, 0, 255)
    
    # Convert back to BGR color space
    adjusted_image = cv2.cvtColor(hls_image, cv2.COLOR_HLS2BGR)
    
    return adjusted_image

def main():
    global contrast_level, brightness_level, image_scale_factor, blur_amount, capture_mode  # Use the global variables
    global key_states

    hwnd = win32gui.GetDesktopWindow()

    cv2.namedWindow("Display", cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)
    cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    is_fullscreen = False
    is_topmost = False

    while True:
        screenshot = capture_screen(hwnd)

        if capture_mode == 'left':
            screenshot = screenshot[:, :screenshot.shape[1]//2]
        elif capture_mode == 'right':
            screenshot = screenshot[:, screenshot.shape[1]//2:]

        flipped_screenshot = cv2.flip(screenshot, 1)

        if flipped_screenshot is not None:
            resized_screenshot = cv2.resize(flipped_screenshot, None, fx=image_scale_factor, fy=image_scale_factor)
            
            # Apply combined contrast and brightness adjustment
            contrasted_screenshot = adjust_contrast(resized_screenshot, contrast_level)
            adjusted_screenshot = adjust_brightness(contrasted_screenshot, brightness_level)
            
            # Apply Gaussian blur with adjustable blur amount
            blurred_screenshot = cv2.GaussianBlur(adjusted_screenshot, (blur_amount, blur_amount), 0)
            
            cv2.imshow("Display", blurred_screenshot)

        key = cv2.waitKey(1)

        if key == 27:
            break
        elif key == ord(' '):
            if not is_fullscreen:
                cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.setWindowProperty("Display", cv2.WND_PROP_TOPMOST, 1)  # Set as topmost window
                is_topmost = True
            else:
                cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                cv2.setWindowProperty("Display", cv2.WND_PROP_TOPMOST, 0)  # Unset topmost window
                is_topmost = False
            is_fullscreen = not is_fullscreen
        elif key == 13:  # Enter key
            capture_mode = cycle_capture_mode(capture_mode)

        for adjust_key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9'), ord('0')]:
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
                    brightness_level -= adjustment_step * 50
                elif key == ord('2'):
                    brightness_level += adjustment_step * 50
                elif key == ord('5'):
                    image_scale_factor = max(image_scale_factor - 0.01, 0.01)
                elif key == ord('6'):
                    image_scale_factor = min(image_scale_factor + 0.01, 1.0)
                elif key == ord('7'):
                    blur_amount = max(blur_amount - 10, 1)
                elif key == ord('8'):
                    blur_amount = min(blur_amount + 10, 999)
                elif key == ord('9'):
                    save_settings()
                elif key == ord('0'):
                    reset_settings()

        if cv2.getWindowProperty("Display", cv2.WND_PROP_ASPECT_RATIO) == -1:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()