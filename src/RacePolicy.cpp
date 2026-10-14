#include "RacePolicy.h"
#include <charconv>

namespace CustomRaces
{
namespace
{
std::string_view Trim(std::string_view text)
{
    auto const first = text.find_first_not_of(" \t\r\n");
    if (first == std::string_view::npos)
        return {};
    auto const last = text.find_last_not_of(" \t\r\n");
    return text.substr(first, last - first + 1);
}
}

bool ParseCreationSelection(std::string_view text, RaceSet const& installed,
    RaceSet& selected, std::string& error)
{
    RaceSet next{};
    text = Trim(text);
    error.clear();
    if (text == "all")
        next = installed;
    else if (text != "none")
    {
        if (text.empty())
        {
            error = "use all, none, or a comma-separated list of installed race IDs";
            return false;
        }
        while (true)
        {
            auto const comma = text.find(',');
            auto const token = Trim(text.substr(0, comma));
            if (token.empty())
            {
                error = "creation selection contains an empty race ID";
                return false;
            }
            unsigned race = 0;
            auto const result = std::from_chars(token.data(), token.data() + token.size(), race);
            if (result.ec != std::errc{} || result.ptr != token.data() + token.size()
                || race == 0 || race >= RaceCapacity || IsStockRace(race)
                || !installed[race] || next[race])
            {
                error = "creation selection contains an invalid, duplicate, stock, or uninstalled race ID";
                return false;
            }
            next[race] = true;
            if (comma == std::string_view::npos)
                break;
            text.remove_prefix(comma + 1);
        }
    }
    selected = next;
    return true;
}
}
