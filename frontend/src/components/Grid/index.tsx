import { cn } from "@/lib/utils";
import { AgGridReact, AgGridReactProps } from "ag-grid-react";
import { useMemo } from "react";
import { COLUMN_TYPES } from "./column-types";

interface GridProps extends AgGridReactProps {}

const Grid = ({ className, defaultColDef, ...props }: GridProps) => {
  const defColDefs = useMemo(
    () => ({
      sortable: true,
      filter: true,
      resizable: true,
      ...defaultColDef,
    }),
    [defaultColDef]
  );

  return (
    <AgGridReact
      className={cn("ag-grid-custom h-full w-full", className)}
      defaultColDef={defColDefs}
      columnTypes={COLUMN_TYPES}
      {...props}
    />
  );
};

export default Grid;
