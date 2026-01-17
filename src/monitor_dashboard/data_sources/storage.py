"""Storage data collection using psutil."""

import logging

import psutil

from monitor_dashboard.models.metrics import DiskInfo

logger = logging.getLogger(__name__)

# Pseudo filesystems to filter out
PSEUDO_FS_TYPES = frozenset(
    {
        "proc",
        "sysfs",
        "devfs",
        "devtmpfs",
        "tmpfs",
        "squashfs",
        "overlay",
        "aufs",
        "none",
    }
)

# Mount point prefixes to filter out
PSEUDO_MOUNT_PREFIXES = ("/proc", "/sys", "/dev", "/run", "/snap")


class StorageCollector:
    """Collects disk partition and usage information using psutil."""

    def collect(self) -> list[DiskInfo]:
        """Gather disk usage for all mounted partitions.

        Filters out pseudo filesystems (proc, sys, dev, etc.) and only
        includes physical partitions. Handles inaccessible partitions
        gracefully by logging a warning and continuing.

        Returns:
            List of DiskInfo objects sorted by mount point.
            Returns empty list if all partitions fail.
        """
        disks: list[DiskInfo] = []

        try:
            partitions = psutil.disk_partitions(all=False)
        except Exception as e:
            logger.error(f"Failed to enumerate partitions: {e}")
            return []

        for part in partitions:
            # Filter pseudo filesystems
            if part.fstype in PSEUDO_FS_TYPES:
                continue

            # Filter pseudo mount points
            if any(part.mountpoint.startswith(prefix) for prefix in PSEUDO_MOUNT_PREFIXES):
                continue

            # Try to get disk usage for this partition
            try:
                usage = psutil.disk_usage(part.mountpoint)

                disks.append(
                    DiskInfo(
                        mount_point=part.mountpoint,
                        device=part.device,
                        fs_type=part.fstype,
                        total=usage.total,
                        used=usage.used,
                        free=usage.free,
                        percent=usage.percent,
                    )
                )
            except PermissionError:
                logger.warning(f"Permission denied accessing partition: {part.mountpoint}")
            except Exception as e:
                logger.warning(f"Failed to get usage for {part.mountpoint}: {e}")

        # Sort by mount point for consistent ordering
        return sorted(disks, key=lambda d: d.mount_point)
