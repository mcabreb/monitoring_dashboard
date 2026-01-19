"""Process data collection using psutil."""

import logging

import psutil

from monitor_dashboard.models.process import ProcessInfo

logger = logging.getLogger(__name__)


class ProcessCollector:
    """Collects information about running processes."""

    def collect(self, max_processes: int = 50) -> list[ProcessInfo]:
        """Collect information about active processes.

        Args:
            max_processes: Maximum number of processes to return.

        Returns:
            List of ProcessInfo objects, sorted by CPU usage (descending).
        """
        processes = []

        try:
            for proc in psutil.process_iter(
                ["pid", "username", "cpu_percent", "memory_percent", "cpu_times", "name", "cmdline"]
            ):
                try:
                    info = proc.info

                    # Format CPU time as HH:MM:SS
                    cpu_times = info.get("cpu_times")
                    if cpu_times:
                        total_seconds = int(cpu_times.user + cpu_times.system)
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        time_str = "00:00:00"

                    # Get command - prefer cmdline, fall back to name
                    cmdline = info.get("cmdline")
                    if cmdline:
                        command = " ".join(cmdline)
                    else:
                        command = info.get("name", "unknown")

                    processes.append(
                        ProcessInfo(
                            pid=info.get("pid", 0),
                            user=info.get("username", "unknown") or "unknown",
                            cpu_percent=info.get("cpu_percent", 0.0) or 0.0,
                            memory_percent=info.get("memory_percent", 0.0) or 0.0,
                            time=time_str,
                            command=command,
                        )
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            # Sort by CPU usage descending, then by memory
            processes.sort(key=lambda p: (p.cpu_percent, p.memory_percent), reverse=True)

            return processes[:max_processes]

        except Exception as e:
            logger.debug(f"Failed to collect process info: {e}")
            return []
