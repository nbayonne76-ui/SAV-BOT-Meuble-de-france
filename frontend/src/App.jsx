import { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import Dashboard from './components/Dashboard'
import VoiceChatWhisper from './components/VoiceChatWhisper'
import { LayoutDashboard, MessageCircle, Phone } from 'lucide-react'

function App() {
  const [currentView, setCurrentView] = useState('chat') // 'chat', 'voice' ou 'dashboard'

  return (
    <div className="h-screen flex flex-col">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-4 py-3">
            <button
              onClick={() => setCurrentView('chat')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                currentView === 'chat'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <MessageCircle className="w-5 h-5" />
              <span className="font-medium">Bot SAV (Texte)</span>
            </button>

            <button
              onClick={() => setCurrentView('voice')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                currentView === 'voice'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Phone className="w-5 h-5" />
              <span className="font-medium">Mode Vocal (Nouveau !)</span>
            </button>

            <button
              onClick={() => setCurrentView('dashboard')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                currentView === 'dashboard'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <LayoutDashboard className="w-5 h-5" />
              <span className="font-medium">Tableau de Bord</span>
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
