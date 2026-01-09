// frontend/src/components/VoiceChatWhisper.jsx
import React, { useState, useRef, useEffect } from "react";
import {
  Phone,
  PhoneOff,
  Mic,
  MicOff,
  Volume2,
  Loader2,
  Info,
  Clock,
  Camera,
  X,
} from "lucide-react";
import { useLanguage } from "../context/LanguageContext";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
console.log(
  "🔧 VoiceChatWhisper - VITE_API_URL:",
  import.meta.env.VITE_API_URL
);
console.log("🔧 VoiceChatWhisper - API_URL utilisé:", API_URL);
console.log("🔧 VoiceChatWhisper - API_URL est vide?", API_URL === "");

// 🔧 Helper to normalize/construct absolute URLs for uploaded files
const getAbsoluteUrl = (rawUrl) => {
  if (!rawUrl) return "";
  const url = String(rawUrl).trim();
  if (url.startsWith("//")) {
    console.warn("Normalizing protocol-relative URL:", url);
    return `https:${url}`;
  }
  if (/^https?:\/\//i.test(url)) return url;
  if (/^https?\/\//i.test(url)) {
    const fixed = url.replace(/^(https?)(\/\/)/i, "$1://");
    console.warn("Fixed malformed URL (missing colon):", url, "->", fixed);
    return fixed;
  }
  if (/^https?/i.test(url) && !url.includes("://")) {
    const fixed = url.replace(/^([a-z]+)(.*)/i, "$1://$2");
    console.warn("Fixed malformed URL (missing ://):", url, "->", fixed);
    return fixed;
  }
  if (url.startsWith("/")) return `${API_URL}${url}`;
  return `${API_URL}/${url}`;
};

/**
 * Composant de conversation vocale avec Whisper + GPT-4 + TTS
 * Alternative à l'API Realtime avec latence de ~1-2 secondes
 */
const VoiceChatWhisper = ({ onTicketCreated }) => {
  // États
  const [isActive, setIsActive] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState("");
  const [conversationHistory, setConversationHistory] = useState([]);
  const [error, setError] = useState(null);
  const [processingStep, setProcessingStep] = useState("");
  const [recordingTime, setRecordingTime] = useState(0); // Temps d'enregistrement en secondes
  const [audioLevels, setAudioLevels] = useState([]); // Niveaux audio pour la visualisation
  const [pendingTicket, setPendingTicket] = useState(null); // Données du ticket en attente de validation
  const [uploadedFiles, setUploadedFiles] = useState([]); // Fichiers uploadés

  // Refs
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioContextRef = useRef(null);
  const currentAudioRef = useRef(null);
  const fileInputRef = useRef(null); // Ref pour input file
  const [micPermission, setMicPermission] = useState(null); // null, 'granted', 'denied'
  const analyserRef = useRef(null); // Analyseur audio pour la détection de silence
  const silenceTimerRef = useRef(null); // Timer pour détecter le silence
  const recordingTimerRef = useRef(null); // Timer pour afficher le temps d'enregistrement
  const animationFrameRef = useRef(null); // Animation frame pour la visualisation

  const { t } = useLanguage();

  // Initialiser le contexte audio et nettoyer lors du démontage
  useEffect(() => {
    audioContextRef.current = new (window.AudioContext ||
      window.webkitAudioContext)();
    return () => {
      // Nettoyer tous les timers et animations
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current?.state !== "closed") {
        audioContextRef.current.close();
      }
    };
  }, []);

  // Demander l'autorisation du microphone dès le chargement du composant
  useEffect(() => {
    const requestMicrophonePermission = async () => {
      try {
        console.log("Demande d'autorisation du microphone...");
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            sampleRate: 44100,
          },
        });

        // Permission accordée
        console.log("✅ Permission microphone accordée");
        setMicPermission("granted");

        // Arrêter le stream (on ne l'utilise pas encore)
        stream.getTracks().forEach((track) => track.stop());
      } catch (err) {
        console.error("❌ Permission microphone refusée:", err);
        setMicPermission("denied");
        setError(t("chat.alert_microphone_denied"));
      }
    };

    requestMicrophonePermission();
  }, []); // S'exécute une seule fois au montage du composant

  /**
   * Démarrer la conversation vocale
   */
  const startVoiceChat = async () => {
    try {
      setError(null);

      // Demander accès au microphone
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        },
      });

      setIsActive(true);

      // Dire bonjour automatiquement avec le nouveau message client
      await speakAndAddToHistory("assistant", t("chat.welcome.long"));

      // Démarrer l'enregistrement après le message de bienvenue
      setTimeout(() => startRecording(stream), 500);
    } catch (err) {
      console.error("Erreur accès microphone:", err);
      setError(t("chat.alert_microphone_denied"));
    }
  };

  /**
   * Démarrer l'enregistrement
   */
  const startRecording = (stream) => {
    audioChunksRef.current = [];
    setRecordingTime(0);
    setAudioLevels([]);

    // Configurer l'analyseur audio pour la détection de silence et la visualisation
    const audioContext = audioContextRef.current;
    const source = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 2048;
    analyser.smoothingTimeConstant = 0.8;
    source.connect(analyser);
    analyserRef.current = analyser;

    // Timer pour afficher le temps d'enregistrement
    const startTime = Date.now();
    recordingTimerRef.current = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      setRecordingTime(elapsed);
    }, 100);

    // Visualisation audio seulement (détection de silence DÉSACTIVÉE temporairement)
    const checkAudioLevels = () => {
      if (!analyserRef.current) return;

      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
      analyserRef.current.getByteTimeDomainData(dataArray);

      // Mettre à jour la visualisation avec les derniers niveaux
      const levels = [];
      for (let i = 0; i < 40; i++) {
        const index = Math.floor((i / 40) * dataArray.length);
        levels.push(Math.abs(dataArray[index] - 128));
      }
      setAudioLevels(levels);

      // NOTE: Détection de silence DÉSACTIVÉE - L'utilisateur doit arrêter manuellement
      // ou attendre la limite de 30 secondes

      animationFrameRef.current = requestAnimationFrame(checkAudioLevels);
    };

    checkAudioLevels();

    const mediaRecorder = new MediaRecorder(stream, {
      mimeType: "audio/webm;codecs=opus",
    });

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunksRef.current.push(event.data);
      }
    };

    mediaRecorder.onstop = async () => {
      // Nettoyer les timers et animations
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
        recordingTimerRef.current = null;
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      setRecordingTime(0);
      setAudioLevels([]);

      const audioBlob = new Blob(audioChunksRef.current, {
        type: "audio/webm",
      });

      // Vérifier que l'audio n'est pas trop court (seuil réduit pour accepter plus d'enregistrements)
      if (audioBlob.size > 500) {
        await processAudio(audioBlob);
      } else {
        console.log(t("voice.processing.recording_too_short"));
        // Reprendre l'enregistrement si trop court
        if (isActive) {
          startRecording(stream);
        }
      }
    };

    mediaRecorderRef.current = mediaRecorder;
    mediaRecorder.start();
    setIsRecording(true);

    console.log("Enregistrement démarré avec détection de silence...");
  };

  /**
   * Arrêter l'enregistrement après un délai
   */
  useEffect(() => {
    if (!isRecording || isProcessing) return;

    // Arrêter l'enregistrement après 30 secondes max (permet des descriptions détaillées)
    const timer = setTimeout(() => {
      if (mediaRecorderRef.current?.state === "recording") {
        console.log("Limite de temps atteinte (30s) - arrêt automatique");
        mediaRecorderRef.current.stop();
        setIsRecording(false);
      }
    }, 30000);

    return () => clearTimeout(timer);
  }, [isRecording, isProcessing]);

  /**
   * Traiter l'audio enregistré
   */
  const processAudio = async (audioBlob) => {
    setIsProcessing(true);
    setIsRecording(false);

    try {
      // Étape 1: Transcription avec Whisper
      setProcessingStep(t("voice.processing.transcription"));
      const transcript = await transcribeAudio(audioBlob);

      if (!transcript || transcript.trim().length === 0) {
        // Reprendre l'enregistrement si pas de texte
        if (isActive) {
          startRecording(mediaRecorderRef.current.stream);
        }
        return;
      }

      setCurrentTranscript(transcript);
      addToHistory("user", transcript);

      // Étape 2: Obtenir la réponse du chatbot
      setProcessingStep(t("voice.processing.generating"));
      const chatData = await getChatResponse(transcript);

      // NE PAS vider les fichiers uploadés ici - ils seront vidés après la création du ticket

      // Étape 3: Si c'est un récapitulatif, stocker les données ET dire le récapitulatif
      if (chatData.ticket_data) {
        setPendingTicket(chatData.ticket_data);
        // Dire le récapitulatif vocalement
        setProcessingStep(t("voice.processing.summary_synthesis"));
        await speakAndAddToHistory("assistant", chatData.response, false);
        // L'enregistrement reprendra automatiquement dans le finally pour écouter "oui" ou "non"
      }
      // Étape 3b: Si l'utilisateur dit "oui" et qu'il y a un ticket en attente, créer le ticket
      else if (
        pendingTicket &&
        /\b(oui|ok|validé|correct|parfait|exactement|c'est bon|tout est bon)\b/i.test(
          transcript
        )
      ) {
        console.log(
          "✅ Validation vocale détectée - création automatique du ticket"
        );
        // Créer le ticket automatiquement
        await handleConfirmTicket();
        return; // Sortir pour éviter de reprendre l'enregistrement
      }
      // Étape 3c: Si l'utilisateur dit "non" et qu'il y a un ticket en attente, annuler
      else if (
        pendingTicket &&
        /\b(non|pas correct|faux|annuler|recommencer)\b/i.test(transcript)
      ) {
        console.log("❌ Annulation vocale détectée - recommencer");
        await handleCancelTicket();
        return;
      } else {
        // Étape 4: Synthèse vocale et lecture pour les autres messages
        setProcessingStep(t("voice.processing.synthesis"));
        await speakAndAddToHistory("assistant", chatData.response, false);
      }
    } catch (err) {
      console.error("❌ Erreur traitement complète:", err);
      console.error("❌ Stack trace:", err.stack);
      console.error("❌ Message:", err.message);
      setError(t("chat.error_general"));
    } finally {
      setIsProcessing(false);
      setProcessingStep("");

      // Reprendre l'enregistrement TOUJOURS (même s'il y a un ticket en attente)
      // Car on attend la validation vocale "oui" ou "non"
      if (isActive && mediaRecorderRef.current?.stream) {
        setTimeout(() => startRecording(mediaRecorderRef.current.stream), 500);
      }
    }
  };

  /**
   * Transcription audio avec Whisper
   */
  const transcribeAudio = async (audioBlob) => {
    const formData = new FormData();
    formData.append("audio_file", audioBlob, "recording.webm");

    const response = await fetch(`${API_URL}/api/voice/transcribe`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(t("voice.error_transcription"));
    }

    const data = await response.json();
    console.log("Transcription:", data.text);
    return data.text;
  };

  /**
   * Obtenir une réponse du chatbot
   */
  const getChatResponse = async (message) => {
    try {
      console.log("📤 Envoi du message au chatbot:", message);
      console.log("📸 Photos attachées:", uploadedFiles.length);
      const response = await fetch(`${API_URL}/api/voice/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          conversation_history: conversationHistory.map((msg) => ({
            role: msg.role,
            content: msg.content,
          })),
          photos: uploadedFiles.map((f) => getAbsoluteUrl(f.url)),
        }),
      });

      console.log("📥 Réponse reçue:", response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("❌ Erreur API:", errorText);
        throw new Error(`Erreur ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log("✅ Réponse:", data.response);
      console.log("🎯 Action:", data.action);
      console.log("🎫 Ticket data:", data.ticket_data);
      return data; // Retourner toutes les données (response, action, ticket_data)
    } catch (err) {
      console.error("❌ Erreur getChatResponse:", err);
      throw err;
    }
  };

  /**
   * Gérer l'upload de fichiers (photos/vidéos)
   */
  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    // Valider les fichiers
    const validFiles = files.filter((file) => {
      const validTypes = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "video/mp4",
        "video/quicktime",
      ];
      const maxSize = 10 * 1024 * 1024; // 10MB

      if (!validTypes.includes(file.type)) {
        alert(t("chat.upload_type_not_supported").replace("{name}", file.name));
        return false;
      }
      if (file.size > maxSize) {
        alert(
          t("chat.upload_file_too_large")
            .replace("{name}", file.name)
            .replace("{max}", "10")
        );
        return false;
      }
      return true;
    });

    if (validFiles.length === 0) return;

    // Upload des fichiers
    const formData = new FormData();
    validFiles.forEach((file) => formData.append("files", file));

    try {
      const response = await fetch(`${API_URL}/api/upload/`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Erreur upload");
      }

      const data = await response.json();
      setUploadedFiles((prev) => [...prev, ...data.files]);

      // NE PAS dire "J'ai reçu les photos" - laissez l'IA générer automatiquement le récapitulatif
      // Le récapitulatif sera généré automatiquement par le backend quand il détectera les photos
      console.log(
        `📸 ${data.files.length} photo(s) uploadée(s) - le récapitulatif sera généré automatiquement`
      );

      // Reprendre l'enregistrement pour que l'utilisateur puisse continuer à parler
      if (isActive && mediaRecorderRef.current?.stream) {
        setTimeout(() => startRecording(mediaRecorderRef.current.stream), 500);
      }
    } catch (error) {
      console.error("Erreur upload:", error);
      setError(t("chat.upload_error"));
    }
  };

  /**
   * Supprimer un fichier de la liste
   */
  const removeFile = (index) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  /**
   * Créer une demande d'accompagnement
   */
  const createTicket = async (ticketData) => {
    try {
      console.log("Création du ticket avec les données:", ticketData);

      // Préparer la transcription de la conversation
      const transcript = conversationHistory
        .map(
          (msg) =>
            `${msg.role === "user" ? "Client" : "Assistant"}: ${msg.content}`
        )
        .join("\n");

      const response = await fetch(`${API_URL}/api/voice/create-ticket`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_name: ticketData.customer_name,
          problem_description: ticketData.problem_description,
          product: ticketData.product,
          order_number: ticketData.order_number,
          conversation_transcript: transcript,
          photos: ticketData.photos || [], // Inclure les photos
        }),
      });

      if (!response.ok) {
        throw new Error("Erreur de création du ticket");
      }

      const result = await response.json();
      console.log("Ticket créé:", result);

      // Afficher une notification de succès
      return result;
    } catch (err) {
      console.error("Erreur création ticket:", err);
      throw err;
    }
  };

  /**
   * Synthèse vocale et lecture
   */
  const speakAndAddToHistory = async (role, text, isTicketCreated = false) => {
    // Ajouter à l'historique avec marqueur de ticket créé
    addToHistory(role, text, isTicketCreated);

    if (role === "assistant") {
      setIsSpeaking(true);

      try {
        const formData = new FormData();
        formData.append("text", text);
        formData.append("voice", "nova"); // Voix féminine chaleureuse

        const response = await fetch(`${API_URL}/api/voice/speak`, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error(t("voice.error_tts"));
        }

        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);

        // Jouer l'audio
        const audio = new Audio(audioUrl);
        currentAudioRef.current = audio;

        try {
          await audio.play();
          console.log("✅ Audio en cours de lecture");
        } catch (playErr) {
          console.error("❌ Erreur play():", playErr);
          console.warn(
            "⚠️ La lecture audio a échoué, probablement bloquée par le navigateur. Continuons sans audio."
          );
          // Ne pas bloquer le workflow si la lecture audio échoue
          setIsSpeaking(false);
          return; // Sortir de la fonction sans attendre la fin de l'audio
        }

        // Attendre la fin de la lecture
        await new Promise((resolve) => {
          audio.onended = resolve;
        });

        URL.revokeObjectURL(audioUrl);
      } catch (err) {
        console.error("❌ Erreur synthèse vocale complète:", err);
        setError(`Erreur audio: ${err.message}`);
      } finally {
        setIsSpeaking(false);
      }
    }
  };

  /**
   * Ajouter un message à l'historique
   */
  const addToHistory = (role, content, isTicketCreated = false) => {
    setConversationHistory((prev) => [
      ...prev,
      {
        role,
        content,
        timestamp: new Date(),
        isTicketCreated,
        isRecap: content.includes(t("chat.recap_trigger")), // Marquer les récapitulatifs
      },
    ]);
  };

  /**
   * Confirmer et créer le ticket
   */
  const handleConfirmTicket = async () => {
    if (!pendingTicket) return;

    setIsProcessing(true);
    setProcessingStep(t("chat.creating_ticket"));

    try {
      // Créer le ticket avec les photos
      const ticketDataWithPhotos = {
        ...pendingTicket,
        photos: uploadedFiles.map((f) => getAbsoluteUrl(f.url)),
      };
      await createTicket(ticketDataWithPhotos);

      // Message de confirmation
      addToHistory("assistant", t("chat.confirm_ticket_success"), true);

      // Réinitialiser
      setPendingTicket(null);
      setUploadedFiles([]); // Vider les photos après création du ticket

      // Attendre un peu puis terminer automatiquement
      setTimeout(() => {
        stopVoiceChat();
      }, 3000);
    } catch (err) {
      console.error("Erreur création ticket:", err);
      setError("Erreur lors de la création du ticket. Veuillez réessayer.");
    } finally {
      setIsProcessing(false);
      setProcessingStep("");
    }
  };

  /**
   * Annuler et recommencer
   */
  const handleCancelTicket = () => {
    setPendingTicket(null);

    // Message d'annulation
    addToHistory("assistant", t("chat.cancel_restart"));

    // Reprendre l'enregistrement
    if (isActive && mediaRecorderRef.current?.stream) {
      setTimeout(() => startRecording(mediaRecorderRef.current.stream), 500);
    }
  };

  /**
   * Arrêter la conversation
   */
  const stopVoiceChat = () => {
    // Arrêter l'enregistrement
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }

    // Arrêter le micro
    if (mediaRecorderRef.current?.stream) {
      mediaRecorderRef.current.stream
        .getTracks()
        .forEach((track) => track.stop());
    }

    // Arrêter l'audio en cours
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current = null;
    }

    // Nettoyer les timers et animations
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    setIsActive(false);
    setIsRecording(false);
    setIsProcessing(false);
    setIsSpeaking(false);
    setRecordingTime(0);
    setAudioLevels([]);
    setPendingTicket(null);
    setUploadedFiles([]); // Vider les fichiers uploadés
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header - Configuration client: BB Expansion Mobilier de France */}
      <div
        className="text-white p-6 shadow-lg"
        style={{ backgroundColor: "#20253F" }}
      >
        <h1
          className="text-3xl font-bold flex items-center"
          style={{ fontFamily: "Segoe UI, sans-serif" }}
        >
          <Phone className="w-8 h-8 mr-3" />
          {t("chat.header_title")}
        </h1>
        <p className="text-sm opacity-90 mt-1">{t("chat.header_subtitle")}</p>
      </div>

      {/* Message d'état du microphone */}
      {!isActive &&
        conversationHistory.length === 0 &&
        micPermission !== null && (
          <div className="mx-6 mt-4">
            {micPermission === "granted" && (
              <div className="bg-green-50 border-l-4 border-green-500 p-3 rounded-r-lg">
                <p className="text-green-800 text-sm font-semibold flex items-center">
                  <span className="mr-2">✅</span>
                  {t("chat.mic_allowed")}
                </p>
              </div>
            )}
            {micPermission === "denied" && (
              <div className="bg-red-50 border-l-4 border-red-500 p-3 rounded-r-lg">
                <p className="text-red-800 text-sm font-semibold flex items-center">
                  <span className="mr-2">❌</span>
                  {t("chat.mic_blocked")}
                </p>
              </div>
            )}
          </div>
        )}

      {/* Bouton de démarrage - Visible en premier */}
      {!isActive && conversationHistory.length === 0 && (
        <div className="text-center py-6 px-6">
          <button
            onClick={startVoiceChat}
            disabled={micPermission !== "granted"}
            className={`px-10 py-5 rounded-full font-bold text-xl shadow-2xl transition-all transform ${
              micPermission === "granted"
                ? "bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 hover:scale-105 animate-pulse cursor-pointer"
                : "bg-gray-400 cursor-not-allowed opacity-50"
            } text-white`}
          >
            <Phone className="w-7 h-7 inline mr-3" />
            {micPermission === null
              ? t("chat.mic_checking")
              : micPermission === "granted"
              ? t("chat.start_button_start")
              : t("chat.start_button_not_allowed")}
          </button>
          <p className="text-gray-600 mt-3 text-sm">
            {micPermission === "granted"
              ? t("chat.start_helper_granted")
              : micPermission === "denied"
              ? t("chat.start_helper_denied")
              : t("chat.start_helper_checking")}
          </p>
        </div>
      )}

      {/* Messages informatifs simplifiés */}
      {!isActive && (
        <div className="mx-6 mt-2 space-y-4">
          {/* Points importants - Version simplifiée */}
          <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-lg shadow-md">
            <div className="flex items-start">
              <Info className="w-6 h-6 text-amber-600 mr-3 flex-shrink-0 mt-1" />
              <div className="w-full">
                <h3 className="font-bold text-amber-900 mb-3">
                  ⚠️ {t("chat.tips_title")}
                </h3>

                <div className="grid grid-cols-2 gap-3">
                  <div className="text-xs">
                    <p className="text-amber-900 font-semibold">
                      ✓ {t("chat.tips_speak_clearly")}
                    </p>
                    <p className="text-amber-800">
                      {t("chat.tips_speak_clearly_desc")}
                    </p>
                  </div>

                  <div className="text-xs">
                    <p className="text-amber-900 font-semibold">
                      ✓ {t("chat.tips_wait_response")}
                    </p>
                    <p className="text-amber-800">
                      {t("chat.tips_wait_response_desc")}
                    </p>
                  </div>

                  <div className="text-xs">
                    <p className="text-amber-900 font-semibold">
                      ✓ {t("chat.tips_speak_naturally")}
                    </p>
                    <p className="text-amber-800">
                      {t("chat.tips_speak_naturally_desc")}
                    </p>
                  </div>

                  <div className="text-xs">
                    <p className="text-amber-900 font-semibold">
                      ✓ {t("chat.tips_manual_stop")}
                    </p>
                    <p className="text-amber-800">{t("chat.recording_help")}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Guide simplifié */}
          <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-lg shadow-md">
            <div className="flex items-start">
              <Phone className="w-6 h-6 text-green-600 mr-3 flex-shrink-0 mt-1" />
              <div className="w-full">
                <h3 className="font-bold text-green-900 mb-3">
                  📋 {t("chat.example_title")}
                </h3>

                <div className="text-xs space-y-2">
                  <div className="flex items-center">
                    <div className="w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center font-bold mr-2 flex-shrink-0">
                      1
                    </div>
                    <p className="text-gray-700">
                      <strong>{t("chat.example_bot")}</strong> "
                      {t("chat.example_bot_greeting")}"
                    </p>
                  </div>
                  <div className="flex items-center">
                    <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold mr-2 flex-shrink-0">
                      2
                    </div>
                    <p className="text-gray-700">
                      <strong>{t("chat.example_user")}</strong> "
                      {t("chat.example_user_input")}"
                    </p>
                  </div>
                  <div className="flex items-center">
                    <div className="w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center font-bold mr-2 flex-shrink-0">
                      3
                    </div>
                    <p className="text-gray-700">
                      <strong>{t("chat.example_bot")}</strong>{" "}
                      {t("chat.recap_label")} {t("chat.example_bot_recap")}
                    </p>
                  </div>
                  <div className="flex items-center">
                    <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold mr-2 flex-shrink-0">
                      4
                    </div>
                    <p className="text-gray-700">
                      <strong>{t("chat.example_user")}</strong> "
                      {t("chat.example_user_confirm")}"
                    </p>
                  </div>
                  <div className="bg-green-100 p-2 rounded border border-green-400 mt-2">
                    <p className="text-green-900 font-bold text-center">
                      {t("chat.auto_ticket_created")}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Bouton caméra flottant - Visible quand la conversation est active */}
      {isActive && !pendingTicket && (
        <div className="fixed top-24 right-6 z-50">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white p-4 rounded-full shadow-2xl transition-all transform hover:scale-110 flex items-center space-x-2"
            title={t("chat.add_photos")}
          >
            <Camera className="w-6 h-6" />
            <span className="font-medium">{t("chat.add_photos")}</span>
          </button>
          {uploadedFiles.length > 0 && (
            <div className="mt-2 bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full text-center">
              {uploadedFiles.length} photo{uploadedFiles.length > 1 ? "s" : ""}
            </div>
          )}
        </div>
      )}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*,video/*"
        className="hidden"
        onChange={handleFileUpload}
      />

      {/* Aperçu des fichiers uploadés */}
      {uploadedFiles.length > 0 && (
        <div className="mx-6 mt-4 bg-white rounded-xl p-4 shadow-lg border-2 border-blue-500">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm font-bold text-gray-700 flex items-center">
              <Camera className="w-4 h-4 mr-2 text-blue-600" />
              {t("chat.photos_uploaded").replace(
                "{count}",
                String(uploadedFiles.length)
              )}
            </p>
          </div>
          <div className="flex space-x-3 overflow-x-auto pb-2">
            {uploadedFiles.map((file, index) => (
              <div key={index} className="relative group flex-shrink-0">
                <div className="w-24 h-24 rounded-lg overflow-hidden border-2 border-blue-500 shadow-md">
                  {file.type === "jpg" ||
                  file.type === "jpeg" ||
                  file.type === "png" ? (
                    <img
                      src={getAbsoluteUrl(file.url)}
                      alt={file.original_name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gray-200 flex items-center justify-center text-xs">
                      📹 Vidéo
                    </div>
                  )}
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-lg hover:bg-red-600 transition-colors"
                  title={t("chat.delete")}
                >
                  <X className="w-4 h-4" />
                </button>
                <p className="text-xs text-gray-600 mt-1 text-center truncate w-24">
                  {file.original_name}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Zone de conversation */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {/* Messages de conversation */}
        {conversationHistory.map((msg, index) => {
          // Style spécial pour le récapitulatif
          const isRecap = msg.isRecap;
          // Style spécial pour la confirmation de ticket
          const isTicketConfirmation = msg.isTicketCreated;

          return (
            <div
              key={index}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[75%] rounded-2xl p-4 shadow-md ${
                  msg.role === "user"
                    ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white"
                    : isTicketConfirmation
                    ? "bg-gradient-to-r from-green-500 to-emerald-600 text-white border-2 border-green-600"
                    : isRecap
                    ? "bg-gradient-to-r from-amber-50 to-amber-100 text-gray-800 border-2 border-amber-400"
                    : "bg-white text-gray-800 border border-gray-200"
                }`}
              >
                <p className="font-medium mb-1 flex items-center">
                  {msg.role === "user"
                    ? t("chat.user_label")
                    : t("chat.assistant_label")}
                  {isRecap && (
                    <span className="ml-2 text-xs bg-amber-500 text-white px-2 py-1 rounded-full">
                      {t("chat.recap_label")}
                    </span>
                  )}
                  {isTicketConfirmation && (
                    <span className="ml-2 text-xs bg-white text-green-600 px-2 py-1 rounded-full font-bold">
                      {t("chat.ticket_created")}
                    </span>
                  )}
                </p>
                <p className="whitespace-pre-line">{msg.content}</p>
                <p
                  className={`text-xs mt-2 ${
                    isTicketConfirmation || isRecap
                      ? "opacity-80"
                      : "opacity-70"
                  }`}
                >
                  {msg.timestamp.toLocaleTimeString(
                    msg.language === "en"
                      ? "en-US"
                      : msg.language === "ar"
                      ? "ar-SA"
                      : localStorage.getItem("selectedLanguage") === "en"
                      ? "en-US"
                      : localStorage.getItem("selectedLanguage") === "ar"
                      ? "ar-SA"
                      : "fr-FR"
                  )}
                </p>
              </div>
            </div>
          );
        })}

        {/* Boutons de validation du ticket */}
        {pendingTicket && (
          <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-400 rounded-2xl p-6 shadow-xl">
            <h3 className="text-xl font-bold text-amber-900 mb-4 flex items-center">
              <Info className="w-6 h-6 mr-2" />
              {t("chat.validate_prompt")}
            </h3>
            <p className="text-gray-700 mb-6">{t("chat.validate_hint")}</p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={handleConfirmTicket}
                disabled={isProcessing}
                className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-bold py-4 px-8 rounded-xl shadow-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <span className="text-2xl mr-2">✅</span>
                {t("chat.btn_validate")}
              </button>
              <button
                onClick={handleCancelTicket}
                disabled={isProcessing}
                className="bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 text-white font-bold py-4 px-8 rounded-xl shadow-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <span className="text-2xl mr-2">❌</span>
                {t("chat.btn_modify")}
              </button>
            </div>
          </div>
        )}

        {/* Indicateur de statut */}
        {isActive && !pendingTicket && (
          <div className="fixed bottom-24 left-1/2 transform -translate-x-1/2 bg-white rounded-2xl shadow-2xl border-2 border-blue-500">
            <div className="px-6 py-4">
              {isRecording && !isProcessing && (
                <div className="space-y-3">
                  {/* Ligne principale avec icône et temps */}
                  <div className="flex items-center justify-between space-x-3">
                    <div className="flex items-center space-x-3">
                      <Mic className="w-6 h-6 text-red-600 animate-pulse" />
                      <div className="flex items-center space-x-2">
                        <Clock className="w-4 h-4 text-gray-600" />
                        <span className="text-gray-800 font-mono font-bold text-lg">
                          {Math.floor(recordingTime / 60)}:
                          {(recordingTime % 60).toString().padStart(2, "0")}
                        </span>
                        <span className="text-gray-500 text-sm">/ 0:30</span>
                      </div>
                      <span className="text-red-600 font-semibold ml-2">
                        {t("chat.recording_label")}
                      </span>
                    </div>

                    {/* Bouton d'arrêt manuel */}
                    <button
                      onClick={() => {
                        if (mediaRecorderRef.current?.state === "recording") {
                          mediaRecorderRef.current.stop();
                          setIsRecording(false);
                        }
                      }}
                      className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-semibold text-sm transition-all shadow-lg hover:scale-105"
                    >
                      ⏹ {t("chat.stop_button")}
                    </button>
                  </div>

                  {/* Visualisation des ondes sonores en temps réel */}
                  <div className="flex items-center justify-center space-x-0.5 h-12 bg-gradient-to-r from-red-50 to-pink-50 rounded-lg px-3">
                    {(audioLevels.length > 0
                      ? audioLevels
                      : Array(40).fill(5)
                    ).map((level, i) => {
                      const normalizedHeight = Math.min(
                        Math.max((level / 128) * 100, 5),
                        100
                      );
                      return (
                        <div
                          key={i}
                          className="w-1 bg-gradient-to-t from-red-600 to-pink-400 rounded-full transition-all duration-75"
                          style={{
                            height: `${normalizedHeight}%`,
                            opacity: 0.7 + (normalizedHeight / 100) * 0.3,
                          }}
                        />
                      );
                    })}
                  </div>

                  {/* Message d'aide */}
                  <p className="text-xs text-gray-500 text-center">
                    {t("chat.recording_help")}
                  </p>
                </div>
              )}

              {isProcessing && (
                <div className="flex items-center space-x-3 py-1">
                  <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
                  <span className="text-blue-600 font-semibold">
                    {processingStep}
                  </span>
                </div>
              )}

              {isSpeaking && (
                <div className="flex items-center space-x-3 py-1">
                  <Volume2 className="w-6 h-6 text-green-600 animate-pulse" />
                  <span className="text-green-600 font-semibold">
                    {t("chat.speaking_label")}
                  </span>
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

      {/* Bouton terminer */}
      {isActive && (
        <div className="p-6 bg-white border-t border-gray-200">
          <button
            onClick={stopVoiceChat}
            className="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-4 rounded-full shadow-lg transition-all transform hover:scale-105 flex items-center justify-center"
          >
            <PhoneOff className="w-6 h-6 mr-2" />
            {t("chat.end_conversation")}
          </button>
        </div>
      )}
    </div>
  );
};

export default VoiceChatWhisper;
