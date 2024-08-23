import { useQuery } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { CensusQueries } from "./queries";
import { useSaveAgeQueryParams } from "./utils";
import SaveAgeTab from "./SaveAgeTab";
import CensusTab from "./CensusTab";
import { StatisticProgressBars } from "./widgets/StatisticProgressBars";
import { IssueAgeDistributionChart } from "./widgets/IssueAgeDistributionAreaChart";

const SaveAgeLanding = () => {
  const { census_master_id, rate_master_id, effective_date } =
    useSaveAgeQueryParams();

  const qrySaveAge = useQuery(
    CensusQueries.calcSaveAge(census_master_id, rate_master_id, effective_date)
  );
  const qryCensusStats = useQuery(
    CensusQueries.getCensusStats(census_master_id)
  );
  console.log("SaveAgeLanding...");

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-2 xl:grid-cols-4">
        <StatisticProgressBars data={qryCensusStats?.data} />
        <IssueAgeDistributionChart
          data={qryCensusStats?.data?.issue_age_stats}
        />
        <Card
          className={
            qrySaveAge.isPlaceholderData ? "text-inherit/90 italic" : ""
          }
        >
          <CardHeader className="pb-2">
            <CardDescription>Premium Foregone</CardDescription>
            <CardTitle className="text-4xl">
              {qrySaveAge && qrySaveAge.data && qrySaveAge.data.stats?.diff
                ? new Intl.NumberFormat("en-US", {
                    style: "currency",
                    currency: "USD",
                    maximumFractionDigits: 0,
                  }).format(qrySaveAge?.data?.stats.diff)
                : "—"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">
              Saving age will result in a loss of this premium!
            </div>
          </CardContent>
          <CardFooter>
            <Progress value={25} aria-label="25% increase" />
          </CardFooter>
        </Card>
      </div>

      <Tabs defaultValue="save-age" className="">
        <TabsList>
          <TabsTrigger value="save-age">Save Age</TabsTrigger>
          <TabsTrigger value="census">Census</TabsTrigger>
          <TabsTrigger value="rates">Rates</TabsTrigger>
        </TabsList>
        <TabsContent value="save-age">
          <SaveAgeTab />
        </TabsContent>
        <TabsContent value="census">
          <CensusTab census_master_id={census_master_id ?? -1} />
        </TabsContent>
        <TabsContent value="rates">
          <div>Enter rates...</div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SaveAgeLanding;
