import { NavLink, useNavigate } from "react-router-dom";
import { Activity, LogOut } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import { Button } from "@/components/ui/button";

const MainNavbar = () => {
  const { user, clearAuth } = useAppStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      const { signOut } = await import("@/services/api");
      await signOut();
    } catch (e) {
      console.error("Logout error:", e);
    } finally {
      clearAuth();
      navigate("/");
    }
  };

  const linkBase =
    "px-3 py-2 text-sm font-medium border-b-2 border-transparent hover:border-primary hover:text-primary transition-colors";
  const activeClasses = "border-primary text-primary";

  return (
    <header className="bg-background border-b shadow-sm">
      <div className="container flex items-center justify-between h-14">
        <div className="flex items-center space-x-2">
          <Activity className="h-7 w-7 text-primary" />
          <span className="text-xl font-bold text-foreground">MedsAI</span>
        </div>

        <nav className="hidden md:flex items-center space-x-2">
          <NavLink
            to="/home"
            className={({ isActive }) =>
              `${linkBase} ${isActive ? activeClasses : "text-muted-foreground"}`
            }
          >
            Home
          </NavLink>
          <NavLink
            to="/consult-doctor"
            className={({ isActive }) =>
              `${linkBase} ${isActive ? activeClasses : "text-muted-foreground"}`
            }
          >
            Consult Doctor
          </NavLink>
          <NavLink
            to="/vaccines-schemes"
            className={({ isActive }) =>
              `${linkBase} ${isActive ? activeClasses : "text-muted-foreground"}`
            }
          >
            Vaccines &amp; Schemes
          </NavLink>
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `${linkBase} ${isActive ? activeClasses : "text-muted-foreground"}`
            }
          >
            AI Diagnosis
          </NavLink>
        </nav>

        <div className="flex items-center space-x-3">
          {user && (
            <span className="hidden sm:inline text-sm text-muted-foreground">
              Welcome, {user.name}
            </span>
          )}
          <Button variant="outline" size="sm" onClick={handleLogout}>
            <LogOut className="w-4 h-4 mr-1" />
            Logout
          </Button>
        </div>
      </div>
    </header>
  );
};

export default MainNavbar;
