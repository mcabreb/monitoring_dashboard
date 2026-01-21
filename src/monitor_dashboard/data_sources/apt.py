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
class UpgradablePackage:
    """Information about a single upgradable package."""

    name: str  # Package name
    current_version: str  # Currently installed version
    new_version: str  # Available version
    repository: str  # Repository source
    is_security: bool  # Whether this is a security update


@dataclass(frozen=True)
class AptStatus:
    """Status of available apt upgrades."""

    packages: tuple[UpgradablePackage, ...]  # List of upgradable packages
    checked: bool  # Whether the check was successful
    cache_age_seconds: int | None  # Age of apt cache in seconds, None if unknown

    @property
    def upgradable_count(self) -> int:
        """Number of packages that can be upgraded."""
        return len(self.packages)

    @property
    def security_count(self) -> int:
        """Number of security updates."""
        return sum(1 for pkg in self.packages if pkg.is_security)


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

    def _parse_package_line(self, line: str) -> UpgradablePackage | None:
        """Parse a single apt list output line into an UpgradablePackage.

        Args:
            line: A line from apt list --upgradable output.

        Returns:
            UpgradablePackage or None if parsing fails.
        """
        # Format: package_name/repository version arch [upgradable from: old_version]
        # Example: google-chrome-stable/stable 144.0.7559.96-1 amd64 [upgradable from: 144.0.7559.59-1]
        try:
            # Split name/repo from the rest
            name_repo, rest = line.split(" ", 1)
            name, repository = name_repo.split("/", 1)

            # Extract new version (first part after name/repo)
            parts = rest.split()
            new_version = parts[0] if parts else "unknown"

            # Extract old version from [upgradable from: X]
            current_version = "unknown"
            if "upgradable from:" in line:
                current_version = line.split("upgradable from:")[-1].strip().rstrip("]")

            is_security = "-security" in repository

            return UpgradablePackage(
                name=name,
                current_version=current_version,
                new_version=new_version,
                repository=repository,
                is_security=is_security,
            )
        except (ValueError, IndexError) as e:
            logger.debug(f"Failed to parse package line '{line}': {e}")
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
                return AptStatus(packages=(), checked=False, cache_age_seconds=cache_age)

            # Parse output - skip the "Listing..." header line
            lines = result.stdout.strip().split("\n")
            upgradable_lines = [line for line in lines if "/" in line and "upgradable" in line.lower()]

            # Parse each line into UpgradablePackage
            packages = []
            for line in upgradable_lines:
                pkg = self._parse_package_line(line)
                if pkg:
                    packages.append(pkg)

            return AptStatus(
                packages=tuple(packages),
                checked=True,
                cache_age_seconds=cache_age,
            )

        except subprocess.TimeoutExpired:
            logger.debug("apt list timed out")
            return AptStatus(packages=(), checked=False, cache_age_seconds=cache_age)
        except FileNotFoundError:
            logger.debug("apt command not found")
            return AptStatus(packages=(), checked=False, cache_age_seconds=cache_age)
        except Exception as e:
            logger.debug(f"Failed to check apt upgrades: {e}")
            return AptStatus(packages=(), checked=False, cache_age_seconds=cache_age)
