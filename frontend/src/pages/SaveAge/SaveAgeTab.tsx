import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Upload } from "lucide-react";

import ComboboxTypeahead from "@/components/Combobox";
import Grid from "@/components/Grid";
import UploadCensusModal from "./UploadCensusModal";
import UploadRatesModal from "./UploadRatesModal";
import { CensusQueries, createSaveAgeGridDatasource } from "./queries";
import { useSaveAgeQueryParams } from "./utils";
import { SAVE_AGE_COL_DEFS } from "./grid";
import { Datepicker } from "@/components/Datepicker";

const SaveAgeTab = () => {
  const { census_master_id, rate_master_id, effective_date } =
    useSaveAgeQueryParams();

  const datasource = useMemo(() => {
    return createSaveAgeGridDatasource(
      census_master_id,
      rate_master_id,
      effective_date
    );
  }, [census_master_id, rate_master_id, effective_date]);

  return (
    <div className="grid grid-cols-3 2xl:grid-cols-8 gap-6">
      <div className="col-span-2 2xl:col-span-6">
        <Card>
          <CardHeader>
            <CardTitle>Save Age Report</CardTitle>
            <CardDescription>Enter a census and some rates!</CardDescription>
          </CardHeader>
          <CardContent className="h-96">
            <Grid
              columnDefs={SAVE_AGE_COL_DEFS}
              rowModelType="infinite"
              datasource={datasource}
              onFirstDataRendered={(params) => {
                params.api.autoSizeAllColumns();
              }}
            />
          </CardContent>
        </Card>
      </div>
      <SelectorSidePanel />
    </div>
  );
};

const SelectorSidePanel = () => {
  const {
    census_master_id,
    set_census_master_id,
    rate_master_id,
    set_rate_master_id,
    effective_date,
    set_effective_date,
  } = useSaveAgeQueryParams();

  const [_, setLocalFormData] = useState({
    census_master_id: census_master_id ? String(census_master_id) : "",
    rate_master_id: rate_master_id ? String(rate_master_id) : "",
    effective_date: effective_date ?? "",
  });

  const qryCensusMaster = useQuery(
    CensusQueries.getCensusMaster(census_master_id)
  );
  const qryRateMaster = useQuery(CensusQueries.getRateMaster(rate_master_id));

  const selectedCensus = useMemo(() => {
    if (!census_master_id) {
      return {
        id: -1,
        name: "",
      };
    }
    return {
      id: census_master_id,
      name: qryCensusMaster.data?.census_name ?? "",
    };
  }, [qryCensusMaster.data]);

  const selectedRateMaster = useMemo(() => {
    if (!rate_master_id) {
      return {
        id: -1,
        name: "",
      };
    }
    return {
      id: rate_master_id,
      name: qryRateMaster.data?.rate_master_name ?? "",
    };
  }, [qryRateMaster.data]);

  return (
    <div className="col-span-1 2xl:col-span-2 flex flex-col space-y-4">
      <Card>
        <CardContent className="py-6">
          <div className="space-y-4">
            <div className="grid grid-cols-4 xl:grid-cols-5 gap-4 items-center">
              <div className="col-span-3 xl:col-span-4 w-full">
                <ComboboxTypeahead
                  label="Census"
                  defaultValue={selectedCensus}
                  onSelect={(selection) =>
                    set_census_master_id(Number(selection.id))
                  }
                  queryOptions={CensusQueries.getCensusMasterListByName}
                />
              </div>
              <div className="h-full flex items-center">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <UploadCensusModal
                        onUploadSuccess={(data) =>
                          set_census_master_id(data.census_master_id)
                        }
                      >
                        <button className="mt-5 w-9 h-9 p-1.5 flex items-center justify-center rounded-lg text-muted-foreground/50 transition-colors hover:text-foreground md:w-8 md:h-8">
                          <Upload />
                          <span className="sr-only">Upload New Census</span>
                        </button>
                      </UploadCensusModal>
                    </TooltipTrigger>
                    <TooltipContent side="left">
                      Upload a new census
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            </div>

            <div className="grid grid-cols-4 xl:grid-cols-5 gap-4 items-center">
              <div className="col-span-3 xl:col-span-4 w-full">
                <ComboboxTypeahead
                  label="Rate Set"
                  defaultValue={selectedRateMaster}
                  onSelect={(selection) =>
                    set_rate_master_id(Number(selection.id))
                  }
                  queryOptions={CensusQueries.getRateMasterListByName}
                />
              </div>
              <div className="h-full flex items-center">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <UploadRatesModal
                        onUploadSuccess={(data) =>
                          set_rate_master_id(data.rate_master_id)
                        }
                      >
                        <button className="mt-5 w-9 h-9 p-1.5 flex items-center justify-center rounded-lg text-muted-foreground/50 transition-colors hover:text-foreground md:w-8 md:h-8">
                          <Upload />
                          <span className="sr-only">Upload New Census</span>
                        </button>
                      </UploadRatesModal>
                    </TooltipTrigger>
                    <TooltipContent side="left">
                      Upload a new census
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            </div>

            <div className="grid grid-cols-4 xl:grid-cols-5 gap-4 items-center">
              <div className="col-span-3 xl:col-span-4 w-full">
                <Datepicker
                  dateFormat="M/d/yyyy"
                  defaultValue={effective_date}
                  onSelect={(dt) => {
                    setLocalFormData((prev) => ({
                      ...prev,
                      effective_date: dt,
                    }));
                    set_effective_date(dt);
                  }}
                >
                  Effective Date
                </Datepicker>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SaveAgeTab;
