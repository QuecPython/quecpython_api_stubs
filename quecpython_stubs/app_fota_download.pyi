"""
FOTA (Firmware Over-The-Air) Update Module
Type definitions for firmware update functionality.

Note: All paths are dynamically generated at runtime based on the FOTA mount point.
"""
from typing import Optional, Dict, List, Any, Union, Tuple
import request
import uos

name, platform = uos.uname()[1].split("=",1)

# Path management functions
def get_updater_dir() -> str:
    """Get the absolute path to the updater directory
    Format: <fota_mount_point>/usr/.updater
    """

def get_download_stat_file() -> str:
    """Get the absolute path to the download status file
    Format: <fota_mount_point>/usr/.updater/download.stat
    """

def get_update_flag_file() -> str:
    """Get the absolute path to the update flag file
    Format: <fota_mount_point>/usr/.updater/update.flag
    """

updater_dir = get_updater_dir()
download_stat_file = get_download_stat_file()
update_flag_file = get_update_flag_file()

# File status operations
def _get_download_stat_by_file(file_name: str) -> Optional[Dict[str, Any]]:
    """Internal: Get download status for a specific file
    
    Args:
        file_name: Target filename (case-insensitive match)
    
    Returns:
        Dictionary containing:
            - url: str - Download source URL
            - name: str - File name
            - total_size: int - Expected file size
            - dl_location: str - Storage path
        None if file not found or error occurred
    """

def _get_download_stat() -> Optional[List[Dict[str, Any]]]:
    """Internal: Get complete download status list
    
    Returns:
        List of status dictionaries (same format as _get_download_stat_by_file)
        None if status file not found or invalid
    """

def get_download_stat() -> Optional[List[Dict[str, Any]]]:
    """Get current download status for all files
    (Wrapper around _get_download_stat)
    """

# Download operations
def _fetch(
    url: str,
    fetched_size: int,
    headers: Optional[Dict[str, str]] = None,
    ipvtype: int = 0,
    username: Optional[str] = None,
    password: Optional[str] = None
) -> request.Response:
    """Internal: Perform HTTP request with range header
    
    Args:
        url: Download URL
        fetched_size: Bytes already downloaded (for Range header)
        headers: Optional HTTP headers
        ipvtype: 0=IPv4, 1=IPv6
        username: HTTP auth username
        password: HTTP auth password
    
    Returns:
        request.Response object
    """

def _update_download_stat(
    url: str,
    file_name: str,
    total_size: Union[int, str],
    download_file_name: Optional[str] = None
) -> None:
    """Internal: Update download status file
    
    Args:
        url: Source URL
        file_name: Target filename
        total_size: Expected file size (int) or "unknown"
        download_file_name: Actual storage path
    """

def update_download_stat(
    url: str,
    file_name: str,
    total_size: Union[int, str]
) -> None:
    """Update download status (public wrapper)
    (Calls _update_download_stat with None for download_file_name)
    """

def delete_update_file(file_name: str) -> None:
    """Remove file entry from download status
    
    Args:
        file_name: Filename to remove from tracking
    """

# Main download function
def download(
    url: str,
    file_name: str,
    headers: Optional[Dict[str, str]] = None,
    ipvtype: int = 0,
    username: Optional[str] = None,
    password: Optional[str] = None,
    ext_enable: bool = False,
    spi_port: Optional[int] = None,
    spi_clk: Optional[int] = None,
    dl_location: Optional[str] = None
) -> int:
    """Download a file for FOTA update
    
    Args:
        url: Download source URL
        file_name: Destination filename (relative path)
        headers: Optional HTTP headers
        ipvtype: IP version (0=IPv4)
        username: HTTP auth username
        password: HTTP auth password
        ext_enable: Enable external storage
        spi_port: SPI port number (required if ext_enable)
        spi_clk: SPI clock speed (required if ext_enable)
        dl_location: Custom storage path
    
    Returns:
        0: Success
        -1: Failure
    """

# Platform-specific implementations
if platform == "FCM362K":
    def download_forFCM362K(
        url: str,
        headers: Optional[Dict[str, str]] = None
    ) -> int:
        """Special download handler for FCM362K platform
        
        Args:
            url: Firmware download URL
            headers: Optional HTTP headers
        
        Returns:
            0: Success (will trigger automatic reboot)
            -1: Failure
        """

# Batch operations
def bulk_download(
    info: Optional[List[Dict[str, Any]]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Optional[List[Dict[str, Any]]]:
    """Batch download multiple files
    
    Args:
        info: List of download items, each containing:
            - url: str
            - file_name: str
            - spi_port: Optional[int]
            - spi_clk: Optional[int]
            - ext_enable: bool
            - dl_location: Optional[str]
        headers: Common HTTP headers for all requests
    
    Returns:
        List of failed items (same format as input)
        None if all succeeded
    """

# Update control
def set_update_flag() -> None:
    """Create the update flag file
    (Triggers update process on next reboot)
    """