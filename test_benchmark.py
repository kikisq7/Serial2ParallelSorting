#!/usr/bin/env python3
"""
Test script to verify the updated benchmark works correctly
"""

import sys
import os
import subprocess

def test_benchmark():
    """Test the updated benchmark"""
    print("Testing updated benchmark...")
    
    # Change to the benchmark directory
    benchmark_dir = "/Users/shiqicheng/Kiki/UROPJulia/Sorting/benchmark"
    os.chdir(benchmark_dir)
    
    # Check if test data exists
    if not os.path.exists("../test_data/test_datasets.json"):
        print("Generating test data...")
        try:
            subprocess.run([sys.executable, "test_data_generator.py"], check=True)
            print("✓ Test data generated")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error generating test data: {e}")
            return False
    
    # Run the benchmark
    print("Running benchmark...")
    try:
        result = subprocess.run([sys.executable, "python_benchmark.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✓ Benchmark completed successfully")
            print("Output:")
            print(result.stdout)
            
            # Check if results file was created
            if os.path.exists("python_benchmark_results.json"):
                print("✓ Results file created")
                return True
            else:
                print("✗ Results file not found")
                return False
        else:
            print(f"✗ Benchmark failed with return code {result.returncode}")
            print("Error output:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Benchmark timed out")
        return False
    except Exception as e:
        print(f"✗ Error running benchmark: {e}")
        return False

def test_visualization():
    """Test the visualization script"""
    print("\nTesting visualization script...")
    
    # Check if results file exists
    if not os.path.exists("python_benchmark_results.json"):
        print("✗ Results file not found, cannot test visualization")
        return False
    
    try:
        # Test importing the visualization script
        import visualize_results
        print("✓ Visualization script imports successfully")
        
        # Test loading results
        results = visualize_results.load_benchmark_results()
        print("✓ Results loaded successfully")
        
        # Test extracting speedup data
        speedup_data = visualize_results.extract_speedup_data(results)
        print("✓ Speedup data extracted successfully")
        
        print("✓ Visualization script test passed")
        return True
        
    except Exception as e:
        print(f"✗ Visualization test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Updated Benchmark and Visualization")
    print("=" * 50)
    
    benchmark_success = test_benchmark()
    visualization_success = test_visualization()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Benchmark: {'✓ PASSED' if benchmark_success else '✗ FAILED'}")
    print(f"Visualization: {'✓ PASSED' if visualization_success else '✗ FAILED'}")
    
    if benchmark_success and visualization_success:
        print("\n🎉 All tests passed! The updated benchmark is ready for ORCD.")
        print("\nTo run on ORCD:")
        print("1. Upload the files to ORCD")
        print("2. Run: python benchmark/python_benchmark.py")
        print("3. Run: python benchmark/visualize_results.py")
    else:
        print("\n❌ Some tests failed. Please fix the issues before running on ORCD.")

if __name__ == "__main__":
    main()
