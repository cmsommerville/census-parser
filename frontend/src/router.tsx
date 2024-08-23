import { createBrowserRouter } from "react-router-dom";
import MainLayout from "./layout";
import App from "./App";
import SaveAgeLanding from "./pages/SaveAge/SaveAgeLanding";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { path: "/", element: <App /> },
      { path: "/save-age", element: <SaveAgeLanding /> },
    ],
  },
]);
