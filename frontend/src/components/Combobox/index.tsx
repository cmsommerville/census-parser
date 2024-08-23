import { useState, useEffect } from "react";

import { ChevronsUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { UseQueryOptions, useQuery } from "@tanstack/react-query";
import { Label } from "@/components/ui/label";

interface ComboboxTypeaheadProps {
  label?: string;
  defaultValue?: DropdownListItem;
  onSelect: (val: DropdownListItem) => void;
  placeholder?: string;
  queryOptions: (
    val: string | undefined
  ) => UseQueryOptions<DropdownListItem[], any, DropdownListItem[], string[]>;
  searchPlaceholder?: string;
}

type DropdownListItem = {
  id: number;
  name: string;
};

export default function ComboboxTypeahead({
  label,
  defaultValue,
  onSelect,
  placeholder = "Select an item...",
  searchPlaceholder = "Begin typing to search...",
  queryOptions,
}: ComboboxTypeaheadProps) {
  const [open, setOpen] = useState(false);
  const [commandInput, setCommandInput] = useState<string>("");
  const [debouncedInput, setDebouncedInput] = useState<string>("");
  const [selection, setSelection] = useState<DropdownListItem | undefined>(
    undefined
  );
  const query = useQuery(queryOptions(debouncedInput));

  const handleSelection = (selection: DropdownListItem) => {
    setSelection(selection);
    onSelect(selection);
    setOpen(false);
  };

  useEffect(() => {
    const timeout = setTimeout(() => {
      setDebouncedInput(commandInput);
    }, 100);
    return () => clearTimeout(timeout);
  }, [commandInput]);

  return (
    <div>
      {label ? <Label>{label}</Label> : null}
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between font-normal px-3"
          >
            {selection
              ? selection.name
              : defaultValue
              ? defaultValue.name
              : placeholder}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="p-0">
          <Command
            className="rounded-lg border shadow-md font-normal"
            shouldFilter={false}
          >
            <CommandInput
              placeholder={searchPlaceholder}
              value={commandInput}
              onValueChange={setCommandInput}
            />
            <CommandList>
              <CommandEmpty>
                {commandInput === ""
                  ? "Start typing to load results"
                  : "No results found."}
              </CommandEmpty>
              <CommandGroup className="">
                {query.data
                  ? query.data.map((result) => (
                      <CommandItem
                        className="!bg-inherit hover:!bg-slate-100 cursor-pointer"
                        key={result.id}
                        value={result.name}
                        onSelect={() => handleSelection(result)}
                      >
                        {result.name}
                      </CommandItem>
                    ))
                  : []}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}
