#!/bin/bash
# Installation script for DNS Changer on Ubuntu Server

echo "🚀 Installing DNS Changer for Ubuntu Server..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script as root or with sudo"
    echo "Usage: sudo bash install.sh"
    exit 1
fi

# Update package list
echo "📦 Updating package list..."
apt update

# Install required packages
echo "📦 Installing required packages..."
apt install -y python3 python3-pip dnsutils

# Make the script executable
chmod +x dns_changer.py

# Create a symbolic link in /usr/local/bin for easy access
ln -sf "$(pwd)/dns_changer.py" /usr/local/bin/dns-changer

echo "✅ Installation completed!"
echo ""
echo "📋 Usage:"
echo "  dns-changer              - Apply DNS configuration"
echo "  dns-changer --status     - Show current DNS status"
echo "  dns-changer --test       - Test DNS resolution"
echo "  dns-changer --help       - Show help"
echo ""
echo "🔧 To apply DNS configuration now, run:"
echo "  sudo dns-changer"
