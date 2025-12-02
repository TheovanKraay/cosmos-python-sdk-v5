"""
Benchmark Runner - Compares V4 (pure Python) vs V5 (Rust-based) SDK performance
"""
import subprocess
import sys
import os
import json
import time
from pathlib import Path

class BenchmarkRunner:
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)
        self.benchmarks_dir = self.repo_root / "benchmarks"
        self.v4_venv = self.benchmarks_dir / "venv_v4"
        self.v5_venv = self.benchmarks_dir / "venv_v5"
        self.results_file = self.benchmarks_dir / "benchmark_results.json"
        
    def setup_venv(self, venv_path, sdk_version):
        """Create and setup a virtual environment for the specified SDK version"""
        print(f"\n{'='*70}")
        print(f"Setting up virtual environment for SDK {sdk_version}")
        print(f"{'='*70}")
        
        # Check if venv already exists
        if venv_path.exists():
            print(f"✅ Using existing venv at {venv_path}")
            # Get python path and return early if it's V4 (nothing to rebuild)
            if sys.platform == "win32":
                python_exe = venv_path / "Scripts" / "python.exe"
            else:
                python_exe = venv_path / "bin" / "python"
            
            # For V5, rebuild in case there were code changes
            if sdk_version == "v5":
                print("Rebuilding V5 SDK in existing venv...")
                env = os.environ.copy()
                env["VIRTUAL_ENV"] = str(venv_path)
                subprocess.run(
                    [str(python_exe), "-m", "maturin", "develop", "--release"],
                    cwd=str(self.repo_root),
                    env=env,
                    check=True
                )
            
            print(f"✅ SDK {sdk_version} environment ready")
            return python_exe
        
        # Create new venv
        print(f"Creating new venv at {venv_path}")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        
        # Get python and pip paths
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
        
        # Skip pip upgrade - not essential and can cause issues on Windows
        # print("Upgrading pip...")
        # subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
        
        if sdk_version == "v4":
            # Install V4 SDK from PyPI
            print("Installing azure-cosmos V4 from PyPI...")
            subprocess.run([str(pip_exe), "install", "azure-cosmos==4.7.0"], check=True)
        else:
            # Install V5 SDK (local build with maturin)
            print("Installing maturin...")
            subprocess.run([str(pip_exe), "install", "maturin"], check=True)
            
            print("Building and installing V5 SDK with maturin...")
            env = os.environ.copy()
            env["VIRTUAL_ENV"] = str(venv_path)
            subprocess.run(
                [str(python_exe), "-m", "maturin", "develop", "--release"],
                cwd=str(self.repo_root),
                env=env,
                check=True
            )
        
        print(f"✅ SDK {sdk_version} environment ready at {venv_path}")
        return python_exe
    
    def run_benchmark(self, python_exe, sdk_version, benchmark_script):
        """Run a benchmark script in the specified environment"""
        print(f"\n{'='*70}")
        print(f"Running benchmark with SDK {sdk_version}")
        print(f"{'='*70}")
        
        # Start with current environment but override specific values
        env = os.environ.copy()
        env["SDK_VERSION"] = sdk_version
        # Don't set COSMOS_ENDPOINT or COSMOS_KEY - they're hard-coded in benchmark_tests.py
        
        result = subprocess.run(
            [str(python_exe), str(benchmark_script)],
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode != 0:
            print(f"❌ Benchmark failed for SDK {sdk_version}")
            print(f"STDERR: {result.stderr}")
            return None
        
        # Parse JSON output from benchmark
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON output from benchmark")
            print(f"Output: {result.stdout}")
            return None
    
    def compare_results(self, v4_results, v5_results):
        """Compare and display results from both SDKs"""
        print(f"\n{'='*70}")
        print("BENCHMARK RESULTS COMPARISON")
        print(f"{'='*70}\n")
        
        if not v4_results or not v5_results:
            print("❌ Missing results from one or both SDKs")
            return
        
        comparison = {
            "v4_results": v4_results,
            "v5_results": v5_results,
            "comparison": {},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"{'Operation':<30} {'V4 (Python)':<20} {'V5 (Rust)':<20} {'Speedup':<15}")
        print("-" * 85)
        
        for test_name in v4_results.get("tests", {}):
            if test_name not in v5_results.get("tests", {}):
                continue
            
            v4_time = v4_results["tests"][test_name]["total_time"]
            v5_time = v5_results["tests"][test_name]["total_time"]
            
            speedup = v4_time / v5_time if v5_time > 0 else 0
            speedup_str = f"{speedup:.2f}x"
            
            if speedup > 1:
                speedup_str = f"🚀 {speedup_str}"
            elif speedup < 1:
                speedup_str = f"🐌 {speedup_str}"
            else:
                speedup_str = f"⚖️  {speedup_str}"
            
            print(f"{test_name:<30} {v4_time:>18.4f}s {v5_time:>18.4f}s {speedup_str:>15}")
            
            comparison["comparison"][test_name] = {
                "v4_time": v4_time,
                "v5_time": v5_time,
                "speedup": speedup,
                "v4_ops_per_sec": v4_results["tests"][test_name].get("ops_per_sec", 0),
                "v5_ops_per_sec": v5_results["tests"][test_name].get("ops_per_sec", 0)
            }
        
        print("-" * 85)
        
        # Calculate overall statistics
        total_v4 = sum(t["total_time"] for t in v4_results["tests"].values())
        total_v5 = sum(t["total_time"] for t in v5_results["tests"].values())
        overall_speedup = total_v4 / total_v5 if total_v5 > 0 else 0
        
        print(f"{'TOTAL':<30} {total_v4:>18.4f}s {total_v5:>18.4f}s {overall_speedup:>14.2f}x")
        print("\n")
        
        comparison["summary"] = {
            "total_v4_time": total_v4,
            "total_v5_time": total_v5,
            "overall_speedup": overall_speedup
        }
        
        # Save results to file
        with open(self.results_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        print(f"📊 Results saved to: {self.results_file}\n")
        
        if overall_speedup > 1:
            print(f"🎉 V5 (Rust) is {overall_speedup:.2f}x faster overall!")
        elif overall_speedup < 1:
            print(f"⚠️  V4 (Python) is {1/overall_speedup:.2f}x faster overall")
        else:
            print(f"⚖️  Both SDKs have similar performance")
    
    def run_all_benchmarks(self):
        """Main entry point to run all benchmarks"""
        print("\n" + "="*70)
        print("COSMOS DB SDK BENCHMARK SUITE")
        print("V4 (Pure Python) vs V5 (Rust-based)")
        print("="*70)
        
        benchmark_script = self.benchmarks_dir / "benchmark_tests.py"
        
        if not benchmark_script.exists():
            print(f"❌ Benchmark script not found: {benchmark_script}")
            return
        
        # Setup V4 environment
        v4_python = self.setup_venv(self.v4_venv, "v4")
        
        # Setup V5 environment
        v5_python = self.setup_venv(self.v5_venv, "v5")
        
        # Run V4 benchmarks
        v4_results = self.run_benchmark(v4_python, "v4", benchmark_script)
        
        # Run V5 benchmarks
        v5_results = self.run_benchmark(v5_python, "v5", benchmark_script)
        
        # Compare results
        self.compare_results(v4_results, v5_results)

if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent
    runner = BenchmarkRunner(repo_root)
    runner.run_all_benchmarks()
