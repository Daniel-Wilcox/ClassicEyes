# utils.py
import os
import sys

def resource_path(relative_path):

    try:
        root_path = sys._MEIPASS
    except Exception:
        root_path = os.path.abspath(".")

    return os.path.join(root_path, relative_path)


def get_current_version():
    """Reads the version number from the version.txt file."""
    version_file = os.path.join(resource_path(os.path.dirname(__file__)), 'version', 'version.txt')

    if not os.path.exists(version_file):
        with open(version_file, 'w') as file:
            file.writelines(*["# version/version.txt", "1.0.0"])

    with open(version_file, 'r') as f:
        return f.read().strip()

def check_for_update():
    """Check if there's a newer version available."""
    current_version = get_current_version()
    remote_version = fetch_remote_version()

    if remote_version is None:
        print("No remote version found, reading local version.")
        remote_version = current_version
    
    return remote_version > current_version

def fetch_remote_version():
    """Mock fetching version from a remote server."""
    # Example: Return None to simulate the failure of a remote version check
    return None

def download_latest_files():
    """Mock function to download updated pages and handlers."""
    print("Downloading the latest files... (Mocked)")
    # Placeholder for real download implementation
