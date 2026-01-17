from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Log, Sparkline, Input
from textual.reactive import reactive
import asyncio
import subprocess
from datetime import datetime
import psutil


def get_bluetooth_batteries() -> list[tuple[str, int]]:
    """Get battery percentage for connected Bluetooth devices using upower."""
    devices = []
    try:
        # List all upower devices
        result = subprocess.run(
            ["upower", "-e"], capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return devices
        
        for device_path in result.stdout.strip().split("\n"):
            if not device_path:
                continue
            
            # Filter: HID batteries (bluetooth peripherals) have "battery_hid_" in path
            if "battery_hid_" not in device_path:
                continue
            
            # Get device info
            info = subprocess.run(
                ["upower", "-i", device_path],
                capture_output=True, text=True, timeout=5
            )
            if info.returncode != 0:
                continue
            
            output = info.stdout
            
            name = None
            percentage = None
            
            for line in output.split("\n"):
                line = line.strip()
                if line.startswith("model:"):
                    name = line.split(":", 1)[1].strip()
                elif line.startswith("percentage:"):
                    pct_str = line.split(":", 1)[1].strip().rstrip("%")
                    try:
                        percentage = int(float(pct_str))
                    except ValueError:
                        pass
            
            if name and percentage is not None:
                devices.append((name, percentage))
    
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    return devices

class MonitoringDashboard(App):
    """A monitoring dashboard with logs, metrics, and input."""
    
    BINDINGS = [
        ("colon", "focus_input", "Command"),
        ("slash", "focus_input", "Command"),
        ("escape", "focus_log", "Logs"),
    ]
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 3;
        grid-rows: auto 1fr 4;
    }
    
    Header {
        column-span: 2;
    }
    
    #metrics {
        height: 100%;
        border: solid green;
        padding: 1;
    }
    
    #cpu_chart {
        height: 100%;
        border: solid cyan;
    }
    
    #log_viewer {
        column-span: 2;
        border: solid yellow;
        height: 100%;
    }
    
    #input_panel {
        column-span: 2;
        height: auto;
        border: solid magenta;
        padding: 1;
    }
    """
    
    cpu_data = reactive([0] * 50)
    
    def compose(self) -> ComposeResult:
        """Build the UI layout."""
        yield Header(show_clock=True)
        
        # Metrics panel (top-left)
        yield Container(
            Static("[bold]System Metrics[/bold]", id="metrics_title"),
            Static("CPU: 0%", id="cpu_metric"),
            Static("Memory: 0 / 0 GB (0%)", id="mem_metric"),
            Static("Disk /: 0 / 0 GB (0%)", id="disk_metric"),
            Static("", id="bt_title"),
            Static("", id="bt_batteries"),
            id="metrics"
        )
        
        # CPU chart (top-right)
        yield Sparkline(self.cpu_data, id="cpu_chart")
        
        # Log viewer (middle, spans both columns)
        log = Log(id="log_viewer", highlight=True)
        log.border_title = "System Logs"
        yield log
        
        # Command input (bottom, spans both columns)
        yield Container(
            Static("Command:"),
            Input(placeholder="Enter command...", id="cmd_input"),
            id="input_panel"
        )
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Start background tasks when app mounts."""
        self.log_viewer = self.query_one("#log_viewer", Log)
        self.cpu_metric = self.query_one("#cpu_metric", Static)
        self.mem_metric = self.query_one("#mem_metric", Static)
        self.cpu_chart = self.query_one("#cpu_chart", Sparkline)
        self.bt_title = self.query_one("#bt_title", Static)
        self.bt_batteries = self.query_one("#bt_batteries", Static)
        
        # Start real-time monitoring
        self.set_interval(1, self.update_metrics)
        # Update bluetooth batteries less frequently (every 30s)
        self.set_interval(30, self.update_bluetooth)
        self.update_bluetooth()  # Initial update
        self.log_viewer.write_line("[bold green]Dashboard started[/bold green]")
        self.log_viewer.write_line("[dim]Press : or / to enter commands, Escape to return to logs[/dim]")
    
    def update_metrics(self) -> None:
        """Update metrics with real system data."""
        # CPU percentage (averaged across cores)
        cpu = psutil.cpu_percent(interval=None)
        
        # Memory stats
        mem = psutil.virtual_memory()
        mem_used_gb = mem.used / (1024 ** 3)
        mem_total_gb = mem.total / (1024 ** 3)
        mem_pct = mem.percent
        
        # Disk stats for root partition
        disk = psutil.disk_usage("/")
        disk_used_gb = disk.used / (1024 ** 3)
        disk_total_gb = disk.total / (1024 ** 3)
        disk_pct = disk.percent
        
        # Update metrics display
        self.cpu_metric.update(f"CPU: {cpu:.1f}%")
        self.mem_metric.update(f"Memory: {mem_used_gb:.1f} / {mem_total_gb:.1f} GB ({mem_pct:.0f}%)")
        self.query_one("#disk_metric", Static).update(f"Disk /: {disk_used_gb:.0f} / {disk_total_gb:.0f} GB ({disk_pct:.0f}%)")
        
        # Update CPU chart
        new_data = list(self.cpu_data[1:]) + [cpu]
        self.cpu_data = new_data
        self.cpu_chart.data = new_data
        
        # Log when CPU spikes above 80%
        if cpu > 80:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_viewer.write_line(
                f"[bold red]{timestamp}[/bold red] High CPU usage: {cpu:.1f}%"
            )
    
    def update_bluetooth(self) -> None:
        """Update Bluetooth device battery info."""
        batteries = get_bluetooth_batteries()
        if batteries:
            self.bt_title.update("[bold cyan]Bluetooth Batteries[/bold cyan]")
            lines = []
            for name, pct in batteries:
                # Color code based on battery level
                if pct <= 20:
                    color = "red"
                elif pct <= 50:
                    color = "yellow"
                else:
                    color = "green"
                lines.append(f"  [{color}]🔋 {name}: {pct}%[/{color}]")
            self.bt_batteries.update("\n".join(lines))
        else:
            self.bt_title.update("")
            self.bt_batteries.update("")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command input."""
        cmd = event.value
        if cmd:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_viewer.write_line(
                f"[bold blue]{timestamp}[/bold blue] Command executed: {cmd}"
            )
            event.input.value = ""
            
            if cmd.lower() == "clear":
                self.log_viewer.clear()
            elif cmd.lower() == "quit":
                self.exit()
    
    def action_focus_input(self) -> None:
        """Focus the command input."""
        self.query_one("#cmd_input", Input).focus()
    
    def action_focus_log(self) -> None:
        """Focus the log viewer."""
        self.log_viewer.focus()

if __name__ == "__main__":
    app = MonitoringDashboard()
    app.run()
