"""
Script to create the executable with PyInstaller.
"""
import PyInstaller.__main__
from pathlib import Path
import os

# Get absolute path to icon
icon_path = Path("icon.ico").resolve()
args = [
    'downloader.py',
    '--onefile',
    '--console',
    '--name=AddonDownloader',
]

# Add icon if exists
if icon_path.exists():
    # Use absolute path and forward slashes
    icon_arg = f'--icon={str(icon_path).replace(chr(92), "/")}'
    args.append(icon_arg)
    print(f"[+] Using icon: {icon_path}")
else:
    print("[i] No icon.ico found, building without custom icon")

print(f"Command: {' '.join(args)}\n")
PyInstaller.__main__.run(args)
