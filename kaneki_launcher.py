#!/usr/bin/env python3
import math
import shlex
import shutil
import subprocess
import tkinter as tk
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = BASE_DIR / "kaneki.png"
ICONS_DIR = BASE_DIR / "icons"

# ---------- Theme ----------
BG = "#0b0b0d"
ACCENT = "#e11d48"  # Kaneki red
GLOW = "#5c1024"
ORBIT = "#22222a"
FALLBACK = "#2e2e36"
TEXT = "#f4f4f5"
MUTED = "#71717a"
FONT = "Helvetica"

# ---------- Layout ----------
WIN_W, WIN_H = 600, 650
CANVAS_H = 610
CX, CY = WIN_W // 2, 290   # center of the circle
ORBIT_R = 185              # distance between center and each app
RING_R = 64                # hover ring radius
DEFAULT_TITLE = "KANEKI"

# ---------- Apps ----------
# "command" can be one command or a list of alternatives (the first one found is used).
# "icon" is a PNG inside ./icons (if missing, a round badge with the first letter is drawn).
APPS = [
    {
        "name": "Ft_lock",
        "icon": "lock.png",
        "command": "ft_lock",
    },
    {
        "name": "Terminal",
        "icon": "terminal.png",
        "command": "x-terminal-emulator",
    },
    {
        "name": "Firefox",
        "icon": "firefox.png",
        "command": [
            "/home/iezzam/.var/app/firefox/firefox",
            "firefox",
            "flatpak run org.mozilla.firefox",
        ],
    },
    {
        "name": "Settings",
        "icon": "settings.png",
        "command": [
            "gnome-control-center",
            "systemsettings",
            "xfce4-settings-manager",
            "cinnamon-settings",
            "mate-control-center",
        ],
    },
    {
        "name": "VS Code",
        "icon": "vscode.png",
        "command": ["code", "codium", "code-oss"],
    },
]


def resolve(command):
    """Return the first runnable command (as an argv list), or None."""
    candidates = [command] if isinstance(command, str) else command
    for cmd in candidates:
        parts = shlex.split(cmd)
        if parts and shutil.which(parts[0]):
            return parts
    return None


def draw_fallback(canvas, x, y, r, letter, fill):
    """Round badge with a letter, used when an icon file is missing."""
    oval = canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline="")
    text = canvas.create_text(
        x, y, text=letter, fill=TEXT, font=(FONT, int(r * 0.7), "bold")
    )
    return [oval, text]


def center_window(win, width, height):
    x = (win.winfo_screenwidth() - width) // 2
    y = (win.winfo_screenheight() - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


def main():
    root = tk.Tk(className="Kaneki")  # WM_CLASS = Kaneki -> dock groups it correctly
    root.title("Kaneki")
    root.configure(bg=BG)
    root.resizable(False, False)

    # ---------- ft_lock pipe ----------
    PIPE_PATH = Path("/dev/shm/ft_lock_d.103903.pipe")
    pipe_process = None

        # Remove old pipe if it exists
    try:
        if PIPE_PATH.exists() or PIPE_PATH.is_symlink():
            PIPE_PATH.unlink()
    except Exception as e:
        print(f"Could not remove old pipe: {e}")

    # Start:
    # cat /dev/random > /dev/shm/ft_lock_d.103903.pipe
    try:
        pipe_process = subprocess.Popen(
            ["cat", "/dev/random"],
            stdout=open(PIPE_PATH, "wb"),
            start_new_session=True,
        )
        print(f"ft_lock pipe started: {PIPE_PATH}")
    except Exception as e:
        print(f"Could not start ft_lock pipe: {e}")
        pipe_process = None

    def cleanup():
        """Stop cat and remove the pipe when Kaneki closes."""
        nonlocal pipe_process

        if pipe_process is not None:
            try:
                pipe_process.terminate()
                pipe_process.wait(timeout=1)
            except Exception:
                try:
                    pipe_process.kill()
                except Exception:
                    pass

        try:
            if PIPE_PATH.exists() or PIPE_PATH.is_symlink():
                PIPE_PATH.unlink()
                print(f"Removed pipe: {PIPE_PATH}")
        except Exception as e:
            print(f"Could not remove pipe: {e}")

        root.destroy()

    # Close window / Alt+F4 / WM close
    root.protocol("WM_DELETE_WINDOW", cleanup)

    try:
        window_icon = tk.PhotoImage(file=str(ICON_PATH))
        root.iconphoto(True, window_icon)
    except tk.TclError as e:
        print(f"Icon not loaded: {e}")

    center_window(root, WIN_W, WIN_H)
    # root.bind("<Escape>", lambda e: root.destroy())
    root.bind("<Escape>", lambda e: cleanup())

    # canvas = tk.Canvas(
    #     root, width=WIN_W, height=CANVAS_H, bg=BG, highlightthickness=0
    # )

    canvas = tk.Canvas(
    root,
    width=WIN_W,
    height=CANVAS_H,
    bg=BG,
    highlightthickness=0
    )
    canvas.pack()

    images = []  # keep references, otherwise Tk garbage-collects the icons

    # ---------- Background ----------
    try:
        bg_image = tk.PhotoImage(file=str(BASE_DIR / "background.png"))
        images.append(bg_image)

        canvas.create_image(
            WIN_W // 2,
            CANVAS_H // 2,
            image=bg_image
        )
    except tk.TclError as e:
        print(f"Background not loaded: {e}")

    def load(name):
        path = ICONS_DIR / name
        if not name or not path.is_file():
            return None
        try:
            img = tk.PhotoImage(file=str(path))
        except tk.TclError:
            return None
        images.append(img)
        return img

    # ----- orbit line + center icon -----
    canvas.create_oval(
        CX - ORBIT_R, CY - ORBIT_R, CX + ORBIT_R, CY + ORBIT_R,
        outline=ORBIT, width=2, dash=(2, 8),
    )
    center_img = load("center.png")
    if center_img:
        canvas.create_image(CX, CY, image=center_img)
    else:
        draw_fallback(canvas, CX, CY, 78, "K", ACCENT)

    # ----- title (changes on hover) -----
    title_id = canvas.create_text(
        CX, 578, text=DEFAULT_TITLE, fill=TEXT, font=(FONT, 22, "bold")
    )
    canvas.create_text(CX, 604, text="金木 研", fill=MUTED, font=(FONT, 11))

    state = {"flash": None}

    def set_title(text, color=TEXT):
        canvas.itemconfigure(title_id, text=text, fill=color)

    def flash(message):
        set_title(message, ACCENT)
        if state["flash"]:
            root.after_cancel(state["flash"])
        state["flash"] = root.after(2200, lambda: set_title(DEFAULT_TITLE))

    def launch(app):
        argv = resolve(app["command"])
        if argv is None:
            flash(f"{app['name']} not found")
            return
        try:
            subprocess.Popen(argv, start_new_session=True)
        except Exception as e:
            print(f"Error: {e}")
            flash(f"Can't open {app['name']}")

    def on_enter(app, glow, ring):
        canvas.itemconfigure(glow, state="normal")
        canvas.itemconfigure(ring, state="normal")
        canvas.configure(cursor="hand2")
        set_title(app["name"], ACCENT)

    def on_leave(glow, ring):
        canvas.itemconfigure(glow, state="hidden")
        canvas.itemconfigure(ring, state="hidden")
        canvas.configure(cursor="")
        set_title(DEFAULT_TITLE)

    # ----- apps around the circle -----
    n = len(APPS)
    for i, app in enumerate(APPS):
        angle = -math.pi / 2 + 2 * math.pi * i / n  # first app at the top
        x = CX + ORBIT_R * math.cos(angle)
        y = CY + ORBIT_R * math.sin(angle)

        glow = canvas.create_oval(
            x - RING_R - 5, y - RING_R - 5, x + RING_R + 5, y + RING_R + 5,
            outline=GLOW, width=8, state="hidden",
        )
        ring = canvas.create_oval(
            x - RING_R, y - RING_R, x + RING_R, y + RING_R,
            outline=ACCENT, width=3, state="hidden",
        )

        img = load(app.get("icon", ""))
        if img:
            hit_items = [canvas.create_image(x, y, image=img)]
        else:
            hit_items = draw_fallback(canvas, x, y, 52, app["name"][0].upper(), FALLBACK)

        for item in hit_items:
            canvas.tag_bind(item, "<Enter>", lambda e, a=app, g=glow, r=ring: on_enter(a, g, r))
            canvas.tag_bind(item, "<Leave>", lambda e, g=glow, r=ring: on_leave(g, r))
            canvas.tag_bind(item, "<Button-1>", lambda e, a=app: launch(a))

    # ----- footer -----
    # tk.Label(root, text="Esc to quit", font=(FONT, 9), fg=MUTED, bg=BG).pack(pady=4)
    tk.Label(root, text="_____________+______________", font=(FONT, 9), fg=MUTED, bg=BG).pack(pady=4)

    root.mainloop()


if __name__ == "__main__":
    main()
