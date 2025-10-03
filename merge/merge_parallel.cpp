#include <iostream>
#include <vector>
#include <thread>
using namespace std;

// Merge function (same as before)
void merge(vector<int>& arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;

    vector<int> L(n1), R(n2);
    for (int i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (int j = 0; j < n2; j++)
        R[j] = arr[mid + 1 + j];

    int i = 0, j = 0, k = left;
    while (i < n1 && j < n2)
        arr[k++] = (L[i] <= R[j]) ? L[i++] : R[j++];

    while (i < n1)
        arr[k++] = L[i++];
    while (j < n2)
        arr[k++] = R[j++];
}

// Parallel Merge Sort
void parallelMergeSort(vector<int>& arr, int left, int right, int depth = 0) {
    if (left >= right)
        return;

    int mid = left + (right - left) / 2;

    // Limit depth to avoid too many threads
    if (depth < 3) {

        thread t1([&arr, left, mid, depth]() {
            parallelMergeSort(arr, left, mid, depth + 1);
        });
        thread t2([&arr, mid, right, depth]() {
            parallelMergeSort(arr, mid + 1, right, depth + 1);
        });
        t1.join();
        t2.join();
    } else {
        // Fallback to serial sort at deeper levels
        parallelMergeSort(arr, left, mid, depth + 1);
        parallelMergeSort(arr, mid + 1, right, depth + 1);
    }

    merge(arr, left, mid, right);
}

// Driver code
int main() {
    int raw[] = {38, 27, 43, 10, 82, 5, 7, 11, 55, 31};
    vector<int> arr(raw, raw + sizeof(raw) / sizeof(raw[0]));
    int n = arr.size();

    parallelMergeSort(arr, 0, n - 1);

    for (int i = 0; i < arr.size(); i++)
        cout << arr[i] << " ";
    cout << endl;

    return 0;
}
