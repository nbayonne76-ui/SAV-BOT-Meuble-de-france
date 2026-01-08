// // import { useState } from "react";
// // import ChatInterface from "./components/ChatInterface";
// // import Dashboard from "./components/Dashboard";
// // import VoiceChatWhisper from "./components/VoiceChatWhisper";
// // import { LayoutDashboard, MessageCircle, Phone } from "lucide-react";
// // import branding from "./config/branding";

// // function App() {
// //   const [currentView, setCurrentView] = useState("chat"); // 'chat', 'voice' ou 'dashboard'

// //   return (
// //     <div
// //       className="h-screen flex flex-col"
// //       style={{
// //         backgroundColor: branding.colors.background.primary,
// //         fontFamily: branding.fonts.primary,
// //         color: branding.colors.text.primary,
// //       }}
// //     >
// //       {/* Navigation */}
// //       <nav
// //         className="border-b shadow-sm"
// //         style={{
// //           backgroundColor: branding.colors.background.secondary,
// //           borderColor: branding.colors.background.light,
// //         }}
// //       >
// //         <div className="max-w-7xl mx-auto px-4">
// //           <div className="flex space-x-4 py-3">
// //             <button
// //               onClick={() => setCurrentView("chat")}
// //               className="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all font-semibold"
// //               style={{
// //                 backgroundColor:
// //                   currentView === "chat"
// //                     ? branding.colors.accent.primary
// //                     : branding.colors.background.light,
// //                 color:
// //                   currentView === "chat"
// //                     ? branding.colors.text.primary
// //                     : branding.colors.text.secondary,
// //               }}
// //               onMouseEnter={(e) => {
// //                 if (currentView !== "chat") {
// //                   e.currentTarget.style.backgroundColor =
// //                     branding.colors.background.secondary;
// //                 }
// //               }}
// //               onMouseLeave={(e) => {
// //                 if (currentView !== "chat") {
// //                   e.currentTarget.style.backgroundColor =
// //                     branding.colors.background.light;
// //                 }
// //               }}
// //             >
// //               <MessageCircle className="w-5 h-5" />
// //               <span>Bot Accompagnement (Texte)</span>
// //             </button>

// //             <button
// //               onClick={() => setCurrentView("voice")}
// //               className="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all font-semibold"
// //               style={{
// //                 backgroundColor:
// //                   currentView === "voice"
// //                     ? branding.colors.accent.primary
// //                     : branding.colors.background.light,
// //                 color:
// //                   currentView === "voice"
// //                     ? branding.colors.text.primary
// //                     : branding.colors.text.secondary,
// //               }}
// //               onMouseEnter={(e) => {
// //                 if (currentView !== "voice") {
// //                   e.currentTarget.style.backgroundColor =
// //                     branding.colors.background.secondary;
// //                 }
// //               }}
// //               onMouseLeave={(e) => {
// //                 if (currentView !== "voice") {
// //                   e.currentTarget.style.backgroundColor =
// //                     branding.colors.background.light;
// //                 }
// //               }}
// //             >
// //               <Phone className="w-5 h-5" />
// //               <span>Mode Vocal</span>
// //             </button>

// //             <button
// //               onClick={() => setCurrentView("dashboard")}
// //               className="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all font-semibold"
// //               style={{
// //                 backgroundColor:
// //                   currentView === "dashboard"
// //                     ? branding.colors.accent.primary
// //                     : branding.colors.background.light,
// //                 color:
// //                   currentView === "dashboard"
// //                     ? branding.colors.text.primary
// //                     : branding.colors.text.secondary,
// //               }}
// //               onMouseEnter={(e) => {
// //                 if (currentView !== "dashboard") {
// //                   e.currentTarget.style.backgroundColor =
// //                     branding.colors.background.secondary;
// //                 }
// //               }}
// //               onMouseLeave={(e) => {
// //                 if (currentView !== "dashboard") {
// //                   e.currentTarget.style.backgroundColor =
// //                     branding.colors.background.light;
// //                 }
// //               }}
// //             >
// //               <LayoutDashboard className="w-5 h-5" />
// //               <span>Tableau de Bord</span>
// //             </button>
// //           </div>
// //         </div>
// //       </nav>

// //       {/* Contenu - render only the active view (unmount inactive components) */}
// //       <div className="flex-1 overflow-hidden">
// //         {currentView === "chat" && (
// //           <div className="h-full">
// //             <ChatInterface />
// //           </div>
// //         )}

// //         {currentView === "voice" && (
// //           <div className="h-full">
// //             <VoiceChatWhisper />
// //           </div>
// //         )}

// //         {currentView === "dashboard" && (
// //           <div className="h-full">
// //             <Dashboard />
// //           </div>
// //         )}
// //       </div>
// //     </div>
// //   );
// // }

// // export default App;

// import { useState } from "react";
// import ChatInterface from "./components/ChatInterface";
// import Dashboard from "./components/Dashboard";
// import VoiceChatWhisper from "./components/VoiceChatWhisper";
// import { LayoutDashboard, MessageCircle, Phone } from "lucide-react";
// import branding from "./config/branding";

// function App() {
//   const [currentView, setCurrentView] = useState("chat"); // 'chat', 'voice' ou 'dashboard'

//   return (
//     <div
//       className="h-screen flex flex-col"
//       style={{
//         backgroundColor: branding.colors.background.primary,
//         fontFamily: branding.fonts.primary,
//         color: branding.colors.text.primary,
//       }}
//     >
//       {/* Navigation */}
//       <nav
//         className="border-b shadow-sm"
//         style={{
//           backgroundColor: branding.colors.background.secondary,
//           borderColor: branding.colors.background.light,
//         }}
//       >
//         <div className="max-w-7xl mx-auto px-4">
//           <div className="flex space-x-4 py-3">
//             <button
//               onClick={() => setCurrentView("chat")}
//               className="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all font-semibold"
//               style={{
//                 backgroundColor:
//                   currentView === "chat"
//                     ? branding.colors.accent.primary
//                     : branding.colors.background.light,
//                 color:
//                   currentView === "chat"
//                     ? branding.colors.text.primary
//                     : branding.colors.text.secondary,
//               }}
//               onMouseEnter={(e) => {
//                 if (currentView !== "chat") {
//                   e.currentTarget.style.backgroundColor =
//                     branding.colors.background.secondary;
//                 }
//               }}
//               onMouseLeave={(e) => {
//                 if (currentView !== "chat") {
//                   e.currentTarget.style.backgroundColor =
//                     branding.colors.background.light;
//                 }
//               }}
//             >
//               <MessageCircle className="w-5 h-5" />
//               <span>Bot Accompagnement (Texte)</span>
//             </button>

//             <button
//               onClick={() => setCurrentView("voice")}
//               className="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all font-semibold"
//               style={{
//                 backgroundColor:
//                   currentView === "voice"
//                     ? branding.colors.accent.primary
//                     : branding.colors.background.light,
//                 color:
//                   currentView === "voice"
//                     ? branding.colors.text.primary
//                     : branding.colors.text.secondary,
//               }}
//               onMouseEnter={(e) => {
//                 if (currentView !== "voice") {
//                   e.currentTarget.style.backgroundColor =
//                     branding.colors.background.secondary;
//                 }
//               }}
//               onMouseLeave={(e) => {
//                 if (currentView !== "voice") {
//                   e.currentTarget.style.backgroundColor =
//                     branding.colors.background.light;
//                 }
//               }}
//             >
//               <Phone className="w-5 h-5" />
//               <span>Mode Vocal</span>
//             </button>

//             <button
//               onClick={() => setCurrentView("dashboard")}
//               className="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all font-semibold"
//               style={{
//                 backgroundColor:
//                   currentView === "dashboard"
//                     ? branding.colors.accent.primary
//                     : branding.colors.background.light,
//                 color:
//                   currentView === "dashboard"
//                     ? branding.colors.text.primary
//                     : branding.colors.text.secondary,
//               }}
//               onMouseEnter={(e) => {
//                 if (currentView !== "dashboard") {
//                   e.currentTarget.style.backgroundColor =
//                     branding.colors.background.secondary;
//                 }
//               }}
//               onMouseLeave={(e) => {
//                 if (currentView !== "dashboard") {
//                   e.currentTarget.style.backgroundColor =
//                     branding.colors.background.light;
//                 }
//               }}
//             >
//               <LayoutDashboard className="w-5 h-5" />
//               <span>Tableau de Bord</span>
//             </button>
//           </div>
//         </div>
//       </nav>

//       {/* Contenu - render only the active view (unmount inactive components) */}
//       <div className="flex-1 overflow-hidden">
//         {currentView === "chat" && (
//           <div className="h-full">
//             <ChatInterface />
//           </div>
//         )}

//         {currentView === "voice" && (
//           <div className="h-full">
//             <VoiceChatWhisper />
//           </div>
//         )}

//         {currentView === "dashboard" && (
//           <div className="h-full">
//             <Dashboard />
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }

// export default App;

import { useState, lazy, Suspense, useCallback, useMemo } from "react";
import { LayoutDashboard, MessageCircle, Phone } from "lucide-react";
import branding from "./config/branding";
import NavTab from "./components/NavTab";

const ChatInterface = lazy(() => import("./components/ChatInterface"));
const Dashboard = lazy(() => import("./components/Dashboard"));
const VoiceChatWhisper = lazy(() => import("./components/VoiceChatWhisper"));

const LoadingSpinner = () => (
  <div className="flex items-center justify-center h-full">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
  </div>
);

function App() {
  const [currentView, setCurrentView] = useState("chat");

  const handleViewChange = useCallback((view) => {
    setCurrentView(view);
  }, []);

  const tabs = useMemo(
    () => [
      { id: "chat", icon: MessageCircle, label: "Bot Accompagnement (Texte)" },
      { id: "voice", icon: Phone, label: "Mode Vocal" },
      { id: "dashboard", icon: LayoutDashboard, label: "Tableau de Bord" },
    ],
    []
  );

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
      <nav className="border-b shadow-sm" style={navStyle}>
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-4 py-3">
            {tabs.map((tab) => (
              <NavTab
                key={tab.id}
                icon={tab.icon}
                label={tab.label}
                isActive={currentView === tab.id}
                onClick={() => handleViewChange(tab.id)}
                colors={branding.colors}
              />
            ))}
          </div>
        </div>
      </nav>

      <div className="flex-1 overflow-hidden">
        <Suspense fallback={<LoadingSpinner />}>
          {currentView === "chat" && (
            <div className="h-full">
              <ChatInterface />
            </div>
          )}
          {currentView === "voice" && (
            <div className="h-full">
              <VoiceChatWhisper />
            </div>
          )}
          {currentView === "dashboard" && (
            <div className="h-full">
              <Dashboard />
            </div>
          )}
        </Suspense>
      </div>
    </div>
  );
}

export default App;
