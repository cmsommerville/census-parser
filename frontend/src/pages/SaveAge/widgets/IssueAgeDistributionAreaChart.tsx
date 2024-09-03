import { useTailwindConfig } from "@/hooks/useTailwindConfig";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import {
  Area,
  AreaChart,
  Label as RechartsLabel,
  XAxis,
  CartesianGrid,
  ReferenceLine,
  Tooltip as TooltipChart,
} from "recharts";
import { ChartConfig, ChartContainer } from "@/components/ui/chart";

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "#2563eb",
  },
  mobile: {
    label: "Mobile",
    color: "#60a5fa",
  },
} satisfies ChartConfig;

interface IssueAgeDistributionChartProps {
  className?: string;
  data: { issue_age: number; count: number }[] | undefined;
}

const calcAgeDistribution = (data: { issue_age: number; count: number }[]) => {
  let total = 0;
  data.forEach((item) => {
    total += item.count;
  });

  return data.map((row) => {
    return { ...row, pct: row.count / total };
  });
};
const calcAverageAge = (data: { issue_age: number; count: number }[]) => {
  let total = 0;
  let count = 0;
  data.forEach((item) => {
    total += item.issue_age * item.count;
    count += item.count;
  });
  return total / count;
};

export const IssueAgeDistributionChart = ({
  className,
  data,
}: IssueAgeDistributionChartProps) => {
  if (!data || data.length === 0) {
    return (
      <Card className={className}>
        <CardHeader className="w-full pt-6 pb-3">
          <CardTitle className="text-2xl font-semibold">
            Issue Age Distribution
          </CardTitle>
        </CardHeader>
        <CardContent className="w-full space-y-6">
          <section id="tobacco-dist-stats">
            <h3 className="text-muted-foreground my-0">
              Please select or upload a census below to see the issue age
              distribution!
            </h3>
          </section>
        </CardContent>
      </Card>
    );
  }

  const tw = useTailwindConfig();
  const chartData = data && data.length > 0 ? calcAgeDistribution(data) : [];
  const averageAge = data && data.length > 0 ? calcAverageAge(data) : undefined;

  return (
    <Card className={className}>
      <CardHeader className="w-full py-6">
        <CardTitle className="text-2xl font-semibold">
          Issue Age Distribution
        </CardTitle>
      </CardHeader>
      <CardContent style={{ backgroundColor: "var(--primary)" }}>
        <ChartContainer config={chartConfig} className="h-32 w-full">
          <AreaChart accessibilityLayer data={chartData}>
            <XAxis
              dataKey="issue_age"
              ticks={[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]}
            >
              <RechartsLabel
                value="Issue Age"
                position="insideBottom"
                offset={-3}
              />
            </XAxis>
            <CartesianGrid strokeDasharray="3 3" />
            <TooltipChart
              formatter={(value) => {
                const val = value as number;
                return [`${(val * 100).toFixed(1)}%`, "Percent"];
              }}
            />
            <Area
              type="monotone"
              dataKey="pct"
              stroke={tw.theme.colors.cyan[600]}
              fillOpacity={0.8}
              fill={tw.theme.colors.cyan[500]}
            />
            <ReferenceLine
              x={Math.round(averageAge ?? 0)}
              isFront
              stroke={tw.theme.colors.cyan[600]}
            >
              <RechartsLabel
                value={`Avg: ${averageAge?.toFixed(1)}`}
                position="insideTopLeft"
              />
            </ReferenceLine>
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};
