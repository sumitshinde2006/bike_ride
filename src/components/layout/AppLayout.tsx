import { useState } from "react";
import { Menu, X, LogOut } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { NavLink } from "@/components/NavLink";

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-20"
        } bg-card border-r border-border transition-all duration-300 flex flex-col shadow-sm`}
      >
        {/* Logo/Brand */}
        <div className="h-16 flex items-center justify-center border-b border-border px-4">
          <div className={`font-bold text-xl text-primary ${!sidebarOpen && "hidden"}`}>
            RideWise
          </div>
          {!sidebarOpen && <div className="text-lg font-bold text-primary">RW</div>}
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-2">
          <NavLink
            to="/dashboard"
            icon="LayoutDashboard"
            label="Dashboard"
            collapsed={!sidebarOpen}
          />
          <NavLink
            to="/prediction"
            icon="TrendingUp"
            label="Predictions"
            collapsed={!sidebarOpen}
          />
          <NavLink
            to="/chatbot"
            icon="MessageSquare"
            label="Chatbot"
            collapsed={!sidebarOpen}
          />
          <NavLink
            to="/reservation"
            icon="Calendar"
            label="Reservation"
            collapsed={!sidebarOpen}
          />
          <NavLink
            to="/profile"
            icon="User"
            label="Profile"
            collapsed={!sidebarOpen}
          />
        </nav>

        {/* Toggle Button */}
        <div className="border-t border-border p-4 flex justify-center">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-muted-foreground"
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="h-16 border-b border-border bg-card flex items-center justify-between px-6 shadow-sm">
          <h2 className="text-lg font-semibold text-foreground">RideWise Analytics</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="text-muted-foreground hover:text-foreground"
          >
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto bg-background">
          <div className="p-6 max-w-7xl mx-auto w-full">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
