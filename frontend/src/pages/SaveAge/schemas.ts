import { z } from "zod";

export const DropdownListItemSchema = z.array(
  z.object({
    id: z.number(),
    name: z.string(),
  })
);

export const CensusDetailSchema = z.object({
  census_detail_id: z.number(),
  census_master_id: z.number(),
  birthdate: z.string(),
  relationship: z.string(),
  tobacco_disposition: z.string(),
  effective_date: z.string(),
});

export const CensusDetailListSchema = z.array(CensusDetailSchema);

export const CensusMasterSchema = z.object({
  census_master_id: z.number(),
  census_name: z.string(),
  census_path: z.string().optional(),
});

export type CensusMasterType = z.infer<typeof CensusMasterSchema>;

export const RateDetailSchema = z.object({
  rate_detail_id: z.number(),
  rate_master_id: z.number(),
  lower_age: z.number(),
  upper_age: z.number(),
  relationship: z.string(),
  tobacco_disposition: z.string(),
  rate: z.number(),
});

export const RateMasterSchema = z.object({
  rate_master_id: z.number(),
  rate_master_name: z.string(),
});

export type RateMasterType = z.infer<typeof RateMasterSchema>;

export const RateMasterWithDetailsSchema = z.object({
  rate_master_id: z.number(),
  rate_master_name: z.string(),
  rate_details: z.array(RateDetailSchema),
});

export const SaveAgeDataSchema = z.object({
  census_detail_id: z.number(),
  relationship: z.string(),
  tobacco_disposition: z.string(),
  issue_age: z.number(),
  birthdate: z.string(),
  save_age_effective_date: z.string(),
  new_effective_date: z.string(),
  save_age_rate: z.number().nullish(),
  new_rate: z.number().nullish(),
  diff: z.number().nullish(),
});

export type SaveAgeDataType = z.infer<typeof SaveAgeDataSchema>;

export const SaveAgeOutputSchema = z.object({
  data: z.array(SaveAgeDataSchema),
  stats: z.object({
    count: z.number(),
    save_age_rate: z.number().nullish(),
    new_rate: z.number().nullish(),
    diff: z.number().nullish(),
  }),
});

export const CensusStatsSchema = z.object({
  tobacco_stats: z.array(
    z.object({
      tobacco_disposition: z.string(),
      count: z.number(),
    })
  ),
  issue_age_stats: z.array(
    z.object({
      issue_age: z.number(),
      count: z.number(),
    })
  ),
  relationship_stats: z.array(
    z.object({
      relationship: z.string(),
      count: z.number(),
    })
  ),
  tenure_stats: z.array(
    z.object({
      tenure: z.number(),
      count: z.number(),
    })
  ),
});

export const ValidEffectiveDateSchema = z.string().date();

export type CensusStatsType = z.infer<typeof CensusStatsSchema>;
