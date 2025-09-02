import time
import threading
import ctypes
from ctypes import wintypes
import sys
import os
import winreg
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

# Funktion för att hitta rätt sökväg för filer när programmet körs som .exe
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Windows API strukturer och helper för GetLastInputInfo ---
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD),
    ]

def get_idle_msecs():
    li = LASTINPUTINFO()
    li.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(li)):
        return 0
    tick = ctypes.windll.kernel32.GetTickCount()
    if tick >= li.dwTime:
        return tick - li.dwTime
    else:
        return (0xFFFFFFFF - li.dwTime) + tick

# --- Structs för SendInput (tangent och mus) ---
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
               ("dy", ctypes.c_long),
               ("mouseData", ctypes.c_ulong),
               ("dwFlags", ctypes.c_ulong),
               ("time", ctypes.c_ulong),
               ("dwExtraInfo", ctypes.c_void_p)]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_void_p)]

class INPUT_union(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]

class INPUT(ctypes.Structure):
    _anonymous_ = ("union",)
    _fields_ = [("type", wintypes.DWORD),
                ("union", INPUT_union)]

# Hjälpfunktioner för mus
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def get_cursor_pos():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return (pt.x, pt.y)

def set_cursor_pos(x, y):
    ctypes.windll.user32.SetCursorPos(x, y)

def send_input_move_smooth(pixels=50, steps=10, delay=0.02):
    """Synlig, mjuk musrörelse: flytta åt höger och tillbaka."""
    try:
        # Spara aktuell position
        start_pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(start_pt))
        start_x, start_y = start_pt.x, start_pt.y

        dx_step = int(pixels / steps)
        if dx_step == 0:
            dx_step = 1

        extra = ctypes.c_void_p(0)

        # Flytta höger i små steg
        for i in range(steps):
            ii = INPUT()
            ii.type = 0  # INPUT_MOUSE
            ii.mi = MOUSEINPUT(dx_step, 0, 0, 0x0001, 0, extra)  # MOUSEEVENTF_MOVE
            ctypes.windll.user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(INPUT))
            time.sleep(delay)

        time.sleep(0.15)

        # Flytta tillbaka i små steg
        for i in range(steps):
            ii = INPUT()
            ii.type = 0
            ii.mi = MOUSEINPUT(-dx_step, 0, 0, 0x0001, 0, extra)
            ctypes.windll.user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(INPUT))
            time.sleep(delay)

        # Säkerställ exakt återställning
        ctypes.windll.user32.SetCursorPos(start_x, start_y)
        return True
    except Exception as e:
        print(f"Fel vid send_input_move_smooth: {e}", flush=True)
        return False

# Modern tangentbordsinput via SendInput
def send_shift_via_sendinput():
    try:
        extra = ctypes.c_void_p(0)
        inp_down = INPUT()
        inp_down.type = 1  # INPUT_KEYBOARD
        inp_down.ki = KEYBDINPUT(0x10, 0, 0, 0, extra)  # VK_SHIFT down
        inp_up = INPUT()
        inp_up.type = 1
        inp_up.ki = KEYBDINPUT(0x10, 0, 0x0002, 0, extra)  # KEYEVENTF_KEYUP

        n = ctypes.windll.user32.SendInput(2, ctypes.byref(inp_down), ctypes.sizeof(INPUT))
        if n != 2:
            # Försök skicka separat om inte båda gick igenom
            ctypes.windll.user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(INPUT))
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(INPUT))
        return True
    except Exception as e:
        print(f"Fel vid send_shift_via_sendinput: {e}", flush=True)
        return False

# Autostart
def get_exe_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        return os.path.abspath(__file__)

def is_autostart_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Run",
                           0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, "Mouser")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False

def set_autostart(enabled):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Run",
                           0, winreg.KEY_SET_VALUE)
        if enabled:
            exe_path = get_exe_path()
            winreg.SetValueEx(key, "Mouser", 0, winreg.REG_SZ, exe_path)
            print(f"✓ Autostart aktiverat: {exe_path}", flush=True)
        else:
            try:
                winreg.DeleteValue(key, "Mouser")
                print("✓ Autostart inaktiverat", flush=True)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Fel vid autostart-inställning: {e}", flush=True)
        return False

running = True
active_img = None
idle_img = None

# Huvudlogik: använder GetLastInputInfo, försöker keyboard först, sedan synlig musrörelse
def keep_awake(icon: Icon):
    global running
    wake_threshold = 35.0  # sekunder
    check_interval = 5.0

    while running:
        try:
            idle_ms = get_idle_msecs()
            idle_s = idle_ms / 1000.0
            print(f"Inaktiv tid enligt GetLastInputInfo: {idle_s:.1f} sek", flush=True)

            if idle_s < 1.0:
                # aktiv
                if active_img and icon.icon != active_img:
                    icon.icon = active_img
            elif idle_s >= wake_threshold:
                # Försök först tangenttryckning (osynlig)
                success = send_shift_via_sendinput()
                if not success:
                    # fallback: synlig musrörelse (då du vill se den)
                    success = send_input_move_smooth(pixels=50, steps=10, delay=0.02)
                else:
                    # även om shift lyckades, gör ändå en synlig liten rörelse om du vill se det
                    success_move = send_input_move_smooth(pixels=20, steps=6, delay=0.02)
                    success = success or success_move

                if success:
                    print("Håller datorn vaken - skickade input", flush=True)

                if idle_img and icon.icon != idle_img:
                    icon.icon = idle_img

        except Exception as e:
            print(f"Fel i keep_awake: {e}", flush=True)

        time.sleep(check_interval)

def on_quit(icon, item):
    global running
    running = False
    icon.stop()

def toggle_autostart(icon, item):
    current_state = is_autostart_enabled()
    new_state = not current_state
    if set_autostart(new_state):
        icon.menu = create_menu()

def create_menu():
    autostart_enabled = is_autostart_enabled()
    autostart_text = "✓ Starta med Windows" if autostart_enabled else "Starta med Windows"
    return Menu(
        MenuItem(autostart_text, toggle_autostart),
        MenuItem("Avsluta", on_quit)
    )

def load_icons():
    global active_img, idle_img
    active_icon_path = resource_path("active.ico")
    idle_icon_path = resource_path("idle.ico")
    try:
        active_img = Image.open(active_icon_path).convert("RGBA").resize((32, 32))
    except:
        active_img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
        draw = ImageDraw.Draw(active_img)
        draw.ellipse([4, 4, 28, 28], fill=(0, 255, 0, 255), outline=(0, 200, 0, 255), width=2)
    try:
        idle_img = Image.open(idle_icon_path).convert("RGBA").resize((32, 32))
    except:
        idle_img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
        draw = ImageDraw.Draw(idle_img)
        draw.ellipse([4, 4, 28, 28], fill=(255, 0, 0, 255), outline=(200, 0, 0, 255), width=2)

def main():
    global running

    # Skapa loggfil i samma katalog som programmet — öppna här för att fånga utskrifter
    log_path = os.path.join(os.path.dirname(get_exe_path()), "mouser.log")
    try:
        logfile = open(log_path, "a", encoding="utf-8")
        sys.stdout = logfile
        sys.stderr = logfile
    except Exception:
        pass

    print("Startar Mouser program...", flush=True)
    load_icons()
    menu = create_menu()
    icon = Icon("KeepAwake", active_img, "Mouser - Håller datorn vaken", menu)

    def setup(icon):
        icon.visible = True
        icon.menu = create_menu()
        threading.Thread(target=keep_awake, args=(icon,), daemon=True).start()

    try:
        icon.run(setup=setup)
    except KeyboardInterrupt:
        running = False
    finally:
        try:
            logfile.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
