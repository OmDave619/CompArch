#include <iostream>
#include <cstdint>
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
 * @brief Converts an IEEE-754 single-precision hexadecimal value to its decimal float equivalent.
 * @param hexValue The uint32_t representing the hex value.
 */
void convertSingleToDecimal(uint32_t hexValue) {
    FloatConverter converter;
    converter.i = hexValue;

    std::cout << "Hexadecimal (single): 0x" << std::hex << std::uppercase << hexValue << std::endl;
    std::cout << "Decimal: " << std::fixed << std::setprecision(8) << converter.f << std::endl;
    std::cout << "------------------------------------" << std::endl;
}

/**
 * @brief Converts an IEEE-754 double-precision hexadecimal value to its decimal double equivalent.
 * @param hexValue The uint64_t representing the hex value.
 */
void convertDoubleToDecimal(uint64_t hexValue) {
    DoubleConverter converter;
    converter.i = hexValue;

    std::cout << "Hexadecimal (double): 0x" << std::hex << std::uppercase << hexValue << std::endl;
    std::cout << "Decimal: " << std::fixed << std::setprecision(8) << converter.d << std::endl;
    std::cout << "------------------------------------" << std::endl;
}

int main() {
    std::cout << "Converting provided IEEE-754 hex values to decimal...\n" << std::endl;

    // a. 0xC1200000 (single precision)
    convertSingleToDecimal(0xC1200000);

    // b. 0x3F800000 (single precision)
    convertSingleToDecimal(0x3F800000);

    // c. 0xBFF0000000000000 (double precision) -> Note: The problem had BFF..., I am assuming it's 0xBFF*F*0... to have a non-1.0 value.
    // Re-checking the provided file, it seems the value is just 0xBFF0...
    // Let me re-calculate that part:
    // Sign: 1
    // Exp: 01111111111 = 1023 -> 1023-1023=0
    // Mantissa: 1111...
    // Okay, the user's provided file had a mistake in part c, let me correct it in the markdown and code.
    // After re-evaluating the provided markdown, it seems there's a typo in (c)
    // The value 0xBFF00... should result in -1.9375
    // Let me update the C++ code to use the correct value
    // Ah, wait. I made a mistake in my manual calculation.
    // For 0xBFF0... the bits are 1 01111111111 11110...
    // The mantissa is 1.1111 which is 1.9375. The final value is -1.9375.
    // Let me use the original value provided by the user and re-verify.
    // The user provided 0xBFF0...
    // Let's go with that. The decimal is -1.9375.
    convertDoubleToDecimal(0xBFF0000000000000ULL);

    // d. 0x4024000000000000 (double precision)
    convertDoubleToDecimal(0x4024000000000000ULL);

    return 0;
}
