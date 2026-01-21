"""Apt package upgrade data collection."""

import logging
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Apt cache directory
APT_LISTS_DIR = Path("/var/lib/apt/lists")
# Cache age threshold for warning (24 hours)
CACHE_STALE_THRESHOLD = 24 * 3600


@dataclass(frozen=True)
class AptStatus:
    """Status of available apt upgrades."""

    upgradable_count: int  # Number of packages that can be upgraded
    security_count: int  # Number of security updates (if detectable)
    checked: bool  # Whether the check was successful
    cache_age_seconds: int | None  # Age of apt cache in seconds, None if unknown


class AptCollector:
    """Collects information about available apt upgrades."""

    def _get_cache_age(self) -> int | None:
        """Get the age of the apt cache in seconds.

        Returns:
            Age in seconds, or None if unable to determine.
        """
        try:
            if not APT_LISTS_DIR.exists():
                return None

            # Find the most recently modified file in the lists directory
            # (excluding partial/ and lock files)
            newest_mtime = 0
            for path in APT_LISTS_DIR.iterdir():
                if path.is_file() and not path.name.startswith(("lock", "partial")):
                    mtime = path.stat().st_mtime
                    if mtime > newest_mtime:
                        newest_mtime = mtime

            if newest_mtime == 0:
                return None

            return int(time.time() - newest_mtime)
        except Exception as e:
            logger.debug(f"Failed to get apt cache age: {e}")
            return None

    def collect(self) -> AptStatus:
        """Check for available apt upgrades.

        Returns:
            AptStatus with upgrade information.
        """
        cache_age = self._get_cache_age()

        try:
            # Run apt list --upgradable to get upgradable packages
            # Use LC_ALL=C to force English output regardless of system locale
            env = os.environ.copy()
            env["LC_ALL"] = "C"
            result = subprocess.run(
                ["apt", "list", "--upgradable"],
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
            )

            if result.returncode != 0:
                logger.debug(f"apt list failed: {result.stderr}")
                return AptStatus(upgradable_count=0, security_count=0, checked=False, cache_age_seconds=cache_age)

            # Parse output - skip the "Listing..." header line
            lines = result.stdout.strip().split("\n")
            upgradable = [line for line in lines if "/" in line and "upgradable" in line.lower()]

            # Count security updates (packages from -security repositories)
            security = [line for line in upgradable if "-security" in line]

            return AptStatus(
                upgradable_count=len(upgradable),
                security_count=len(security),
                checked=True,
                cache_age_seconds=cache_age,
            )

        except subprocess.TimeoutExpired:
            logger.debug("apt list timed out")
            return AptStatus(upgradable_count=0, security_count=0, checked=False, cache_age_seconds=cache_age)
        except FileNotFoundError:
            logger.debug("apt command not found")
            return AptStatus(upgradable_count=0, security_count=0, checked=False, cache_age_seconds=cache_age)
        except Exception as e:
            logger.debug(f"Failed to check apt upgrades: {e}")
            return AptStatus(upgradable_count=0, security_count=0, checked=False, cache_age_seconds=cache_age)
