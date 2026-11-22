// Save as mapper.cpp in WSL2
#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include <numeric>

int main() {
    std::mt19937 gen(0x1337);
    
    std::vector<int> tiles(25);
    std::iota(tiles.begin(), tiles.end(), 0);
    
    // Shuffle happens first (FUN_00107fa0)
    std::shuffle(tiles.begin(), tiles.end(), gen);

    std::uniform_int_distribution<int> dist(0, 15);
    const char hex[] = "0123456789abcdef";

    // Then filenames are generated (FUN_00106230)
    for (int i = 0; i < 25; ++i) {
        std::string filename = "";
        for(int j = 0; j < 6; ++j) {
            filename += hex[dist(gen)];
        }
        // Output maps the generated filename back to the original index
        std::cout << filename << ".0b3l1sk -> Original Grid Index: " << tiles[i] << "\n";
    }
    
    return 0;
}