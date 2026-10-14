#include "Config.h"
#include "Log.h"
#include "ScriptMgr.h"
#include "RacePolicy.h"
#include "generated/RaceDefinitions.h"
#include <mutex>

namespace
{
CustomRaces::Policy RacePolicy{CustomRaces::InstalledRaces};
std::mutex PolicyMutex;

// This source distribution does not yet supply a validated core/client adapter.
// A config switch must never substitute for a compiled, matched release contract.
constexpr bool MatchedReleaseReady = false;
}

class CustomRacesWorldScript final : public WorldScript
{
public:
    CustomRacesWorldScript() : WorldScript("CustomRacesWorldScript",
        { WORLDHOOK_ON_AFTER_CONFIG_LOAD, WORLDHOOK_ON_STARTUP }) { }

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        std::lock_guard<std::mutex> lock(PolicyMutex);
        auto next = RacePolicy;
        next.enabled = sConfigMgr->GetOption<bool>("CustomRaces.Enable", false);
        next.ready = CustomRaces::IdentityPolicyResolved && MatchedReleaseReady;
        std::string error;
        if (!CustomRaces::ParseCreationSelection(
            sConfigMgr->GetOption<std::string>("CustomRaces.CreationRaces", "all"),
            next.installed, next.creation, error))
        {
            // Fail closed for owned races while keeping the last valid selector.
            RacePolicy.enabled = false;
            LOG_ERROR("module.custom-races", "CustomRaces.CreationRaces: {}; owned creation disabled.", error);
            return;
        }
        RacePolicy = next;
        if (RacePolicy.enabled && !RacePolicy.ready)
            LOG_ERROR("module.custom-races", "Custom races cannot be enabled: a reconciled identity policy "
                "and matched core/client/data release are required. Owned creation remains disabled.");
    }

    void OnStartup() override
    {
        // Load explicitly as well: initial config dispatch can precede module loading.
        OnAfterConfigLoad(false);
        std::lock_guard<std::mutex> lock(PolicyMutex);
        LOG_INFO("module.custom-races", "mod-custom-races: requested={}, ready={}, identity policy={}",
            RacePolicy.enabled, RacePolicy.ready, CustomRaces::PolicyDigest);
    }
};

class CustomRacesAccountScript final : public AccountScript
{
public:
    CustomRacesAccountScript() : AccountScript("CustomRacesAccountScript",
        { ACCOUNTHOOK_CAN_ACCOUNT_CREATE_CHARACTER }) { }

    bool CanAccountCreateCharacter(uint32 /*accountId*/, uint8 race, uint8 /*charClass*/) override
    {
        std::lock_guard<std::mutex> lock(PolicyMutex);
        return RacePolicy.CanCreate(race);
    }
};

void AddSC_mod_custom_races()
{
    new CustomRacesWorldScript();
    new CustomRacesAccountScript();
}
