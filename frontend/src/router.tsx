import { createBrowserRouter } from "react-router-dom";
import MainLayout from "./layout";
import App from "./App";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [{ path: "/", element: <App /> }],
  },
]);
