"""
FOTA Package Mount Controller (Singleton)
Handles mounting/unmounting of FOTA update packages
"""
import uos
from typing import Optional, Any

class AppFotaPkgMount:
    __instance: Optional['AppFotaPkgMount'] = None
    __mount_state: bool
    __can_mount: bool
    __fota_dir: str

    def __new__(cls, *args: Any, **kwargs: Any) -> 'AppFotaPkgMount':
        """Singleton instance getter
        Returns:
            Existing instance if available, otherwise creates new instance
        """

    def __init__(self) -> None:
        """Initialize FOTA mount point (default: /fota)"""

    @property
    def mount_state(self) -> bool:
        """Current mount status (read-only)
        Returns:
            True if FOTA package is currently mounted
        """

    @property
    def can_mount(self) -> bool:
        """Mount capability flag (read-only)
        Returns:
            True if system supports FOTA mounting
        """

    @property
    def fota_dir(self) -> str:
        """FOTA mount directory path (read-only)
        Format: "/fota" or custom mounted path
        """

    def umount_disk(self) -> None:
        """Unmount FOTA package if mounted
        Side Effects:
            Updates mount_state flag
        """

    def get_fota_file_name(self, path: str) -> str:
        """Get absolute path within FOTA mount
        Args:
            path: Relative path (e.g. "/usr/package.bin")
        Returns:
            Absolute path (e.g. "/fota/usr/package.bin")
        """