import {
  ColDef,
  ValueFormatterParams,
  ValueParserParams,
  ValueSetterParams,
} from "ag-grid-community";
import { parseISO } from "date-fns";

type ColumnType = { [k: string]: ColDef };

const REGEX_PERCENT_W_COMMAS = /^-{0,1}\d{1,3}(,\d{3})*(\.\d+){0,1}%$/;
const REGEX_PERCENT_WO_COMMAS = /^-{0,1}\d*(\.\d+){0,1}%$/;
const REGEX_PERCENT_NO_INTEGRAL_PART = /^-{0,1}\.\d+%$/;
const REGEX_NUMBER_W_COMMAS_OPTIONAL_DOLLAR_SIGN =
  /^-{0,1}\${0,1}\d{1,3}(,\d{3})*(\.\d+){0,1}$/;
const REGEX_NUMBER_WO_COMMAS_OPTIONAL_DOLLAR_SIGN =
  /^-{0,1}\${0,1}\d*(\.\d+){0,1}$/;

const numericValueFormatter =
  (decimals: number, style?: string) => (params: ValueFormatterParams) => {
    if (params.value == null) return params.value;
    if (isNaN(Number(params.value))) return params.value;
    return Number(params.value).toLocaleString("en-US", {
      ...(style ? { style } : {}),
      currency: "USD",
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  };

const currencyValueParser = (params: ValueParserParams) => {
  let val = String(params.newValue);
  if (REGEX_NUMBER_W_COMMAS_OPTIONAL_DOLLAR_SIGN.test(val)) {
    val = val.replaceAll(",", "").replaceAll("$", "");
    return Number(val);
  } else if (REGEX_NUMBER_WO_COMMAS_OPTIONAL_DOLLAR_SIGN.test(val)) {
    val = val.replaceAll("$", "");
    return Number(val);
  }
  return Number(val);
};

const percentValueParser = (params: ValueParserParams) => {
  let val = String(params.newValue);
  if (REGEX_PERCENT_W_COMMAS.test(val)) {
    val = val.replaceAll(",", "").replaceAll("%", "");
    return Number(val) / 100;
  } else if (REGEX_PERCENT_WO_COMMAS.test(val)) {
    val = val.replaceAll("%", "");
    return Number(val) / 100;
  } else if (REGEX_PERCENT_NO_INTEGRAL_PART.test(val)) {
    val = val.replaceAll("%", "");
    return Number(val) / 100;
  }
  return Number(val);
};

const numericValueSetter = (params: ValueSetterParams) => {
  if (isNaN(params.newValue)) return false;
  const col = params.column.getColId();
  params.data[col] = params.newValue;
  return true;
};

export const COLUMN_TYPES: ColumnType = {
  number0: {
    cellClass: "text-right",
    valueFormatter: numericValueFormatter(0),
    valueParser: currencyValueParser,
    valueSetter: numericValueSetter,
  },
  number2: {
    cellClass: "text-right",
    valueFormatter: numericValueFormatter(2),
    valueParser: currencyValueParser,
    valueSetter: numericValueSetter,
  },
  number3: {
    cellClass: "text-right",
    valueFormatter: numericValueFormatter(3),
    valueParser: currencyValueParser,
    valueSetter: numericValueSetter,
  },
  date: {
    cellClass: "text-right",
    valueFormatter: (params: ValueFormatterParams) => {
      if (params.value == null) return params.value;
      return parseISO(params.value).toLocaleDateString("en-US");
    },
  },
  dollars: {
    cellClass: "text-right",
    valueFormatter: numericValueFormatter(0, "currency"),
    valueParser: currencyValueParser,
    valueSetter: numericValueSetter,
  },
  dollarsandcents: {
    cellClass: "text-right",
    valueFormatter: numericValueFormatter(2, "currency"),
    valueParser: currencyValueParser,
    valueSetter: numericValueSetter,
  },
  percent1: {
    cellClass: "text-right",
    valueFormatter: numericValueFormatter(1, "percent"),
    valueParser: percentValueParser,
    valueSetter: numericValueSetter,
  },
  percent2: {
    cellClass: "text-right",
    valueFormatter: numericValueFormatter(2, "percent"),
    valueParser: percentValueParser,
    valueSetter: numericValueSetter,
  },
  percent3: {
    cellClass: "text-right",
    valueFormatter: numericValueFormatter(3, "percent"),
    valueParser: percentValueParser,
    valueSetter: numericValueSetter,
  },
};
