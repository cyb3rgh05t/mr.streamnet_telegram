import { Navigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import LoadingSpinner from "./LoadingSpinner";

export default function ProtectedRoute({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, authEnabled, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner message="Loading..." />;
  }

  if (authEnabled && !user) {
    return <Navigate to="/login" />;
  }

  return <>{children}</>;
}
