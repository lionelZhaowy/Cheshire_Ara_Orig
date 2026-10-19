// SPDX-License-Identifier: Apache-2.0
#include <iostream>
#include <map>
#include <string>
#include <vector>
int main() {
    std::map<std::string, std::vector<int> > values;
    values["probe"] = {2, 3, 5};
    int sum = 0;
    for (int n : values.at("probe")) sum += n;
    if (sum != 10) return 1;
    std::cout << "E01_NATIVE_CXX_PASS sum=" << sum << '\n';
    return 0;
}
