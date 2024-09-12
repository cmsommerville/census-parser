import { skipToken, queryOptions } from "@tanstack/react-query";
import { queryClient } from "@/extensions";
import { z } from "zod";
import {
  CensusMasterSchema,
  CensusStatsSchema,
  CensusUploadResponseSchema,
  CensusDetailListSchema,
  DropdownListItemSchema,
  RateMasterSchema,
  SaveAgeOutputSchema,
} from "./schemas";
import { FilterModel, IDatasource, SortModelItem } from "ag-grid-community";

const filterHandler = (filterModel: FilterModel | undefined) => {
  if (!filterModel) {
    return "";
  }
  const filterArray: string[] = [];
  for (const key in filterModel) {
    const filter = filterModel[key];
    if (filter.operator === "OR") {
      return;
    } else if (filter.operator === "AND") {
      for (const condition of filter.conditions) {
        filterArray.push(`${key}::${condition.type}::${condition.filter}`);
      }
    } else {
      filterArray.push(`${key}::${filter.type}::${filter.filter}`);
    }
  }
  return filterArray.join(";;");
};

const sortHandler = (sortModel: SortModelItem[] | undefined) => {
  if (!sortModel) {
    return "";
  }
  return sortModel
    .map((sort) => `${sort.sort === "desc" ? "-" : ""}${sort.colId}`)
    .join(",");
};

const getCensusMaster = async (id: number) => {
  const res = await fetch(`/api/census/${id}`);
  if (!res.ok) {
    throw new Error("Failed to fetch census");
  }
  const data = await res.json();
  return CensusMasterSchema.parse(data);
};

const getCensusMasterListByName = async (name: string) => {
  const res = await fetch(`/api/dd/census?name=${name}`);
  if (!res.ok) {
    throw new Error("Failed to fetch census");
  }
  const data = await res.json();
  return DropdownListItemSchema.parse(data);
};

const getRateMaster = async (id: number) => {
  const res = await fetch(`/api/rates/${id}`);
  if (!res.ok) {
    throw new Error("Failed to fetch rates");
  }
  const data = await res.json();
  return RateMasterSchema.parse(data);
};

const getRateMasterListByName = async (name: string) => {
  const res = await fetch(`/api/dd/rates?name=${name}`);
  if (!res.ok) {
    throw new Error("Failed to fetch rates");
  }
  const data = await res.json();
  return DropdownListItemSchema.parse(data);
};

const getCensusDetails = async (master_id: number) => {
  const res = await fetch(`/api/census/${master_id}/details`);
  if (!res.ok) {
    throw new Error("Failed to fetch census details");
  }
  const data = await res.json();
  return CensusDetailListSchema.parse(data);
};

const getCensusStatistics = async (master_id: number) => {
  const res = await fetch(`/api/census/${master_id}/stats`);
  if (!res.ok) {
    throw new Error("Failed to fetch census statistics");
  }
  const data = await res.json();
  return CensusStatsSchema.parse(data);
};

const calcSaveAge = async (
  census_master_id: number,
  rate_master_id: number,
  effective_date: string,
  offset: number = 0,
  limit: number = 100,
  filterModel: FilterModel | undefined = undefined,
  sortModel: SortModelItem[] | undefined = undefined
) => {
  let url = `/api/save-age?limit=${limit}&offset=${offset}`;
  if (filterModel && Object.keys(filterModel).length > 0) {
    url += `&filters=${filterHandler(filterModel)}`;
  }
  if (sortModel && sortModel.length > 0) {
    url += `&sort=${sortHandler(sortModel)}`;
  }

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ census_master_id, rate_master_id, effective_date }),
  });
  if (!res.ok) {
    throw new Error("Failed to calculate save age");
  }
  const data = await res.json();
  return SaveAgeOutputSchema.parse(data);
};

export const postNewCensus = async (files: File[], name?: string) => {
  const formData = new FormData();

  if (name) {
    formData.append("name", name);
  }
  files.forEach((file) => {
    formData.append("file", file);
  });

  const res = await fetch("/api/census/upload", {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    throw new Error("Failed to upload new census");
  }
  const data = await res.json();
  return CensusUploadResponseSchema.parse(data);
};

export const postNewRates = async (files: File[], name?: string) => {
  const formData = new FormData();
  if (name) {
    formData.append("name", name);
  }
  files.forEach((file) => {
    formData.append("file", file);
  });

  const res = await fetch("/api/rates/upload?umin=Y&umax=Y", {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    throw new Error("Failed to upload new rates");
  }
  const data = await res.json();
  return RateMasterSchema.parse(data);
};

export const CensusQueries = {
  getCensusMaster: (id: number | null | undefined) => {
    return queryOptions({
      queryKey: ["census", String(id)],
      queryFn: id ? () => getCensusMaster(id) : skipToken,
      staleTime: 1000 * 5,
      placeholderData: {
        census_master_id: -1,
        census_name: "",
      },
    });
  },
  getCensusMasterListByName: (name: string | undefined) => {
    return queryOptions({
      queryKey: ["census", "list", name ?? ""],
      queryFn: name ? () => getCensusMasterListByName(name) : skipToken,
      placeholderData: [],
    });
  },
  getCensusDetails: (master_id: number | null | undefined) => {
    return queryOptions({
      queryKey: ["census", String(master_id), "details"],
      queryFn: master_id ? () => getCensusDetails(master_id) : skipToken,
      placeholderData: [],
    });
  },
  getCensusStats: (master_id: number | null | undefined) => {
    return queryOptions({
      queryKey: ["census", String(master_id), "stats"],
      queryFn: master_id ? () => getCensusStatistics(master_id) : skipToken,
      placeholderData: {
        tobacco_stats: [],
        issue_age_stats: [],
        relationship_stats: [],
        tenure_stats: [],
      },
    });
  },
  calcSaveAge: (
    census_master_id: number | null | undefined,
    rate_master_id: number | null | undefined,
    effective_date: string | null | undefined,
    filterModel: FilterModel | undefined = undefined,
    sortModel: SortModelItem[] | undefined = undefined,
    offset: number = 0,
    limit: number = 100
  ) => {
    return queryOptions({
      queryKey: [
        "save-age",
        String(census_master_id),
        String(rate_master_id),
        String(effective_date),
        String(offset),
        String(limit),
        filterModel,
        sortModel,
      ],
      queryFn:
        census_master_id != null &&
        rate_master_id != null &&
        !!effective_date &&
        z.string().date().safeParse(effective_date).success
          ? () =>
              calcSaveAge(
                census_master_id,
                rate_master_id,
                effective_date,
                offset,
                limit,
                filterModel,
                sortModel
              )
          : skipToken,
      staleTime: 1000 * 5,
      placeholderData: (previousData) => {
        if (previousData) return previousData;
        return {
          data: [],
          stats: { count: 0 },
        };
      },
    });
  },
  getRateMaster: (id: number | null | undefined) => {
    return queryOptions({
      queryKey: ["rates", String(id)],
      queryFn: id ? () => getRateMaster(id) : skipToken,
      placeholderData: {
        rate_master_id: -1,
        rate_master_name: "",
      },
    });
  },
  getRateMasterListByName: (name: string | undefined) => {
    return queryOptions({
      queryKey: ["rates", "list", name ?? ""],
      queryFn: name ? () => getRateMasterListByName(name) : skipToken,
      placeholderData: [],
    });
  },
};

export const createSaveAgeGridDatasource: (
  census_master_id: number | null | undefined,
  rate_master_id: number | null | undefined,
  effective_date: string | null | undefined
) => IDatasource = (census_master_id, rate_master_id, effective_date) => ({
  // called by the grid when more rows are required
  getRows: async (params) => {
    const { endRow, filterModel, sortModel, startRow } = params;
    const offset = startRow ?? 0;
    const limit = (endRow ?? offset + 100) - offset;

    try {
      // get data for request from server
      const d = await queryClient.ensureQueryData(
        CensusQueries.calcSaveAge(
          census_master_id,
          rate_master_id,
          effective_date,
          filterModel,
          sortModel,
          offset,
          limit
        )
      );
      const { data, stats } = d;
      params.successCallback(data, stats.count);
    } catch (err) {
      console.log(err);
      params.failCallback();
    }
  },
});
