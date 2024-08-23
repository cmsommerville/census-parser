import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { LoadingSpinner } from "@/components/ui/spinner";
import { FileUploader } from "@/components/FileUploader";
import { postNewRates } from "./queries";
import { RateMasterType } from "./schemas";
import { useMutation, useQueryClient } from "@tanstack/react-query";

interface UploadRatesModalProps {
  children: React.ReactNode;
  onUploadSuccess?: (data: RateMasterType) => void;
}

const UploadRatesModal = ({
  children,
  onUploadSuccess,
}: UploadRatesModalProps) => {
  const [open, setOpen] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [rateMasterName, setRateMasterName] = useState<string>("");

  const queryClient = useQueryClient();
  const postNewRatesMutation = useMutation({
    mutationFn: () => postNewRates(files, rateMasterName),
    onSuccess: (data) => {
      if (onUploadSuccess) {
        onUploadSuccess(data);
      }
      setFiles([]);
      setRateMasterName("");
      setOpen(false);
      queryClient.invalidateQueries({
        queryKey: ["census", "list"],
      });
    },
  });

  const uploadHandler = async () => {
    postNewRatesMutation.mutate();
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Upload Rates</DialogTitle>
          <DialogDescription>
            Upload rates to generate a new save age report.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          {files.length ? (
            <div>
              <Label htmlFor="name" className="">
                Name
              </Label>
              <Input
                id="name"
                defaultValue={files[0]?.name ?? ""}
                placeholder="Enter a friendly name for the rates"
                onChange={(e) => setRateMasterName(e.target.value)}
                className=""
              />
            </div>
          ) : null}

          <FileUploader onValueChange={setFiles} />
        </div>
        <DialogFooter>
          <div className="flex flex-col space-y-4">
            <Button
              type="button"
              disabled={!files.length || postNewRatesMutation.isPending}
              onClick={uploadHandler}
            >
              {postNewRatesMutation.isPending ? (
                <>
                  <LoadingSpinner className="mr-1" />
                  <span>Uploading...</span>
                </>
              ) : (
                <span>Upload</span>
              )}
            </Button>
            {postNewRatesMutation.isError ? (
              <div className="mt-1 text-red-500 text-xs">
                {postNewRatesMutation.error.name}:
                {postNewRatesMutation.error.message}
              </div>
            ) : null}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
export default UploadRatesModal;
