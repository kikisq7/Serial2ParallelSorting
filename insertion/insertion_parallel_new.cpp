// C++ program for parallel implementation of Insertion Sort
#include <iostream>
#include <vector>
#include <thread>
#include <future>
#include <algorithm>
using namespace std;

// Parallel insertion sort using divide and conquer approach
void parallelInsertionSort(vector<int>& arr, int start, int end) {
    if (start >= end) return;
    
    // For small arrays, use sequential insertion sort
    if (end - start < 100) {
        for (int i = start + 1; i <= end; ++i) {
            int key = arr[i];
            int j = i - 1;
            
            while (j >= start && arr[j] > key) {
                arr[j + 1] = arr[j];
                j = j - 1;
            }
            arr[j + 1] = key;
        }
        return;
    }
    
    // Divide the array into two halves
    int mid = start + (end - start) / 2;
    
    // Sort both halves in parallel
    auto future1 = async(launch::async, [&]() {
        parallelInsertionSort(arr, start, mid);
    });
    
    auto future2 = async(launch::async, [&]() {
        parallelInsertionSort(arr, mid + 1, end);
    });
    
    // Wait for both halves to complete
    future1.get();
    future2.get();
    
    // Merge the two sorted halves
    vector<int> temp(end - start + 1);
    int i = start, j = mid + 1, k = 0;
    
    while (i <= mid && j <= end) {
        if (arr[i] <= arr[j]) {
            temp[k++] = arr[i++];
        } else {
            temp[k++] = arr[j++];
        }
    }
    
    while (i <= mid) temp[k++] = arr[i++];
    while (j <= end) temp[k++] = arr[j++];
    
    // Copy back to original array
    for (int i = 0; i < k; ++i) {
        arr[start + i] = temp[i];
    }
}

/* A utility function to print array of size n */
void printArray(const vector<int>& arr) {
    for (int val : arr)
        cout << val << " ";
    cout << endl;
}

// Driver method
int main() {
    vector<int> arr = {12, 11, 13, 5, 6, 7, 8, 1, 9, 2, 4, 3};
    
    cout << "Original array: ";
    printArray(arr);
    
    parallelInsertionSort(arr, 0, arr.size() - 1);
    
    cout << "Sorted array: ";
    printArray(arr);
    
    return 0;
}
