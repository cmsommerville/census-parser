import { createContext, useContext } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ColDef } from "ag-grid-community";
import Grid from "./components/Grid";

const DATA = [
  { age: 0, rate: 0.0 },
  { age: 1, rate: 1.0 },
  { age: 2, rate: 2.0 },
  { age: 3, rate: 3.0 },
  { age: 4, rate: 4.0 },
];

const COL_DEFS: ColDef[] = [
  { headerName: "Age", field: "age" },
  { headerName: "Rate", field: "rate" },
];

const SaveAgeContext = createContext({
  data: DATA,
});

function App() {
  return (
    <SaveAgeContext.Provider value={{ data: DATA }}>
      <div className="grid grid-cols-3">
        <div className="col-span-2">
          <Tabs defaultValue="account" className="">
            <TabsList>
              <TabsTrigger value="account">Save Age</TabsTrigger>
              <TabsTrigger value="password">Password</TabsTrigger>
            </TabsList>
            <TabsContent value="account">
              <SaveAgeGrid />
            </TabsContent>
            <TabsContent value="password">
              Change your password here.
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </SaveAgeContext.Provider>
  );
}

const SaveAgeGrid = () => {
  const { data } = useContext(SaveAgeContext);
  return (
    <Card>
      <CardHeader>
        <CardTitle>Save Age Report</CardTitle>
        <CardDescription>Enter a census and some rates!</CardDescription>
      </CardHeader>
      <CardContent className="h-96">
        <Grid
          className="ag-theme-quartz"
          rowData={data}
          columnDefs={COL_DEFS}
        />
      </CardContent>
    </Card>
  );
};

export default App;
