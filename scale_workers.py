#!/usr/bin/env python3
"""
Worker Scaling Script for LLMs.txt Generator
Allows you to easily scale up/down the number of worker processes
"""

import subprocess
import sys
import os
import time

def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip(), e.returncode

def get_current_workers():
    """Get the current number of worker containers."""
    stdout, stderr, code = run_command("docker-compose ps worker", check=False)
    if code != 0:
        return 0
    
    # Count lines that contain "worker" and are "Up"
    lines = stdout.split('\n')
    worker_count = 0
    for line in lines:
        if 'worker' in line and 'Up' in line:
            worker_count += 1
    return worker_count

def scale_workers(num_workers):
    """Scale the number of worker containers."""
    print(f"🔄 Scaling workers to {num_workers} instances...")
    
    # Stop current workers
    print("⏹️  Stopping current workers...")
    run_command("docker-compose stop worker worker-2", check=False)
    
    # Remove current workers
    print("🗑️  Removing current workers...")
    run_command("docker-compose rm -f worker worker-2", check=False)
    
    # Start new workers
    print(f"🚀 Starting {num_workers} worker instances...")
    
    if num_workers == 1:
        run_command("docker-compose up -d worker")
    elif num_workers == 2:
        run_command("docker-compose up -d worker worker-2")
    else:
        # For more than 2 workers, we need to scale
        run_command("docker-compose up -d worker")
        time.sleep(2)
        run_command(f"docker-compose up -d --scale worker={num_workers}")
    
    print("✅ Worker scaling complete!")
    
    # Show status
    time.sleep(3)
    show_status()

def show_status():
    """Show current worker status."""
    print("\n📊 Current Status:")
    print("=" * 50)
    
    # Show containers
    stdout, stderr, code = run_command("docker-compose ps")
    if code == 0:
        print(stdout)
    
    # Show worker count
    worker_count = get_current_workers()
    print(f"\n🔧 Active Workers: {worker_count}")
    
    # Show queue status
    print("\n📋 Queue Status:")
    stdout, stderr, code = run_command("docker-compose exec redis redis-cli llen rq:queue:default")
    if code == 0:
        queue_length = stdout.strip()
        print(f"   Jobs in queue: {queue_length}")
    
    # Show recent logs
    print("\n📝 Recent Worker Logs:")
    stdout, stderr, code = run_command("docker-compose logs --tail=5 worker")
    if code == 0:
        print(stdout)

def monitor_jobs():
    """Monitor active jobs and queue status."""
    print("🔍 Monitoring jobs... (Press Ctrl+C to stop)")
    print("=" * 50)
    
    try:
        while True:
            # Clear screen
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("🕐 " + time.strftime("%H:%M:%S"))
            print("=" * 50)
            
            # Show queue status
            stdout, stderr, code = run_command("docker-compose exec redis redis-cli llen rq:queue:default")
            if code == 0:
                queue_length = stdout.strip()
                print(f"📋 Jobs in queue: {queue_length}")
            
            # Show active jobs
            stdout, stderr, code = run_command("docker-compose exec redis redis-cli keys 'rq:job:*' | wc -l")
            if code == 0:
                active_jobs = stdout.strip()
                print(f"⚡ Active jobs: {active_jobs}")
            
            # Show worker status
            worker_count = get_current_workers()
            print(f"🔧 Active workers: {worker_count}")
            
            # Show recent logs
            print("\n📝 Recent activity:")
            stdout, stderr, code = run_command("docker-compose logs --tail=3 worker")
            if code == 0:
                print(stdout)
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("🚀 LLMs.txt Generator - Worker Scaling Tool")
        print("=" * 50)
        print("Usage:")
        print("  python scale_workers.py scale <number>  - Scale to N workers")
        print("  python scale_workers.py status         - Show current status")
        print("  python scale_workers.py monitor        - Monitor jobs in real-time")
        print("  python scale_workers.py restart        - Restart all workers")
        print("\nExamples:")
        print("  python scale_workers.py scale 1        - Single worker")
        print("  python scale_workers.py scale 2        - Two workers")
        print("  python scale_workers.py scale 4        - Four workers")
        return
    
    command = sys.argv[1]
    
    if command == "scale":
        if len(sys.argv) < 3:
            print("❌ Please specify number of workers")
            return
        
        try:
            num_workers = int(sys.argv[2])
            if num_workers < 1 or num_workers > 10:
                print("❌ Number of workers must be between 1 and 10")
                return
            scale_workers(num_workers)
        except ValueError:
            print("❌ Invalid number of workers")
    
    elif command == "status":
        show_status()
    
    elif command == "monitor":
        monitor_jobs()
    
    elif command == "restart":
        print("🔄 Restarting all workers...")
        run_command("docker-compose restart worker worker-2")
        time.sleep(3)
        show_status()
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main() 