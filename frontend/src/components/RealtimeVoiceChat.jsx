// frontend/src/components/RealtimeVoiceChat.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Phone, PhoneOff, Mic, Volume2, Loader2 } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL ?? '';

/**
 * Composant de conversation vocale en temps réel avec OpenAI Realtime API
 * Permet une communication vocale bidirectionnelle naturelle (comme un appel téléphonique)
 */
const RealtimeVoiceChat = ({ onTicketCreated }) => {
  // États
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [error, setError] = useState(null);

  // Refs
  const wsRef = useRef(null);
  const audioContextRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const audioQueueRef = useRef([]);
  const isPlayingRef = useRef(false);

  // Instructions système pour le bot SAV
  const systemInstructions = `Tu es l'assistant SAV vocal de Mobilier de France.

🎯 TON RÔLE:
- Aide le client avec son problème SAV de manière naturelle et conversationnelle
- Collecte les informations nécessaires: nom, problème, numéro de commande
- Sois chaleureux, empathique et efficace
- Parle de manière concise (2-3 phrases maximum par réponse)

📋 INFORMATIONS À COLLECTER:
1. Nom complet du client
2. Description du problème
3. Numéro de commande (format: CMD-YYYY-XXXXX)
4. Produit concerné

⚠️ IMPORTANT:
- Écoute activement et reformule pour confirmer
- Pose UNE question à la fois
- Ne propose JAMAIS de solutions toi-même
- Ton rôle est de COLLECTER les informations, pas de résoudre
- Une fois toutes les infos collectées, demande confirmation pour créer le ticket

EXEMPLE DE CONVERSATION:
Client: "Bonjour"
Bot: "Bonjour ! Je suis votre assistant SAV Mobilier de France. Quel est votre nom ?"
Client: "Marie Dupont"
Bot: "Enchanté Marie. Quel est votre problème ?"
Client: "Mon canapé a un pied cassé"
Bot: "Je comprends, c'est embêtant. Quel est votre numéro de commande ?"
Client: "CMD-2024-12345"
Bot: "Parfait. Je récapitule : Marie Dupont, canapé avec pied cassé, commande CMD-2024-12345. Je crée votre ticket ?"

Reste naturel, conversationnel et bref !`;

  /**
   * Initialiser le contexte audio
   */
  useEffect(() => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 24000 // Format requis par Realtime API
      });
    }

    return () => {
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close();
      }
    };
  }, []);

  /**
   * Démarrer la conversation vocale
   */
  const startVoiceCall = async () => {
    try {
      setIsConnecting(true);
      setError(null);

      // 1. Obtenir l'accès au microphone
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 24000
        }
      });
      mediaStreamRef.current = stream;

      // 2. Se connecter au proxy WebSocket backend
      // Le backend gère l'authentification avec OpenAI
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = API_URL.replace('http://', '').replace('https://', '');
      const wsUrl = `${wsProtocol}//${wsHost}/api/realtime/ws`;

      console.log('🔌 Connexion au proxy backend:', wsUrl);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('✅ Connexion WebSocket établie avec le proxy backend');

        // Configurer la session
        const sessionConfig = {
          type: 'session.update',
          session: {
            modalities: ['text', 'audio'],
            instructions: systemInstructions,
            voice: 'alloy', // Voix féminine naturelle
            input_audio_format: 'pcm16',
            output_audio_format: 'pcm16',
            input_audio_transcription: {
              model: 'whisper-1'
            },
            turn_detection: {
              type: 'server_vad', // Détection automatique de fin de parole
              threshold: 0.5,
              prefix_padding_ms: 300,
              silence_duration_ms: 500
            },
            temperature: 0.7,
            max_response_output_tokens: 300
          }
        };

        ws.send(JSON.stringify(sessionConfig));

        setIsConnected(true);
        setIsConnecting(false);

        // Dire bonjour automatiquement
        const greeting = {
          type: 'conversation.item.create',
          item: {
            type: 'message',
            role: 'user',
            content: [{
              type: 'input_text',
              text: 'Bonjour'
            }]
          }
        };
        ws.send(JSON.stringify(greeting));

        // Demander une réponse
        ws.send(JSON.stringify({ type: 'response.create' }));
      };

      // Gérer les messages reçus
      ws.onmessage = (event) => {
        handleRealtimeEvent(JSON.parse(event.data));
      };

      ws.onerror = (error) => {
        console.error('❌ Erreur WebSocket:', error);
        setError('Erreur de connexion vocale');
        setIsConnected(false);
        setIsConnecting(false);
      };

      ws.onclose = () => {
        console.log('🔌 Connexion WebSocket fermée');
        setIsConnected(false);
        setIsListening(false);
        setIsSpeaking(false);
      };

      wsRef.current = ws;

      // 4. Commencer à envoyer l'audio du microphone
      startAudioCapture(stream, ws);

    } catch (error) {
      console.error('❌ Erreur démarrage appel:', error);
      setError(error.message || 'Impossible de démarrer l\'appel vocal');
      setIsConnecting(false);
    }
  };

  /**
   * Capturer l'audio du microphone et l'envoyer via WebSocket
   */
  const startAudioCapture = (stream, ws) => {
    const audioContext = audioContextRef.current;
    const source = audioContext.createMediaStreamSource(stream);

    // Créer un processeur audio pour convertir en PCM16
    const processor = audioContext.createScriptProcessor(4096, 1, 1);

    processor.onaudioprocess = (e) => {
      if (!ws || ws.readyState !== WebSocket.OPEN) return;

      const inputData = e.inputBuffer.getChannelData(0);

      // Convertir Float32 en PCM16
      const pcm16 = new Int16Array(inputData.length);
      for (let i = 0; i < inputData.length; i++) {
        const s = Math.max(-1, Math.min(1, inputData[i]));
        pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
      }

      // Convertir en base64
      const base64Audio = btoa(String.fromCharCode.apply(null, new Uint8Array(pcm16.buffer)));

      // Envoyer l'audio au serveur
      ws.send(JSON.stringify({
        type: 'input_audio_buffer.append',
        audio: base64Audio
      }));

      setIsListening(true);
    };

    source.connect(processor);
    processor.connect(audioContext.destination);
  };

  /**
   * Gérer les événements reçus de Realtime API
   */
  const handleRealtimeEvent = (event) => {
    console.log('📨 Event:', event.type);

    switch (event.type) {
      case 'session.created':
      case 'session.updated':
        console.log('✅ Session configurée');
        break;

      case 'conversation.item.created':
        // Nouvel item de conversation créé
        if (event.item.role === 'assistant' && event.item.content) {
          const textContent = event.item.content.find(c => c.type === 'text');
          if (textContent) {
            setTranscript(textContent.text);
            addToHistory('assistant', textContent.text);
          }
        }
        break;

      case 'conversation.item.input_audio_transcription.completed':
        // Transcription de l'audio utilisateur
        if (event.transcript) {
          setTranscript(event.transcript);
          addToHistory('user', event.transcript);
        }
        break;

      case 'response.audio.delta':
        // Chunk d'audio de la réponse
        if (event.delta) {
          playAudioChunk(event.delta);
          setIsSpeaking(true);
        }
        break;

      case 'response.audio.done':
        setIsSpeaking(false);
        break;

      case 'response.done':
        setIsListening(true);
        setIsSpeaking(false);
        break;

      case 'error':
        console.error('❌ Erreur API:', event.error);
        setError(event.error.message);
        break;

      default:
        // Autres événements
        break;
    }
  };

  /**
   * Jouer un chunk audio reçu
   */
  const playAudioChunk = (base64Audio) => {
    try {
      // Décoder base64 en PCM16
      const binaryString = atob(base64Audio);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      const pcm16 = new Int16Array(bytes.buffer);

      // Convertir PCM16 en Float32
      const float32 = new Float32Array(pcm16.length);
      for (let i = 0; i < pcm16.length; i++) {
        float32[i] = pcm16[i] / 0x8000;
      }

      // Ajouter à la queue de lecture
      audioQueueRef.current.push(float32);

      // Commencer la lecture si pas déjà en cours
      if (!isPlayingRef.current) {
        playNextAudioChunk();
      }
    } catch (error) {
      console.error('❌ Erreur lecture audio:', error);
    }
  };

  /**
   * Jouer le prochain chunk audio de la queue
   */
  const playNextAudioChunk = () => {
    if (audioQueueRef.current.length === 0) {
      isPlayingRef.current = false;
      return;
    }

    isPlayingRef.current = true;
    const float32Data = audioQueueRef.current.shift();

    const audioContext = audioContextRef.current;
    const audioBuffer = audioContext.createBuffer(1, float32Data.length, 24000);
    audioBuffer.getChannelData(0).set(float32Data);

    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);

    source.onended = () => {
      playNextAudioChunk();
    };

    source.start();
  };

  /**
   * Ajouter un message à l'historique
   */
  const addToHistory = (role, content) => {
    setConversationHistory(prev => [...prev, { role, content, timestamp: new Date() }]);
  };

  /**
   * Arrêter l'appel vocal
   */
  const stopVoiceCall = () => {
    // Fermer WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Arrêter le microphone
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }

    // Réinitialiser les états
    setIsConnected(false);
    setIsListening(false);
    setIsSpeaking(false);
    audioQueueRef.current = [];
    isPlayingRef.current = false;
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 shadow-lg">
        <h1 className="text-3xl font-bold flex items-center">
          <Phone className="w-8 h-8 mr-3" />
          Assistant Vocal SAV - Conversation en Temps Réel
        </h1>
        <p className="text-sm opacity-90 mt-1">
          Parlez naturellement, comme au téléphone • Latence &lt;200ms
        </p>
      </div>

      {/* Zone de conversation */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {conversationHistory.length === 0 && !isConnected && (
          <div className="text-center py-12">
            <Phone className="w-24 h-24 mx-auto text-blue-300 mb-4" />
            <h2 className="text-2xl font-bold text-gray-700 mb-2">
              Conversation Vocale Bidirectionnelle
            </h2>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Cliquez sur "Démarrer l'appel" pour parler avec l'assistant SAV.
              Pas besoin de cliquer sur un bouton pour parler, la conversation est fluide et naturelle !
            </p>
            <button
              onClick={startVoiceCall}
              disabled={isConnecting}
              className={`px-8 py-4 rounded-full font-bold text-lg shadow-xl transition-all transform hover:scale-105 ${
                isConnecting
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white'
              }`}
            >
              {isConnecting ? (
                <>
                  <Loader2 className="w-6 h-6 animate-spin inline mr-2" />
                  Connexion en cours...
                </>
              ) : (
                <>
                  <Phone className="w-6 h-6 inline mr-2" />
                  Démarrer l'Appel Vocal
                </>
              )}
            </button>
          </div>
        )}

        {/* Messages de conversation */}
        {conversationHistory.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[75%] rounded-2xl p-4 shadow-md ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white'
                  : 'bg-white text-gray-800 border border-gray-200'
              }`}
            >
              <p className="font-medium mb-1">
                {msg.role === 'user' ? '👤 Vous' : '🤖 Assistant'}
              </p>
              <p className="whitespace-pre-line">{msg.content}</p>
              <p className="text-xs opacity-70 mt-2">
                {msg.timestamp.toLocaleTimeString('fr-FR')}
              </p>
            </div>
          </div>
        ))}

        {/* Indicateur de statut */}
        {isConnected && (
          <div className="fixed bottom-24 left-1/2 transform -translate-x-1/2 bg-white rounded-full shadow-2xl px-6 py-3 border-2 border-blue-500">
            <div className="flex items-center space-x-4">
              {isListening && (
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    {[0, 1, 2, 3, 4].map(i => (
                      <div
                        key={i}
                        className="w-1 bg-green-500 rounded animate-pulse"
                        style={{
                          height: `${Math.random() * 20 + 10}px`,
                          animationDelay: `${i * 0.1}s`
                        }}
                      />
                    ))}
                  </div>
                  <span className="text-green-600 font-medium">Écoute...</span>
                </div>
              )}

              {isSpeaking && (
                <div className="flex items-center space-x-2">
                  <Volume2 className="w-5 h-5 text-blue-600 animate-pulse" />
                  <span className="text-blue-600 font-medium">Parle...</span>
                </div>
              )}

              {transcript && (
                <div className="text-sm text-gray-600 italic max-w-md truncate">
                  "{transcript}"
                </div>
              )}
            </div>
          </div>
        )}

        {/* Erreur */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <p className="font-bold">Erreur</p>
            <p>{error}</p>
          </div>
        )}
      </div>

      {/* Bouton de raccrocher */}
      {isConnected && (
        <div className="p-6 bg-white border-t border-gray-200">
          <button
            onClick={stopVoiceCall}
            className="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-4 rounded-full shadow-lg transition-all transform hover:scale-105 flex items-center justify-center"
          >
            <PhoneOff className="w-6 h-6 mr-2" />
            Raccrocher
          </button>
          <p className="text-center text-xs text-gray-500 mt-3">
            La conversation se termine automatiquement après 10 minutes d'inactivité
          </p>
        </div>
      )}
    </div>
  );
};

export default RealtimeVoiceChat;
