export const formatDate = (dateStr) => {
  try {
    const lang = localStorage.getItem("selectedLanguage") || "fr";
    const locale = lang === "en" ? "en-US" : lang === "ar" ? "ar-SA" : "fr-FR";
    return new Date(dateStr).toLocaleString(locale, {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch (e) {
    return dateStr;
  }
};

export const formatTime = (timestamp) => {
  const lang = localStorage.getItem("selectedLanguage") || "fr";
  const locale = lang === "en" ? "en-US" : lang === "ar" ? "ar-SA" : "fr-FR";
  return timestamp.toLocaleTimeString(locale, {
    hour: "2-digit",
    minute: "2-digit",
  });
};

export const getPriorityColor = (priority) => {
  const colors = {
    P0: "bg-red-100 text-red-800 border-red-300",
    P1: "bg-orange-100 text-orange-800 border-orange-300",
    P2: "bg-yellow-100 text-yellow-800 border-yellow-300",
    P3: "bg-green-100 text-green-800 border-green-300",
    UNKNOWN: "bg-gray-100 text-gray-600 border-gray-400",
  };
  return colors[priority] || "bg-gray-100 text-gray-800 border-gray-300";
};

export const getStatusLabel = (status) => {
  const labels = {
    escalated_to_human: "Escaladé",
    awaiting_technician: "En attente technicien",
    auto_resolved: "Résolu auto",
    evidence_collection: "Collecte preuves",
    pending: "En attente",
    unknown: "Statut inconnu",
  };
  return labels[status] || status;
};
