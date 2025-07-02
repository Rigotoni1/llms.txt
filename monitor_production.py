#!/usr/bin/env python3
"""
Production monitoring for LLMs.txt generator
"""

import os
import redis
import json
import time
import psutil
from datetime import datetime
import docker
import requests

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_conn = redis.Redis.from_url(REDIS_URL)

def get_production_stats():
    """Get comprehensive production statistics."""
    stats = {
        'timestamp': datetime.now().isoformat(),
        'system': get_system_stats(),
        'redis': get_redis_stats(),
        'queues': get_queue_stats(),
        'docker': get_docker_stats(),
        'web_health': get_web_health(),
        'active_jobs': get_active_jobs()
    }
    return stats

def get_system_stats():
    """Get system resource usage."""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'memory_available_gb': psutil.virtual_memory().available / (1024**3),
        'disk_usage_percent': psutil.disk_usage('/').percent
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
            'total_workers': len(redis_conn.smembers('rq:workers'))
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
                    'memory_usage_mb': container_stats.get('memory_stats', {}).get('usage', 0) / (1024**2),
                    'memory_limit_mb': container_stats.get('memory_stats', {}).get('limit', 0) / (1024**2)
                }
            except Exception as e:
                stats[container.name] = {'error': str(e)}
        
        return stats
    except Exception as e:
        return {'error': str(e)}

def get_web_health():
    """Check web interface health."""
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        return {
            'status_code': response.status_code,
            'response_time_ms': response.elapsed.total_seconds() * 1000,
            'healthy': response.status_code == 200
        }
    except Exception as e:
        return {'error': str(e), 'healthy': False}

def get_active_jobs():
    """Get information about currently active jobs."""
    try:
        job_keys = redis_conn.keys('rq:job:*')
        active_jobs = []
        
        for key in job_keys[:20]:  # Limit to 20 jobs for performance
            try:
                job_data = redis_conn.hgetall(key)
                if job_data:
                    job_info = {
                        'id': key.decode('utf-8').split(':')[-1],
                        'status': job_data.get(b'status', b'unknown').decode('utf-8'),
                        'created_at': job_data.get(b'created_at', b'').decode('utf-8')
                    }
                    active_jobs.append(job_info)
            except Exception as e:
                continue
        
        return active_jobs
    except Exception as e:
        return {'error': str(e)}

def log_production_stats():
    """Log production statistics."""
    stats = get_production_stats()
    
    # Log to file
    with open('production_stats.log', 'a') as f:
        f.write(json.dumps(stats) + '\n')
    
    # Print summary
    print(f"\n=== Production Stats - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"CPU: {stats['system']['cpu_percent']:.1f}% | Memory: {stats['system']['memory_percent']:.1f}%")
    print(f"Workers: {stats['queues'].get('total_workers', 0)} | Batch Queue: {stats['queues'].get('batch_queue_length', 0)}")
    print(f"Web Health: {'✅' if stats['web_health'].get('healthy', False) else '❌'}")
    
    return stats

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        print(f"Starting continuous production monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                log_production_stats()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nProduction monitoring stopped.")
    else:
        log_production_stats()
