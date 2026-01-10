import { lazy, Suspense, useCallback, useMemo } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { LayoutDashboard, MessageCircle, Phone } from "lucide-react";
import branding from "./config/branding";
import NavTab from "./components/NavTab";
import { useLanguage } from "./context/LanguageContext";
import LanguageSelector from "./components/LanguageSelector";

const ChatInterface = lazy(() => import("./components/ChatInterface"));
const Dashboard = lazy(() => import("./components/Dashboard"));
const VoiceChatWhisper = lazy(() => import("./components/VoiceChatWhisper"));

const LoadingSpinner = () => (
  <div className="flex items-center justify-center h-full">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
  </div>
);

function App() {
  const { t } = useLanguage();
  const location = useLocation();

  const tabs = useMemo(
    () => [
      { id: "chat", icon: MessageCircle, label: t("nav.chat") },
      { id: "voice", icon: Phone, label: t("nav.voice") },
      { id: "dashboard", icon: LayoutDashboard, label: t("nav.dashboard") },
    ],
    [t]
  );

  const normalized = location.pathname.replace(/\/$/, "") || "/";
  const isActive = (id) => normalized === `/${id}`;

  const containerStyle = useMemo(
    () => ({
      backgroundColor: branding.colors.background.primary,
      fontFamily: branding.fonts.primary,
      color: branding.colors.text.primary,
    }),
    []
  );

  const navStyle = useMemo(
    () => ({
      backgroundColor: branding.colors.background.secondary,
      borderColor: branding.colors.background.light,
    }),
    []
  );

  return (
    <div className="h-screen flex flex-col" style={containerStyle}>
      <nav className="border-b shadow-md" style={navStyle}>
        <div className="w-full px-6 py-4">
          <div className="flex items-center justify-between gap-8">
            <div className="flex items-center gap-2">
              {tabs.map((tab) => (
                <NavTab
                  key={tab.id}
                  icon={tab.icon}
                  label={tab.label}
                  isActive={isActive(tab.id)}
                  to={`/${tab.id}`}
                  colors={branding.colors}
                />
              ))}
            </div>
            <LanguageSelector />
          </div>
        </div>
      </nav>

      <div className="flex-1 overflow-hidden">
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route
              path="/chat"
              element={
                <div className="h-full">
                  <ChatInterface />
                </div>
              }
            />
            <Route
              path="/voice"
              element={
                <div className="h-full">
                  <VoiceChatWhisper />
                </div>
              }
            />
            <Route
              path="/dashboard"
              element={
                <div className="h-full">
                  <Dashboard />
                </div>
              }
            />
            <Route path="*" element={<Navigate to="/chat" replace />} />
          </Routes>
        </Suspense>
      </div>
    </div>
  );
}

export default App;
