import { z } from "zod";
import { useSearchParams } from "react-router-dom";
import { useMemo } from "react";

const SaveAgeQPCensusId = z.coerce.number().nullish().optional();
const SaveAgeQPRateId = z.coerce.number().nullish().optional();
const SaveAgeQPEffectiveDate = z.coerce.string().nullish().optional();

export const useSaveAgeQueryParams = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const params = useMemo(
    () => ({
      census_master_id: SaveAgeQPCensusId.parse(searchParams.get("cid")),
      set_census_master_id: (cid: number) => {
        searchParams.set("cid", cid.toString());
        setSearchParams(searchParams, { replace: true });
      },
      rate_master_id: SaveAgeQPRateId.parse(searchParams.get("rid")),
      set_rate_master_id: (rid: number) => {
        searchParams.set("rid", rid.toString());
        setSearchParams(searchParams, { replace: true });
      },
      effective_date: SaveAgeQPEffectiveDate.parse(searchParams.get("ed")),
      set_effective_date: (ed: string) => {
        searchParams.set("ed", ed);
        setSearchParams(searchParams, { replace: true });
      },
    }),
    [searchParams, setSearchParams]
  );
  return params;
};
