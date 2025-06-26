# DNS Changer for Ubuntu Server

A Python script that applies DNS configuration similar to YogaDNS on Ubuntu Server. This script configures your system to use Iranian DNS servers (Shecan) for most traffic while routing social media sites through Cloudflare DNS.

## Features

- 🔧 **Multiple DNS Configuration Methods**: Configures systemd-resolved, resolv.conf, and netplan
- 🌐 **Smart DNS Routing**: Different DNS servers for different site categories
- 🛡️ **Backup System**: Automatically backs up existing DNS configuration
- 🧪 **Testing Tools**: Built-in DNS resolution testing
- 📊 **Status Monitoring**: View current DNS configuration status

## DNS Server Configuration

Based on your YogaDNS profile, the script configures:

### Primary DNS Pool (Shecan - Iranian DNS)
- **Primary**: 178.22.122.100 (Shecan 1)
- **Secondary**: 185.51.200.2 (Shecan 2)
- **Used for**: Development sites, general browsing

### Cloudflare DNS (1.1.1.1)
- **Primary**: 1.1.1.1
- **Secondary**: 1.0.0.1
- **Used for**: Social media sites (YouTube, Instagram, Facebook, X/Twitter)

## Site Categories

### Development Sites (Shecan DNS)
- Visual Studio Code related (*.visualstudio.com, *.vscode-cdn.net)
- GitHub (*.github.com, *.githubusercontent.com)
- Docker (*.docker.io, *.docker.com)
- Google Cloud/APIs (*.googleapis.com, *.dl.google.com)
- Development tools (*.npmjs.org, *.golang.org, *.k8s.io)
- And many more...

### Social Media Sites (Cloudflare DNS)
- YouTube (*.youtube.com, *.ytimg.com, *.googlevideo.com)
- Instagram (*.instagram.com, *.cdninstagram.com)
- Facebook (*.facebook.com, *.fbcdn.net)
- X/Twitter (*.x.com, *.twimg.com)

## Installation

1. **Download the script to your Ubuntu server**:
   ```bash
   wget https://github.com/ahyaghoubi/dns-changer/raw/main/dns_changer.py
   # OR
   git clone https://github.com/ahyaghoubi/dns-changer.git
   cd dns-changer
   ```

2. **Run the installation script**:
   ```bash
   sudo bash install.sh
   ```

3. **Or install manually**:
   ```bash
   # Make executable
   chmod +x dns_changer.py
   
   # Install required packages
   sudo apt update
   sudo apt install -y python3 python3-pip dnsutils
   ```

## Usage

### Apply DNS Configuration
```bash
sudo python3 dns_changer.py
# OR if installed via install.sh
sudo dns-changer
```

### Check Current DNS Status
```bash
sudo python3 dns_changer.py --status
# OR
sudo dns-changer --status
```

### Test DNS Resolution
```bash
sudo python3 dns_changer.py --test
# OR
sudo dns-changer --test
```

### Show Help
```bash
python3 dns_changer.py --help
# OR
dns-changer --help
```

## What the Script Does

1. **Backup Configuration**: Creates backups of existing DNS configuration files
2. **Configure systemd-resolved**: Updates `/etc/systemd/resolved.conf`
3. **Configure resolv.conf**: Updates `/etc/resolv.conf` with new DNS servers
4. **Configure Netplan**: Updates netplan configuration if present
5. **Install dnsmasq**: Sets up advanced DNS routing for different site categories
6. **Flush DNS Cache**: Clears existing DNS cache
7. **Test Configuration**: Verifies DNS resolution is working

## Configuration Files Modified

- `/etc/resolv.conf` - Primary DNS configuration
- `/etc/systemd/resolved.conf` - systemd-resolved configuration
- `/etc/netplan/*.yaml` - Network configuration (if present)
- `/etc/dnsmasq.conf` - Advanced DNS routing configuration

## Backup Location

All original configuration files are backed up to `/etc/dns-backup/` before making changes.

## Troubleshooting

### DNS Not Working
```bash
# Check DNS status
sudo dns-changer --status

# Test DNS resolution
sudo dns-changer --test

# Restart services
sudo systemctl restart systemd-resolved
sudo systemctl restart dnsmasq
sudo systemctl restart networking
```

### Restore Original Configuration
```bash
# Restore from backup
sudo cp /etc/dns-backup/resolv.conf /etc/resolv.conf
sudo cp /etc/dns-backup/resolved.conf /etc/systemd/resolved.conf

# Restart services
sudo systemctl restart systemd-resolved
sudo systemctl restart networking
```

### Check Service Status
```bash
# Check systemd-resolved
sudo systemctl status systemd-resolved

# Check dnsmasq
sudo systemctl status dnsmasq

# Check DNS resolution manually
nslookup google.com
dig @178.22.122.100 github.com
```

## Requirements

- Ubuntu Server 18.04 or later
- Python 3.6 or later
- Root/sudo privileges
- Internet connection

## Security Notes

- This script requires root privileges to modify system DNS configuration
- All changes are logged and backed up
- Original configuration can be easily restored
- The script only modifies DNS settings, not other network configurations

## License

This script is provided as-is for educational and personal use. Use at your own risk.

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your Ubuntu version is supported
3. Ensure you have root privileges
4. Check if your system uses systemd-resolved or other DNS management systems
