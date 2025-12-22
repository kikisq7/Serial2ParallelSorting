#!/usr/bin/env python3
"""
Visualization script for parallel sorting algorithm benchmark results
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from typing import Dict, Any, List, Tuple
import os

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_benchmark_results(filename: str = "python_benchmark_results.json") -> Dict[str, Any]:
    """Load benchmark results from JSON file"""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Benchmark results file {filename} not found!")
    
    with open(filename, 'r') as f:
        return json.load(f)

def extract_speedup_data(results: Dict[str, Any]) -> Dict[str, Dict[str, List[Tuple[int, float]]]]:
    """Extract speedup data from benchmark results"""
    speedup_data = {}
    
    # Algorithm pairs mapping
    algorithm_pairs = {
        "bubble": ("bubble_parallel", "bubble_serial"),
        "insertion": ("insertion_parallel", "insertion_serial"),
        "merge": ("merge_parallel", "merge_serial"),
        "quick": ("quick_parallel", "quick_serial"),
        "selection": ("selection_parallel", "selection_serial")
    }
    
    for data_type in results:
        speedup_data[data_type] = {}
        
        for size_str in results[data_type]:
            size = int(size_str)
            
            for algo_name, (parallel_name, serial_name) in algorithm_pairs.items():
                if algo_name not in speedup_data[data_type]:
                    speedup_data[data_type][algo_name] = []
                
                if (parallel_name in results[data_type][size_str] and 
                    serial_name in results[data_type][size_str]):
                    
                    parallel_result = results[data_type][size_str][parallel_name]
                    serial_result = results[data_type][size_str][serial_name]
                    
                    if ("mean_time_ns" in parallel_result and parallel_result["mean_time_ns"] != float('inf') and
                        "mean_time_ns" in serial_result and serial_result["mean_time_ns"] != float('inf')):
                        
                        parallel_time = parallel_result["mean_time_ns"]
                        serial_time = serial_result["mean_time_ns"]
                        speedup = serial_time / parallel_time if parallel_time > 0 else 0
                        
                        speedup_data[data_type][algo_name].append((size, speedup))
    
    return speedup_data

def plot_speedup_comparison(speedup_data: Dict[str, Dict[str, List[Tuple[int, float]]]]):
    """Create speedup comparison plots"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Parallel vs Serial Sorting Algorithm Performance Comparison', fontsize=16, fontweight='bold')
    
    # Flatten axes for easier indexing
    axes_flat = axes.flatten()
    
    algorithms = list(speedup_data['random'].keys())
    colors = plt.cm.Set1(np.linspace(0, 1, len(algorithms)))
    
    # Plot 1: Speedup by Algorithm Type
    ax1 = axes_flat[0]
    sizes = []
    speedups_by_algo = {algo: [] for algo in algorithms}
    
    for algo in algorithms:
        if speedup_data['random'][algo]:
            sizes = [size for size, _ in speedup_data['random'][algo]]
            speedups_by_algo[algo] = [speedup for _, speedup in speedup_data['random'][algo]]
    
    x = np.arange(len(sizes))
    width = 0.15
    
    for i, algo in enumerate(algorithms):
        if speedups_by_algo[algo]:
            ax1.bar(x + i * width, speedups_by_algo[algo], width, 
                   label=algo.capitalize(), color=colors[i], alpha=0.8)
    
    ax1.set_xlabel('Array Size')
    ax1.set_ylabel('Speedup (Serial Time / Parallel Time)')
    ax1.set_title('Speedup by Algorithm Type')
    ax1.set_xticks(x + width * 2)
    ax1.set_xticklabels([str(s) for s in sizes])
    ax1.legend()
    ax1.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Break-even')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Speedup Trends
    ax2 = axes_flat[1]
    for i, algo in enumerate(algorithms):
        if speedup_data['random'][algo]:
            sizes = [size for size, _ in speedup_data['random'][algo]]
            speedups = [speedup for _, speedup in speedup_data['random'][algo]]
            ax2.plot(sizes, speedups, marker='o', linewidth=2, markersize=8,
                    label=algo.capitalize(), color=colors[i])
    
    ax2.set_xlabel('Array Size')
    ax2.set_ylabel('Speedup')
    ax2.set_title('Speedup Trends Across Array Sizes')
    ax2.legend()
    ax2.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Break-even')
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    
    # Plot 3: Performance Comparison (Runtime)
    ax3 = axes_flat[2]
    parallel_times = []
    serial_times = []
    algorithm_labels = []
    
    for algo in algorithms:
        if speedup_data['random'][algo]:
            # Get the largest size for comparison
            largest_size_data = max(speedup_data['random'][algo], key=lambda x: x[0])
            size, speedup = largest_size_data
            
            # We need to get actual times from results
            # This is a simplified version - in practice, you'd extract from the full results
            algorithm_labels.append(algo.capitalize())
            # Placeholder values - would need actual time extraction
            parallel_times.append(1.0)  # Normalized
            serial_times.append(speedup)  # Relative to parallel
    
    x = np.arange(len(algorithm_labels))
    ax3.bar(x - 0.2, parallel_times, 0.4, label='Parallel', alpha=0.8, color='skyblue')
    ax3.bar(x + 0.2, serial_times, 0.4, label='Serial', alpha=0.8, color='lightcoral')
    
    ax3.set_xlabel('Algorithm')
    ax3.set_ylabel('Relative Runtime')
    ax3.set_title('Runtime Comparison (Normalized)')
    ax3.set_xticks(x)
    ax3.set_xticklabels(algorithm_labels)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Efficiency Analysis
    ax4 = axes_flat[3]
    efficiency_data = []
    algo_names = []
    
    for algo in algorithms:
        if speedup_data['random'][algo]:
            # Calculate average speedup
            avg_speedup = np.mean([speedup for _, speedup in speedup_data['random'][algo]])
            efficiency_data.append(avg_speedup)
            algo_names.append(algo.capitalize())
    
    bars = ax4.bar(algo_names, efficiency_data, color=colors[:len(algo_names)], alpha=0.8)
    ax4.set_xlabel('Algorithm')
    ax4.set_ylabel('Average Speedup')
    ax4.set_title('Average Speedup Across All Sizes')
    ax4.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Break-even')
    ax4.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars, efficiency_data):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{value:.2f}x', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig

def plot_detailed_runtime_analysis(results: Dict[str, Any]):
    """Create detailed runtime analysis plots"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Detailed Runtime Analysis', fontsize=16, fontweight='bold')
    
    # Algorithm pairs
    algorithm_pairs = {
        "bubble": ("bubble_parallel", "bubble_serial"),
        "insertion": ("insertion_parallel", "insertion_serial"),
        "merge": ("merge_parallel", "merge_serial"),
        "quick": ("quick_parallel", "quick_serial"),
        "selection": ("selection_parallel", "selection_serial")
    }
    
    colors = plt.cm.Set1(np.linspace(0, 1, len(algorithm_pairs)))
    
    # Plot 1: Runtime vs Array Size
    ax1 = axes[0, 0]
    sizes = [100, 1000, 10000]
    
    for i, (algo_name, (parallel_name, serial_name)) in enumerate(algorithm_pairs.items()):
        parallel_times = []
        serial_times = []
        
        for size in sizes:
            size_str = str(size)
            if (size_str in results['random'] and 
                parallel_name in results['random'][size_str] and 
                serial_name in results['random'][size_str]):
                
                parallel_result = results['random'][size_str][parallel_name]
                serial_result = results['random'][size_str][serial_name]
                
                if ("mean_time_ns" in parallel_result and parallel_result["mean_time_ns"] != float('inf') and
                    "mean_time_ns" in serial_result and serial_result["mean_time_ns"] != float('inf')):
                    
                    parallel_times.append(parallel_result["mean_time_ns"] / 1_000_000)  # Convert to ms
                    serial_times.append(serial_result["mean_time_ns"] / 1_000_000)  # Convert to ms
        
        if parallel_times and serial_times:
            ax1.plot(sizes[:len(parallel_times)], parallel_times, 'o-', 
                    color=colors[i], label=f'{algo_name.capitalize()} Parallel', linewidth=2)
            ax1.plot(sizes[:len(serial_times)], serial_times, 's--', 
                    color=colors[i], alpha=0.7, label=f'{algo_name.capitalize()} Serial', linewidth=2)
    
    ax1.set_xlabel('Array Size')
    ax1.set_ylabel('Runtime (ms)')
    ax1.set_title('Runtime vs Array Size')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Speedup Heatmap
    ax2 = axes[0, 1]
    speedup_matrix = []
    algorithm_names = []
    
    for algo_name, (parallel_name, serial_name) in algorithm_pairs.items():
        algorithm_names.append(algo_name.capitalize())
        speedup_row = []
        
        for size in sizes:
            size_str = str(size)
            if (size_str in results['random'] and 
                parallel_name in results['random'][size_str] and 
                serial_name in results['random'][size_str]):
                
                parallel_result = results['random'][size_str][parallel_name]
                serial_result = results['random'][size_str][serial_name]
                
                if ("mean_time_ns" in parallel_result and parallel_result["mean_time_ns"] != float('inf') and
                    "mean_time_ns" in serial_result and serial_result["mean_time_ns"] != float('inf')):
                    
                    parallel_time = parallel_result["mean_time_ns"]
                    serial_time = serial_result["mean_time_ns"]
                    speedup = serial_time / parallel_time if parallel_time > 0 else 0
                    speedup_row.append(speedup)
                else:
                    speedup_row.append(0)
            else:
                speedup_row.append(0)
        
        speedup_matrix.append(speedup_row)
    
    if speedup_matrix:
        im = ax2.imshow(speedup_matrix, cmap='RdYlGn', aspect='auto')
        ax2.set_xticks(range(len(sizes)))
        ax2.set_xticklabels([str(s) for s in sizes])
        ax2.set_yticks(range(len(algorithm_names)))
        ax2.set_yticklabels(algorithm_names)
        ax2.set_xlabel('Array Size')
        ax2.set_ylabel('Algorithm')
        ax2.set_title('Speedup Heatmap')
        
        # Add text annotations
        for i in range(len(algorithm_names)):
            for j in range(len(sizes)):
                text = ax2.text(j, i, f'{speedup_matrix[i][j]:.2f}',
                               ha="center", va="center", color="black", fontweight='bold')
        
        plt.colorbar(im, ax=ax2, label='Speedup')
    
    # Plot 3: Performance Improvement Percentage
    ax3 = axes[1, 0]
    improvement_data = []
    algo_labels = []
    
    for algo_name, (parallel_name, serial_name) in algorithm_pairs.items():
        improvements = []
        
        for size in sizes:
            size_str = str(size)
            if (size_str in results['random'] and 
                parallel_name in results['random'][size_str] and 
                serial_name in results['random'][size_str]):
                
                parallel_result = results['random'][size_str][parallel_name]
                serial_result = results['random'][size_str][serial_name]
                
                if ("mean_time_ns" in parallel_result and parallel_result["mean_time_ns"] != float('inf') and
                    "mean_time_ns" in serial_result and serial_result["mean_time_ns"] != float('inf')):
                    
                    parallel_time = parallel_result["mean_time_ns"]
                    serial_time = serial_result["mean_time_ns"]
                    improvement = ((serial_time - parallel_time) / serial_time) * 100
                    improvements.append(improvement)
        
        if improvements:
            improvement_data.append(improvements)
            algo_labels.append(algo_name.capitalize())
    
    if improvement_data:
        x = np.arange(len(sizes))
        width = 0.15
        
        for i, improvements in enumerate(improvement_data):
            ax3.bar(x + i * width, improvements, width, 
                   label=algo_labels[i], alpha=0.8)
        
        ax3.set_xlabel('Array Size')
        ax3.set_ylabel('Performance Improvement (%)')
        ax3.set_title('Performance Improvement Percentage')
        ax3.set_xticks(x + width * 2)
        ax3.set_xticklabels([str(s) for s in sizes])
        ax3.legend()
        ax3.axhline(y=0, color='red', linestyle='--', alpha=0.7)
        ax3.grid(True, alpha=0.3)
    
    # Plot 4: Algorithm Efficiency Ranking
    ax4 = axes[1, 1]
    avg_speedups = []
    algo_names_rank = []
    
    for algo_name, (parallel_name, serial_name) in algorithm_pairs.items():
        speedups = []
        
        for size in sizes:
            size_str = str(size)
            if (size_str in results['random'] and 
                parallel_name in results['random'][size_str] and 
                serial_name in results['random'][size_str]):
                
                parallel_result = results['random'][size_str][parallel_name]
                serial_result = results['random'][size_str][serial_name]
                
                if ("mean_time_ns" in parallel_result and parallel_result["mean_time_ns"] != float('inf') and
                    "mean_time_ns" in serial_result and serial_result["mean_time_ns"] != float('inf')):
                    
                    parallel_time = parallel_result["mean_time_ns"]
                    serial_time = serial_result["mean_time_ns"]
                    speedup = serial_time / parallel_time if parallel_time > 0 else 0
                    speedups.append(speedup)
        
        if speedups:
            avg_speedup = np.mean(speedups)
            avg_speedups.append(avg_speedup)
            algo_names_rank.append(algo_name.capitalize())
    
    if avg_speedups:
        # Sort by average speedup
        sorted_data = sorted(zip(algo_names_rank, avg_speedups), key=lambda x: x[1], reverse=True)
        sorted_names, sorted_speedups = zip(*sorted_data)
        
        bars = ax4.barh(sorted_names, sorted_speedups, color=colors[:len(sorted_names)], alpha=0.8)
        ax4.set_xlabel('Average Speedup')
        ax4.set_title('Algorithm Efficiency Ranking')
        ax4.axvline(x=1, color='red', linestyle='--', alpha=0.7, label='Break-even')
        
        # Add value labels
        for bar, value in zip(bars, sorted_speedups):
            width = bar.get_width()
            ax4.text(width + 0.01, bar.get_y() + bar.get_height()/2.,
                    f'{value:.2f}x', ha='left', va='center', fontweight='bold')
        
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_summary_report(results: Dict[str, Any], output_dir: str = "."):
    """Create a comprehensive summary report"""
    report_path = os.path.join(output_dir, "benchmark_summary_report.txt")
    
    with open(report_path, 'w') as f:
        f.write("PARALLEL SORTING ALGORITHM BENCHMARK SUMMARY REPORT\n")
        f.write("=" * 60 + "\n\n")
        
        algorithm_pairs = {
            "bubble": ("bubble_parallel", "bubble_serial"),
            "insertion": ("insertion_parallel", "insertion_serial"),
            "merge": ("merge_parallel", "merge_serial"),
            "quick": ("quick_parallel", "quick_serial"),
            "selection": ("selection_parallel", "selection_serial")
        }
        
        for data_type in results:
            f.write(f"DATA TYPE: {data_type.upper()}\n")
            f.write("-" * 30 + "\n\n")
            
            for size_str in sorted(results[data_type].keys(), key=int):
                size = int(size_str)
                f.write(f"Array Size: {size}\n")
                f.write("-" * 20 + "\n")
                
                for algo_name, (parallel_name, serial_name) in algorithm_pairs.items():
                    if (parallel_name in results[data_type][size_str] and 
                        serial_name in results[data_type][size_str]):
                        
                        parallel_result = results[data_type][size_str][parallel_name]
                        serial_result = results[data_type][size_str][serial_name]
                        
                        if ("mean_time_ns" in parallel_result and parallel_result["mean_time_ns"] != float('inf') and
                            "mean_time_ns" in serial_result and serial_result["mean_time_ns"] != float('inf')):
                            
                            parallel_time = parallel_result["mean_time_ns"] / 1_000_000  # Convert to ms
                            serial_time = serial_result["mean_time_ns"] / 1_000_000  # Convert to ms
                            speedup = serial_time / parallel_time if parallel_time > 0 else 0
                            
                            f.write(f"{algo_name.capitalize()} Sort:\n")
                            f.write(f"  Parallel: {parallel_time:.6f} ms\n")
                            f.write(f"  Serial:   {serial_time:.6f} ms\n")
                            f.write(f"  Speedup:  {speedup:.2f}x\n")
                            f.write(f"  Status:   {'Parallel faster' if speedup > 1 else 'Serial faster'}\n\n")
                        else:
                            f.write(f"{algo_name.capitalize()} Sort: ERROR\n\n")
                    else:
                        f.write(f"{algo_name.capitalize()} Sort: NOT AVAILABLE\n\n")
                
                f.write("\n")
    
    print(f"Summary report saved to {report_path}")

def main():
    """Main function"""
    print("Parallel Sorting Algorithm Results Visualization")
    print("=" * 50)
    
    try:
        # Load results
        results = load_benchmark_results()
        print("✓ Benchmark results loaded successfully")
        
        # Extract speedup data
        speedup_data = extract_speedup_data(results)
        print("✓ Speedup data extracted")
        
        # Create visualizations
        print("Creating visualizations...")
        
        # Speedup comparison plots
        fig1 = plot_speedup_comparison(speedup_data)
        fig1.savefig("speedup_comparison.png", dpi=300, bbox_inches='tight')
        print("✓ Speedup comparison plot saved as 'speedup_comparison.png'")
        
        # Detailed runtime analysis
        fig2 = plot_detailed_runtime_analysis(results)
        fig2.savefig("detailed_runtime_analysis.png", dpi=300, bbox_inches='tight')
        print("✓ Detailed runtime analysis plot saved as 'detailed_runtime_analysis.png'")
        
        # Create summary report
        create_summary_report(results)
        print("✓ Summary report created")
        
        print("\nVisualization complete! Generated files:")
        print("  - speedup_comparison.png")
        print("  - detailed_runtime_analysis.png")
        print("  - benchmark_summary_report.txt")
        
        # Show plots
        plt.show()
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run the benchmark first to generate results.")
    except Exception as e:
        print(f"Error creating visualizations: {e}")

if __name__ == "__main__":
    main()
