#!/usr/bin/env python3
"""
Startup script for the AI Interview Service Streamlit UI

This script:
1. Checks if the Interview Service is running
2. Validates database connectivity
3. Launches the Streamlit application
4. Provides helpful error messages and setup guidance
"""

import subprocess
import requests
import time
import sys
import os
from pathlib import Path

def check_service_running(url: str, service_name: str) -> bool:
    """Check if a service is running and accessible"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} is running and accessible")
            return True
        else:
            print(f"❌ {service_name} responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {service_name} at {url}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {service_name} connection timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking {service_name}: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit', 'requests', 'pandas', 'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Install with: pip install -r interview/streamlit_requirements.txt")
        return False
    
    # Check Streamlit version for switch_page compatibility
    try:
        import streamlit as st
        from packaging import version
        st_version = st.__version__
        required_version = "1.29.0"
        
        if version.parse(st_version) < version.parse(required_version):
            print(f"⚠️  Streamlit {st_version} found, but {required_version}+ required for full functionality")
            print("📦 Upgrade with: pip install --upgrade streamlit>=1.29.0")
            response = input("Continue anyway? (y/N): ").lower()
            if response != 'y':
                return False
        else:
            print(f"✅ Streamlit {st_version} is compatible")
    except ImportError:
        print("⚠️  Could not check Streamlit version")
    
    print("✅ All required packages are available")
    return True

def main():
    """Main startup function"""
    print("🚀 Starting AI Interview Service Streamlit UI")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("interview/streamlit_app.py"):
        print("❌ Please run this script from the project root directory")
        print("💡 Expected structure: /project-root/interview/streamlit_app.py")
        sys.exit(1)
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Check Interview Service
    print("\n🔍 Checking Interview Service...")
    interview_service_url = "http://localhost:8001/health"
    
    if not check_service_running(interview_service_url, "Interview Service"):
        print("\n💡 To start the Interview Service:")
        print("   cd interview/")
        print("   python main.py")
        print("\n⚠️  The Interview Service must be running before using the UI")
        
        # Ask if user wants to continue anyway
        response = input("\nContinue without the service? (y/N): ").lower()
        if response != 'y':
            sys.exit(1)
    
    # Check if questions are available
    print("\n📚 Checking question availability...")
    try:
        response = requests.get("http://localhost:8001/api/v1/interview", timeout=5)
        if response.status_code == 200:
            data = response.json()
            question_count = data.get("statistics", {}).get("questions", {}).get("total", 0)
            
            if question_count > 0:
                print(f"✅ Found {question_count} questions available")
            else:
                print("⚠️  No questions found in database")
                print("💡 Run the Generator Service first to create questions")
        else:
            print("⚠️  Could not check question availability")
    except:
        print("⚠️  Could not check question availability")
    
    # Launch Streamlit
    print("\n🎯 Launching Streamlit UI...")
    print("📍 URL: http://localhost:8502")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Change to the correct directory
        os.chdir(Path(__file__).parent.parent)
        
        # Launch Streamlit with virtual environment
        venv_python = "/Users/shtlpmac090/Desktop/environments/genai/bin/python"
        
        if os.path.exists(venv_python):
            print(f"🐍 Using virtual environment: {venv_python}")
            cmd = [
                venv_python, "-m", "streamlit", "run",
                "interview/streamlit_app.py",
                "--server.port", "8502",
                "--server.address", "localhost",
                "--browser.gatherUsageStats", "false"
            ]
        else:
            print(f"🐍 Using system Python: {sys.executable}")
            cmd = [
                sys.executable, "-m", "streamlit", "run",
                "interview/streamlit_app.py",
                "--server.port", "8502",
                "--server.address", "localhost",
                "--browser.gatherUsageStats", "false"
            ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n👋 Streamlit UI stopped by user")
    except Exception as e:
        print(f"\n❌ Error launching Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 