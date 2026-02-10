import hashlib
import platform
import socket
import subprocess  # nosec
import uuid
from dataclasses import dataclass, field

import psutil


def _generate_impersistent_host_id():
    """Generate a unique host ID based on system attributes."""
    # TODO: Using impersistent host ID. ID may change and cause issues with data consistency.
    system_info = [
        socket.gethostname(),
        platform.processor(),
        platform.system(),
        platform.release(),
    ]
    # Optionally include the MAC address of the primary network interface for added uniqueness
    mac_address = ":".join([f"{(uuid.getnode() >> elements) & 0xff:02x}" for elements in range(2, 2 + 6 * 2, 2)][::-1])
    system_info_string = "_".join(system_info) + mac_address
    # Use SHA-256 hash to generate a unique ID from system information
    host_id = hashlib.sha256(system_info_string.encode()).hexdigest()
    return host_id


@dataclass
class HostSystem:
    hostname: str = field(default_factory=lambda: socket.gethostname())
    ip_address: str = field(default_factory=lambda: socket.gethostbyname(socket.gethostname()))
    operating_system: str = field(default_factory=lambda: f"{platform.system()} {platform.release()}")
    cpu_name: str = field(default_factory=lambda: HostSystem.get_cpu_name())
    cpu_cores: int = field(default_factory=lambda: psutil.cpu_count(logical=False))
    cpu_threads: int = field(default_factory=lambda: psutil.cpu_count(logical=True))
    cpu_speed: float = field(default_factory=lambda: psutil.cpu_freq().max if psutil.cpu_freq() else 0)  # MHz
    total_memory: float = field(default_factory=lambda: psutil.virtual_memory().total / (1024**3))  # GB
    disk_storage: float = field(default_factory=lambda: psutil.disk_usage("/").total / (1024**3))  # GB
    available_storage: float = field(default_factory=lambda: psutil.disk_usage("/").free / (1024**3))  # GB
    used_storage: float = field(default_factory=lambda: psutil.disk_usage("/").used / (1024**3))  # GB
    network_interface: str = field(default_factory=lambda: HostSystem.get_active_network_interface())
    host_identifier: str = field(default_factory=_generate_impersistent_host_id)

    @staticmethod
    def get_cpu_name():
        """Retrieve the CPU name using system commands based on the OS."""
        try:
            if platform.system() == "Windows":
                command = ["wmic", "cpu", "get", "name"]
            elif platform.system() == "Linux":
                command = ["lscpu"]
            elif platform.system() == "Darwin":  # macOS
                command = ["sysctl", "-n", "machdep.cpu.brand_string"]
            else:
                return "Unavailable"

            if platform.system() == "Linux":
                # Using subprocess.run() to replace subprocess.check_output()
                # This only a small security risk since the command is not user-provided
                result = subprocess.run(command, text=True, capture_output=True, check=True)  # nosec
                output = result.stdout
                # Parse the output of lscpu directly in Python to find the model name
                for line in output.split("\n"):
                    if "Model name" in line:
                        return line.split(":")[1].strip()
                return "Unavailable"
            else:
                # For Windows and macOS, the command does not require parsing the output
                # This only a small security risk since the command is not user-provided
                result = subprocess.run(command, text=True, capture_output=True, check=True)  # nosec
                return result.stdout.strip()

        except subprocess.CalledProcessError:
            return "Unavailable"

    @staticmethod
    def get_active_network_interface():
        """Identify the currently active network interface."""
        active_interfaces = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    active_interfaces.append(interface)
        return ", ".join(active_interfaces) if active_interfaces else "None"

    def __str__(self):
        return (
            f"Host ID: {self.host_identifier}, "
            f"Hostname: {self.hostname}, IP Address: {self.ip_address}, "
            f"Operating System: {self.operating_system}, Total Memory: {self.total_memory:.1f}GB, "
            f"CPU: {self.cpu_name} {self.cpu_speed:.2f}MHz {self.cpu_cores}C/{self.cpu_threads}T, "
            f"Storage Used: {self.used_storage:.2f}/{self.disk_storage:.2f}GB, Network Interface: {self.network_interface}"
        )


CURRENT_HOST_INFO = HostSystem()

if __name__ == "__main__":
    # Example Usage
    print(CURRENT_HOST_INFO)
    another_host = HostSystem(
        hostname="AnotherHost",
        ip_address="192.168.1.2",
        operating_system="Linux",
        cpu_cores=4,
        cpu_threads=4,
        total_memory=16.0,
    )
    print(another_host)
