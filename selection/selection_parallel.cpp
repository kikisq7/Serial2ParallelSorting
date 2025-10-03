#include <iostream>
#include <vector>
#include <algorithm>
#include <limits>
#include <thread>
#include <mutex>
#include <future>

using namespace std;

void selectionSortParallel(vector<int> &arr) {
    int n = arr.size();

    for (int i = 0; i < n - 1; ++i) {
        int min_idx = i;
        
        // Use multiple threads to find minimum in parallel
        int num_threads = min(4, (int)thread::hardware_concurrency());
        if (num_threads == 0) num_threads = 2;
        
        vector<future<int>> futures;
        int chunk_size = (n - i - 1) / num_threads;
        
        for (int t = 0; t < num_threads; ++t) {
            int start = i + 1 + t * chunk_size;
            int end = (t == num_threads - 1) ? n : i + 1 + (t + 1) * chunk_size;
            
            futures.push_back(async(launch::async, [&arr, start, end, i]() {
                int local_min_idx = i;
                for (int j = start; j < end; ++j) {
                    if (arr[j] < arr[local_min_idx]) {
                        local_min_idx = j;
                    }
                }
                return local_min_idx;
            }));
        }
        
        // Collect results and find global minimum
        for (auto& future : futures) {
            int local_min = future.get();
            if (arr[local_min] < arr[min_idx]) {
                min_idx = local_min;
            }
        }

        swap(arr[i], arr[min_idx]);
    }s
}

void printArray(const vector<int> &arr) {
    for (int val : arr) {
        cout << val << " ";
    }
    cout << endl;
}

int main() {
    vector<int> arr = {64, 25, 12, 22, 11};

    cout << "Original array: ";
    printArray(arr);

    selectionSortParallel(arr);

    cout << "Sorted array: ";
    printArray(arr);

    return 0;
}
