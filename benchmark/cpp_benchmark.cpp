#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <functional>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>
#include <cmath>
#include <iomanip>
#include <omp.h>
#include <execution>

using Clock = std::chrono::high_resolution_clock;
using namespace std;

void bubble_sort_parallel(std::vector<int>& arr) {
    const int n = static_cast<int>(arr.size());
    if (n <= 1) return;
    bool swapped = true;
    while (swapped) {
        swapped = false;
        // Even phase
        int limit = n - 1;
        #pragma omp parallel for reduction(|| : swapped) schedule(static)
        for (int i = 0; i < limit; i += 2) {
            if (arr[i] > arr[i + 1]) {
                std::swap(arr[i], arr[i + 1]);
                swapped = true;
            }
        }
        // Odd phase
        #pragma omp parallel for reduction(|| : swapped) schedule(static)
        for (int i = 1; i < limit; i += 2) {
            if (arr[i] > arr[i + 1]) {
                std::swap(arr[i], arr[i + 1]);
                swapped = true;
            }
        }
    }
}

#define BENCHMARK_MODE
#include "../insertion/insertion_parallel_new.cpp"
#include "../merge/merge_parallel_new.cpp"
#include "../quick/quick_parallel.cpp"
#include "../selection/selection_parallel_new.cpp"
#undef BENCHMARK_MODE

void bubble_sort_serial(std::vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                std::swap(arr[j], arr[j + 1]);
            }
        }
    }
}

void insertionSort_serial(std::vector<int>& arr) {
    int n = arr.size();
    for (int i = 1; i < n; i++) {
        int key = arr[i];
        int j = i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

void merge_serial(vector<int>& arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    vector<int> L(n1), R(n2);
    for (int i = 0; i < n1; i++) L[i] = arr[left + i];
    for (int j = 0; j < n2; j++) R[j] = arr[mid + 1 + j];
    int i = 0, j = 0, k = left;
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k++] = L[i++];
        } else {
            arr[k++] = R[j++];
        }
    }
    while (i < n1) arr[k++] = L[i++];
    while (j < n2) arr[k++] = R[j++];
}

void mergeSort_serial(vector<int>& arr, int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        mergeSort_serial(arr, left, mid);
        mergeSort_serial(arr, mid + 1, right);
        merge_serial(arr, left, mid, right);
    }
}

int partition_serial(std::vector<int>& arr, int low, int high) {
    int pivot = arr[high];
    int i = low - 1;
    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            std::swap(arr[i], arr[j]);
        }
    }
    std::swap(arr[i + 1], arr[high]);
    return i + 1;
}

void quicksort_serial(std::vector<int>& arr, int low, int high) {
    if (low < high) {
        int pi = partition_serial(arr, low, high);
        quicksort_serial(arr, low, pi - 1);
        quicksort_serial(arr, pi + 1, high);
    }
}

void selectionSort_serial(std::vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        int min_idx = i;
        for (int j = i + 1; j < n; j++) {
            if (arr[j] < arr[min_idx]) {
                min_idx = j;
            }
        }
        if (min_idx != i) {
            std::swap(arr[i], arr[min_idx]);
        }
    }
}

static const int ITER = 5;
static const int WARMUP = 1;

static vector<int> read_data(int n, int iteration = -1) {
    vector<string> candidates;
    string fname;
    if (iteration >= 0) {
        // Try numbered dataset file
        fname = "data_" + to_string(n) + "_" + to_string(iteration + 1) + ".txt";
    } else {
        // Default file
        fname = "data_" + to_string(n) + ".txt";
    }
    
    candidates.push_back(string("test_data/") + fname);
    candidates.push_back(string("../test_data/") + fname);
    candidates.push_back(string("../../test_data/") + fname);
    candidates.push_back(string("benchmark/../test_data/") + fname);
    candidates.push_back(string("./benchmark/../test_data/") + fname);

    string src = string(__FILE__);
    size_t pos = src.find_last_of("/\\");
    if (pos != string::npos) {
        string src_dir = src.substr(0, pos); // benchmark
        size_t pos2 = src_dir.find_last_of("/\\");
        if (pos2 != string::npos) {
            string repo_dir = src_dir.substr(0, pos2);
            candidates.push_back(repo_dir + "/test_data/" + fname);
        }
    }

    ifstream in;
    string used_path;
    for (const auto& p : candidates) {
        in.open(p);
        if (in.is_open()) { used_path = p; break; }
        in.clear();
    }

    if (!in.is_open()) {
        cerr << "Error: Could not open any test data file for size " << n;
        if (iteration >= 0) cerr << " iteration " << (iteration + 1);
        cerr << ". Tried:\n";
        for (const auto& p : candidates) cerr << "  " << p << "\n";
        exit(1);
    }

    vector<int> a;
    int x;
    while (in >> x) a.push_back(x);
    return a;
}

template <typename F>
static long long time_once(F&& f) {
    auto t0 = Clock::now();
    f();
    auto t1 = Clock::now();
    return std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count();
}

struct Stat { long long mean, median, stdev, mn, mx; };

static Stat summarize(const vector<long long>& v) {
    vector<long long> t = v;
    sort(t.begin(), t.end());
    long long sum = accumulate(t.begin(), t.end(), 0LL);
    long long mean = sum / (long long)t.size();
    long long median = t[t.size()/2];
    long long mn = t.front();
    long long mx = t.back();
    long double m = (long double)mean;
    long double var = 0.0L;
    for (auto x : t) { long double d = x - m; var += d*d; }
    var /= (long double)max<size_t>(1, t.size()-1);
    long long stdev = (long long) llround(sqrt((double)var));
    return {mean, median, stdev, mn, mx};
}

// Helper function to benchmark with different datasets per iteration
template <typename F>
static Stat bench_with_iterations(F&& bench_func, int n) {
    vector<long long> times;
    
    // Warmup with first dataset
    auto warmup_data = read_data(n, 0);
    for (int i = 0; i < WARMUP; ++i) {
        auto tmp = warmup_data;
        bench_func(tmp);
    }
    
    // Run iterations with different datasets
    for (int iteration = 0; iteration < ITER; ++iteration) {
        auto data = read_data(n, iteration);
        auto tmp = data;
        times.push_back(time_once([&]{ bench_func(tmp); }));
    }
    
    return summarize(times);
}

// Serial benchmark functions
static Stat bench_bubble_serial(int n) {
    return bench_with_iterations([](vector<int>& tmp) { bubble_sort_serial(tmp); }, n);
}

static Stat bench_insertion_serial(int n) {
    return bench_with_iterations([](vector<int>& tmp) { insertionSort_serial(tmp); }, n);
}

static Stat bench_merge_serial(int n) {
    return bench_with_iterations([](vector<int>& tmp) { mergeSort_serial(tmp, 0, (int)tmp.size()-1); }, n);
}

static Stat bench_quick_serial(int n) {
    return bench_with_iterations([](vector<int>& tmp) { quicksort_serial(tmp, 0, (int)tmp.size()-1); }, n);
}

static Stat bench_selection_serial(int n) {
    return bench_with_iterations([](vector<int>& tmp) { selectionSort_serial(tmp); }, n);
}

static Stat bench_builtin_serial(int n) {
    omp_set_num_threads(1);
    return bench_with_iterations([](vector<int>& tmp) { sort(tmp.begin(), tmp.end()); }, n);
}

static Stat bench_builtin_parallel(int n) {
    omp_set_num_threads(64);
    return bench_with_iterations([](vector<int>& tmp) { sort(std::execution::par_unseq, tmp.begin(), tmp.end()); }, n);
}

// Parallel benchmark functions
static Stat bench_bubble(int n) {
    return bench_with_iterations([](vector<int>& tmp) { bubble_sort_parallel(tmp); }, n);
}

static Stat bench_insertion(int n) {
    return bench_with_iterations([](vector<int>& tmp) { parallelInsertionSort(tmp, 0, (int)tmp.size()-1); }, n);
}

static Stat bench_merge(int n) {
    return bench_with_iterations([](vector<int>& tmp) { parallelMergeSort(tmp, 0, (int)tmp.size()-1); }, n);
}

static Stat bench_quick(int n) {
    return bench_with_iterations([](vector<int>& tmp) { quicksort_parallel_entry(tmp); }, n);
}

static Stat bench_selection(int n) {
    return bench_with_iterations([](vector<int>& tmp) { parallelSelectionSort(tmp, 0, (int)tmp.size()-1); }, n);
}

static void print_comparison(const string& parallel_name, const Stat& parallel_stat, 
                           const string& serial_name, const Stat& serial_stat) {
    double parallel_ms = parallel_stat.mean / 1e6;
    double serial_ms = serial_stat.mean / 1e6;
    double speedup = (double)serial_stat.mean / (double)parallel_stat.mean;
    string speedup_text = speedup > 1 ? "(parallel faster)" : "(serial faster)";
    
    cout << "  " << parallel_name << ": " << fixed << setprecision(6) << parallel_ms << " ms\n";
    cout << "  " << serial_name << ": " << fixed << setprecision(6) << serial_ms << " ms\n";
    cout << "  Speedup: " << fixed << setprecision(2) << speedup << "x " << speedup_text << "\n\n";
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cout << "C++ Parallel vs Serial Sorting Algorithm Benchmark\n";
    cout << "=================================================\n";

    // vector<int> sizes = {10000000, 100000000};
    // vector<int> sizes = {1000000};
    vector<int> sizes = {10000};
    for (int n : sizes) {
        cout << "\n--- Size: " << n << " ---\n";

        cout << "Benchmarking builtin_sort_serial...\n";
        auto builtin_serial = bench_builtin_serial(n);
        cout << "Benchmarking builtin_sort_parallel...\n";
        auto builtin_parallel = bench_builtin_parallel(n);

        struct AlgoPair {
            string name;
            function<Stat(int)> parallel_bench;
            function<Stat(int)> serial_bench;
        };

        vector<AlgoPair> algos = {
            {"bubble", bench_bubble, bench_bubble_serial},
            {"insertion", bench_insertion, bench_insertion_serial},
            {"merge", bench_merge, bench_merge_serial},
            {"quick", bench_quick, bench_quick_serial},
            {"selection", bench_selection, bench_selection_serial}
        };

        for (const auto& algo : algos) {
            cout << "Benchmarking " << algo.name << "_parallel...\n";
            auto parallel_stat = algo.parallel_bench(n);
            cout << "Benchmarking " << algo.name << "_serial...\n";
            auto serial_stat = algo.serial_bench(n);

            cout << "\nComparing " << algo.name << "_parallel vs " << algo.name << "_serial vs builtin_sort:\n";
            print_comparison(algo.name + "_parallel", parallel_stat, algo.name + "_serial", serial_stat);
            
            double builtin_parallel_ms = builtin_parallel.mean / 1e6;
            double builtin_serial_ms = builtin_serial.mean / 1e6;
            cout << "  builtin_sort_parallel: " << fixed << setprecision(6) << builtin_parallel_ms << " ms\n";
            cout << "  builtin_sort_serial: " << fixed << setprecision(6) << builtin_serial_ms << " ms\n";
            
            double builtin_vs_parallel = (double)builtin_parallel.mean / (double)parallel_stat.mean;
            double builtin_vs_serial = (double)builtin_serial.mean / (double)serial_stat.mean;
            string faster1 = builtin_vs_parallel < 1 ? "(" + algo.name + "_parallel faster)" : "(builtin_sort_parallel faster)";
            string faster2 = builtin_vs_serial < 1 ? "(" + algo.name + "_serial faster)" : "(builtin_sort_serial faster)";
            cout << "  builtin_sort_parallel vs " << algo.name << "_parallel: " 
                 << fixed << setprecision(2) << builtin_vs_parallel << "x " << faster1 << "\n";
            cout << "  builtin_sort_serial vs " << algo.name << "_serial: " 
                 << fixed << setprecision(2) << builtin_vs_serial << "x " << faster2 << "\n\n";
        }
    }
    return 0;
}