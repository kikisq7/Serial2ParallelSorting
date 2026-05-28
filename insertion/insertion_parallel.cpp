#include <iostream>
#include <omp.h>
using namespace std;

/* Parallel Shell Sort using OpenMP 

LLM suggests "✅ Recommended Parallel Adaptation: Shell Sort with OpenMP"
Difference between shell sort and insertion sort: gap 

*/
void parallelShellSort(int arr[], int n) {
    // Start with a big gap, then reduce the gap
    for (int gap = n / 2; gap > 0; gap /= 2) {
        // Parallelize outer loop over different starting positions
        #pragma omp parallel for default(none) shared(arr, n, gap)
        for (int i = gap; i < n; ++i) {
            int temp = arr[i];
            int j = i;

            // Standard insertion sort logic with current gap
            while (j >= gap && arr[j - gap] > temp) {
                arr[j] = arr[j - gap];
                j -= gap;
            }
            arr[j] = temp;
        }
    }
}

/* Utility to print array */
void printArray(int arr[], int n) {
    for (int i = 0; i < n; ++i)
        cout << arr[i] << " ";
    cout << endl;
}

int main() {
    int arr[] = { 12, 11, 13, 5, 6, 15, 2, 18, 9, 1 };
    int n = sizeof(arr) / sizeof(arr[0]);

    parallelShellSort(arr, n);
    printArray(arr, n);

    return 0;
}
