#ifndef CUSTOM_RACES_POLICY_H
#define CUSTOM_RACES_POLICY_H

#include <array>
#include <cstdint>
#include <string>
#include <string_view>

namespace CustomRaces
{
inline constexpr std::size_t RaceCapacity = 129; // zero is not a race
using RaceSet = std::array<bool, RaceCapacity>;

constexpr bool IsStockRace(unsigned race)
{
    return race >= 1 && race <= 11 && race != 9;
}

// Parse a narrowing selector against immutable, generated content ownership.
// Invalid input never updates the caller's prior policy.
bool ParseCreationSelection(std::string_view text, RaceSet const& installed,
    RaceSet& selected, std::string& error);

struct Policy
{
    RaceSet installed{};
    RaceSet creation{};
    bool enabled = false;
    bool ready = false;

    bool CanCreate(unsigned race) const
    {
        if (race == 0 || race >= RaceCapacity)
            return false;
        if (IsStockRace(race) || !installed[race])
            return true; // foreign races remain the host core/module's responsibility
        return enabled && ready && creation[race];
    }
};
}
#endif
