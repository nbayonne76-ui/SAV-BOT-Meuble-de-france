import React, { createContext, useContext, useState, useEffect } from "react";
import translations, { supportedLanguages } from "../i18n/translations";

const LanguageContext = createContext(null);

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    try {
      if (typeof window !== "undefined") {
        return localStorage.getItem("selectedLanguage") || "fr";
      }
    } catch (e) {
      // localStorage not available (SSR), default to 'fr'
    }
    return "fr";
  });

  useEffect(() => {
    try {
      if (typeof window !== "undefined") {
        localStorage.setItem("selectedLanguage", language);
      }
    } catch (e) {
      // ignore (localStorage unavailable)
    }
  }, [language]);

  const t = (key) => {
    const parts = key.split(".");
    let node = translations[language] || translations["fr"];
    for (const p of parts) {
      if (node && node[p] !== undefined) {
        node = node[p];
      } else {
        return key; // fallback to key if missing
      }
    }
    return node;
  };

  return (
    <LanguageContext.Provider
      value={{ language, setLanguage, t, languages: supportedLanguages }}
    >
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
};
