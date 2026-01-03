import { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import Dashboard from './components/Dashboard'
import VoiceChatWhisper from './components/VoiceChatWhisper'
import { LayoutDashboard, MessageCircle, Phone } from 'lucide-react'
import branding from './config/branding'

function App() {
  const [currentView, setCurrentView] = useState('chat') // 'chat', 'voice' ou 'dashboard'

  return (
    <div
      className="h-screen flex flex-col"
      style={{
        backgroundColor: branding.colors.background.primary,
        fontFamily: branding.fonts.primary,
        color: branding.colors.text.primary
      }}
    >
      {/* Navigation */}
      <nav
        className="border-b shadow-sm"
        style={{
          backgroundColor: branding.colors.background.secondary,
          borderColor: branding.colors.background.light
        }}
      >
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-4 py-3">
            <button
              onClick={() => setCurrentView('chat')}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all font-semibold"
              style={{
                backgroundColor: currentView === 'chat'
                  ? branding.colors.accent.primary
                  : branding.colors.background.light,
                color: currentView === 'chat'
                  ? branding.colors.text.primary
                  : branding.colors.text.secondary,
              }}
              onMouseEnter={(e) => {
                if (currentView !== 'chat') {
                  e.currentTarget.style.backgroundColor = branding.colors.background.secondary;
                }
              }}
              onMouseLeave={(e) => {
                if (currentView !== 'chat') {
                  e.currentTarget.style.backgroundColor = branding.colors.background.light;
                }
              }}
            >
              <MessageCircle className="w-5 h-5" />
              <span>Bot Accompagnement (Texte)</span>
            </button>

            <button
              onClick={() => setCurrentView('voice')}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all font-semibold"
              style={{
                backgroundColor: currentView === 'voice'
                  ? branding.colors.accent.primary
                  : branding.colors.background.light,
                color: currentView === 'voice'
                  ? branding.colors.text.primary
                  : branding.colors.text.secondary,
              }}
              onMouseEnter={(e) => {
                if (currentView !== 'voice') {
                  e.currentTarget.style.backgroundColor = branding.colors.background.secondary;
                }
              }}
              onMouseLeave={(e) => {
                if (currentView !== 'voice') {
                  e.currentTarget.style.backgroundColor = branding.colors.background.light;
                }
              }}
            >
              <Phone className="w-5 h-5" />
              <span>Mode Vocal</span>
            </button>

            <button
              onClick={() => setCurrentView('dashboard')}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all font-semibold"
              style={{
                backgroundColor: currentView === 'dashboard'
                  ? branding.colors.accent.primary
                  : branding.colors.background.light,
                color: currentView === 'dashboard'
                  ? branding.colors.text.primary
                  : branding.colors.text.secondary,
              }}
              onMouseEnter={(e) => {
                if (currentView !== 'dashboard') {
                  e.currentTarget.style.backgroundColor = branding.colors.background.secondary;
                }
              }}
              onMouseLeave={(e) => {
                if (currentView !== 'dashboard') {
                  e.currentTarget.style.backgroundColor = branding.colors.background.light;
                }
              }}
            >
              <LayoutDashboard className="w-5 h-5" />
              <span>Tableau de Bord</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Contenu */}
      <div className="flex-1 overflow-hidden">
        {/* Garder les composants montés pour préserver l'état */}
        <div className={currentView === 'chat' ? 'h-full' : 'hidden'}>
          <ChatInterface />
        </div>
        <div className={currentView === 'voice' ? 'h-full' : 'hidden'}>
          <VoiceChatWhisper />
        </div>
        <div className={currentView === 'dashboard' ? 'h-full' : 'hidden'}>
          <Dashboard />
        </div>
      </div>
    </div>
  )
}

export default App
