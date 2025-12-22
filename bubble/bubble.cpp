#ifndef BENCHMARK_MODE

#include <iostream>
#include <vector>

void bubble_sort(std::vector<int>& arr) {
    int n = static_cast<int>(arr.size());
    for (int i = 0; i < n; ++i) {
        bool swapped = false;
        for (int j = 0; j < n - i - 1; ++j) {
            if (arr[j] > arr[j + 1]) {
                std::swap(arr[j], arr[j + 1]);
                swapped = true;
            }
        }
        if (!swapped) {
            break;
        }
    }
}

void print_array(const std::vector<int>& arr) {
    for (const auto& v : arr) {
        std::cout << v << " ";
    }
    std::cout << std::endl;
}

int main() {
    std::vector<int> arr{64, 34, 25, 12, 22, 11, 90};
    std::cout << "Original array: ";
    print_array(arr);
    bubble_sort(arr);
    std::cout << "Sorted array: ";
    print_array(arr);
    return 0;
}


#endif
