import Header from "./components/Header";
import Sidenav from "./components/Sidenav";
import { Outlet } from "react-router-dom";

const MainLayout = () => {
  return (
    <main className="h-screen bg-muted/40 grid grid-cols-main-layout">
      <div>
        <Sidenav />
      </div>
      <div>
        <Header />
        <div className="h-full bg-green-100 p-4 bg-slate-50 text-slate-700 text-sm">
          <Outlet />
        </div>
      </div>
    </main>
  );
};

export default MainLayout;
