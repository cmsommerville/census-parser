import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { router } from "./router.tsx";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./extensions.ts";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { Toaster } from "@/components/ui/sonner.tsx";
import "./index.css";
import "./assets/ag-grid-theme-builder.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <Toaster />
      <ReactQueryDevtools />
    </QueryClientProvider>
  </StrictMode>
);
