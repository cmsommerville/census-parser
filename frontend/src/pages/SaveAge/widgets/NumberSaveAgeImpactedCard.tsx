import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { SaveAgeOutputType } from "../schemas";
import { UseQueryResult } from "@tanstack/react-query";

interface NumberSaveAgeImpactedCardProps {
  className?: string;
  query: UseQueryResult<SaveAgeOutputType>;
}
export const NumberSaveAgeImpactedCard = ({
  className,
  query,
}: NumberSaveAgeImpactedCardProps) => {
  if (!query || !query.data || query.data.data.length === 0) {
    return (
      <Card className={className}>
        <CardHeader className="w-full pt-6 pb-3">
          <CardTitle className="text-2xl font-semibold"># Impacted</CardTitle>
        </CardHeader>
        <CardContent className="w-full space-y-6">
          <section id="tobacco-dist-stats">
            <h3 className="text-muted-foreground my-0">
              Make sure that you have selected a census, rate set, and effective
              date below to see how many people will have rate changes!
            </h3>
          </section>
        </CardContent>
      </Card>
    );
  }

  if (query.data && !query.isPlaceholderData) {
    return (
      <Card
        className={cn(
          className,
          query.isPlaceholderData ? "text-inherit/90 italic" : ""
        )}
      >
        <CardHeader className="pb-4">
          <CardTitle># Impacted</CardTitle>
          <CardDescription>
            Number of insureds with X% rate increase
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="text-medium min-w-24">Same or less</div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Progress
                    value={
                      ((query.data.stats.pct_range_le_0 ?? 0) /
                        (query.data.stats.count ?? 0)) *
                      100
                    }
                  />
                </TooltipTrigger>
                <TooltipContent>
                  <p>
                    {query.data.stats.pct_range_le_0} out of{" "}
                    {query.data.stats.count} insureds
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <div className="flex items-center justify-between">
            <div className="text-medium min-w-24">0 - 10%</div>

            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Progress
                    value={
                      (((query.data.stats.pct_range_00_05 ?? 0) +
                        (query.data.stats.pct_range_05_10 ?? 0)) /
                        (query.data.stats.count ?? 0)) *
                      100
                    }
                  />
                </TooltipTrigger>
                <TooltipContent>
                  <p>
                    {(query.data.stats.pct_range_00_05 ?? 0) +
                      (query.data.stats.pct_range_05_10 ?? 0)}{" "}
                    out of {query.data.stats.count} insureds
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <div className="flex items-center justify-between">
            <div className="text-medium min-w-24">10 - 20%</div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Progress
                    value={
                      ((query.data.stats.pct_range_10_20 ?? 0) /
                        (query.data.stats.count ?? 0)) *
                      100
                    }
                  />
                </TooltipTrigger>
                <TooltipContent>
                  <p>
                    {query.data.stats.pct_range_10_20 ?? 0} out of{" "}
                    {query.data.stats.count} insureds
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <div className="flex items-center justify-between">
            <div className="text-medium min-w-24">{"> 20%"}</div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Progress
                    value={
                      ((query.data.stats.pct_range_gt_20 ?? 0) /
                        (query.data.stats.count ?? 0)) *
                      100
                    }
                  />
                </TooltipTrigger>
                <TooltipContent>
                  <p>
                    {query.data.stats.pct_range_gt_20 ?? 0} out of{" "}
                    {query.data.stats.count} insureds
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </CardContent>
        <CardFooter></CardFooter>
      </Card>
    );
  }
  return (
    <Card
      className={cn(
        className,
        query.isPlaceholderData ? "text-inherit/90 italic" : ""
      )}
    >
      <CardHeader className="pb-2">
        <CardDescription># Impacted</CardDescription>
        <CardTitle className="text-4xl">—</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-xs text-muted-foreground">
          Select a census, rate set, and effective date!
        </div>
      </CardContent>
      <CardFooter>
        <Progress value={0} aria-label="0" />
      </CardFooter>
    </Card>
  );
};
