import { useState, useRef, useEffect, useCallback } from "react";
import { useLanguage } from "../context/LanguageContext";

export const useSpeechSynthesis = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isEnabled, setIsEnabled] = useState(true);
  const synthRef = useRef(null);
  const { language } = useLanguage();

  useEffect(() => {
    if ("speechSynthesis" in window) {
      synthRef.current = window.speechSynthesis;
    }

    return () => {
      if (synthRef.current) {
        synthRef.current.cancel();
      }
    };
  }, []);

  const speak = useCallback(
    (text) => {
      if (!synthRef.current || !isEnabled || !text) return Promise.resolve();

      return new Promise((resolve, reject) => {
        synthRef.current.cancel();

        const cleanText = text
          .replace(/[#*_`]/g, "")
          .replace(/\*\*/g, "")
          .replace(/\n\n/g, ". ")
          .replace(/\n/g, " ")
          .replace(/[🎯📋⚡🔒🛡️🎤]/g, "")
          .trim();

        const utterance = new SpeechSynthesisUtterance(cleanText);
        const selectedLang =
          language || localStorage.getItem("selectedLanguage") || "fr";
        const locale =
          selectedLang === "en"
            ? "en-US"
            : selectedLang === "ar"
            ? "ar-SA"
            : "fr-FR";
        utterance.lang = locale;
        utterance.rate = 1.1;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        const voices = synthRef.current.getVoices();
        const languageShort =
          selectedLang === "en" ? "en" : selectedLang === "ar" ? "ar" : "fr";
        const matchedVoice = voices.find(
          (voice) => voice.lang && voice.lang.startsWith(languageShort)
        );
        if (matchedVoice) {
          utterance.voice = matchedVoice;
        }

        utterance.onstart = () => setIsSpeaking(true);
        utterance.onend = () => {
          setIsSpeaking(false);
          resolve();
        };
        utterance.onerror = (error) => {
          if (error.error !== "interrupted") {
            console.error("Speech synthesis error:", error);
          }
          setIsSpeaking(false);
          reject(error);
        };

        synthRef.current.speak(utterance);
      });
    },
    [isEnabled]
  );

  const stop = useCallback(() => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
    }
  }, []);

  const toggle = useCallback(() => {
    if (isSpeaking) {
      stop();
    }
    setIsEnabled((prev) => !prev);
  }, [isSpeaking, stop]);

  return {
    isSpeaking,
    isEnabled,
    speak,
    stop,
    toggle,
  };
};
