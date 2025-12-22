#include <iostream>
#include <vector>
#include <thread>
#include <future>
using namespace std;

// Merges two subarrays of arr[].
// First subarray is arr[left..mid]
// Second subarray is arr[mid+1..right]
void merge(vector<int>& arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;

    // Create temp vectors
    vector<int> L(n1), R(n2);

    // Copy data to temp vectors L[] and R[]
    for (int i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (int j = 0; j < n2; j++)
        R[j] = arr[mid + 1 + j];

    int i = 0, j = 0;
    int k = left;

    // Merge the temp vectors back 
    // into arr[left..right]
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        }
        else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }

    // Copy the remaining elements of L[], 
    // if there are any
    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }

    // Copy the remaining elements of R[], 
    // if there are any
    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }
}

// Parallel merge sort implementation
void parallelMergeSort(vector<int>& arr, int left, int right) {
    if (left >= right)
        return;

    // For small arrays, use sequential merge sort
    if (right - left < 100) {
        int mid = left + (right - left) / 2;
        parallelMergeSort(arr, left, mid);
        parallelMergeSort(arr, mid + 1, right);
        merge(arr, left, mid, right);
        return;
    }

    int mid = left + (right - left) / 2;
    
    // Sort both halves in parallel
    auto future1 = async(launch::async, [&]() {
        parallelMergeSort(arr, left, mid);
    });
    
    auto future2 = async(launch::async, [&]() {
        parallelMergeSort(arr, mid + 1, right);
    });
    
    // Wait for both halves to complete
    future1.get();
    future2.get();
    
    // Merge the sorted halves
    merge(arr, left, mid, right);
}

// Driver code
#if !defined(SORTING_LIBRARY) && !defined(BENCHMARK_MODE)
int main() {
    vector<int> arr = {38, 27, 43, 10, 15, 8, 22, 5, 12, 3, 18, 7};
    
    cout << "Original array: ";
    for (int val : arr)
        cout << val << " ";
    cout << endl;

    parallelMergeSort(arr, 0, arr.size() - 1);
    
    cout << "Sorted array: ";
    for (int val : arr)
        cout << val << " ";
    cout << endl;
    
    return 0;
}
#endif
