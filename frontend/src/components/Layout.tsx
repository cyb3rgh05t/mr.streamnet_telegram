import { Outlet, Link, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faThLarge,
  faCog,
  faFilm,
  faUsers,
  faSignOutAlt,
  faBars,
  faPaperPlane,
  faClock,
  faUser,
  faInfoCircle,
} from "@fortawesome/free-solid-svg-icons";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import api from "@/lib/api";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: faThLarge },
  { name: "Media", href: "/media", icon: faFilm },
  { name: "Groups", href: "/groups", icon: faUsers },
  { name: "Settings", href: "/settings", icon: faCog },
  { name: "About", href: "/about", icon: faInfoCircle },
];

export default function Layout() {
  const { user, logout, authEnabled } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [botStatus, setBotStatus] = useState({ online: false });

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchBotStatus = async () => {
      try {
        const response = await api.get("/dashboard/bot-status");
        if (response.data) {
          setBotStatus(response.data);
        }
      } catch (error) {
        console.error("Failed to fetch bot status:", error);
      }
    };

    fetchBotStatus();
    const interval = setInterval(fetchBotStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen">
      {/* Top Navbar */}
      <nav className="navbar">
        <div className="navbar-container">
          <div className="flex items-center gap-6">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 text-text hover:bg-white/10 rounded transition-colors"
            >
              <FontAwesomeIcon icon={faBars} className="w-5 h-5" />
            </button>
            <Link to="/dashboard" className="navbar-brand">
              <FontAwesomeIcon
                icon={faPaperPlane}
                className="w-6 h-6 text-telegram-blue"
              />
              <span>Telegram Bot Manager</span>
            </Link>
            <div className="bot-status-indicator">
              <span
                className={cn(
                  "status-dot",
                  botStatus.online ? "online" : "offline",
                )}
              ></span>
              <span className="text-sm text-text-muted">
                {botStatus.online ? "Online" : "Offline"}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-text-muted text-sm">
              <FontAwesomeIcon icon={faClock} className="w-4 h-4" />
              <span>{currentTime.toLocaleTimeString()}</span>
            </div>

            {authEnabled && user && (
              <div className="flex items-center gap-3 px-3 py-2 rounded hover:bg-white/10 transition-colors">
                <FontAwesomeIcon
                  icon={faUser}
                  className="w-4 h-4 text-text-muted"
                />
                <span className="text-sm text-text">{user.username}</span>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "sidebar",
          sidebarOpen ? "translate-x-0" : "-translate-x-full",
          "lg:translate-x-0",
        )}
      >
        <div className="sidebar-content">
          <nav className="sidebar-nav">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn("nav-item", isActive && "active")}
                  onClick={() => setSidebarOpen(false)}
                >
                  <FontAwesomeIcon icon={item.icon} className="w-5 h-5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {authEnabled && (
            <div className="sidebar-footer">
              <button onClick={logout} className="sidebar-logout">
                <FontAwesomeIcon icon={faSignOutAlt} className="w-5 h-5" />
                <span>Logout</span>
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
