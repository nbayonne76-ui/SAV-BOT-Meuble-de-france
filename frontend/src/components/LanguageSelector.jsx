import { useLanguage } from "../context/LanguageContext";

function LanguageSelector() {
  const { language, setLanguage, t, languages } = useLanguage();
  const selectedLanguage = language;

  return (
    <>
      <select
        value={selectedLanguage}
        onChange={(e) => {
          setLanguage(e.target.value);
        }}
        className="ml-auto text-white bg-transparent text-sm font-medium rounded px-3 py-2 border-0 cursor-pointer transition-all duration-200 hover:opacity-80"
        title={t("chat.language_label")}
      >
        {Object.entries(languages).map(([k, v]) => (
          <option
            key={k}
            value={k}
            style={{
              backgroundColor: "#2d3748",
              color: "white",
            }}
          >
            {v.label}
          </option>
        ))}
      </select>
    </>
  );
}

export default LanguageSelector;
