#!/bin/bash
# DNS Troubleshooting Script for Ubuntu Server

echo "🔧 DNS Troubleshooting Script"
echo "============================="

# Check if dnsmasq is installed and running
echo -e "\n📦 Checking dnsmasq status..."
if systemctl is-active --quiet dnsmasq; then
    echo "✅ dnsmasq is running"
    systemctl status dnsmasq --no-pager -l
else
    echo "❌ dnsmasq is not running"
    echo "🔧 Attempting to fix dnsmasq..."
    
    # Stop systemd-resolved first
    systemctl stop systemd-resolved
    echo "✅ Stopped systemd-resolved"
    
    # Start dnsmasq
    systemctl start dnsmasq
    if systemctl is-active --quiet dnsmasq; then
        echo "✅ dnsmasq started successfully"
    else
        echo "❌ Failed to start dnsmasq"
        echo "📋 dnsmasq service status:"
        systemctl status dnsmasq --no-pager -l
        echo "📋 dnsmasq logs:"
        journalctl -u dnsmasq --no-pager -l -n 20
    fi
fi

# Check port 53 usage
echo -e "\n🔍 Checking port 53 usage..."
netstat -tulpn | grep :53 || echo "No services listening on port 53"

# Test DNS resolution
echo -e "\n🧪 Testing DNS resolution..."
test_domains=("google.com" "github.com" "youtube.com" "facebook.com")

for domain in "${test_domains[@]}"; do
    if nslookup "$domain" >/dev/null 2>&1; then
        echo "✅ $domain - OK"
    else
        echo "❌ $domain - FAILED"
    fi
done

# Show current DNS configuration
echo -e "\n📄 Current DNS Configuration:"
echo "--- /etc/resolv.conf ---"
cat /etc/resolv.conf

if [ -f /etc/dnsmasq.conf ]; then
    echo -e "\n--- /etc/dnsmasq.conf (first 20 lines) ---"
    head -20 /etc/dnsmasq.conf
fi

# Test specific DNS servers
echo -e "\n🧪 Testing specific DNS servers..."
echo "Testing Shecan DNS (178.22.122.100):"
nslookup google.com 178.22.122.100 | grep -E "(Server|Address|Name)"

echo -e "\nTesting Cloudflare DNS (1.1.1.1):"
nslookup google.com 1.1.1.1 | grep -E "(Server|Address|Name)"

echo -e "\n✅ Troubleshooting complete!"
