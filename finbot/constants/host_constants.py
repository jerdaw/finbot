import hashlib
import importlib
import platform
import socket
import subprocess  # nosec
import uuid
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

try:
    psutil: Any = importlib.import_module("psutil")
except Exception:  # pragma: no cover - only hit when psutil is unavailable
    psutil = None

UNAVAILABLE = "Unavailable"


def _safe_hostname() -> str:
    """Return the local hostname without raising."""
    try:
        hostname = socket.gethostname()
    except Exception:
        return UNAVAILABLE
    return hostname or UNAVAILABLE


def _safe_ip_address() -> str:
    """Resolve the local hostname without raising."""
    hostname = _safe_hostname()
    if hostname == UNAVAILABLE:
        return UNAVAILABLE

    try:
        ip_address = socket.gethostbyname(hostname)
    except Exception:
        return UNAVAILABLE
    return ip_address or UNAVAILABLE


def _safe_cpu_count(*, logical: bool) -> int:
    """Return a CPU core count or 0 when unavailable."""
    if psutil is None:
        return 0

    try:
        return psutil.cpu_count(logical=logical) or 0
    except Exception:
        return 0


def _safe_cpu_speed() -> float:
    """Return the max CPU speed in MHz or 0 when unavailable."""
    if psutil is None:
        return 0.0

    try:
        frequency = psutil.cpu_freq()
    except Exception:
        return 0.0

    return float(frequency.max) if frequency is not None else 0.0


def _safe_memory_gb() -> float:
    """Return total memory in GB or 0 when unavailable."""
    if psutil is None:
        return 0.0

    try:
        return float(psutil.virtual_memory().total / (1024**3))
    except Exception:
        return 0.0


def _safe_disk_usage_gb(field_name: str) -> float:
    """Return a disk-usage field in GB or 0 when unavailable."""
    if psutil is None:
        return 0.0

    try:
        usage = psutil.disk_usage("/")
    except Exception:
        return 0.0

    return float(getattr(usage, field_name, 0) / (1024**3))


def _generate_impersistent_host_id() -> str:
    """Generate a unique host ID based on system attributes."""
    # TODO: Using impersistent host ID. ID may change and cause issues with data consistency.
    system_info = [
        _safe_hostname(),
        platform.processor(),
        platform.system(),
        platform.release(),
    ]
    # Optionally include the MAC address of the primary network interface for added uniqueness
    mac_address = ":".join([f"{(uuid.getnode() >> elements) & 0xFF:02x}" for elements in range(2, 2 + 6 * 2, 2)][::-1])
    system_info_string = "_".join(system_info) + mac_address
    # Use SHA-256 hash to generate a unique ID from system information
    host_id = hashlib.sha256(system_info_string.encode()).hexdigest()
    return host_id


@dataclass
class HostSystem:
    """Snapshot of the current host's hardware and network configuration.

    All fields default to auto-detected values via ``platform``, ``psutil``,
    and ``socket``. Instantiate with no arguments to capture the current host,
    or pass keyword arguments to describe a hypothetical host.
    """

    hostname: str = field(default_factory=_safe_hostname)
    ip_address: str = field(default_factory=_safe_ip_address)
    operating_system: str = field(default_factory=lambda: f"{platform.system()} {platform.release()}")
    cpu_name: str = field(default_factory=lambda: HostSystem.get_cpu_name())
    cpu_cores: int = field(default_factory=lambda: _safe_cpu_count(logical=False))
    cpu_threads: int = field(default_factory=lambda: _safe_cpu_count(logical=True))
    cpu_speed: float = field(default_factory=_safe_cpu_speed)  # MHz
    total_memory: float = field(default_factory=_safe_memory_gb)  # GB
    disk_storage: float = field(default_factory=lambda: _safe_disk_usage_gb("total"))  # GB
    available_storage: float = field(default_factory=lambda: _safe_disk_usage_gb("free"))  # GB
    used_storage: float = field(default_factory=lambda: _safe_disk_usage_gb("used"))  # GB
    network_interface: str = field(default_factory=lambda: HostSystem.get_active_network_interface())
    host_identifier: str = field(default_factory=_generate_impersistent_host_id)

    @staticmethod
    def get_cpu_name() -> str:
        """Retrieve the CPU name using system commands based on the OS."""
        try:
            if platform.system() == "Windows":
                command = ["wmic", "cpu", "get", "name"]
            elif platform.system() == "Linux":
                command = ["lscpu"]
            elif platform.system() == "Darwin":  # macOS
                command = ["sysctl", "-n", "machdep.cpu.brand_string"]
            else:
                return UNAVAILABLE

            if platform.system() == "Linux":
                # Using subprocess.run() to replace subprocess.check_output()
                # This only a small security risk since the command is not user-provided
                result = subprocess.run(command, text=True, capture_output=True, check=True)  # nosec
                output = result.stdout
                # Parse the output of lscpu directly in Python to find the model name
                for line in output.split("\n"):
                    if "Model name" in line:
                        return line.split(":")[1].strip()
                return UNAVAILABLE

            # For Windows and macOS, the command does not require parsing the output
            # This only a small security risk since the command is not user-provided
            result = subprocess.run(command, text=True, capture_output=True, check=True)  # nosec
            return result.stdout.strip() or UNAVAILABLE

        except (OSError, subprocess.CalledProcessError):
            return UNAVAILABLE

    @staticmethod
    def get_active_network_interface() -> str:
        """Identify the currently active network interface."""
        if psutil is None:
            return "None"

        try:
            interfaces = psutil.net_if_addrs().items()
        except Exception:
            return "None"

        active_interfaces = []
        for interface, addrs in interfaces:
            for addr in addrs:
                if getattr(addr, "family", None) == socket.AF_INET and not getattr(addr, "address", "").startswith("127."):
                    active_interfaces.append(interface)
                    break  # Only add each interface once
        return ", ".join(active_interfaces) if active_interfaces else "None"

    def __str__(self) -> str:
        """Return a single-line human-readable summary of the host configuration."""
        return (
            f"Host ID: {self.host_identifier}, "
            f"Hostname: {self.hostname}, IP Address: {self.ip_address}, "
            f"Operating System: {self.operating_system}, Total Memory: {self.total_memory:.1f}GB, "
            f"CPU: {self.cpu_name} {self.cpu_speed:.2f}MHz {self.cpu_cores}C/{self.cpu_threads}T, "
            f"Storage Used: {self.used_storage:.2f}/{self.disk_storage:.2f}GB, Network Interface: {self.network_interface}"
        )


@lru_cache(maxsize=1)
def get_current_host_info() -> HostSystem:
    """Return a cached snapshot of the current host."""
    return HostSystem()


def __getattr__(name: str) -> Any:
    """Provide lazy backward-compatible access to CURRENT_HOST_INFO."""
    if name == "CURRENT_HOST_INFO":
        return get_current_host_info()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """Expose lazy module attributes in dir() output."""
    return sorted([*globals().keys(), "CURRENT_HOST_INFO"])


if __name__ == "__main__":
    # Example Usage
    print(get_current_host_info())
    another_host = HostSystem(
        hostname="AnotherHost",
        ip_address="192.168.1.2",
        operating_system="Linux",
        cpu_cores=4,
        cpu_threads=4,
        total_memory=16.0,
    )
    print(another_host)
