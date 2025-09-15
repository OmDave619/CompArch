#include <iostream>
#include <cstdint>
#include <cstring>
#include <iomanip>

// Union to easily access the bits of a float
union FloatConverter {
    float f;
    uint32_t i;
};

// Union to easily access the bits of a double
union DoubleConverter {
    double d;
    uint64_t i;
};

/**
 * @brief Converts a float to its IEEE-754 single-precision hexadecimal representation.
 * @param value The float value to convert.
 */
void convertSinglePrecision(float value) {
    FloatConverter converter;
    converter.f = value;

    std::cout << "Decimal (single): " << std::fixed << std::setprecision(8) << value << std::endl;
    std::cout << "Hexadecimal: 0x" << std::hex << std::uppercase << converter.i << std::endl;
    std::cout << "------------------------------------" << std::endl;
}

/**
 * @brief Converts a double to its IEEE-754 double-precision hexadecimal representation.
 * @param value The double value to convert.
 */
void convertDoublePrecision(double value) {
    DoubleConverter converter;
    converter.d = value;

    std::cout << "Decimal (double): " << std::fixed << std::setprecision(8) << value << std::endl;
    std::cout << "Hexadecimal: 0x" << std::hex << std::uppercase << converter.i << std::endl;
    std::cout << "------------------------------------" << std::endl;
}

int main() {
    // --- Test Cases from the problem ---
    std::cout << "Converting provided decimal numbers to IEEE-754 format...\n" << std::endl;

    // a. -13.25 (single precision)
    convertSinglePrecision(-13.25f);

    // b. 0.1 (single precision)
    convertSinglePrecision(0.1f);

    // c. 156.75 (double precision)
    convertDoublePrecision(156.75);

    // d. -0.0078125 (double precision)
    convertDoublePrecision(-0.0078125);

    float a = 16777218;
    float b = 1;

    std::cout << a+b << "\n";

    return 0;
}
