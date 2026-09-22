# Kaneki Launcher 🩸

 A lightweight, anime-inspired application launcher for Linux, built with **Python and Tkinter**.

 Kaneki Launcher provides a simple circular interface for quickly launching your favorite applications, with a custom Kaneki-themed design, icons, hover effects, and desktop integration.

 ## ✨ Features

 - 🩸 Kaneki-inspired dark/red interface
- 🔴 Circular application layout
- 🖱️ Hover animations and application highlighting
- 🚀 Launch applications with a single click
- 🖼️ Custom application icons
- 🎨 Custom background and theme
- 🔍 Automatically detects available application commands
- 🧩 Fallback icons when an application icon is missing
- 🖥️ Desktop application-menu integration
- ⌨️ Press `Esc` to close the launcher
- 🧹 Easy installation and uninstallation

 ## 📦 Included Applications

 The default configuration includes:

 - **Ft\_lock**
- **Terminal**
- **Firefox**
- **Settings**
- **VS Code**

 Applications can be customized directly in `kaneki_launcher.py`.

 ## 🛠️ Requirements

 Kaneki Launcher is designed for **Linux**.

 ### Required

 - Python 3
- Tkinter
- Linux desktop environment
- Applications you want to launch

 On Debian/Ubuntu-based distributions:

```
sudo apt install python3-tk
```

 ## 🚀 Installation

 Clone the repository:

```
git clone https://github.com/KanekiEzz/kaneki_launcher.git
cd kaneki_launcher
```

 Make the installer executable:

```
chmod +x install.sh
```

 Run the installer:

```
./install.sh
```

 After installation, search for **Kaneki** in your application menu.

 ## ▶️ Run Without Installing

 You can also run the launcher directly:

```
python3 kaneki_launcher.py
```

 Or:

```
chmod +x kaneki_launcher.py
./kaneki_launcher.py
```

 ## 🗑️ Uninstall

 If you installed Kaneki Launcher using the installer:

```
./install.sh --uninstall
```

 ## ⚙️ Customization

 Applications are configured inside `kaneki_launcher.py`.

 For example:

```
{
    "name": "Firefox",
    "icon": "firefox.png",
    "command": [
        "firefox",
        "flatpak run org.mozilla.firefox",
    ],
}
```

 ### Adding an Application

 Add another application to the `APPS` list:

```
{
    "name": "Discord",
    "icon": "discord.png",
    "command": "discord",
}
```

 Then place the corresponding icon inside:

```
icons/
```

 The launcher checks the configured commands and uses the first available one.

 ## 📁 Project Structure

```
kaneki_launcher/
├── icons/
│   └── *.png
├── background.png
├── kaneki.png
├── kaneki_launcher.py
├── install.sh
├── make_icons.py
├── make_wallpaper.py
└── README.md
```

 ## 📄 File Description

 | File | Description |
| --- | --- |
| `kaneki_launcher.py` | Main launcher application |
| `install.sh` | Installation and uninstallation script |
| `icons/` | Application icons |
| `background.png` | Launcher background |
| `kaneki.png` | Launcher/application icon |
| `make_icons.py` | Icon generation utility |
| `make_wallpaper.py` | Wallpaper generation utility |
| `README.md` | Project documentation |

## 🎨 How It Works

 Kaneki Launcher uses **Tkinter Canvas** to create its graphical interface.

 Applications are arranged around a central Kaneki icon in a circular layout.

 When you hover over an application:

 - The application is highlighted.
- Its name is displayed.
- The interface responds visually.

 Clicking an application launches it using the configured command.

 If an application icon is unavailable, the launcher generates a simple fallback icon.

 ## 🖥️ Desktop Integration

 The installer integrates Kaneki Launcher with the Linux desktop environment.

 The launcher is installed into:

```
~/.local/share/kaneki-launcher
```

 A desktop entry is also created in:

```
~/.local/share/applications
```

 This allows Kaneki Launcher to appear in your application menu and be pinned to your dock.

 ## 🔧 Troubleshooting

 ### Tkinter is missing

 Install Tkinter:

```
sudo apt install python3-tk
```

 ### An application doesn't launch

 Check whether the application's command exists:

```
which <application>
```

 For example:

```
which firefox
```

 If the application is installed through Flatpak, add its Flatpak command to the application configuration.

 ### An icon is missing

 Make sure the PNG icon exists inside:

```
icons/
```

 If the icon cannot be loaded, Kaneki Launcher will use a fallback icon.

 ## 🤝 Contributing

 Contributions, improvements, new themes, icons, and bug fixes are welcome.

 1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Test the launcher on Linux.
5. Commit your changes.
6. Open a pull request.

 ## ❤️ Credits

 Created by **KanekiEzz**.

 GitHub repository:

 https://github.com/KanekiEzz/kaneki\_launcher

---

 ⭐ If you like this project, consider giving the repository a star!

 **Kaneki Launcher — simple, dark, and made for Linux.** 🩸
