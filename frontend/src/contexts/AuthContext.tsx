import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import api from "@/lib/api";

interface User {
  username: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  authEnabled: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [authEnabled, setAuthEnabled] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      // Check if auth is enabled
      const enabledResponse = await api.get("/auth/enabled");
      const enabled = enabledResponse.data.enabled;
      setAuthEnabled(enabled);

      if (!enabled) {
        setUser({ username: "admin" });
        setLoading(false);
        return;
      }

      // Check if we have a valid token
      const token = localStorage.getItem("token");
      if (token) {
        const response = await api.get("/auth/me");
        setUser(response.data);
      }
    } catch (error) {
      console.error("Auth check failed:", error);
      localStorage.removeItem("token");
    } finally {
      setLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    const response = await api.post("/auth/login", { username, password });
    const { access_token, username: user_name } = response.data;
    localStorage.setItem("token", access_token);
    setUser({ username: user_name });
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, authEnabled, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
