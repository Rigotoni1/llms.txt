#!/usr/bin/env python3
"""
Real-time monitoring script for Railway-deployed LLMs.txt Generator
Continuously monitors app health, performance, and logs
"""

import requests
import time
import json
import threading
from datetime import datetime, timedelta
import signal
import sys

# Replace with your actual Railway app URL
RAILWAY_URL = "https://llms-txt-production.up.railway.app"

class RailwayMonitor:
    def __init__(self, base_url, check_interval=30):
        self.base_url = base_url
        self.check_interval = check_interval
        self.running = True
        self.stats = {
            'checks': 0,
            'successful': 0,
            'failed': 0,
            'avg_response_time': 0,
            'response_times': [],
            'last_check': None,
            'uptime': datetime.now()
        }
        self.lock = threading.Lock()
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down monitor...")
        self.running = False
    
    def check_health(self):
        """Check basic app health"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            duration = time.time() - start_time
            
            with self.lock:
                self.stats['checks'] += 1
                self.stats['last_check'] = datetime.now()
                self.stats['response_times'].append(duration)
                
                # Keep only last 100 response times
                if len(self.stats['response_times']) > 100:
                    self.stats['response_times'] = self.stats['response_times'][-100:]
                
                self.stats['avg_response_time'] = sum(self.stats['response_times']) / len(self.stats['response_times'])
                
                if response.status_code == 200:
                    self.stats['successful'] += 1
                    return True, duration, response.status_code
                else:
                    self.stats['failed'] += 1
                    return False, duration, response.status_code
                    
        except Exception as e:
            duration = time.time() - start_time
            with self.lock:
                self.stats['checks'] += 1
                self.stats['failed'] += 1
                self.stats['last_check'] = datetime.now()
            
            return False, duration, str(e)
    
    def check_api_endpoints(self):
        """Check API endpoints health"""
        endpoints = [
            "/api/sample-config",
            "/api/tiers"
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                results[endpoint] = {
                    'status': response.status_code,
                    'healthy': response.status_code == 200
                }
            except Exception as e:
                results[endpoint] = {
                    'status': str(e),
                    'healthy': False
                }
        
        return results
    
    def check_redis_connection(self):
        """Check if Redis is accessible (if you have Redis monitoring endpoint)"""
        try:
            # This assumes you have a Redis health check endpoint
            response = requests.get(f"{self.base_url}/api/health/redis", timeout=5)
            return response.status_code == 200
        except:
            return None  # Endpoint might not exist
    
    def check_worker_status(self):
        """Check worker queue status"""
        try:
            response = requests.get(f"{self.base_url}/api/queue-status", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def display_status(self):
        """Display current status"""
        with self.lock:
            uptime = datetime.now() - self.stats['uptime']
            success_rate = (self.stats['successful'] / self.stats['checks'] * 100) if self.stats['checks'] > 0 else 0
            
            print(f"\n📊 RAILWAY APP STATUS - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 60)
            print(f"🏥 Health Checks: {self.stats['checks']} total")
            print(f"✅ Successful: {self.stats['successful']}")
            print(f"❌ Failed: {self.stats['failed']}")
            print(f"📈 Success Rate: {success_rate:.1f}%")
            print(f"⏱️ Avg Response Time: {self.stats['avg_response_time']:.2f}s")
            print(f"⏰ Uptime: {str(uptime).split('.')[0]}")
            
            if self.stats['last_check']:
                time_since_last = datetime.now() - self.stats['last_check']
                print(f"🕐 Last Check: {time_since_last.total_seconds():.0f}s ago")
    
    def display_api_status(self, api_results):
        """Display API endpoints status"""
        print(f"\n🔌 API ENDPOINTS STATUS")
        print("-" * 30)
        for endpoint, result in api_results.items():
            status_icon = "✅" if result['healthy'] else "❌"
            print(f"{status_icon} {endpoint}: {result['status']}")
    
    def display_worker_status(self, worker_status):
        """Display worker queue status"""
        if worker_status:
            print(f"\n👷 WORKER STATUS")
            print("-" * 20)
            print(f"Batch Queue: {worker_status.get('batch_queue', 'N/A')}")
            print(f"Merge Queue: {worker_status.get('merge_queue', 'N/A')}")
            print(f"Active Workers: {worker_status.get('workers', 'N/A')}")
    
    def log_alert(self, message, level="WARNING"):
        """Log alerts to file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        with open('railway_monitor.log', 'a') as f:
            f.write(log_entry)
        
        print(f"🚨 {level}: {message}")
    
    def check_for_alerts(self, health_ok, response_time, api_results):
        """Check for potential issues and alert"""
        alerts = []
        
        # Response time alerts
        if response_time > 5.0:
            alerts.append(f"High response time: {response_time:.2f}s")
        
        # Health check alerts
        if not health_ok:
            alerts.append("Health check failed")
        
        # API endpoint alerts
        failed_apis = [ep for ep, result in api_results.items() if not result['healthy']]
        if failed_apis:
            alerts.append(f"Failed APIs: {', '.join(failed_apis)}")
        
        # Success rate alerts
        with self.lock:
            if self.stats['checks'] > 10:
                recent_success_rate = (self.stats['successful'] / self.stats['checks']) * 100
                if recent_success_rate < 90:
                    alerts.append(f"Low success rate: {recent_success_rate:.1f}%")
        
        # Log alerts
        for alert in alerts:
            self.log_alert(alert)
    
    def run_monitoring_loop(self):
        """Main monitoring loop"""
        print(f"🔍 Starting Railway App Monitor")
        print(f"🎯 Target: {self.base_url}")
        print(f"⏰ Check Interval: {self.check_interval}s")
        print("Press Ctrl+C to stop monitoring")
        print("=" * 60)
        
        while self.running:
            try:
                # Health check
                health_ok, response_time, status = self.check_health()
                
                # API endpoints check
                api_results = self.check_api_endpoints()
                
                # Worker status check
                worker_status = self.check_worker_status()
                
                # Display status
                self.display_status()
                self.display_api_status(api_results)
                self.display_worker_status(worker_status)
                
                # Check for alerts
                self.check_for_alerts(health_ok, response_time, api_results)
                
                # Wait for next check
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log_alert(f"Monitor error: {str(e)}", "ERROR")
                time.sleep(self.check_interval)
        
        # Final summary
        self.display_final_summary()
    
    def display_final_summary(self):
        """Display final monitoring summary"""
        with self.lock:
            uptime = datetime.now() - self.stats['uptime']
            success_rate = (self.stats['successful'] / self.stats['checks'] * 100) if self.stats['checks'] > 0 else 0
            
            print(f"\n📋 MONITORING SUMMARY")
            print("=" * 40)
            print(f"Total Runtime: {str(uptime).split('.')[0]}")
            print(f"Total Checks: {self.stats['checks']}")
            print(f"Success Rate: {success_rate:.1f}%")
            print(f"Average Response Time: {self.stats['avg_response_time']:.2f}s")
            print(f"Log File: railway_monitor.log")

def main():
    """Start the monitoring"""
    if not RAILWAY_URL or RAILWAY_URL == "https://your-app-name.railway.app":
        print("❌ Please update RAILWAY_URL with your actual Railway app URL")
        return
    
    # Get check interval from command line or use default
    check_interval = 30
    if len(sys.argv) > 1:
        try:
            check_interval = int(sys.argv[1])
        except ValueError:
            print("Invalid check interval. Using default 30 seconds.")
    
    monitor = RailwayMonitor(RAILWAY_URL, check_interval)
    monitor.run_monitoring_loop()

if __name__ == "__main__":
    main() 