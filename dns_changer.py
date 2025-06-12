#!/usr/bin/env python3
"""
DNS Configuration Script for Ubuntu Server
Applies DNS settings similar to YogaDNS configuration
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

class DNSManager:
    def __init__(self):
        self.dns_servers = {
            'shecan_doh': '178.22.122.100',
            'shecan_1': '178.22.122.100', 
            'shecan_2': '185.51.200.2',
            'cloudflare': '1.1.1.1',
            'cloudflare_secondary': '1.0.0.1'
        }
        
        # Host categories based on YogaDNS rules
        self.host_categories = {
            'development_hosts': [
                '*.default.exp-tas.com',
                '*.main.vscode-cdn.net', 
                '*.update.code.visualstudio.com',
                '*.mobile.events.data.microsoft.com',
                '*.vscode-sync.trafficmanager.net',
                '*.visualstudio.com',
                '*.githubusercontent.com',
                '*.github.com',
                '*.azure.com',
                '*.githubcopilot.com',
                '*.npmjs.org',
                '*.gemini.google.com',
                '*.notebooklm.google.com',
                '*.cursor.com',
                '*.mozgcp.net',
                '*.ubuntu.com',
                '*.docker.io',
                '*.docker.com',
                '*.k8s.io',
                '*.warp.dev',
                '*.dl.google.com',
                '*.golang.org',
                '*.go.dev',
                '*.googleapis.com',
                '*.intel.com',
                '*.enterprisedb.com',
                '*.modernc.org',
                '*.upwork.com',
                '*.udemy.com',
                '*.udemycdn.com',
                '*.onetrust.com',
                '*.nvidia.com'
            ],
            'social_media_hosts': [
                '*.youtube.com',
                '*.ytimg.com',
                '*.googlevideo.com',
                '*.x.com',
                '*.instagram.com',
                '*.fbcdn.net',
                '*.cdninstagram.com',
                '*.facebook.com',
                '*.twimg.com'
            ]
        }

    def check_root_privileges(self):
        """Check if script is running with root privileges"""
        if os.geteuid() != 0:
            print("❌ This script requires root privileges!")
            print("Please run with: sudo python3 dns_changer.py")
            sys.exit(1)

    def backup_dns_config(self):
        """Backup current DNS configuration"""
        backup_dir = Path("/etc/dns-backup")
        backup_dir.mkdir(exist_ok=True)
        
        files_to_backup = [
            "/etc/resolv.conf",
            "/etc/systemd/resolved.conf",
            "/etc/netplan/00-installer-config.yaml"
        ]
        
        for file_path in files_to_backup:
            if Path(file_path).exists():
                backup_path = backup_dir / Path(file_path).name
                shutil.copy2(file_path, backup_path)
                print(f"✅ Backed up {file_path} to {backup_path}")

    def configure_systemd_resolved(self):
        """Configure systemd-resolved with our DNS servers"""
        config_content = f"""[Resolve]
DNS={self.dns_servers['shecan_1']} {self.dns_servers['shecan_2']} {self.dns_servers['cloudflare']}
FallbackDNS={self.dns_servers['cloudflare_secondary']}
Domains=~.
DNSSEC=no
DNSOverTLS=no
Cache=yes
DNSStubListener=yes
ReadEtcHosts=yes
"""
        
        try:
            with open("/etc/systemd/resolved.conf", "w") as f:
                f.write(config_content)
            print("✅ Updated /etc/systemd/resolved.conf")
            
            # Restart systemd-resolved
            subprocess.run(["systemctl", "restart", "systemd-resolved"], check=True)
            print("✅ Restarted systemd-resolved service")
            
        except Exception as e:
            print(f"❌ Error configuring systemd-resolved: {e}")

    def configure_resolv_conf(self):
        """Configure /etc/resolv.conf"""
        resolv_content = f"""# DNS configuration applied by dns_changer.py
nameserver {self.dns_servers['shecan_1']}
nameserver {self.dns_servers['shecan_2']}
nameserver {self.dns_servers['cloudflare']}
options timeout:2 attempts:3 rotate single-request-reopen
"""
        
        try:
            # Remove symlink if it exists
            resolv_path = Path("/etc/resolv.conf")
            if resolv_path.is_symlink():
                resolv_path.unlink()
            
            with open("/etc/resolv.conf", "w") as f:
                f.write(resolv_content)
            print("✅ Updated /etc/resolv.conf")
            
        except Exception as e:
            print(f"❌ Error configuring resolv.conf: {e}")

    def configure_netplan(self):
        """Configure netplan if it exists"""
        netplan_files = list(Path("/etc/netplan").glob("*.yaml"))
        
        if not netplan_files:
            print("ℹ️  No netplan configuration found")
            return
            
        for netplan_file in netplan_files:
            try:
                # Read existing configuration
                with open(netplan_file, 'r') as f:
                    content = f.read()
                
                # Add DNS configuration if not present
                if 'nameservers:' not in content:
                    dns_config = f"""
      nameservers:
        addresses:
          - {self.dns_servers['shecan_1']}
          - {self.dns_servers['shecan_2']}
          - {self.dns_servers['cloudflare']}
"""
                    
                    # Simple insertion after dhcp4 line
                    if 'dhcp4: true' in content:
                        content = content.replace('dhcp4: true', 
                                                f'dhcp4: true{dns_config}')
                        
                        with open(netplan_file, 'w') as f:
                            f.write(content)
                        
                        print(f"✅ Updated {netplan_file}")
                        
                        # Apply netplan configuration
                        subprocess.run(["netplan", "apply"], check=True)
                        print("✅ Applied netplan configuration")
                
            except Exception as e:
                print(f"❌ Error configuring netplan {netplan_file}: {e}")

    def install_dnsmasq(self):
        """Install and configure dnsmasq for advanced DNS routing"""
        try:
            # Install dnsmasq
            subprocess.run(["apt", "update"], check=True)
            subprocess.run(["apt", "install", "-y", "dnsmasq"], check=True)
            print("✅ Installed dnsmasq")
            
            # Stop systemd-resolved to free port 53
            subprocess.run(["systemctl", "stop", "systemd-resolved"], check=False)
            print("✅ Stopped systemd-resolved to free port 53")
            
            # Configure dnsmasq
            dnsmasq_config = f"""# DNS configuration for YogaDNS-like behavior
port=53
domain-needed
bogus-priv
no-resolv
cache-size=1000
listen-address=127.0.0.1
bind-interfaces

# Default DNS servers (Shecan)
server={self.dns_servers['shecan_1']}
server={self.dns_servers['shecan_2']}

# Social media sites use Cloudflare
"""
            
            # Add specific server configurations for social media
            for host in self.host_categories['social_media_hosts']:
                domain = host.replace('*.', '')
                dnsmasq_config += f"server=/{domain}/{self.dns_servers['cloudflare']}\n"
            
            dnsmasq_config += f"""
# Development sites use Shecan pool
"""
            for host in self.host_categories['development_hosts']:
                domain = host.replace('*.', '')
                dnsmasq_config += f"server=/{domain}/{self.dns_servers['shecan_1']}\n"
            
            with open("/etc/dnsmasq.conf", "w") as f:
                f.write(dnsmasq_config)
            
            print("✅ Configured dnsmasq")
            
            # Update resolv.conf to point to localhost
            resolv_content = """# DNS configuration - pointing to local dnsmasq
nameserver 127.0.0.1
options timeout:2 attempts:3
"""
            with open("/etc/resolv.conf", "w") as f:
                f.write(resolv_content)
            print("✅ Updated resolv.conf to use local dnsmasq")
            
            # Start and enable dnsmasq
            subprocess.run(["systemctl", "enable", "dnsmasq"], check=True)
            subprocess.run(["systemctl", "restart", "dnsmasq"], check=True)
            print("✅ Started dnsmasq service")
            
            # Check if dnsmasq is running
            result = subprocess.run(["systemctl", "is-active", "dnsmasq"], 
                                  capture_output=True, text=True)
            if result.stdout.strip() == "active":
                print("✅ dnsmasq service is running successfully")
            else:
                print("⚠️  dnsmasq may not be running properly")
            
        except Exception as e:
            print(f"❌ Error installing/configuring dnsmasq: {e}")
            print("ℹ️  Attempting fallback configuration...")
            # Fallback: restart systemd-resolved if dnsmasq fails
            try:
                subprocess.run(["systemctl", "start", "systemd-resolved"], check=False)
                print("✅ Restarted systemd-resolved as fallback")
            except:
                pass

    def flush_dns_cache(self):
        """Flush DNS cache"""
        try:
            # Try resolvectl first (newer Ubuntu versions)
            result = subprocess.run(["resolvectl", "flush-caches"], check=False)
            if result.returncode == 0:
                print("✅ Flushed DNS cache with resolvectl")
            else:
                # Fallback to systemd-resolve (older versions)
                subprocess.run(["systemd-resolve", "--flush-caches"], check=True)
                print("✅ Flushed systemd-resolved cache")
            
            # Restart networking
            subprocess.run(["systemctl", "restart", "networking"], check=False)
            print("✅ Restarted networking service")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not flush DNS cache: {e}")

    def test_dns_resolution(self):
        """Test DNS resolution with configured servers"""
        test_domains = ['google.com', 'github.com', 'youtube.com', 'iana.org']
        
        print("\n🧪 Testing DNS resolution...")
        for domain in test_domains:
            try:
                result = subprocess.run(['nslookup', domain], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"✅ {domain} - Resolved successfully")
                else:
                    print(f"❌ {domain} - Resolution failed")
            except Exception as e:
                print(f"❌ {domain} - Error: {e}")

    def show_current_dns_status(self):
        """Show current DNS configuration status"""
        print("\n📋 Current DNS Status:")
        
        try:
            # Show resolv.conf content
            with open("/etc/resolv.conf", "r") as f:
                print("📄 /etc/resolv.conf:")
                print(f.read())
        except Exception as e:
            print(f"❌ Could not read resolv.conf: {e}")
        
        try:
            # Show systemd-resolved status - try newer command first
            result = subprocess.run(["resolvectl", "status"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("📄 resolvectl status:")
                print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            else:
                # Fallback to older command
                result = subprocess.run(["systemd-resolve", "--status"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("📄 systemd-resolved status:")
                    print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        except Exception as e:
            print(f"❌ Could not get DNS resolver status: {e}")
        
        try:
            # Show dnsmasq status if running
            result = subprocess.run(["systemctl", "is-active", "dnsmasq"], 
                                  capture_output=True, text=True)
            if result.stdout.strip() == "active":
                print("📄 dnsmasq service: ✅ Active")
            else:
                print("📄 dnsmasq service: ❌ Inactive")
        except Exception as e:
            print(f"📄 dnsmasq service: ❓ Status unknown")

    def apply_configuration(self):
        """Apply all DNS configurations"""
        print("🚀 Starting DNS configuration...")
        
        self.check_root_privileges()
        self.backup_dns_config()
        
        print("\n📝 Applying DNS configuration...")
        self.configure_resolv_conf()
        self.configure_systemd_resolved()
        self.configure_netplan()
        
        print("\n🔧 Installing advanced DNS routing...")
        self.install_dnsmasq()
        
        print("\n🧹 Flushing DNS cache...")
        self.flush_dns_cache()
        
        print("\n📋 Current configuration:")
        self.show_current_dns_status()
        
        print("\n🧪 Testing DNS resolution:")
        self.test_dns_resolution()
        
        print("\n✅ DNS configuration applied successfully!")
        print("📌 Configuration details:")
        print(f"   • Primary DNS: {self.dns_servers['shecan_1']} (Shecan)")
        print(f"   • Secondary DNS: {self.dns_servers['shecan_2']} (Shecan)")
        print(f"   • Fallback DNS: {self.dns_servers['cloudflare']} (Cloudflare)")
        print("   • Social media sites routed through Cloudflare")
        print("   • Development sites routed through Shecan")
        print("   • All other sites use default Shecan servers")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            dns_manager = DNSManager()
            dns_manager.show_current_dns_status()
            return
        elif sys.argv[1] == "--test":
            dns_manager = DNSManager()
            dns_manager.test_dns_resolution()
            return
        elif sys.argv[1] == "--help":
            print("DNS Changer for Ubuntu Server")
            print("Usage:")
            print("  python3 dns_changer.py          - Apply DNS configuration")
            print("  python3 dns_changer.py --status - Show current DNS status")
            print("  python3 dns_changer.py --test   - Test DNS resolution")
            print("  python3 dns_changer.py --help   - Show this help")
            return
    
    dns_manager = DNSManager()
    dns_manager.apply_configuration()

if __name__ == "__main__":
    main()
