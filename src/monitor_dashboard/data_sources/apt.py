"""Apt package upgrade data collection."""

import logging
import subprocess
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AptStatus:
    """Status of available apt upgrades."""

    upgradable_count: int  # Number of packages that can be upgraded
    security_count: int  # Number of security updates (if detectable)
    checked: bool  # Whether the check was successful


class AptCollector:
    """Collects information about available apt upgrades."""

    def collect(self) -> AptStatus:
        """Check for available apt upgrades.

        Returns:
            AptStatus with upgrade information.
        """
        try:
            # Run apt list --upgradable to get upgradable packages
            result = subprocess.run(
                ["apt", "list", "--upgradable"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                logger.debug(f"apt list failed: {result.stderr}")
                return AptStatus(upgradable_count=0, security_count=0, checked=False)

            # Parse output - skip the "Listing..." header line
            lines = result.stdout.strip().split("\n")
            upgradable = [line for line in lines if "/" in line and "upgradable" in line.lower()]

            # Count security updates (packages from -security repositories)
            security = [line for line in upgradable if "-security" in line]

            return AptStatus(
                upgradable_count=len(upgradable),
                security_count=len(security),
                checked=True,
            )

        except subprocess.TimeoutExpired:
            logger.debug("apt list timed out")
            return AptStatus(upgradable_count=0, security_count=0, checked=False)
        except FileNotFoundError:
            logger.debug("apt command not found")
            return AptStatus(upgradable_count=0, security_count=0, checked=False)
        except Exception as e:
            logger.debug(f"Failed to check apt upgrades: {e}")
            return AptStatus(upgradable_count=0, security_count=0, checked=False)
