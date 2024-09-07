import { createBrowserRouter } from "react-router-dom";
import MainLayout from "./layout";
import App from "./App";
import SaveAgeLanding from "./pages/SaveAge/SaveAgeLanding";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    handle: {
      breadcrumb: () => "Home",
    },
    children: [
      { path: "/", element: <App /> },
      {
        path: "/save-age",
        element: <SaveAgeLanding />,
        handle: {
          breadcrumb: () => {
            return "Save Age Report";
          },
        },
      },
    ],
  },
]);
