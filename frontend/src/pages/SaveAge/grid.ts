import { ColDef } from "ag-grid-community";

export const SAVE_AGE_COL_DEFS: ColDef[] = [
  { headerName: "Birthdate", field: "birthdate" },
  { headerName: "Relationship", field: "relationship" },
  { headerName: "Tobacco", field: "tobacco_disposition" },
  {
    headerName: "Issue Age",
    field: "issue_age",
    filter: "agNumberColumnFilter",
    type: "number0",
  },
  { headerName: "Save Age Effective Date", field: "save_age_effective_date" },
  { headerName: "New Effective Date", field: "new_effective_date" },
  {
    headerName: "Save Age Rate",
    field: "save_age_rate",
    filter: "agNumberColumnFilter",
    type: "dollarsandcents",
  },
  {
    headerName: "New Rate",
    field: "new_rate",
    filter: "agNumberColumnFilter",
    type: "dollarsandcents",
  },
  {
    headerName: "Diff",
    field: "diff",
    filter: "agNumberColumnFilter",
    type: "dollarsandcents",
    pinned: "right",
  },
];
