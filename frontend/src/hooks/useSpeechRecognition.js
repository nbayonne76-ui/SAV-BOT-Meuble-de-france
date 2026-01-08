import { useState, useRef, useEffect, useCallback } from "react";
import { useLanguage } from "../context/LanguageContext";

export const useSpeechRecognition = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [transcript, setTranscript] = useState("");
  const recognitionRef = useRef(null);
  const isActiveRef = useRef(false);

  const { language } = useLanguage();

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setIsSupported(false);
      return;
    }

    setIsSupported(true);
    const recognition = new SpeechRecognition();
    const selectedLang =
      language || localStorage.getItem("selectedLanguage") || "fr";
    const locale =
      selectedLang === "en"
        ? "en-US"
        : selectedLang === "ar"
        ? "ar-SA"
        : "fr-FR";
    recognition.lang = locale;
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      let interimTranscript = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPiece = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcriptPiece + " ";
        } else {
          interimTranscript += transcriptPiece;
        }
      }

      if (interimTranscript) {
        setTranscript(interimTranscript);
      }

      if (finalTranscript && recognition.onfinal) {
        recognition.onfinal(finalTranscript);
        setTranscript("");
      }
    };

    recognition.onerror = (event) => {
      if (event.error !== "no-speech" && event.error !== "aborted") {
        console.error("Speech recognition error:", event.error);
      }
      isActiveRef.current = false;
      setIsRecording(false);
      setTranscript("");
    };

    recognition.onend = () => {
      if (isActiveRef.current && isRecording) {
        try {
          recognition.start();
        } catch (error) {
          isActiveRef.current = false;
          setIsRecording(false);
        }
      } else {
        isActiveRef.current = false;
        setIsRecording(false);
        setTranscript("");
      }
    };

    recognition.onstart = () => {
      isActiveRef.current = true;
      setIsRecording(true);
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (error) {
          console.log("Cleanup error:", error);
        }
      }
    };
  }, [isRecording, language]);

  const start = useCallback(
    (onFinal) => {
      if (!recognitionRef.current || !isSupported) return false;

      if (recognitionRef.current.onfinal) {
        recognitionRef.current.onfinal = onFinal;
      }

      try {
        isActiveRef.current = true;
        recognitionRef.current.start();
        return true;
      } catch (error) {
        console.error("Failed to start recognition:", error);
        return false;
      }
    },
    [isSupported]
  );

  const stop = useCallback(() => {
    if (!recognitionRef.current) return;

    try {
      isActiveRef.current = false;
      recognitionRef.current.stop();
      setIsRecording(false);
      setTranscript("");
    } catch (error) {
      console.error("Failed to stop recognition:", error);
    }
  }, []);

  return {
    isRecording,
    isSupported,
    transcript,
    start,
    stop,
  };
};
