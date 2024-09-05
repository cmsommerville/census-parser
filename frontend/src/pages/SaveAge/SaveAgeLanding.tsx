import { useQuery } from "@tanstack/react-query";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CensusQueries } from "./queries";
import { useSaveAgeQueryParams } from "./utils";
import SaveAgeTab from "./SaveAgeTab";
import CensusTab from "./CensusTab";
import { StatisticProgressBars } from "./widgets/StatisticProgressBars";
import { IssueAgeDistributionChart } from "./widgets/IssueAgeDistributionAreaChart";
import { NumberSaveAgeImpactedCard } from "./widgets/NumberSaveAgeImpactedCard";

const SaveAgeLanding = () => {
  const { tab, set_tab, census_master_id, rate_master_id, effective_date } =
    useSaveAgeQueryParams();

  const qrySaveAge = useQuery(
    CensusQueries.calcSaveAge(census_master_id, rate_master_id, effective_date)
  );
  const qryCensusStats = useQuery(
    CensusQueries.getCensusStats(census_master_id)
  );

  const handleTabChange = (tab: string) => {
    if (!tab) {
      set_tab("save-age");
    } else {
      set_tab(tab);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-4 grid-cols-3 lg:grid-cols-3">
        <StatisticProgressBars
          className="hidden lg:block"
          data={qryCensusStats?.data}
        />
        <IssueAgeDistributionChart
          className=""
          data={qryCensusStats?.data?.issue_age_stats}
        />
        <NumberSaveAgeImpactedCard
          className="col-span-2 lg:col-span-1"
          query={qrySaveAge}
        />
      </div>

      <Tabs
        defaultValue={tab ?? "save-age"}
        onValueChange={handleTabChange}
        className=""
      >
        <TabsList>
          <TabsTrigger value="save-age">Save Age</TabsTrigger>
          <TabsTrigger value="census">Census</TabsTrigger>
          <TabsTrigger value="rates">Rates</TabsTrigger>
        </TabsList>
        <TabsContent value="save-age">
          <SaveAgeTab />
        </TabsContent>
        <TabsContent value="census">
          <CensusTab />
        </TabsContent>
        <TabsContent value="rates">
          <div>Enter rates...</div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SaveAgeLanding;
