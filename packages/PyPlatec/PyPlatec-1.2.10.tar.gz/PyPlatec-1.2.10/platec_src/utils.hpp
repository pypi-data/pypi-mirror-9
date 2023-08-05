#ifndef UTILS_HPP
#define UTILS_HPP

#include <string>

#if _WIN32 || _WIN64
#include <Windows.h>
typedef UINT32 uint32_t;
typedef INT32 int32_t;
#else
#include <cstdint>
#endif

namespace Platec {

std::string to_string(uint32_t value);

}

#endif
