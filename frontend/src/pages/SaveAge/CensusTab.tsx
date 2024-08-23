import { ColDef } from "ag-grid-community";
import { useQuery } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { Button } from "@/components/ui/button";
import Grid from "@/components/Grid";
import { CensusQueries } from "./queries";

const CENSUS_COL_DEFS: ColDef[] = [
  { headerName: "Birthdate", field: "birthdate" },
  { headerName: "Relationship", field: "relationship" },
  { headerName: "Tobacco", field: "tobacco_disposition" },
  { headerName: "Effective Date", field: "effective_date" },
];

interface CensusTabProps {
  census_master_id: number;
}
const CensusTab = ({ census_master_id }: CensusTabProps) => {
  const qryCensusMaster = useQuery(
    CensusQueries.getCensusMaster(census_master_id)
  );
  const qryCensusDetails = useQuery(
    CensusQueries.getCensusDetails(census_master_id)
  );

  if (qryCensusDetails.data) {
    return (
      <div className="grid grid-cols-3 2xl:grid-cols-5 gap-6">
        <div className="col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Census</CardTitle>
              <CardDescription>Enter a census and some rates!</CardDescription>
            </CardHeader>
            <CardContent className="h-96">
              <Grid
                rowData={qryCensusDetails.data}
                columnDefs={CENSUS_COL_DEFS}
              />
            </CardContent>
          </Card>
        </div>

        <div className="">
          <Card>
            <CardHeader>
              <CardTitle>Census</CardTitle>
              <CardDescription>
                {qryCensusMaster.data
                  ? qryCensusMaster.data.census_name
                  : "Select a census!"}
              </CardDescription>
            </CardHeader>
            <CardContent className="h-96">
              <Button onClick={() => console.log("clicked")}>
                Upload Census
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }
  if (qryCensusDetails.isError) {
    return <div>Error: {qryCensusDetails.error.message}</div>;
  }
  return <div>Loading...</div>;
};

export default CensusTab;
