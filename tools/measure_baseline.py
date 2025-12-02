#!/usr/bin/env python3

import time
import psutil
import requests
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any

class PerformanceBaseline:
    """Establish performance baseline for CogOS constellation optimization"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'api_performance': {},
            'system_metrics': {},
            'frontend_metrics': {},
            'baseline_targets': {
                'api_response_time_ms': 50,
                'memory_usage_mb': 200,
                'cpu_usage_percent': 30,
                'frontend_bundle_size_mb': 1,
                'fps_target': 60
            }
        }

    def measure_api_performance(self) -> Dict[str, Any]:
        """Measure API endpoint performance"""
        print("📊 Measuring API Performance...")
        
        endpoints = [
            '/ping',
            '/health', 
            '/api/memories',
            '/api/contexts',
            '/api/agent/actions',
            '/api/knowledge-graph',
            '/api/stats'
        ]
        
        api_metrics = {}
        
        for endpoint in endpoints:
            print(f"   Testing {endpoint}...")
            times = []
            errors = 0
            
            for i in range(10):  # 10 requests per endpoint
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                    end_time = time.time()
                    
                    response_time = (end_time - start_time) * 1000  # Convert to ms
                    times.append(response_time)
                    
                    if response.status_code != 200:
                        errors += 1
                        
                except Exception as e:
                    errors += 1
                    print(f"     ⚠️  Error: {e}")
                
                time.sleep(0.1)  # Small delay between requests
            
            if times:
                api_metrics[endpoint] = {
                    'avg_response_time_ms': round(statistics.mean(times), 2),
                    'min_response_time_ms': round(min(times), 2),
                    'max_response_time_ms': round(max(times), 2),
                    'median_response_time_ms': round(statistics.median(times), 2),
                    'std_dev_ms': round(statistics.stdev(times) if len(times) > 1 else 0, 2),
                    'error_rate': errors / 10,
                    'requests_tested': len(times)
                }
            else:
                api_metrics[endpoint] = {
                    'status': 'failed',
                    'error_rate': 1.0
                }
        
        return api_metrics

    def measure_system_metrics(self) -> Dict[str, Any]:
        """Measure system resource usage"""
        print("💻 Measuring System Metrics...")
        
        # Take measurements over 30 seconds
        cpu_readings = []
        memory_readings = []
        
        for i in range(30):
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            
            cpu_readings.append(cpu_percent)
            memory_readings.append(memory_info.used / 1024 / 1024)  # Convert to MB
            
            if i % 10 == 0:
                print(f"   Sample {i+1}/30 - CPU: {cpu_percent:.1f}%, Memory: {memory_info.used/1024/1024:.1f}MB")
        
        return {
            'cpu_usage': {
                'avg_percent': round(statistics.mean(cpu_readings), 2),
                'min_percent': round(min(cpu_readings), 2),
                'max_percent': round(max(cpu_readings), 2),
                'median_percent': round(statistics.median(cpu_readings), 2)
            },
            'memory_usage': {
                'avg_mb': round(statistics.mean(memory_readings), 2),
                'min_mb': round(min(memory_readings), 2),
                'max_mb': round(max(memory_readings), 2),
                'median_mb': round(statistics.median(memory_readings), 2)
            },
            'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
            'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
        }

    def measure_frontend_size(self) -> Dict[str, Any]:
        """Measure frontend bundle sizes"""
        print("📦 Measuring Frontend Bundle Sizes...")
        
        import os
        import glob
        
        frontend_dir = "frontend/build"
        if not os.path.exists(frontend_dir):
            frontend_dir = "frontend/.next"
            if not os.path.exists(frontend_dir):
                return {'status': 'not_built', 'message': 'Frontend not built yet'}
        
        bundle_sizes = {}
        total_size = 0
        
        # Find JavaScript bundles
        js_files = glob.glob(f"{frontend_dir}/**/*.js", recursive=True)
        css_files = glob.glob(f"{frontend_dir}/**/*.css", recursive=True)
        
        for js_file in js_files:
            size_mb = os.path.getsize(js_file) / 1024 / 1024
            bundle_sizes[os.path.basename(js_file)] = round(size_mb, 3)
            total_size += size_mb
        
        for css_file in css_files:
            size_mb = os.path.getsize(css_file) / 1024 / 1024
            bundle_sizes[os.path.basename(css_file)] = round(size_mb, 3)
            total_size += size_mb
        
        return {
            'total_size_mb': round(total_size, 3),
            'individual_bundles': bundle_sizes,
            'bundle_count': len(js_files) + len(css_files),
            'js_files': len(js_files),
            'css_files': len(css_files)
        }

    def run_baseline(self) -> Dict[str, Any]:
        """Run complete performance baseline"""
        print("🌟 Starting CogOS Constellation Performance Baseline")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # API Performance
            self.results['api_performance'] = self.measure_api_performance()
            
            # System Metrics
            self.results['system_metrics'] = self.measure_system_metrics()
            
            # Frontend Bundle Size
            self.results['frontend_metrics'] = self.measure_frontend_size()
            
            # Overall assessment
            self.results['total_measurement_time_seconds'] = round(time.time() - start_time, 2)
            self.results['assessment'] = self.assess_performance()
            
        except Exception as e:
            print(f"❌ Error during baseline measurement: {e}")
            self.results['error'] = str(e)
        
        return self.results

    def assess_performance(self) -> Dict[str, Any]:
        """Assess current performance against targets"""
        assessment = {
            'api_status': 'unknown',
            'system_status': 'unknown',
            'frontend_status': 'unknown',
            'overall_grade': 'unknown',
            'recommendations': []
        }
        
        targets = self.results['baseline_targets']
        
        # Assess API performance
        api_metrics = self.results['api_performance']
        avg_api_time = 0
        api_tests = 0
        
        for endpoint, metrics in api_metrics.items():
            if isinstance(metrics, dict) and 'avg_response_time_ms' in metrics:
                avg_api_time += metrics['avg_response_time_ms']
                api_tests += 1
        
        if api_tests > 0:
            avg_api_time /= api_tests
            if avg_api_time <= targets['api_response_time_ms']:
                assessment['api_status'] = 'excellent'
            elif avg_api_time <= targets['api_response_time_ms'] * 2:
                assessment['api_status'] = 'good'
                assessment['recommendations'].append('API response times could be optimized')
            else:
                assessment['api_status'] = 'needs_improvement'
                assessment['recommendations'].append('API response times are too slow - consider caching')
        
        # Assess system performance
        system_metrics = self.results['system_metrics']
        if 'memory_usage' in system_metrics and 'cpu_usage' in system_metrics:
            avg_memory = system_metrics['memory_usage']['avg_mb']
            avg_cpu = system_metrics['cpu_usage']['avg_percent']
            
            if avg_memory <= targets['memory_usage_mb'] and avg_cpu <= targets['cpu_usage_percent']:
                assessment['system_status'] = 'excellent'
            elif avg_memory <= targets['memory_usage_mb'] * 1.5 and avg_cpu <= targets['cpu_usage_percent'] * 1.5:
                assessment['system_status'] = 'good'
            else:
                assessment['system_status'] = 'needs_improvement'
                if avg_memory > targets['memory_usage_mb']:
                    assessment['recommendations'].append('Memory usage is high - consider optimization')
                if avg_cpu > targets['cpu_usage_percent']:
                    assessment['recommendations'].append('CPU usage is high - consider optimization')
        
        # Assess frontend
        frontend_metrics = self.results['frontend_metrics']
        if 'total_size_mb' in frontend_metrics:
            total_size = frontend_metrics['total_size_mb']
            if total_size <= targets['frontend_bundle_size_mb']:
                assessment['frontend_status'] = 'excellent'
            elif total_size <= targets['frontend_bundle_size_mb'] * 2:
                assessment['frontend_status'] = 'good'
                assessment['recommendations'].append('Frontend bundle size could be reduced')
            else:
                assessment['frontend_status'] = 'needs_improvement'
                assessment['recommendations'].append('Frontend bundle size is too large - implement code splitting')
        
        # Overall grade
        statuses = [assessment['api_status'], assessment['system_status'], assessment['frontend_status']]
        if all(s == 'excellent' for s in statuses):
            assessment['overall_grade'] = 'A'
        elif all(s in ['excellent', 'good'] for s in statuses):
            assessment['overall_grade'] = 'B'
        else:
            assessment['overall_grade'] = 'C'
        
        return assessment

    def save_results(self, filename: str = None):
        """Save baseline results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_baseline_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Results saved to: {filename}")

    def print_summary(self):
        """Print performance summary"""
        print("\n" + "=" * 60)
        print("🎯 PERFORMANCE BASELINE SUMMARY")
        print("=" * 60)
        
        assessment = self.results.get('assessment', {})
        
        print(f"Overall Grade: {assessment.get('overall_grade', 'Unknown')}")
        print(f"API Status: {assessment.get('api_status', 'Unknown')}")
        print(f"System Status: {assessment.get('system_status', 'Unknown')}")  
        print(f"Frontend Status: {assessment.get('frontend_status', 'Unknown')}")
        
        if 'api_performance' in self.results:
            avg_times = []
            for endpoint, metrics in self.results['api_performance'].items():
                if isinstance(metrics, dict) and 'avg_response_time_ms' in metrics:
                    avg_times.append(metrics['avg_response_time_ms'])
            
            if avg_times:
                print(f"\nAPI Performance:")
                print(f"  Average Response Time: {statistics.mean(avg_times):.2f}ms")
                print(f"  Target: <{self.results['baseline_targets']['api_response_time_ms']}ms")
        
        if 'system_metrics' in self.results:
            system = self.results['system_metrics']
            if 'memory_usage' in system and 'cpu_usage' in system:
                print(f"\nSystem Performance:")
                print(f"  Memory Usage: {system['memory_usage']['avg_mb']:.1f}MB")
                print(f"  CPU Usage: {system['cpu_usage']['avg_percent']:.1f}%")
                print(f"  Targets: <{self.results['baseline_targets']['memory_usage_mb']}MB, <{self.results['baseline_targets']['cpu_usage_percent']}%")
        
        if 'frontend_metrics' in self.results:
            frontend = self.results['frontend_metrics']
            if 'total_size_mb' in frontend:
                print(f"\nFrontend Performance:")
                print(f"  Bundle Size: {frontend['total_size_mb']:.3f}MB")
                print(f"  Target: <{self.results['baseline_targets']['frontend_bundle_size_mb']}MB")
        
        recommendations = assessment.get('recommendations', [])
        if recommendations:
            print(f"\n📋 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    baseline = PerformanceBaseline()
    results = baseline.run_baseline()
    baseline.print_summary()
    baseline.save_results()
    
    print(f"\n✅ Baseline measurement complete!")
    print(f"🎯 Next steps: Run constellation interface and compare performance")
    print(f"🚀 Use: ./start_constellation.sh")
