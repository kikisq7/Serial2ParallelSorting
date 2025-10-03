// C++ program to implement parallel Selection Sort
#include <iostream>
#include <vector>
#include <thread>
#include <future>
#include <algorithm>
using namespace std;

// Parallel selection sort using divide and conquer approach
void parallelSelectionSort(vector<int>& arr, int start, int end) {
    if (start >= end) return;
    
    // For small arrays, use sequential selection sort
    if (end - start < 50) {
        for (int i = start; i < end; ++i) {
            int min_idx = i;
            
            for (int j = i + 1; j <= end; ++j) {
                if (arr[j] < arr[min_idx]) {
                    min_idx = j;
                }
            }
            
            swap(arr[i], arr[min_idx]);
        }
        return;
    }
    
    // Find minimum element in parallel
    int mid = start + (end - start) / 2;
    
    // Find minimum in both halves in parallel
    auto future1 = async(launch::async, [&]() {
        int min_idx = start;
        for (int i = start + 1; i <= mid; ++i) {
            if (arr[i] < arr[min_idx]) {
                min_idx = i;
            }
        }
        return min_idx;
    });
    
    auto future2 = async(launch::async, [&]() {
        int min_idx = mid + 1;
        for (int i = mid + 2; i <= end; ++i) {
            if (arr[i] < arr[min_idx]) {
                min_idx = i;
            }
        }
        return min_idx;
    });
    
    int min1 = future1.get();
    int min2 = future2.get();
    
    // Find overall minimum
    int global_min = (arr[min1] < arr[min2]) ? min1 : min2;
    
    // Swap with first element
    swap(arr[start], arr[global_min]);
    
    // Recursively sort the rest
    parallelSelectionSort(arr, start + 1, end);
}

void printArray(const vector<int>& arr) {
    for (int val : arr) {
        cout << val << " ";
    }
    cout << endl;
}

int main() {
    vector<int> arr = {64, 25, 12, 22, 11, 8, 5, 3, 1, 9, 7, 4};
    
    cout << "Original array: ";
    printArray(arr);
    
    parallelSelectionSort(arr, 0, arr.size() - 1);
    
    cout << "Sorted array: ";
    printArray(arr);
    
    return 0;
}
