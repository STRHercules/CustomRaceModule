#include "RacePolicy.h"
#include <cstdlib>
#include <iostream>

void Check(bool condition)
{
    if (!condition)
    {
        std::cerr << "RacePolicy check failed\n";
        std::exit(1);
    }
}

int main()
{
    CustomRaces::Policy policy;
    policy.installed[48] = policy.installed[128] = true;
    std::string error;
    Check(CustomRaces::ParseCreationSelection("all", policy.installed, policy.creation, error));
    for (unsigned race : {1u, 2u, 3u, 4u, 5u, 6u, 7u, 8u, 10u, 11u, 66u})
        Check(policy.CanCreate(race)); // stock and foreign checks stay with the host
    Check(!policy.CanCreate(0) && !policy.CanCreate(129));
    Check(!policy.CanCreate(48) && !policy.CanCreate(128));
    policy.enabled = true;
    Check(!policy.CanCreate(48)); // no ready adapter
    policy.ready = true;
    Check(policy.CanCreate(48) && policy.CanCreate(128));
    Check(CustomRaces::ParseCreationSelection(" 128 ", policy.installed, policy.creation, error));
    Check(policy.CanCreate(128) && !policy.CanCreate(48));
    auto const prior = policy.creation;
    for (auto const* invalid : {"", "48,", ",48", "48,,128", "48,48", "1", "66", "0", "129", "-1", "+48", "48junk", "ALL", "4294967296"})
    {
        Check(!CustomRaces::ParseCreationSelection(invalid, policy.installed, policy.creation, error));
        Check(policy.creation == prior && !error.empty());
    }
    Check(CustomRaces::ParseCreationSelection("none", policy.installed, policy.creation, error));
    Check(!policy.CanCreate(48) && !policy.CanCreate(128) && policy.CanCreate(1));
    Check(CustomRaces::ParseCreationSelection("48, 128", policy.installed, policy.creation, error));
    Check(policy.CanCreate(48) && policy.CanCreate(128));
    policy.enabled = false;
    Check(!policy.CanCreate(48) && policy.CanCreate(1) && policy.CanCreate(66));
    std::cout << "RacePolicy: boundary, ownership, selector and readiness checks passed\n";
}
