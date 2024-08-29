import { format, parseISO } from "date-fns";
import { Calendar as CalendarIcon } from "lucide-react";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

import { cn } from "@/lib/utils";
import { useState } from "react";

interface DatePickerProps {
  children?: React.ReactNode;
  dateFormat?: string;
  defaultValue?: string | null | undefined;
  onSelect: (date: string) => void;
}

export const Datepicker = ({
  children,
  dateFormat = "yyyy-MM-dd",
  defaultValue,
  onSelect,
}: DatePickerProps) => {
  const [date, setDate] = useState<Date | null>(null);

  const selectHandler = (dt: Date | undefined) => {
    if (!dt) return;
    setDate(dt);
    onSelect(format(dt.toISOString(), "yyyy-MM-dd"));
  };

  const x = defaultValue != null ? parseISO(defaultValue) : null;

  const displayDate = date ? date : x;

  return (
    <>
      <Label>{children}</Label>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            variant={"outline"}
            className={cn(
              "w-full justify-start text-left font-normal",
              !displayDate && "text-muted-foreground"
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {displayDate ? (
              format(displayDate, "yyyy-MM-dd")
            ) : (
              <span>Pick a date</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0">
          <Calendar
            mode="single"
            selected={displayDate ?? new Date()}
            onSelect={selectHandler}
            initialFocus
            fixedWeeks
          />
        </PopoverContent>
      </Popover>
    </>
  );
};
