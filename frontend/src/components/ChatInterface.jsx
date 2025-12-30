// frontend/src/components/ChatInterface.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Send, Camera, X, Loader2, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import DOMPurify from 'dompurify';

const API_URL = import.meta.env.VITE_API_URL ?? '';

// Validate API URL is configured
if (!API_URL) {
  console.error('VITE_API_URL is not configured. Please set it in your .env file.');
}

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [sessionId] = useState(() => crypto.randomUUID()); // Secure random session ID
  const [isRecording, setIsRecording] = useState(false);
  const [isVoiceSupported, setIsVoiceSupported] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSpeechEnabled, setIsSpeechEnabled] = useState(true); // Activer voix par défaut
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [pendingTicket, setPendingTicket] = useState(null); // Données du ticket en attente de validation
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);
  const isRecognitionActive = useRef(false);
  const speechSynthesisRef = useRef(null);

  // Message d'accueil - VERSION SIMPLIFIÉE
  useEffect(() => {
    const welcomeMessage = `👋 Bonjour ! Je suis votre assistant SAV Mobilier de France.

Décrivez-moi votre problème avec votre numéro de commande, je m'occupe du reste !

💡 **Exemple** : "Bonjour, je m'appelle Marie Martin. Mon canapé OSLO a le pied cassé, commande CMD-2024-12345"`;

    setMessages([{
      role: 'assistant',
      content: welcomeMessage,
      timestamp: new Date()
    }]);

    // 🔊 Parler le message d'accueil - VERSION COURTE
    setTimeout(() => {
      if (isSpeechEnabled) {
        const shortWelcome = "Bonjour ! Décrivez-moi votre problème avec votre numéro de commande.";
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
      console.error('❌ Erreur synthèse vocale:', error);
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
      // Si aucun message mais des photos, envoyer un message par défaut
      const messageToSend = inputMessage.trim() || (currentFiles.length > 0 ? "[Photo envoyée]" : "");

      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageToSend,
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
            const welcomeMessage = `Bonjour ! Bienvenue au Service Après-Vente de Mobilier de France 🛠️

Je suis votre assistant SAV intelligent et je suis là pour vous aider avec votre réclamation.

🎯 **Je vais vous aider à :**
• Analyser votre problème automatiquement
• Vérifier votre garantie instantanément
• Collecter les preuves nécessaires (photos/vidéos)
• Créer votre ticket SAV en quelques secondes
• Calculer la priorité et le délai de traitement

📋 **Pour commencer, veuillez me fournir :**
1. **Votre nom complet**
2. **Votre numéro de commande**
3. **La description détaillée de votre problème**
4. **Des photos du problème** (si possible)

**Exemple :**
"Bonjour, je m'appelle Jean Dupont. Mon canapé OSLO a un pied cassé, c'est dangereux pour mon enfant! Numéro de commande: CMD-2024-12345"

🎤 **Nouveauté : Communication vocale bidirectionnelle !**
• Parlez avec le bouton microphone 🎤
• J'écouterai votre problème
• Je vous répondrai avec ma voix 🔊

**Je m'occupe du reste automatiquement ! Présentez-vous et expliquez votre problème :**`;

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
        isRecap: data.response.includes('Je récapitule') // Marquer les récapitulatifs
      };

      setMessages(prev => [...prev, assistantMessage]);

      // 🎯 NOUVEAU: Si le bot envoie des données de ticket (récapitulatif), stocker pour validation
      if (data.ticket_data) {
        setPendingTicket(data.ticket_data);
        console.log('📋 Ticket en attente de validation:', data.ticket_data);
        // Ne pas faire parler le bot, attendre la validation
      } else {
        // 🔊 Faire parler le bot automatiquement (sauf pour les récapitulatifs)
        if (isSpeechEnabled && data.response) {
          // Petit délai pour laisser le message s'afficher
          setTimeout(() => {
            speakText(data.response);
          }, 300);
        }
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

  // 🎯 Confirmer et créer le ticket SAV
  const handleConfirmTicket = async () => {
    if (!pendingTicket) return;

    setIsTyping(true);

    try {
      // Vérifier si le ticket est déjà créé (contient ticket_id)
      if (pendingTicket.ticket_id) {
        // Le ticket est déjà créé par le chatbot, juste afficher la confirmation
        console.log('✅ Ticket déjà créé:', pendingTicket.ticket_id);

        const confirmMessage = {
          role: 'assistant',
          content: `Parfait ! Votre ticket SAV a été créé avec succès (N° ${pendingTicket.ticket_id}). Vous pouvez le consulter dans le tableau de bord. Souhaitez-vous autre chose ?`,
          timestamp: new Date(),
          isTicketCreated: true
        };

        setMessages(prev => [...prev, confirmMessage]);
        setPendingTicket(null);

        // 🔊 Faire parler le message de confirmation
        if (isSpeechEnabled) {
          setTimeout(() => {
            speakText(confirmMessage.content);
          }, 300);
        }

        return;
      }

      // Sinon, créer le ticket via l'API
      const transcript = messages
        .map(msg => `${msg.role === 'user' ? 'Client' : 'Assistant'}: ${msg.content}`)
        .join('\n');

      // Les données sont dans validation_data
      const ticketData = pendingTicket.validation_data || pendingTicket;

      const response = await fetch(`${API_URL}/api/chat/create-ticket`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_name: ticketData.customer_name,
          problem_description: ticketData.problem_description,
          product: ticketData.product_name || ticketData.product,
          order_number: ticketData.order_number,
          conversation_transcript: transcript,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la création du ticket');
      }

      const result = await response.json();
      console.log('✅ Ticket créé:', result);

      // Message de confirmation
      const confirmMessage = {
        role: 'assistant',
        content: `Parfait ! Votre ticket SAV a été créé avec succès (N° ${result.ticket_id}). Vous pouvez le consulter dans le tableau de bord. Souhaitez-vous autre chose ?`,
        timestamp: new Date(),
        isTicketCreated: true
      };

      setMessages(prev => [...prev, confirmMessage]);

      // Réinitialiser le ticket en attente
      setPendingTicket(null);

      // 🔊 Faire parler le message de confirmation
      if (isSpeechEnabled) {
        setTimeout(() => {
          speakText(confirmMessage.content);
        }, 300);
      }

    } catch (error) {
      console.error('Erreur création ticket:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Désolé, une erreur s'est produite lors de la création du ticket. Veuillez réessayer.",
        timestamp: new Date()
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  // 🎯 Annuler et recommencer
  const handleCancelTicket = () => {
    setPendingTicket(null);

    // Message d'annulation
    const cancelMessage = {
      role: 'assistant',
      content: "D'accord, recommençons. Pouvez-vous me donner les informations correctes ?",
      timestamp: new Date()
    };

    setMessages(prev => [...prev, cancelMessage]);

    // 🔊 Faire parler le message
    if (isSpeechEnabled) {
      setTimeout(() => {
        speakText(cancelMessage.content);
      }, 300);
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
      const response = await fetch(`${API_URL}/api/upload`, {
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
    <div className="flex flex-col h-full max-w-5xl mx-auto bg-gradient-to-br from-amber-50 to-orange-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Service clientèle du groupe Mobilier de France</h1>
            <p className="text-sm opacity-90 mt-1">Service Après-Vente Intelligent • Traitement automatisé en temps réel</p>
          </div>

          {/* 🔊 Contrôle vocal */}
          <div className="flex items-center space-x-4">
            <button
              onClick={toggleSpeech}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${
                isSpeechEnabled
                  ? 'bg-white text-blue-600 hover:bg-gray-100'
                  : 'bg-blue-800 text-white hover:bg-blue-900'
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
                  <p
                    className="whitespace-pre-line leading-relaxed"
                    dangerouslySetInnerHTML={{
                      __html: DOMPurify.sanitize(msg.content, {
                        ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'br'],
                        ALLOWED_ATTR: ['href', 'target']
                      })
                    }}
                  />

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

        {/* 🎯 Boutons de validation du ticket SAV */}
        {pendingTicket && (
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-400 rounded-2xl p-6 shadow-xl max-w-2xl mx-auto fade-in">
            <h3 className="text-xl font-bold text-green-900 mb-3 flex items-center">
              <span className="text-2xl mr-2">✅</span>
              Validation du ticket SAV
            </h3>
            <p className="text-gray-700 mb-6">
              Veuillez vérifier les informations ci-dessus et confirmer la création du ticket.
            </p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={handleConfirmTicket}
                disabled={isTyping}
                className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-bold py-4 px-8 rounded-xl shadow-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <span className="text-2xl mr-2">✅</span>
                Valider le ticket
              </button>
              <button
                onClick={handleCancelTicket}
                disabled={isTyping}
                className="bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 text-white font-bold py-4 px-8 rounded-xl shadow-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <span className="text-2xl mr-2">❌</span>
                Recommencer
              </button>
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
          <div className="mb-4 p-4 bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-300 rounded-xl shadow-lg">
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
              className="w-full border-2 border-gray-300 rounded-2xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
              rows="1"
              style={{
                minHeight: '50px',
                maxHeight: '150px'
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
