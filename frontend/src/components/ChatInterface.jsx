// frontend/src/components/ChatInterface.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Send, Camera, X, Loader2, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [sessionId] = useState(`session-${Date.now()}`);
  const [isRecording, setIsRecording] = useState(false);
  const [isVoiceSupported, setIsVoiceSupported] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSpeechEnabled, setIsSpeechEnabled] = useState(true); // Activer voix par défaut
  const [isSpeaking, setIsSpeaking] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);
  const isRecognitionActive = useRef(false);
  const speechSynthesisRef = useRef(null);

  // Message d'accueil
  useEffect(() => {
    const welcomeMessage = `Bonjour et bienvenue au service clientèle du groupe Mobilier de France.
Nous sommes à votre écoute pour un accompagnement personnalisé.

Pour vous aider rapidement, donnez-moi :
• Votre nom
• Votre numéro de commande
• Une description de votre problème

Vous pouvez écrire ou utiliser le microphone 🎤`;

    setMessages([{
      role: 'assistant',
      content: welcomeMessage,
      timestamp: new Date()
    }]);

    // 🔊 Parler le message d'accueil après 1 seconde
    setTimeout(() => {
      if (isSpeechEnabled) {
        const shortWelcome = "Bonjour et bienvenue au service clientèle du groupe Mobilier de France. Nous sommes à votre écoute pour un accompagnement personnalisé. Pour vous aider rapidement, donnez-moi votre nom, votre numéro de commande, et une description de votre problème.";
        speakText(shortWelcome);
      }
    }, 1000);
  }, []);

  // Auto-scroll vers le bas
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 🎤 Initialiser Web Speech API - VERSION AMÉLIORÉE
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn('⚠️ Web Speech API non supportée');
      setIsVoiceSupported(false);
      return;
    }

    setIsVoiceSupported(true);
    const recognition = new SpeechRecognition();

    // Configuration optimisée
    recognition.lang = 'fr-FR';
    recognition.continuous = true; // Continuer à écouter
    recognition.interimResults = true; // Afficher résultats en temps réel
    recognition.maxAlternatives = 1;

    // 🎯 Gérer les résultats (interim + final)
    recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPiece = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcriptPiece + ' ';
        } else {
          interimTranscript += transcriptPiece;
        }
      }

      // Afficher résultats en temps réel
      if (interimTranscript) {
        setTranscript(interimTranscript);
      }

      // Ajouter résultat final au champ de saisie
      if (finalTranscript) {
        setInputMessage(prev => {
          const current = prev.trim();
          const newText = finalTranscript.trim();
          return current ? `${current} ${newText}` : newText;
        });
        setTranscript('');
      }
    };

    // 🎯 Gérer les erreurs
    recognition.onerror = (event) => {
      console.error('❌ Erreur reconnaissance:', event.error);

      // Ne pas afficher d'alerte pour "no-speech" ou "aborted"
      if (event.error === 'no-speech' || event.error === 'aborted') {
        console.log('🔇 Pas de parole détectée ou arrêt manuel');
      } else if (event.error === 'not-allowed') {
        alert('🚫 Accès au microphone refusé.\n\nVeuillez autoriser l\'accès dans les paramètres de votre navigateur.');
      } else if (event.error === 'network') {
        alert('🌐 Erreur réseau. Vérifiez votre connexion internet.');
      } else {
        console.error('Erreur inconnue:', event.error);
      }

      isRecognitionActive.current = false;
      setIsRecording(false);
      setTranscript('');
    };

    // 🎯 Redémarrer automatiquement si arrêt inattendu
    recognition.onend = () => {
      console.log('🎤 Reconnaissance terminée');

      // Si on devrait toujours enregistrer, redémarrer
      if (isRecognitionActive.current && isRecording) {
        try {
          recognition.start();
          console.log('🔄 Redémarrage automatique...');
        } catch (error) {
          console.error('❌ Impossible de redémarrer:', error);
          isRecognitionActive.current = false;
          setIsRecording(false);
        }
      } else {
        isRecognitionActive.current = false;
        setIsRecording(false);
        setTranscript('');
      }
    };

    // 🎯 Événement de démarrage
    recognition.onstart = () => {
      console.log('✅ Reconnaissance démarrée');
      isRecognitionActive.current = true;
      setIsRecording(true);
    };

    recognitionRef.current = recognition;

    // Cleanup au démontage
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (error) {
          console.log('Cleanup error:', error);
        }
      }
    };
  }, []);

  // 🔊 Initialiser Text-to-Speech (Synthèse vocale)
  useEffect(() => {
    if ('speechSynthesis' in window) {
      speechSynthesisRef.current = window.speechSynthesis;
      console.log('✅ Synthèse vocale disponible');
    } else {
      console.warn('⚠️ Synthèse vocale non supportée');
    }

    // Cleanup: arrêter la voix au démontage
    return () => {
      if (speechSynthesisRef.current) {
        speechSynthesisRef.current.cancel();
      }
    };
  }, []);

  // 🔊 Fonction pour faire parler le bot
  const speakText = (text) => {
    if (!speechSynthesisRef.current || !isSpeechEnabled) return;

    // Arrêter toute parole en cours
    speechSynthesisRef.current.cancel();

    // Nettoyer le texte (enlever markdown, emojis complexes, etc.)
    const cleanText = text
      .replace(/[#*_`]/g, '') // Enlever markdown
      .replace(/\*\*/g, '') // Enlever gras
      .replace(/\n\n/g, '. ') // Remplacer doubles sauts par point
      .replace(/\n/g, ' ') // Remplacer sauts simples par espace
      .replace(/[🎯📋⚡🔒🛡️🎤]/g, '') // Enlever certains emojis
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);

    // Configuration voix française
    utterance.lang = 'fr-FR';
    utterance.rate = 1.1; // Vitesse (0.5 à 2)
    utterance.pitch = 1.0; // Tonalité (0 à 2)
    utterance.volume = 1.0; // Volume (0 à 1)

    // Chercher une voix française
    const voices = speechSynthesisRef.current.getVoices();
    const frenchVoice = voices.find(voice => voice.lang.startsWith('fr'));
    if (frenchVoice) {
      utterance.voice = frenchVoice;
    }

    // Événements
    utterance.onstart = () => {
      setIsSpeaking(true);
      console.log('🔊 Le bot parle...');
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      console.log('🔇 Le bot a fini de parler');
    };

    utterance.onerror = (error) => {
      // L'erreur "interrupted" est normale quand on annule pour démarrer une nouvelle synthèse
      if (error.error !== 'interrupted') {
        console.error('❌ Erreur synthèse vocale:', error);
      }
      setIsSpeaking(false);
    };

    // Parler
    speechSynthesisRef.current.speak(utterance);
  };

  // 🔊 Arrêter la parole
  const stopSpeaking = () => {
    if (speechSynthesisRef.current) {
      speechSynthesisRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  // 🔊 Toggle activation voix
  const toggleSpeech = () => {
    if (isSpeaking) {
      stopSpeaking();
    }
    setIsSpeechEnabled(!isSpeechEnabled);
  };

  // 🎯 Fonction pour valider un ticket
  const handleValidateTicket = async (ticketId) => {
    try {
      const response = await fetch(`${API_URL}/api/chat/validate/${ticketId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error('Erreur validation');
      }

      const data = await response.json();

      // Afficher le message de confirmation
      const confirmationMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, confirmationMessage]);

      // 🔊 Faire parler le bot
      if (isSpeechEnabled && data.response) {
        setTimeout(() => speakText(data.response), 300);
      }
    } catch (error) {
      console.error('Erreur validation ticket:', error);
      alert('Erreur lors de la validation du ticket. Veuillez réessayer.');
    }
  };

  // 🎯 Fonction pour annuler/modifier un ticket
  const handleCancelTicket = async (ticketId) => {
    try {
      const response = await fetch(`${API_URL}/api/chat/cancel/${ticketId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error('Erreur annulation');
      }

      const data = await response.json();

      // Afficher le message de réinitialisation
      const resetMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, resetMessage]);

      // 🔊 Faire parler le bot
      if (isSpeechEnabled && data.response) {
        setTimeout(() => speakText(data.response), 300);
      }
    } catch (error) {
      console.error('Erreur annulation ticket:', error);
      alert('Erreur lors de l\'annulation du ticket. Veuillez réessayer.');
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() && uploadedFiles.length === 0) return;

    // Ajouter message utilisateur
    const userMessage = {
      role: 'user',
      content: inputMessage,
      files: uploadedFiles.length > 0 ? uploadedFiles : null,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    const currentFiles = [...uploadedFiles];
    setUploadedFiles([]);
    setIsTyping(true);

    try {
      // Appel API backend
      const response = await fetch(`${API_URL}/api/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputMessage,
          session_id: sessionId,
          photos: currentFiles.map(f => f.url)
        })
      });

      if (!response.ok) {
        throw new Error('Erreur réseau');
      }

      const data = await response.json();

      // 🎯 NOUVEAU: Gérer la clôture de conversation
      if (data.should_close_session) {
        // Afficher message d'au revoir
        const goodbyeMessage = {
          role: 'assistant',
          content: data.response,
          language: data.language,
          conversation_type: data.conversation_type,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, goodbyeMessage]);
        setIsTyping(false);

        // 🔊 Faire parler le message d'au revoir
        if (isSpeechEnabled && data.response) {
          speakText(data.response);
        }

        // Attendre 3 secondes puis effacer la conversation
        setTimeout(async () => {
          console.log('👋 Clôture de la conversation - Effacement des messages');
          setMessages([]);

          // Appeler l'endpoint de suppression de session
          try {
            await fetch(`${API_URL}/api/chat/${sessionId}`, {
              method: 'DELETE'
            });
            console.log('✅ Session backend supprimée');
          } catch (error) {
            console.error('❌ Erreur suppression session:', error);
          }

          // Réafficher le message d'accueil après 500ms
          setTimeout(() => {
            const welcomeMessage = `Bonjour et bienvenue au service clientèle du groupe Mobilier de France.
Nous sommes à votre écoute pour un accompagnement personnalisé.

Pour vous aider rapidement, donnez-moi :
• Votre nom
• Votre numéro de commande
• Une description de votre problème

Vous pouvez écrire ou utiliser le microphone 🎤`;

            setMessages([{
              role: 'assistant',
              content: welcomeMessage,
              timestamp: new Date()
            }]);
          }, 500);
        }, 3000);

        return; // Arrêter le traitement ici
      }

      // Ajouter réponse assistant (traitement normal si pas de clôture)
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        language: data.language,
        conversation_type: data.conversation_type,
        timestamp: new Date(),
        // 🎯 NOUVEAU: Ajouter les infos de validation
        requires_validation: data.requires_validation,
        ticket_id: data.ticket_id
      };

      setMessages(prev => [...prev, assistantMessage]);

      // 🔊 Faire parler le bot automatiquement
      if (isSpeechEnabled && data.response) {
        // Petit délai pour laisser le message s'afficher
        setTimeout(() => {
          speakText(data.response);
        }, 300);
      }

    } catch (error) {
      console.error('Erreur:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Désolé, j'ai rencontré un problème technique. Pouvez-vous réessayer ?",
        timestamp: new Date()
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    // Validate files
    const validFiles = files.filter(file => {
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'video/mp4', 'video/quicktime'];
      const maxSize = 10 * 1024 * 1024; // 10MB

      if (!validTypes.includes(file.type)) {
        alert(`Type de fichier non supporté: ${file.name}`);
        return false;
      }
      if (file.size > maxSize) {
        alert(`Fichier trop volumineux: ${file.name} (max 10MB)`);
        return false;
      }
      return true;
    });

    if (validFiles.length === 0) return;

    // Upload files
    const formData = new FormData();
    validFiles.forEach(file => formData.append('files', file));

    try {
      const response = await fetch(`${API_URL}/api/upload/`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Erreur upload');
      }

      const data = await response.json();
      setUploadedFiles(prev => [...prev, ...data.files]);

    } catch (error) {
      console.error('Erreur upload:', error);
      alert('Erreur lors de l\'upload des fichiers');
    }
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // 🎤 Gérer l'enregistrement vocal - VERSION AMÉLIORÉE
  const toggleVoiceRecording = () => {
    if (!isVoiceSupported || !recognitionRef.current) {
      alert('⚠️ Reconnaissance vocale non disponible\n\nUtilisez Chrome ou Edge pour cette fonctionnalité.');
      return;
    }

    if (isRecording || isRecognitionActive.current) {
      // ⛔ Arrêter l'enregistrement
      try {
        isRecognitionActive.current = false;
        recognitionRef.current.stop();
        setIsRecording(false);
        setTranscript('');
        console.log('🛑 Enregistrement arrêté par l\'utilisateur');
      } catch (error) {
        console.error('❌ Erreur arrêt:', error);
        setIsRecording(false);
        setTranscript('');
      }
    } else {
      // ▶️ Démarrer l'enregistrement
      try {
        isRecognitionActive.current = true;
        recognitionRef.current.start();
        console.log('▶️ Démarrage enregistrement...');
      } catch (error) {
        console.error('❌ Erreur démarrage:', error);

        // Si déjà en cours, arrêter puis redémarrer
        if (error.message && error.message.includes('already')) {
          try {
            recognitionRef.current.stop();
            setTimeout(() => {
              try {
                recognitionRef.current.start();
              } catch (e) {
                console.error('❌ Redémarrage échoué:', e);
                alert('Impossible de démarrer le microphone. Rechargez la page.');
              }
            }, 100);
          } catch (e) {
            console.error('❌ Impossible d\'arrêter:', e);
          }
        } else {
          alert('❌ Erreur microphone\n\nVérifiez que le microphone est autorisé dans votre navigateur.');
        }
        isRecognitionActive.current = false;
        setIsRecording(false);
      }
    }
  };

  return (
    <div className="flex flex-col h-full max-w-5xl mx-auto" style={{background: 'linear-gradient(to bottom right, #20253F, #2C3650)'}}>
      {/* Header */}
      <div style={{background: 'linear-gradient(to right, #2C3650, #3A4560)'}} className="text-white p-6 shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">🛠️ Mobilier de France - Accompagnement</h1>
            <p className="text-sm opacity-90 mt-1">Service d'Accompagnement Intelligent • Traitement automatisé en temps réel</p>
          </div>

          {/* 🔊 Contrôle vocal */}
          <div className="flex items-center space-x-4">
            <button
              onClick={toggleSpeech}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${
                isSpeechEnabled
                  ? 'bg-white text-red-600 hover:bg-gray-100'
                  : 'bg-red-800 text-white hover:bg-red-900'
              }`}
              title={isSpeechEnabled ? "Désactiver la voix du bot" : "Activer la voix du bot"}
            >
              {isSpeechEnabled ? (
                <>
                  <Volume2 className={`w-5 h-5 ${isSpeaking ? 'animate-pulse' : ''}`} />
                  <span className="text-sm">Voix ON</span>
                  {isSpeaking && <span className="text-xs opacity-75">(parle...)</span>}
                </>
              ) : (
                <>
                  <VolumeX className="w-5 h-5" />
                  <span className="text-sm">Voix OFF</span>
                </>
              )}
            </button>

            <div className="text-right text-xs opacity-80 border-l border-white/30 pl-4">
              <p className="font-semibold">🎯 100% Automatisé</p>
              <p className="text-xs">✅ Analyse TON • ✅ Garantie • ✅ Priorité</p>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} fade-in`}
          >
            <div
              className={`max-w-[75%] rounded-2xl p-4 shadow-md ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white'
                  : 'bg-white text-gray-800 border border-gray-200'
              }`}
            >
              {/* Avatar */}
              <div className="flex items-start space-x-3">
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-amber-500 to-orange-500 flex items-center justify-center text-white font-bold flex-shrink-0">
                    M
                  </div>
                )}
                <div className="flex-1">
                  <p className="whitespace-pre-line leading-relaxed">{msg.content}</p>

                  {/* Files attachées */}
                  {msg.files && msg.files.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {msg.files.map((file, idx) => (
                        <div key={idx} className="relative group">
                          {file.type === 'jpg' || file.type === 'jpeg' || file.type === 'png' ? (
                            <img
                              src={`${API_URL}${file.url}`}
                              alt={file.original_name}
                              className="w-24 h-24 object-cover rounded-lg border-2 border-white"
                            />
                          ) : (
                            <div className="w-24 h-24 bg-gray-200 rounded-lg flex items-center justify-center text-xs text-gray-600">
                              📹 Vidéo
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* 🎯 NOUVEAU: Boutons de validation */}
                  {msg.role === 'assistant' && msg.requires_validation && msg.ticket_id && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <p className="text-sm font-semibold text-gray-700 mb-3">
                        ⚡ Ces informations sont-elles correctes ?
                      </p>
                      <div className="flex gap-3">
                        <button
                          onClick={() => handleValidateTicket(msg.ticket_id)}
                          className="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition-all transform hover:scale-105"
                        >
                          ✅ Valider
                        </button>
                        <button
                          onClick={() => handleCancelTicket(msg.ticket_id)}
                          className="flex-1 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition-all transform hover:scale-105"
                        >
                          ✏️ Modifier
                        </button>
                      </div>
                      <p className="text-xs text-gray-500 mt-2 text-center">
                        Cliquez sur "Valider" pour créer votre ticket, ou "Modifier" pour corriger les informations
                      </p>
                    </div>
                  )}

                  {/* Metadata */}
                  <div className={`flex items-center justify-between mt-2 text-xs ${
                    msg.role === 'user' ? 'text-white/70' : 'text-gray-500'
                  }`}>
                    <span>
                      {msg.timestamp.toLocaleTimeString('fr-FR', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                    {msg.language && msg.language !== 'fr' && (
                      <span className="ml-2">🌍 {msg.language.toUpperCase()}</span>
                    )}
                  </div>
                </div>
                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center text-amber-600 font-bold flex-shrink-0">
                    V
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex justify-start fade-in">
            <div className="bg-white rounded-2xl p-4 shadow-md border border-gray-200">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-amber-500 to-orange-500 flex items-center justify-center text-white font-bold">
                  M
                </div>
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-amber-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-amber-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-amber-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Uploaded Files Preview */}
      {uploadedFiles.length > 0 && (
        <div className="px-6 py-3 bg-white border-t border-gray-200">
          <p className="text-sm text-gray-600 mb-2 font-medium">
            📎 Fichiers à envoyer ({uploadedFiles.length}):
          </p>
          <div className="flex space-x-2 overflow-x-auto pb-2">
            {uploadedFiles.map((file, index) => (
              <div key={index} className="relative group flex-shrink-0">
                <div className="w-20 h-20 rounded-lg overflow-hidden border-2 border-amber-500">
                  {file.type === 'jpg' || file.type === 'jpeg' || file.type === 'png' ? (
                    <img
                      src={`${API_URL}${file.url}`}
                      alt={file.original_name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gray-200 flex items-center justify-center text-xs">
                      📹
                    </div>
                  )}
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-lg hover:bg-red-600 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
                <p className="text-xs text-gray-600 mt-1 text-center truncate w-20">
                  {file.original_name}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="bg-white p-6 border-t border-gray-200 shadow-lg">
        {/* 🎤 Recording Indicator - VERSION AMÉLIORÉE */}
        {isRecording && (
          <div className="mb-4 p-4 border-2 rounded-xl shadow-lg" style={{background: 'linear-gradient(to right, rgba(44, 54, 80, 0.1), rgba(58, 69, 96, 0.1))', borderColor: '#2C3650'}}>
            <div className="flex items-center space-x-3 mb-2">
              <div className="flex space-x-1">
                <div className="w-2 h-6 bg-red-500 rounded animate-pulse" style={{animationDelay: '0s'}}></div>
                <div className="w-2 h-8 bg-red-500 rounded animate-pulse" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-6 bg-red-500 rounded animate-pulse" style={{animationDelay: '0.2s'}}></div>
                <div className="w-2 h-10 bg-red-500 rounded animate-pulse" style={{animationDelay: '0.3s'}}></div>
                <div className="w-2 h-6 bg-red-500 rounded animate-pulse" style={{animationDelay: '0.4s'}}></div>
              </div>
              <span className="text-red-700 font-bold text-lg">🎤 Écoute en cours...</span>
              <button
                onClick={toggleVoiceRecording}
                className="ml-auto bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                ⛔ Arrêter
              </button>
            </div>
            {transcript && (
              <div className="mt-2 p-3 bg-white rounded-lg border border-red-200">
                <p className="text-sm text-gray-500 mb-1">Transcription en direct:</p>
                <p className="text-gray-800 font-medium italic">"{transcript}"</p>
              </div>
            )}
            {!transcript && (
              <p className="text-sm text-gray-600 italic">Parlez maintenant... Le texte apparaîtra ici en temps réel</p>
            )}
          </div>
        )}

        <div className="flex items-end space-x-3">
          {/* Upload Button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="bg-amber-100 hover:bg-amber-200 text-amber-700 p-3 rounded-full transition-colors flex-shrink-0"
            title="Ajouter des photos"
          >
            <Camera className="w-6 h-6" />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*,video/*"
            className="hidden"
            onChange={handleFileUpload}
          />

          {/* 🎤 Voice Button - VERSION AMÉLIORÉE */}
          {isVoiceSupported && (
            <button
              onClick={toggleVoiceRecording}
              className={`relative p-3 rounded-full transition-all flex-shrink-0 shadow-lg ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 text-white ring-4 ring-red-200 animate-pulse'
                  : 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white'
              }`}
              title={isRecording ? "⛔ Arrêter l'enregistrement vocal" : "🎤 Parler au lieu de taper"}
            >
              {isRecording ? (
                <>
                  <MicOff className="w-6 h-6" />
                  <span className="absolute -top-1 -right-1 flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
                  </span>
                </>
              ) : (
                <Mic className="w-6 h-6" />
              )}
            </button>
          )}

          {/* Message Input */}
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Nom complet + Problème + N° commande... (Ex: Jean Dupont, mon canapé OSLO a un pied cassé, CMD-2024-12345)"
              className="w-full border-2 border-gray-300 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none text-gray-900"
              rows="1"
              style={{
                minHeight: '50px',
                maxHeight: '150px',
                color: '#1F2937'
              }}
            />
          </div>

          {/* Send Button */}
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() && uploadedFiles.length === 0}
            className={`p-3 rounded-full flex-shrink-0 transition-all ${
              inputMessage.trim() || uploadedFiles.length > 0
                ? 'bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white shadow-lg'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isTyping ? (
              <Loader2 className="w-6 h-6 animate-spin" />
            ) : (
              <Send className="w-6 h-6" />
            )}
          </button>
        </div>

        {/* Info Text */}
        <p className="text-xs text-gray-500 mt-3 text-center">
          🔒 Données sécurisées • ⚡ Réponse immédiate • 🎤 Conversation vocale complète • 🔊 Le bot vous parle • 🎯 Analyse automatique du TON et PRIORITÉ • 🛡️ Vérification garantie instantanée
        </p>
        {isSpeaking && (
          <p className="text-xs text-blue-600 font-medium mt-2 text-center animate-pulse">
            🔊 Le bot est en train de parler... Écoutez sa réponse
          </p>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
