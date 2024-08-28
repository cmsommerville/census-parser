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
import { postNewCensus } from "./queries";
import { CensusMasterType } from "./schemas";
import { useMutation, useQueryClient } from "@tanstack/react-query";

interface UploadCensusModalProps {
  children: React.ReactNode;
  onUploadSuccess?: (data: CensusMasterType) => void;
}

const UploadCensusModal = ({
  children,
  onUploadSuccess,
}: UploadCensusModalProps) => {
  const [open, setOpen] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [censusName, setCensusName] = useState<string>("");

  const queryClient = useQueryClient();

  const postNewCensusMutation = useMutation({
    mutationFn: () => postNewCensus(files, censusName),
    onSuccess: (data) => {
      if (onUploadSuccess) {
        onUploadSuccess(data);
      }
      setFiles([]);
      setCensusName("");
      setOpen(false);
      queryClient.invalidateQueries({
        queryKey: ["census", "list"],
      });
    },
  });

  const uploadHandler = async () => {
    postNewCensusMutation.mutate();
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Upload New Census</DialogTitle>
          <DialogDescription>
            Upload a new census to generate a new save age report.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          {files.length ? (
            <div className="flex flex-col space-y-4">
              <div>
                <Label htmlFor="name" className="">
                  Census Name
                </Label>
                <Input
                  id="name"
                  defaultValue={files[0]?.name ?? ""}
                  placeholder="Enter a name for the census"
                  onChange={(e) => setCensusName(e.target.value)}
                  className=""
                />
              </div>
            </div>
          ) : null}

          <FileUploader onValueChange={setFiles} />
        </div>
        <DialogFooter>
          <div className="flex flex-col space-y-4">
            <Button
              type="button"
              disabled={!files.length || postNewCensusMutation.isPending}
              onClick={uploadHandler}
            >
              {postNewCensusMutation.isPending ? (
                <>
                  <LoadingSpinner className="mr-1" />
                  <span>Uploading...</span>
                </>
              ) : (
                <span>Upload</span>
              )}
            </Button>
            {postNewCensusMutation.isError ? (
              <div className="mt-1 text-red-500 text-xs">
                {postNewCensusMutation.error.name}:
                {postNewCensusMutation.error.message}
              </div>
            ) : null}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
export default UploadCensusModal;
