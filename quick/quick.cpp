#include <iostream>
#include <vector>
#include <utility>

int partition(std::vector<int>& arr, int low, int high) {
    int pivot = arr[high];
    int i = low - 1;
    for (int j = low; j < high; ++j) {
        if (arr[j] <= pivot) {
            ++i;
            std::swap(arr[i], arr[j]);
        }
    }
    std::swap(arr[i + 1], arr[high]);
    return i + 1;
}

void quicksort(std::vector<int>& arr, int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quicksort(arr, low, pi - 1);
        quicksort(arr, pi + 1, high);
    }
}

void print_array(const std::vector<int>& arr) {
    for (const auto& v : arr) std::cout << v << ' ';
    std::cout << '\n';
}

int main() {
    std::vector<int> arr{10, 7, 8, 9, 1, 5};
    std::cout << "Original array: ";
    print_array(arr);
    quicksort(arr, 0, static_cast<int>(arr.size() - 1));
    std::cout << "Sorted array: ";
    print_array(arr);
    return 0;
}


