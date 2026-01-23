import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { CacheProvider } from "./contexts/CacheContext";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Settings from "./pages/Settings";
import Media from "./pages/Media";
import Groups from "./pages/Groups";
import About from "./pages/About";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <CacheProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="settings" element={<Settings />} />
              <Route path="media" element={<Media />} />
              <Route path="groups" element={<Groups />} />
              <Route path="about" element={<About />} />
            </Route>
          </Routes>
        </CacheProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
