// frontend/src/components/Dashboard.jsx
import { useState, useEffect } from "react";
import {
  FileText,
  Download,
  Eye,
  AlertCircle,
  Clock,
  CheckCircle,
  XCircle,
  Filter,
  RefreshCw,
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

import { useLanguage } from "../context/LanguageContext";

const Dashboard = () => {
  const { t } = useLanguage();
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterPriority, setFilterPriority] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [dossier, setDossier] = useState(null);

  // Charger tous les tickets
  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log("🔄 Fetching tickets from:", `${API_URL}/api/sav/tickets`);

      const response = await fetch(`${API_URL}/api/sav/tickets`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      });

      console.log("📡 Response status:", response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log("✅ Tickets received:", data);

      if (data.success) {
        setTickets(data.tickets || []);
        setError(null);
      } else {
        setError("Erreur lors du chargement des tickets");
      }
    } catch (err) {
      console.error("❌ Error:", err);
      setError(`Erreur de connexion: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchDossier = async (ticketId) => {
    try {
      const response = await fetch(
        `${API_URL}/api/sav/ticket/${ticketId}/dossier`
      );
      const data = await response.json();

      if (data.success) {
        setDossier(data.dossier);
        setSelectedTicket(ticketId);
      }
    } catch (err) {
      console.error("Erreur:", err);
      alert("Erreur lors du chargement du dossier");
    }
  };

  const downloadDossier = (ticket) => {
    const dataStr = JSON.stringify(dossier, null, 2);
    const dataUri =
      "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);
    const exportFileDefaultName = `dossier_${ticket.ticket_id}.json`;
    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
  };

  // Filtrer les tickets
  const filteredTickets = tickets.filter((ticket) => {
    if (filterPriority !== "all" && ticket.priority !== filterPriority)
      return false;
    if (filterStatus !== "all" && ticket.status !== filterStatus) return false;
    return true;
  });

  // Statistiques
  const stats = {
    total: tickets.length,
    p0: tickets.filter((t) => t.priority === "P0").length,
    p1: tickets.filter((t) => t.priority === "P1").length,
    p2: tickets.filter((t) => t.priority === "P2").length,
    p3: tickets.filter((t) => t.priority === "P3").length,
    autoResolved: tickets.filter((t) => t.auto_resolved).length,
    escalated: tickets.filter((t) => t.status === "escalated_to_human").length,
    awaitingTech: tickets.filter((t) => t.status === "awaiting_technician")
      .length,
  };

  const getPriorityColor = (priority) => {
    const colors = {
      P0: "bg-red-100 text-red-800 border-red-300",
      P1: "bg-orange-100 text-orange-800 border-orange-300",
      P2: "bg-yellow-100 text-yellow-800 border-yellow-300",
      P3: "bg-green-100 text-green-800 border-green-300",
    };
    return colors[priority] || "bg-gray-100 text-gray-800 border-gray-300";
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "escalated_to_human":
        return <AlertCircle className="w-4 h-4 text-orange-600" />;
      case "awaiting_technician":
        return <Clock className="w-4 h-4 text-blue-600" />;
      case "auto_resolved":
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case "evidence_collection":
        return <FileText className="w-4 h-4 text-purple-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusLabel = (status) => {
    const labels = {
      escalated_to_human: "Escaladé",
      awaiting_technician: "En attente technicien",
      auto_resolved: "Résolu auto",
      evidence_collection: "Collecte preuves",
      pending: "En attente",
    };
    return labels[status] || status;
  };

  const formatDate = (dateStr) => {
    try {
      const lang = localStorage.getItem("selectedLanguage") || "fr";
      const locale =
        lang === "en" ? "en-US" : lang === "ar" ? "ar-SA" : "fr-FR";
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">
            Chargement des demandes d'accompagnement...
          </p>
          <p className="text-xs text-gray-400 mt-2">
            {API_URL}/api/sav/tickets
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center max-w-md">
          <XCircle className="w-16 h-16 mx-auto mb-4 text-red-600" />
          <p className="text-xl font-semibold text-red-600 mb-2">
            Erreur de connexion
          </p>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="bg-gray-100 p-4 rounded-lg mb-4 text-left">
            <p className="text-xs text-gray-600 mb-1">
              <strong>URL API:</strong>
            </p>
            <p className="text-xs font-mono text-gray-800 break-all">
              {API_URL}/api/sav/tickets
            </p>
          </div>
          <button
            onClick={fetchTickets}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center space-x-2 mx-auto"
          >
            <RefreshCw className="w-5 h-5" />
            <span>Réessayer</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white p-6 shadow-lg">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">{t("dashboard.title")}</h1>
            <p className="text-sm opacity-90 mt-1">
              Gestion centralisée des demandes de la clientèle groupe Mobilier
              de France
            </p>
          </div>
          <button
            onClick={fetchTickets}
            className="flex items-center space-x-2 px-4 py-2 bg-white text-red-600 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>{t("dashboard.refresh")}</span>
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* Statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="text-sm text-gray-600">Total Tickets</div>
            <div className="text-3xl font-bold text-gray-800">
              {stats.total}
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-red-500">
            <div className="text-sm text-gray-600">Critiques (P0)</div>
            <div className="text-3xl font-bold text-red-600">{stats.p0}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-orange-500">
            <div className="text-sm text-gray-600">Urgents (P1)</div>
            <div className="text-3xl font-bold text-orange-600">{stats.p1}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-green-500">
            <div className="text-sm text-gray-600">Auto-résolus</div>
            <div className="text-3xl font-bold text-green-600">
              {stats.autoResolved}
            </div>
          </div>
        </div>

        {/* Filtres */}
        <div className="bg-white p-4 rounded-lg shadow-md mb-6">
          <div className="flex items-center space-x-4">
            <Filter className="w-5 h-5 text-gray-600" />
            <div className="flex-1 flex space-x-4">
              <div>
                <label className="text-sm text-gray-600 mr-2">
                  {t("dashboard.filters.priority")}
                </label>
                <select
                  value={filterPriority}
                  onChange={(e) => setFilterPriority(e.target.value)}
                  className="border border-gray-300 rounded px-3 py-1"
                >
                  <option value="all">Toutes</option>
                  <option value="P0">P0 - Critique</option>
                  <option value="P1">P1 - Urgent</option>
                  <option value="P2">P2 - Modéré</option>
                  <option value="P3">P3 - Faible</option>
                </select>
              </div>
              <div>
                <label className="text-sm text-gray-600 mr-2">
                  {t("dashboard.filters.status")}
                </label>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="border border-gray-300 rounded px-3 py-1"
                >
                  <option value="all">Tous</option>
                  <option value="escalated_to_human">Escaladés</option>
                  <option value="awaiting_technician">
                    En attente technicien
                  </option>
                  <option value="auto_resolved">Auto-résolus</option>
                  <option value="evidence_collection">Collecte preuves</option>
                </select>
              </div>
            </div>
            <div className="text-sm text-gray-600">
              {filteredTickets.length} ticket(s)
            </div>
          </div>
        </div>

        {/* Liste des tickets */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {filteredTickets.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-xl font-semibold mb-2">
                Aucune demande trouvée
              </p>
              <p className="text-sm">
                Créez votre première demande via le Bot Accompagnement (Texte)
                ou le Mode Vocal
              </p>
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Ticket
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Client
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Problème
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Priorité
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Ton
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Statut
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredTickets.map((ticket) => (
                  <tr key={ticket.ticket_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {ticket.ticket_id}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      <div>{ticket.customer_name || "Client"}</div>
                      <div className="text-xs text-gray-400">
                        {ticket.order_number}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      <div className="font-medium">{ticket.product_name}</div>
                      <div className="text-xs text-gray-400 truncate max-w-xs">
                        {ticket.problem_description}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full border ${getPriorityColor(
                          ticket.priority
                        )}`}
                      >
                        {ticket.priority}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {ticket.tone ? (
                        <div className="flex items-center space-x-1">
                          <div
                            className={`w-2 h-2 rounded-full ${
                              ticket.urgency === "critical"
                                ? "bg-red-500"
                                : ticket.urgency === "high"
                                ? "bg-orange-500"
                                : ticket.urgency === "medium"
                                ? "bg-yellow-500"
                                : "bg-green-500"
                            }`}
                          ></div>
                          <span className="text-xs text-gray-600 uppercase">
                            {ticket.tone}
                          </span>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(ticket.status)}
                        <span className="text-xs text-gray-600">
                          {getStatusLabel(ticket.status)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {formatDate(ticket.created_at)}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <button
                        onClick={() => fetchDossier(ticket.ticket_id)}
                        className="text-blue-600 hover:text-blue-800 mr-3"
                        title="Voir le dossier"
                      >
                        <Eye className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Modal Dossier */}
      {selectedTicket && dossier && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white p-4 flex justify-between items-center">
              <h2 className="text-xl font-bold">
                📄 Dossier Clientèle - {selectedTicket}
              </h2>
              <div className="flex space-x-2">
                <button
                  onClick={() =>
                    downloadDossier(
                      tickets.find((t) => t.ticket_id === selectedTicket)
                    )
                  }
                  className="bg-white text-red-600 px-4 py-2 rounded hover:bg-gray-100 flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>Télécharger JSON</span>
                </button>
                <button
                  onClick={() => {
                    setSelectedTicket(null);
                    setDossier(null);
                  }}
                  className="bg-white text-red-600 px-4 py-2 rounded hover:bg-gray-100"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
              <pre className="bg-gray-50 p-4 rounded-lg text-xs overflow-x-auto">
                {JSON.stringify(dossier, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;

// import { useState, useEffect, useMemo, useCallback } from "react";
// import { FileText, Download, XCircle, Filter, RefreshCw } from "lucide-react";
// import { API_URL } from "../utils/url";
// import TicketRow from "./TicketRow";

// const Dashboard = () => {
//   const [tickets, setTickets] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);
//   const [filterPriority, setFilterPriority] = useState("all");
//   const [filterStatus, setFilterStatus] = useState("all");
//   const [selectedTicket, setSelectedTicket] = useState(null);
//   const [dossier, setDossier] = useState(null);

//   useEffect(() => {
//     fetchTickets();
//   }, []);

//   const fetchTickets = useCallback(async () => {
//     try {
//       setLoading(true);
//       setError(null);

//       const response = await fetch(`${API_URL}/api/sav/tickets`, {
//         method: "GET",
//         headers: {
//           Accept: "application/json",
//           "Content-Type": "application/json",
//         },
//       });

//       if (!response.ok) {
//         throw new Error(`HTTP ${response.status}: ${response.statusText}`);
//       }

//       const data = await response.json();

//       if (data.success) {
//         setTickets(data.tickets || []);
//         setError(null);
//       } else {
//         setError("Erreur lors du chargement des tickets");
//       }
//     } catch (err) {
//       console.error("Error:", err);
//       setError(`Erreur de connexion: ${err.message}`);
//     } finally {
//       setLoading(false);
//     }
//   }, []);

//   const fetchDossier = useCallback(async (ticketId) => {
//     try {
//       const response = await fetch(
//         `${API_URL}/api/sav/ticket/${ticketId}/dossier`
//       );
//       const data = await response.json();

//       if (data.success) {
//         setDossier(data.dossier);
//         setSelectedTicket(ticketId);
//       }
//     } catch (err) {
//       console.error("Erreur:", err);
//       alert("Erreur lors du chargement du dossier");
//     }
//   }, []);

//   const downloadDossier = useCallback(() => {
//     if (!dossier) return;
//     const dataStr = JSON.stringify(dossier, null, 2);
//     const dataUri =
//       "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);
//     const exportFileDefaultName = `dossier_${selectedTicket}.json`;
//     const linkElement = document.createElement("a");
//     linkElement.setAttribute("href", dataUri);
//     linkElement.setAttribute("download", exportFileDefaultName);
//     linkElement.click();
//   }, [dossier, selectedTicket]);

//   const closeModal = useCallback(() => {
//     setSelectedTicket(null);
//     setDossier(null);
//   }, []);

//   const filteredTickets = useMemo(() => {
//     return tickets.filter((ticket) => {
//       if (filterPriority !== "all" && ticket.priority !== filterPriority)
//         return false;
//       if (filterStatus !== "all" && ticket.status !== filterStatus)
//         return false;
//       return true;
//     });
//   }, [tickets, filterPriority, filterStatus]);

//   const stats = useMemo(() => {
//     return {
//       total: tickets.length,
//       p0: tickets.filter((t) => t.priority === "P0").length,
//       p1: tickets.filter((t) => t.priority === "P1").length,
//       p2: tickets.filter((t) => t.priority === "P2").length,
//       p3: tickets.filter((t) => t.priority === "P3").length,
//       autoResolved: tickets.filter((t) => t.auto_resolved).length,
//       escalated: tickets.filter((t) => t.status === "escalated_to_human")
//         .length,
//       awaitingTech: tickets.filter((t) => t.status === "awaiting_technician")
//         .length,
//     };
//   }, [tickets]);

//   if (loading) {
//     return (
//       <div className="flex items-center justify-center h-screen bg-gray-50">
//         <div className="text-center">
//           <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-red-600 mx-auto mb-4"></div>
//           <p className="text-gray-600">
//             Chargement des demandes d'accompagnement...
//           </p>
//         </div>
//       </div>
//     );
//   }

//   if (error) {
//     return (
//       <div className="flex items-center justify-center h-screen bg-gray-50">
//         <div className="text-center max-w-md">
//           <XCircle className="w-16 h-16 mx-auto mb-4 text-red-600" />
//           <p className="text-xl font-semibold text-red-600 mb-2">
//             Erreur de connexion
//           </p>
//           <p className="text-gray-600 mb-4">{error}</p>
//           <button
//             onClick={fetchTickets}
//             className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center space-x-2 mx-auto"
//           >
//             <RefreshCw className="w-5 h-5" />
//             <span>Réessayer</span>
//           </button>
//         </div>
//       </div>
//     );
//   }

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
//       <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white p-6 shadow-lg">
//         <div className="max-w-7xl mx-auto flex justify-between items-center">
//           <div>
//             <h1 className="text-3xl font-bold">
//               Tableau de Bord - Accompagnement
//             </h1>
//             <p className="text-sm opacity-90 mt-1">
//               Gestion centralisée des demandes de la clientèle groupe Mobilier
//               de France
//             </p>
//           </div>
//           <button
//             onClick={fetchTickets}
//             className="flex items-center space-x-2 px-4 py-2 bg-white text-red-600 rounded-lg hover:bg-gray-100 transition-colors"
//           >
//             <RefreshCw className="w-4 h-4" />
//             <span>Actualiser</span>
//           </button>
//         </div>
//       </div>

//       <div className="max-w-7xl mx-auto p-6">
//         <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
//           <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-blue-500">
//             <div className="text-sm text-gray-600">Total Tickets</div>
//             <div className="text-3xl font-bold text-gray-800">
//               {stats.total}
//             </div>
//           </div>
//           <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-red-500">
//             <div className="text-sm text-gray-600">Critiques (P0)</div>
//             <div className="text-3xl font-bold text-red-600">{stats.p0}</div>
//           </div>
//           <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-orange-500">
//             <div className="text-sm text-gray-600">Urgents (P1)</div>
//             <div className="text-3xl font-bold text-orange-600">{stats.p1}</div>
//           </div>
//           <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-green-500">
//             <div className="text-sm text-gray-600">Auto-résolus</div>
//             <div className="text-3xl font-bold text-green-600">
//               {stats.autoResolved}
//             </div>
//           </div>
//         </div>

//         <div className="bg-white p-4 rounded-lg shadow-md mb-6">
//           <div className="flex items-center space-x-4">
//             <Filter className="w-5 h-5 text-gray-600" />
//             <div className="flex-1 flex space-x-4">
//               <div>
//                 <label className="text-sm text-gray-600 mr-2">Priorité:</label>
//                 <select
//                   value={filterPriority}
//                   onChange={(e) => setFilterPriority(e.target.value)}
//                   className="border border-gray-300 rounded px-3 py-1"
//                 >
//                   <option value="all">Toutes</option>
//                   <option value="P0">P0 - Critique</option>
//                   <option value="P1">P1 - Urgent</option>
//                   <option value="P2">P2 - Modéré</option>
//                   <option value="P3">P3 - Faible</option>
//                 </select>
//               </div>
//               <div>
//                 <label className="text-sm text-gray-600 mr-2">Statut:</label>
//                 <select
//                   value={filterStatus}
//                   onChange={(e) => setFilterStatus(e.target.value)}
//                   className="border border-gray-300 rounded px-3 py-1"
//                 >
//                   <option value="all">Tous</option>
//                   <option value="escalated_to_human">Escaladés</option>
//                   <option value="awaiting_technician">
//                     En attente technicien
//                   </option>
//                   <option value="auto_resolved">Auto-résolus</option>
//                   <option value="evidence_collection">Collecte preuves</option>
//                 </select>
//               </div>
//             </div>
//             <div className="text-sm text-gray-600">
//               {filteredTickets.length} ticket(s)
//             </div>
//           </div>
//         </div>

//         <div className="bg-white rounded-lg shadow-md overflow-hidden">
//           {filteredTickets.length === 0 ? (
//             <div className="p-12 text-center text-gray-500">
//               <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
//               <p className="text-xl font-semibold mb-2">
//                 Aucune demande trouvée
//               </p>
//               <p className="text-sm">
//                 Créez votre première demande via le Bot Accompagnement (Texte)
//                 ou le Mode Vocal
//               </p>
//             </div>
//           ) : (
//             <table className="w-full">
//               <thead className="bg-gray-50 border-b border-gray-200">
//                 <tr>
//                   <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     Ticket
//                   </th>
//                   <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     Client
//                   </th>
//                   <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     Problème
//                   </th>
//                   <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     Priorité
//                   </th>
//                   <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     Ton
//                   </th>
//                   <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     Statut
//                   </th>
//                   <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     Date
//                   </th>
//                   <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     Actions
//                   </th>
//                 </tr>
//               </thead>
//               <tbody className="divide-y divide-gray-200">
//                 {filteredTickets.map((ticket) => (
//                   <TicketRow
//                     key={ticket.ticket_id}
//                     ticket={ticket}
//                     onViewDossier={fetchDossier}
//                   />
//                 ))}
//               </tbody>
//             </table>
//           )}
//         </div>
//       </div>

//       {selectedTicket && dossier && (
//         <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
//           <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
//             <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white p-4 flex justify-between items-center">
//               <h2 className="text-xl font-bold">
//                 Dossier Clientèle - {selectedTicket}
//               </h2>
//               <div className="flex space-x-2">
//                 <button
//                   onClick={downloadDossier}
//                   className="bg-white text-red-600 px-4 py-2 rounded hover:bg-gray-100 flex items-center space-x-2"
//                 >
//                   <Download className="w-4 h-4" />
//                   <span>Télécharger JSON</span>
//                 </button>
//                 <button
//                   onClick={closeModal}
//                   className="bg-white text-red-600 px-4 py-2 rounded hover:bg-gray-100"
//                 >
//                   X
//                 </button>
//               </div>
//             </div>

//             <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
//               <pre className="bg-gray-50 p-4 rounded-lg text-xs overflow-x-auto">
//                 {JSON.stringify(dossier, null, 2)}
//               </pre>
//             </div>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default Dashboard;
