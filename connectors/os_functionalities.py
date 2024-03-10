import platform
import subprocess
import distro


def discover_package_manager():
    # Discover the Linux distribution using 'distro'
    distro_info = distro.id().lower()

    if 'centos' in distro_info or 'redhat' in distro_info:
        return 'yum'
    elif 'ubuntu' in distro_info or 'debian' in distro_info:
        return 'apt'
    elif 'fedora' in distro_info:
        return 'dnf'
    elif 'suse' in distro_info or 'opensuse' in distro_info:
        return 'zypper'
    else:
        # For other distributions, attempt to determine the package manager dynamically
        try:
            result = subprocess.run(['which', 'yum'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                return 'yum'
        except FileNotFoundError:
            pass

        try:
            result = subprocess.run(['which', 'apt-get'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                return 'apt'
        except FileNotFoundError:
            pass

        try:
            result = subprocess.run(['which', 'dnf'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                return 'dnf'
        except FileNotFoundError:
            pass

        try:
            result = subprocess.run(['which', 'zypper'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                return 'zypper'
        except FileNotFoundError:
            pass

    # If no package manager is found, return None
    return None


def check_distro_and_kernel():
    # Discover the Linux distribution
    distro_name = distro.name().lower()

    # Get the kernel version
    kernel_version = platform.release()

    # Check if the distribution is up to date
    distro_up_to_date = False
    if 'centos' in distro_name or 'red hat' in distro_name:
        # For CentOS and Red Hat, check for updates using 'yum'
        result = subprocess.run(['yum', 'check-update'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        distro_up_to_date = result.returncode != 100
    elif 'ubuntu' in distro_name or 'debian' in distro_name:
        # For Ubuntu and Debian, check for updates using 'apt-get'
        result = subprocess.run(['apt-get', 'update', '-qq'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            result = subprocess.run(['apt-get', 'upgrade', '-s'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            distro_up_to_date = result.returncode == 0
    elif 'fedora' in distro_name:
        # For Fedora, check for updates using 'dnf'
        result = subprocess.run(['dnf', 'check-update'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        distro_up_to_date = result.returncode != 0
    elif 'suse' in distro_name or 'opensuse' in distro_name:
        # For SUSE and openSUSE, check for updates using 'zypper'
        result = subprocess.run(['zypper', '--non-interactive', 'lu'], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        distro_up_to_date = result.returncode != 0

    # Return the distribution name, kernel version, and update status
    return distro_name, kernel_version, distro_up_to_date


print(check_distro_and_kernel())
print(discover_package_manager())
