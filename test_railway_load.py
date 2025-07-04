#!/usr/bin/env python3
"""
Load testing script for Railway-deployed LLMs.txt Generator
Tests concurrent requests and performance
"""

import requests
import time
import threading
import concurrent.futures
from datetime import datetime

# Replace with your actual Railway app URL
RAILWAY_URL = "https://llms-txt-production.up.railway.app"

class LoadTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.results = []
        self.lock = threading.Lock()
    
    def make_request(self, endpoint, method="GET", data=None, timeout=10):
        """Make a single request and record results"""
        start_time = time.time()
        success = False
        status_code = None
        error = None
        
        try:
            if method == "GET":
                response = requests.get(f"{self.base_url}{endpoint}", timeout=timeout)
            elif method == "POST":
                response = requests.post(f"{self.base_url}{endpoint}", json=data, timeout=timeout)
            
            status_code = response.status_code
            success = response.status_code < 400
            
        except Exception as e:
            error = str(e)
        
        end_time = time.time()
        duration = end_time - start_time
        
        with self.lock:
            self.results.append({
                'endpoint': endpoint,
                'method': method,
                'success': success,
                'status_code': status_code,
                'duration': duration,
                'error': error,
                'timestamp': datetime.now()
            })
        
        return success, status_code, duration, error
    
    def test_concurrent_health_checks(self, num_requests=10):
        """Test concurrent health check requests"""
        print(f"🏥 Testing {num_requests} concurrent health checks...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [
                executor.submit(self.make_request, "/")
                for _ in range(num_requests)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                future.result()
    
    def test_concurrent_api_calls(self, num_requests=5):
        """Test concurrent API calls"""
        print(f"🔌 Testing {num_requests} concurrent API calls...")
        
        endpoints = [
            ("/api/sample-config", "GET"),
            ("/api/tiers", "GET"),
        ]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = []
            for endpoint, method in endpoints:
                for _ in range(num_requests // len(endpoints)):
                    futures.append(
                        executor.submit(self.make_request, endpoint, method)
                    )
            
            for future in concurrent.futures.as_completed(futures):
                future.result()
    
    def test_sitemap_validation_load(self, num_requests=3):
        """Test sitemap validation under load"""
        print(f"🗺️ Testing {num_requests} concurrent sitemap validations...")
        
        test_sitemaps = [
            "https://example.com/sitemap.xml",
            "https://google.com/sitemap.xml",
            "https://github.com/sitemap.xml"
        ]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = []
            for i in range(num_requests):
                sitemap = test_sitemaps[i % len(test_sitemaps)]
                futures.append(
                    executor.submit(
                        self.make_request, 
                        "/api/validate-sitemap", 
                        "POST", 
                        {"sitemap_url": sitemap}
                    )
                )
            
            for future in concurrent.futures.as_completed(futures):
                future.result()
    
    def test_generation_requests(self, num_requests=2):
        """Test generation requests (be careful with this!)"""
        print(f"🚀 Testing {num_requests} generation requests...")
        
        test_configs = [
            {
                "site_name": f"Test Site {i}",
                "sitemap_url": "https://example.com/sitemap.xml",
                "max_pages_to_process": 1,
                "max_blogs": 1,
                "max_products": 1
            }
            for i in range(num_requests)
        ]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = []
            for config in test_configs:
                futures.append(
                    executor.submit(
                        self.make_request, 
                        "/generate", 
                        "POST", 
                        config
                    )
                )
            
            for future in concurrent.futures.as_completed(futures):
                future.result()
    
    def print_results(self):
        """Print test results summary"""
        if not self.results:
            print("❌ No results to display")
            return
        
        print("\n📊 LOAD TEST RESULTS")
        print("=" * 50)
        
        # Overall stats
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r['success'])
        failed_requests = total_requests - successful_requests
        
        print(f"Total Requests: {total_requests}")
        print(f"Successful: {successful_requests}")
        print(f"Failed: {failed_requests}")
        print(f"Success Rate: {(successful_requests/total_requests)*100:.1f}%")
        
        # Duration stats
        durations = [r['duration'] for r in self.results if r['duration'] is not None]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            
            print(f"\n⏱️ Response Times:")
            print(f"Average: {avg_duration:.2f}s")
            print(f"Maximum: {max_duration:.2f}s")
            print(f"Minimum: {min_duration:.2f}s")
        
        # Endpoint breakdown
        print(f"\n🔍 Endpoint Breakdown:")
        endpoint_stats = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {'total': 0, 'success': 0, 'durations': []}
            
            endpoint_stats[endpoint]['total'] += 1
            if result['success']:
                endpoint_stats[endpoint]['success'] += 1
            if result['duration']:
                endpoint_stats[endpoint]['durations'].append(result['duration'])
        
        for endpoint, stats in endpoint_stats.items():
            success_rate = (stats['success'] / stats['total']) * 100
            avg_dur = sum(stats['durations']) / len(stats['durations']) if stats['durations'] else 0
            print(f"  {endpoint}: {stats['success']}/{stats['total']} ({success_rate:.1f}%) - avg {avg_dur:.2f}s")
        
        # Error summary
        errors = [r for r in self.results if r['error']]
        if errors:
            print(f"\n❌ Errors:")
            error_counts = {}
            for error in errors:
                error_msg = error['error']
                error_counts[error_msg] = error_counts.get(error_msg, 0) + 1
            
            for error_msg, count in error_counts.items():
                print(f"  {error_msg}: {count} times")

def main():
    """Run load tests"""
    if not RAILWAY_URL or RAILWAY_URL == "https://your-app-name.railway.app":
        print("❌ Please update RAILWAY_URL with your actual Railway app URL")
        return
    
    print("🧪 Railway App Load Testing")
    print("=" * 50)
    
    tester = LoadTester(RAILWAY_URL)
    
    # Run different load tests
    tester.test_concurrent_health_checks(10)
    time.sleep(2)  # Brief pause between tests
    
    tester.test_concurrent_api_calls(5)
    time.sleep(2)
    
    tester.test_sitemap_validation_load(3)
    time.sleep(2)
    
    # Be careful with generation tests - they can be resource intensive
    print("⚠️ Generation tests can be resource intensive. Continue? (y/n): ", end="")
    if input().lower() == 'y':
        tester.test_generation_requests(2)
    
    # Print results
    tester.print_results()

if __name__ == "__main__":
    main() 