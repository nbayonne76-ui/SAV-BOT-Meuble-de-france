// frontend/src/components/ChatInterface.jsx
import { useState, useEffect, useRef } from "react";
import {
  Send,
  Mic,
  X,
  Loader2,
} from "lucide-react";
import { useLanguage } from "../context/LanguageContext";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [sessionId] = useState(`session-${Date.now()}`);
  const [isInputFocused, setIsInputFocused] = useState(false);
  const { language, t } = useLanguage();
  const selectedLanguage = language;
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Message d'accueil (i18n)
  useEffect(() => {
    const welcomeMessage = t("chat.welcome.long");

    setMessages([
      {
        role: "assistant",
        content: welcomeMessage,
        timestamp: new Date(),
      },
    ]);
  }, [selectedLanguage]);

  // Auto-scroll vers le bas
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Helper to build absolute URLs for files (handles absolute, protocol-missing, and relative paths)
  const getAbsoluteUrl = (rawUrl) => {
    if (!rawUrl) return "";
    const url = String(rawUrl).trim();

    // Protocol-relative (e.g., //res.cloudinary.com/...) -> prefix https:
    if (url.startsWith("//")) {
      console.warn("Normalizing protocol-relative URL:", url);
      return `https:${url}`;
    }

    // Already well-formed (http:// or https://)
    if (/^https?:\/\//i.test(url)) return url;

    // Malformed but starts with 'https//' or 'http//' (missing colon) -> fix
    if (/^https?\/\//i.test(url)) {
      const fixed = url.replace(/^(https?)(\/\/)/i, "$1://");
      console.warn("Fixed malformed URL (missing colon):", url, "->", fixed);
      return fixed;
    }

    // Starts with 'http' but missing '://', try to insert it
    if (/^https?/i.test(url) && !url.includes("://")) {
      const fixed = url.replace(/^([a-z]+)(.*)/i, "$1://$2");
      console.warn("Fixed malformed URL (missing ://):", url, "->", fixed);
      return fixed;
    }

    // Relative path starting with '/'
    if (url.startsWith("/")) return `${API_URL}${url}`;

    // Otherwise assume relative resource path
    return `${API_URL}/${url}`;
  };

  // 🎯 Fonction pour valider un ticket
  const handleValidateTicket = async (ticketId) => {
    try {
      const response = await fetch(
        `${API_URL}/api/chat/validate/${ticketId}?language=${selectedLanguage}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }
      );

      // Attempt to parse body regardless of status for better error messages
      const responseBody = await response.json().catch(() => null);

      if (!response.ok) {
        console.error(
          "Validation error response:",
          response.status,
          responseBody
        );
        const serverMsg =
          responseBody?.detail ||
          responseBody?.error ||
          responseBody?.message ||
          t("chat.error_ticket_validation");
        alert(serverMsg);
        return;
      }

      const data = responseBody;

      // Afficher le message de confirmation
      const confirmationMessage = {
        role: "assistant",
        content: data.response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, confirmationMessage]);
    } catch (error) {
      console.error("Erreur validation ticket:", error);
      alert(t("chat.error_ticket_validation"));
    }
  };

  // 🎯 Fonction pour annuler/modifier un ticket
  const handleCancelTicket = async (ticketId) => {
    try {
      const response = await fetch(
        `${API_URL}/api/chat/cancel/${ticketId}?language=${selectedLanguage}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }
      );

      // Attempt to parse body regardless of status for better error messages
      const responseBody = await response.json().catch(() => null);

      if (!response.ok) {
        console.error("Cancel error response:", response.status, responseBody);
        const serverMsg =
          responseBody?.detail ||
          responseBody?.error ||
          responseBody?.message ||
          t("chat.error_ticket_cancel");
        alert(serverMsg);
        return;
      }

      const data = responseBody;

      // Afficher le message de réinitialisation
      const resetMessage = {
        role: "assistant",
        content: data.response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, resetMessage]);
    } catch (error) {
      console.error("Erreur annulation ticket:", error);
      alert(t("chat.error_ticket_cancel"));
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() && uploadedFiles.length === 0) return;

    // Ajouter message utilisateur
    const userMessage = {
      role: "user",
      content: inputMessage,
      language: selectedLanguage,
      files: uploadedFiles.length > 0 ? uploadedFiles : null,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    const currentFiles = [...uploadedFiles];
    setUploadedFiles([]);
    setIsTyping(true);

    try {
      // Appel API backend (envoi de la langue sélectionnée)
      const response = await fetch(`${API_URL}/api/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: inputMessage,
          session_id: sessionId,
          photos: currentFiles.map((f) => getAbsoluteUrl(f.url)),
          language: selectedLanguage,
        }),
      });

      if (!response.ok) {
        throw new Error("Erreur réseau");
      }

      const data = await response.json();

      // 🎯 NOUVEAU: Gérer la clôture de conversation
      if (data.should_close_session) {
        // Afficher message d'au revoir
        const goodbyeMessage = {
          role: "assistant",
          content: data.response,
          language: data.language,
          conversation_type: data.conversation_type,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, goodbyeMessage]);
        setIsTyping(false);

        // Attendre 3 secondes puis effacer la conversation
        setTimeout(async () => {
          console.log(
            "👋 Clôture de la conversation - Effacement des messages"
          );
          setMessages([]);

          // Appeler l'endpoint de suppression de session
          try {
            await fetch(`${API_URL}/api/chat/${sessionId}`, {
              method: "DELETE",
            });
            console.log("✅ Session backend supprimée");
          } catch (error) {
            console.error("❌ Erreur suppression session:", error);
          }

          // Réafficher le message d'accueil après 500ms
          setTimeout(() => {
            const welcomeMessagesReset = {
              fr: t("chat.welcome_message_reset"),
              en: t("chat.welcome_message_reset"),
              ar: t("chat.welcome_message_reset"),
            };
            const welcomeMessage =
              welcomeMessagesReset[selectedLanguage] || welcomeMessagesReset.fr;

            setMessages([
              {
                role: "assistant",
                content: welcomeMessage,
                timestamp: new Date(),
              },
            ]);
          }, 500);
        }, 3000);

        return; // Arrêter le traitement ici
      }

      // Ajouter réponse assistant (traitement normal si pas de clôture)
      const assistantMessage = {
        role: "assistant",
        content: data.response,
        language: data.language,
        conversation_type: data.conversation_type,
        timestamp: new Date(),
        // 🎯 NOUVEAU: Ajouter les infos de validation
        requires_validation: data.requires_validation,
        ticket_id: data.ticket_id,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Erreur:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: t("chat.error_problem"),
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    // Validate files
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

    // Upload files
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
    } catch (error) {
      console.error("Erreur upload:", error);
      alert(t("chat.upload_error"));
    }
  };

  const removeFile = (index) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div
      className="flex flex-col h-full"
      style={{
        backgroundColor: "#f5f5f5",
      }}
    >
      {/* Header avec logo Mobilier de France - Fond bleu fonce */}
      <div className="py-6 px-6" style={{ backgroundColor: "#20253F" }}>
        <div className="flex items-center justify-center gap-2">
          {/* Logo MF stylise en SVG */}
          <svg
            width="50"
            height="40"
            viewBox="0 0 50 40"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="flex-shrink-0"
          >
            {/* M stylise */}
            <path
              d="M2 38V8L14 24L26 8V38"
              stroke="white"
              strokeWidth="3"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            {/* F stylise */}
            <path
              d="M32 38V8H48M32 22H44"
              stroke="white"
              strokeWidth="3"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <span className="text-white text-xl font-light tracking-wide">Mobilier de France</span>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* SUIVI CLIENTELE - Centré exactement au milieu de la page */}
        <div
          className="absolute flex flex-col items-center justify-center"
          style={{
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)',
          }}
        >
          <h2
            className="text-lg font-semibold tracking-wide mb-2 underline"
            style={{ color: "#20253F" }}
          >
            SUIVI CLIENTELE
          </h2>
          <a
            href="#"
            className="text-sm underline hover:no-underline"
            style={{ color: "#20253F" }}
            onClick={(e) => {
              e.preventDefault();
              // Navigate to voice interface
              window.location.href = '/voice';
            }}
          >
            Interface vocale dynamique
          </a>
        </div>

        {/* Right Section - Chat Messages (40% de largeur, poussé à droite) */}
        <div className="w-2/5 ml-auto flex flex-col p-4 pr-6">
          <div className="flex-1 overflow-y-auto space-y-3">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                } fade-in`}
              >
                <div
                  className={`max-w-[85%] rounded-lg p-4 ${
                    msg.role === "user"
                      ? "text-white"
                      : "text-white"
                  }`}
                  style={{ backgroundColor: "#20253F" }}
                >
                  <p className="whitespace-pre-line leading-relaxed text-sm">
                    {msg.content}
                  </p>

                  {/* Files attachées */}
                  {msg.files && msg.files.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {msg.files.map((file, idx) => (
                        <div key={idx} className="relative group">
                          {file.type === "jpg" ||
                          file.type === "jpeg" ||
                          file.type === "png" ? (
                            <img
                              src={getAbsoluteUrl(file.url)}
                              alt={file.original_name}
                              className="w-20 h-20 object-cover rounded-lg border-2 border-white/30"
                            />
                          ) : (
                            <div className="w-20 h-20 bg-gray-700 rounded-lg flex items-center justify-center text-xs text-gray-300">
                              {t("chat.file_video_label")}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Boutons de validation */}
                  {msg.role === "assistant" &&
                    msg.requires_validation &&
                    msg.ticket_id && (
                      <div className="mt-4 pt-4 border-t border-white/20">
                        <p className="text-sm font-semibold text-white/90 mb-3">
                          {t("chat.validate_prompt")}
                        </p>
                        <div className="flex gap-3">
                          <button
                            onClick={() => handleValidateTicket(msg.ticket_id)}
                            className="flex-1 bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-lg transition-all"
                          >
                            {t("chat.btn_validate")}
                          </button>
                          <button
                            onClick={() => handleCancelTicket(msg.ticket_id)}
                            className="flex-1 bg-orange-500 hover:bg-orange-600 text-white font-bold py-2 px-4 rounded-lg transition-all"
                          >
                            {t("chat.btn_modify")}
                          </button>
                        </div>
                      </div>
                    )}
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {isTyping && (
              <div className="flex justify-start fade-in">
                <div
                  className="rounded-lg p-4 text-white"
                  style={{ backgroundColor: "#20253F" }}
                >
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-white rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-white rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Uploaded Files Preview */}
      {uploadedFiles.length > 0 && (
        <div className="px-6 py-3 bg-white border-t border-gray-200">
          <p className="text-sm text-gray-600 mb-2 font-medium">
            {t("chat.files_to_send").replace("{count}", uploadedFiles.length)}
          </p>
          <div className="flex space-x-2 overflow-x-auto pb-2">
            {uploadedFiles.map((file, index) => (
              <div key={index} className="relative group flex-shrink-0">
                <div className="w-16 h-16 rounded-lg overflow-hidden border-2 border-gray-300">
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
                      Video
                    </div>
                  )}
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-lg hover:bg-red-600 transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input Area - Style comme la capture d'écran */}
      <div className="bg-white p-4 border-t border-gray-200">
        <div className="flex items-center space-x-3 max-w-4xl mx-auto">
          {/* Camera Button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="text-gray-400 hover:text-gray-600 p-2 transition-colors flex-shrink-0"
            title={t("chat.add_photos")}
          >
            <Mic className="w-6 h-6" />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*,video/*"
            className="hidden"
            onChange={handleFileUpload}
          />

          {/* Message Input - Gris qui devient bleu au focus */}
          <div className="flex-1">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              onFocus={() => setIsInputFocused(true)}
              onBlur={() => setIsInputFocused(false)}
              placeholder="Si vous preferez l'ecrit : n° de commande + Nom client + Description de votre attente"
              className={`w-full border rounded-full px-5 py-3 focus:outline-none transition-colors text-sm ${
                isInputFocused
                  ? "border-blue-500 text-blue-600"
                  : "border-gray-300 text-gray-500"
              }`}
            />
          </div>

          {/* Send Button (hidden when empty) */}
          {(inputMessage.trim() || uploadedFiles.length > 0) && (
            <button
              onClick={sendMessage}
              className="p-2 rounded-full flex-shrink-0 transition-all text-white"
              style={{ backgroundColor: "#20253F" }}
            >
              {isTyping ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
