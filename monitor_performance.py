#!/usr/bin/env python3
"""
Performance monitoring for LLMs.txt generator
"""

import os
import redis
import json
import time
import psutil
from datetime import datetime
import docker

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_conn = redis.Redis.from_url(REDIS_URL)

def get_system_stats():
    """Get current system resource usage."""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'memory_available': psutil.virtual_memory().available / (1024**3),  # GB
        'disk_usage': psutil.disk_usage('/').percent
    }

def get_redis_stats():
    """Get Redis performance statistics."""
    try:
        info = redis_conn.info()
        return {
            'connected_clients': info.get('connected_clients', 0),
            'used_memory_human': info.get('used_memory_human', '0B'),
            'total_commands_processed': info.get('total_commands_processed', 0),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0)
        }
    except Exception as e:
        return {'error': str(e)}

def get_queue_stats():
    """Get RQ queue statistics."""
    try:
        from rq import Queue
        
        batch_queue = Queue('batch_processing', connection=redis_conn)
        merge_queue = Queue('merge_processing', connection=redis_conn)
        default_queue = Queue(connection=redis_conn)
        
        return {
            'batch_queue_length': len(batch_queue),
            'merge_queue_length': len(merge_queue),
            'default_queue_length': len(default_queue),
            'workers': len(redis_conn.smembers('rq:workers'))
        }
    except Exception as e:
        return {'error': str(e)}

def get_docker_stats():
    """Get Docker container statistics."""
    try:
        client = docker.from_env()
        containers = client.containers.list()
        
        stats = {}
        for container in containers:
            try:
                container_stats = container.stats(stream=False)
                stats[container.name] = {
                    'status': container.status,
                    'cpu_percent': container_stats.get('cpu_stats', {}).get('cpu_usage', {}).get('total_usage', 0),
                    'memory_usage': container_stats.get('memory_stats', {}).get('usage', 0),
                    'memory_limit': container_stats.get('memory_stats', {}).get('limit', 0)
                }
            except Exception as e:
                stats[container.name] = {'error': str(e)}
        
        return stats
    except Exception as e:
        return {'error': str(e)}

def get_active_jobs():
    """Get information about currently active jobs."""
    try:
        # Get all job keys
        job_keys = redis_conn.keys('rq:job:*')
        active_jobs = []
        
        for key in job_keys[:10]:  # Limit to 10 jobs for performance
            try:
                job_data = redis_conn.hgetall(key)
                if job_data:
                    job_info = {
                        'id': key.decode('utf-8').split(':')[-1],
                        'status': job_data.get(b'status', b'unknown').decode('utf-8'),
                        'created_at': job_data.get(b'created_at', b'').decode('utf-8'),
                        'started_at': job_data.get(b'started_at', b'').decode('utf-8')
                    }
                    active_jobs.append(job_info)
            except Exception as e:
                continue
        
        return active_jobs
    except Exception as e:
        return {'error': str(e)}

def monitor_performance():
    """Main monitoring function."""
    print(f"\n=== LLMs.txt Performance Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    # System stats
    print("\n📊 System Resources:")
    system_stats = get_system_stats()
    for key, value in system_stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.1f}")
        else:
            print(f"  {key}: {value}")
    
    # Redis stats
    print("\n🔴 Redis Performance:")
    redis_stats = get_redis_stats()
    for key, value in redis_stats.items():
        print(f"  {key}: {value}")
    
    # Queue stats
    print("\n📋 Queue Status:")
    queue_stats = get_queue_stats()
    for key, value in queue_stats.items():
        print(f"  {key}: {value}")
    
    # Docker stats
    print("\n🐳 Docker Containers:")
    docker_stats = get_docker_stats()
    for container, stats in docker_stats.items():
        print(f"  {container}:")
        for key, value in stats.items():
            print(f"    {key}: {value}")
    
    # Active jobs
    print("\n⚡ Active Jobs:")
    active_jobs = get_active_jobs()
    if isinstance(active_jobs, list):
        for job in active_jobs:
            print(f"  Job {job['id']}: {job['status']}")
    else:
        print(f"  Error: {active_jobs.get('error', 'Unknown error')}")

def continuous_monitoring(interval=30):
    """Run continuous monitoring."""
    print(f"Starting continuous monitoring (interval: {interval}s)")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            monitor_performance()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        continuous_monitoring(interval)
    else:
        monitor_performance() 