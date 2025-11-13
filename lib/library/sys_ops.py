from pathlib import Path


def is_vm() -> bool:
    """Detect if the system is a VM using DMI information"""

    dmi_path = Path("/sys/class/dmi/id")

    vm_signatures = [
        "vmware",
        "virtualbox",
        "innotek gmbh",
        "kvm",
        "qemu",
        "xen",
        "microsoft corporation",
        "virtual machine",
        "amazon ec2",
        "google compute engine",
    ]

    for field in ["product_name", "sys_vendor", "bios_vendor"]:
        file_path = dmi_path / field
        if file_path.exists():
            try:
                content = file_path.read_text().strip().lower()
                if any(sig in content for sig in vm_signatures):
                    return True
            except (IOError, PermissionError):
                continue

    return False


def is_laptop(logger) -> bool:
    """Detect if the system is a laptop or desktop on Linux systems"""

    battery_dir = Path("/sys/class/power_supply")
    battery_found = False
    ac_power_found = False

    try:
        if not battery_dir.is_dir():
            logger.debug("Power supply directory not found")
            return False

        for entry in battery_dir.iterdir():
            if not entry.is_dir():
                continue

            name = entry.name.upper()

            # Check for battery devices
            if name.startswith("BAT"):
                # Check if it has capacity file
                capacity_file = entry / "capacity"
                if capacity_file.exists():
                    battery_found = True
                    logger.debug(f"Found battery: {entry.name}")

            # Check for AC power (common on laptops)
            elif name.startswith(("AC", "ADP")):
                ac_power_found = True
                logger.debug(f"Found AC power supply: {entry.name}")

        # Consider it a laptop if we found a battery with capacity info
        # or if we found both battery and AC power
        return battery_found or (
            ac_power_found
            and any(
                e.name.upper().startswith("BAT")
                for e in battery_dir.iterdir()
                if e.is_dir()
            )
        )

    except PermissionError:
        logger.warning("Permission denied accessing power supply information")
        return False
    except Exception as e:
        logger.error(f"Unexpected error detecting laptop: {e}")
        return False
