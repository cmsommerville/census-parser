import resolveConfig from "tailwindcss/resolveConfig";
import tailwindConfig from "../../tailwind.config";

const tw = resolveConfig(tailwindConfig);

export const useTailwindConfig = () => {
  return tw;
};
