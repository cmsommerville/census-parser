import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { Progress } from "@/components/ui/progress";
import { CensusStatsType } from "../schemas";

interface StatisticProgressBarsProps {
  data: CensusStatsType | undefined;
}

export const StatisticProgressBars = ({ data }: StatisticProgressBarsProps) => {
  if (data == null) {
    return "Loading..."; // TODO: add skeleton components
  }

  const tobacco_distribution = calcTobaccoPercentages(data.tobacco_stats);
  const { avg: avgTenure, max: maxTenure } = calcTenureSummaryStats(
    data.tenure_stats
  );

  return (
    <Card className="">
      <CardHeader className="w-full pt-6 pb-3">
        <CardTitle className="text-2xl font-semibold">
          Census Statistics
        </CardTitle>
      </CardHeader>
      <CardContent className="w-full space-y-6">
        <section id="tobacco-dist-stats">
          <h3 className="text-muted-foreground my-0">% Non Tobacco Users</h3>
          <div className="grid grid-cols-5 xl:grid-cols-3 2xl:grid-cols-5 gap-4 items-center">
            <div className="text-2xl font-semibold">
              {`${(tobacco_distribution?.N * 100).toFixed(0)}%`}
            </div>
            <Progress
              className="[&>*]:bg-rose-500 col-span-4 xl:col-span-2 2xl:col-span-4"
              value={tobacco_distribution?.N * 100}
              aria-label={`${(tobacco_distribution?.N * 100).toFixed(
                0
              )}% increase`}
            />
          </div>
        </section>
        <section id="tenure-dist-stats">
          <h3 className="text-muted-foreground my-0">Average Tenure</h3>
          <div className="grid grid-cols-5 xl:grid-cols-3 2xl:grid-cols-5 gap-4 items-center">
            <div className="text-2xl font-semibold">
              {`${avgTenure.toFixed(0)} Yrs`}
            </div>
            <Progress
              className="[&>*]:bg-emerald-500 col-span-4 xl:col-span-2 2xl:col-span-4"
              color="green"
              value={(avgTenure / maxTenure) * 100}
              aria-label={`${avgTenure.toFixed(1)}% increase`}
            />
          </div>
        </section>
      </CardContent>
    </Card>
  );
};

const calcTobaccoPercentages = (
  data: {
    tobacco_disposition: string;
    count: number;
  }[]
) => {
  const total = data.reduce((acc, item) => acc + item.count, 0);
  return data.reduce((acc, item) => {
    const { tobacco_disposition } = item;
    const pct = item.count / total;
    return { ...acc, [tobacco_disposition]: pct };
  }, {} as { [k: string]: number });
};

const calcTenureSummaryStats = (data: { tenure: number; count: number }[]) => {
  const total = data.reduce((acc, item) => acc + item.count, 0);
  const max = data.reduce((acc, item) => Math.max(acc, item.tenure), 0);
  const avg = data.reduce(
    (acc, item) => acc + item.tenure * (item.count / total),
    0
  );
  return { avg, max };
};
