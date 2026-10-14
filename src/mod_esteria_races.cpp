#include "Config.h"
#include "Log.h"
#include "ScriptMgr.h"

namespace
{
bool ModuleEnabled = false;
bool StrictStartup = true;
}

class EsteriaRacesWorldScript final : public WorldScript
{
public:
    EsteriaRacesWorldScript() : WorldScript("EsteriaRacesWorldScript")
    {
    }

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        ModuleEnabled = sConfigMgr->GetOption<bool>("EsteriaRaces.Enable", false);
        StrictStartup = sConfigMgr->GetOption<bool>("EsteriaRaces.StrictStartup", true);
    }

    void OnStartup() override
    {
        if (!ModuleEnabled)
        {
            LOG_INFO("module.esteria-races", "mod-esteria-races is installed but disabled.");
            return;
        }

        if (StrictStartup)
        {
            LOG_ERROR("module.esteria-races",
                "mod-esteria-races cannot enable custom race creation yet: the reconciled identity policy "
                "and pinned AzerothCore adapter have not been generated. Custom race behavior remains disabled.");
            return;
        }

        LOG_WARN("module.esteria-races",
            "EsteriaRaces.StrictStartup is disabled, but no reconciled identity policy is installed. "
            "This development skeleton does not enable custom race behavior.");
    }
};

void AddSC_mod_esteria_races()
{
    new EsteriaRacesWorldScript();
}
