#!/usr/bin/env python3
"""
Plot comparison of serial and parallel implementations across C++, Julia, and Python
"""

import re
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

def parse_results(filepath, language):
    """Parse results file and extract timing data"""
    data = defaultdict(lambda: {'serial': {}, 'parallel': {}})
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract size sections
    size_pattern = r'--- Size: (\d+) ---'
    sizes = [int(m) for m in re.findall(size_pattern, content)]
    
    for size in sizes:
        # Find section for this size
        size_section = re.search(
            rf'--- Size: {size} ---(.*?)(?=--- Size: |$)',
            content,
            re.DOTALL
        )
        if not size_section:
            continue
        
        section = size_section.group(1)
        
        # Extract all algorithm results
        algorithms = ['bubble', 'insertion', 'merge', 'quick', 'selection']
        for alg in algorithms:
            # Look for parallel and serial times
            parallel_pattern = rf'{alg}_parallel:\s*([\d.]+)\s*ms'
            serial_pattern = rf'{alg}_serial:\s*([\d.]+)\s*ms'
            
            parallel_match = re.search(parallel_pattern, section)
            serial_match = re.search(serial_pattern, section)
            
            if parallel_match:
                data[alg]['parallel'][size] = float(parallel_match.group(1))
            if serial_match:
                data[alg]['serial'][size] = float(serial_match.group(1))
    
    return data

# Parse all three result files
cpp_data = parse_results('benchmark/cppresults.txt', 'C++')
julia_data = parse_results('benchmark/juliaresults.txt', 'Julia')
python_data = parse_results('benchmark/python_results.txt', 'Python')

# Prepare data for plotting
algorithms = ['bubble', 'insertion', 'merge', 'quick', 'selection']
sizes = [100, 1000, 10000]
languages = ['C++', 'Julia', 'Python']
colors = {'C++': '#1f77b4', 'Julia': '#ff7f0e', 'Python': '#2ca02c'}

# Create figure with subplots for each algorithm
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten()

for idx, alg in enumerate(algorithms):
    ax = axes[idx]
    
    # Prepare data
    serial_data = {'C++': [], 'Julia': [], 'Python': []}
    parallel_data = {'C++': [], 'Julia': [], 'Python': []}
    
    for size in sizes:
        # Serial times
        for lang, data_dict in [('C++', cpp_data), ('Julia', julia_data), ('Python', python_data)]:
            time = data_dict[alg]['serial'].get(size, 0)
            serial_data[lang].append(time if time > 0 else np.nan)
        
        # Parallel times
        for lang, data_dict in [('C++', cpp_data), ('Julia', julia_data), ('Python', python_data)]:
            time = data_dict[alg]['parallel'].get(size, 0)
            parallel_data[lang].append(time if time > 0 else np.nan)
    
    # Create line plots for serial
    for lang in languages:
        ax.plot(sizes, serial_data[lang], marker='o', linewidth=2, 
               label=f'{lang} Serial', color=colors[lang], linestyle='-', markersize=8, alpha=0.7)
    
    # Create line plots for parallel
    for lang in languages:
        ax.plot(sizes, parallel_data[lang], marker='s', linewidth=2,
               label=f'{lang} Parallel', color=colors[lang], linestyle='--', markersize=8, alpha=0.9)
    
    ax.set_xlabel('Array Size', fontsize=11)
    ax.set_ylabel('Time (ms)', fontsize=11)
    ax.set_title(f'{alg.capitalize()} Sort', fontsize=13, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')  # Use log scale for better visualization
    ax.set_xticks(sizes)
    ax.set_xticklabels([f'{s:,}' for s in sizes])
    ax.legend(fontsize=9, loc='best')
    ax.grid(True, alpha=0.3, which='both')

# Remove the 6th subplot (we only have 5 algorithms)
fig.delaxes(axes[5])

plt.suptitle('Performance Comparison: Serial vs Parallel Implementations Across Languages', 
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('benchmark/comparison_plot.png', dpi=300, bbox_inches='tight')
plt.savefig('benchmark/comparison_plot.pdf', bbox_inches='tight')
print("Plot saved to benchmark/comparison_plot.png and benchmark/comparison_plot.pdf")

