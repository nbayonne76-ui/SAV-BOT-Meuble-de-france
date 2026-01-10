import { useState, useEffect, useMemo, useCallback } from "react";
import { FileText, Download, XCircle, Filter, RefreshCw } from "lucide-react";
import { API_URL } from "../utils/url";
import TicketRow from "./TicketRow";
import { useLanguage } from "../context/LanguageContext";

const Dashboard = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterPriority, setFilterPriority] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [dossier, setDossier] = useState(null);
  const { language, setLanguage, t, languages } = useLanguage();
  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      console.log(`[Dashboard] Fetching tickets from: ${API_URL}/api/sav/tickets`);

      const response = await fetch(`${API_URL}/api/sav/tickets`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      });

      console.log(`[Dashboard] Response status: ${response.status} ${response.statusText}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`[Dashboard] Error response:`, errorText);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`[Dashboard] Response data:`, data);
      console.log(`[Dashboard] Number of tickets:`, data.tickets ? data.tickets.length : 0);

      if (data.success) {
        setTickets(data.tickets || []);
        setError(null);
        console.log(`[Dashboard] ✅ Successfully loaded ${data.tickets?.length || 0} tickets`);
      } else {
        console.error(`[Dashboard] ❌ API returned success=false`);
        setError("Erreur lors du chargement des tickets");
      }
    } catch (err) {
      console.error("[Dashboard] ❌ Fetch error:", err);
      setError(`Erreur de connexion: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchDossier = useCallback(async (ticketId) => {
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
  }, []);

  const downloadDossier = useCallback(() => {
    if (!dossier) return;
    const dataStr = JSON.stringify(dossier, null, 2);
    const dataUri =
      "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);
    const exportFileDefaultName = `dossier_${selectedTicket}.json`;
    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
  }, [dossier, selectedTicket]);

  const closeModal = useCallback(() => {
    setSelectedTicket(null);
    setDossier(null);
  }, []);

  const filteredTickets = useMemo(() => {
    console.log(`[Dashboard] Filtering ${tickets.length} tickets`);
    console.log(`[Dashboard] Current filters - Priority: ${filterPriority}, Status: ${filterStatus}`);

    const filtered = tickets.filter((ticket) => {
      console.log(`[Dashboard] Checking ticket:`, ticket);
      console.log(`[Dashboard]   - ticket.priority: ${ticket.priority}`);
      console.log(`[Dashboard]   - ticket.status: ${ticket.status}`);

      if (filterPriority !== "all" && ticket.priority !== filterPriority) {
        console.log(`[Dashboard]   - FILTERED OUT by priority`);
        return false;
      }
      if (filterStatus !== "all" && ticket.status !== filterStatus) {
        console.log(`[Dashboard]   - FILTERED OUT by status`);
        return false;
      }
      console.log(`[Dashboard]   - ✅ PASSED filters`);
      return true;
    });

    console.log(`[Dashboard] Filtered result: ${filtered.length} tickets`);
    return filtered;
  }, [tickets, filterPriority, filterStatus]);

  const stats = useMemo(() => {
    return {
      total: tickets.length,
      p0: tickets.filter((t) => t.priority === "P0").length,
      p1: tickets.filter((t) => t.priority === "P1").length,
      p2: tickets.filter((t) => t.priority === "P2").length,
      p3: tickets.filter((t) => t.priority === "P3").length,
      autoResolved: tickets.filter((t) => t.auto_resolved).length,
      escalated: tickets.filter((t) => t.status === "escalated_to_human")
        .length,
      awaitingTech: tickets.filter((t) => t.status === "awaiting_technician")
        .length,
    };
  }, [tickets]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">
            Chargement des demandes d'accompagnement...
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
          <button
            onClick={fetchTickets}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center space-x-2 mx-auto"
          >
            <RefreshCw className="w-5 h-5" />
            <span>{t("dashboard.retry")}</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white p-6 shadow-lg">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">{t("dashboard.title")}</h1>
            <p className="text-sm opacity-90 mt-1">{t("dashboard.subtitle")}</p>
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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="text-sm text-gray-600">
              {t("dashboard.stats.total_label")}
            </div>
            <div className="text-3xl font-bold text-gray-800">
              {stats.total}
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-red-500">
            <div className="text-sm text-gray-600">
              {t("dashboard.stats.p0_label")}
            </div>
            <div className="text-3xl font-bold text-red-600">{stats.p0}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-orange-500">
            <div className="text-sm text-gray-600">
              {t("dashboard.stats.p1_label")}
            </div>
            <div className="text-3xl font-bold text-orange-600">{stats.p1}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-green-500">
            <div className="text-sm text-gray-600">
              {t("dashboard.stats.auto_resolved")}
            </div>
            <div className="text-3xl font-bold text-green-600">
              {stats.autoResolved}
            </div>
          </div>
        </div>

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
                  <option value="all">
                    {t("dashboard.filters.all_priority")}
                  </option>
                  <option value="P0">
                    {t("dashboard.filters.p0_critical")}
                  </option>
                  <option value="P1">{t("dashboard.filters.p1_urgent")}</option>
                  <option value="P2">
                    {t("dashboard.filters.p2_moderate")}
                  </option>
                  <option value="P3">{t("dashboard.filters.p3_low")}</option>
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
                  <option value="all">{t("dashboard.filters.all")}</option>
                  <option value="escalated_to_human">
                    {t("dashboard.filters.escalated")}
                  </option>
                  <option value="awaiting_technician">
                    {t("dashboard.filters.awaiting_tech")}
                  </option>
                  <option value="auto_resolved">
                    {t("dashboard.filters.auto_resolved_filter")}
                  </option>
                  <option value="evidence_collection">
                    {t("dashboard.filters.evidence_collection_filter")}
                  </option>
                </select>
              </div>
            </div>
            <div className="text-sm text-gray-600">
              {filteredTickets.length} ticket(s)
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {filteredTickets.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-xl font-semibold mb-2">
                {t("dashboard.no_tickets")}
              </p>
              <p className="text-sm">{t("dashboard.no_tickets_hint")}</p>
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
                {filteredTickets.map((ticket) => {
                  // Normalize null values to prevent rendering issues
                  const normalizedTicket = {
                    ...ticket,
                    priority: ticket.priority || "UNKNOWN",
                    status: ticket.status || "unknown",
                    tone: ticket.tone || null,
                    urgency: ticket.urgency || "low",
                    problem_description: ticket.problem_description || "Pas de description",
                  };

                  console.log(`[Dashboard] Rendering ticket ${ticket.ticket_id}:`);
                  console.log(JSON.stringify(normalizedTicket, null, 2));

                  return (
                    <TicketRow
                      key={ticket.ticket_id}
                      ticket={normalizedTicket}
                      onViewDossier={fetchDossier}
                    />
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {selectedTicket && dossier && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white p-4 flex justify-between items-center">
              <h2 className="text-xl font-bold">
                {t("dashboard.dossier_title")} - {selectedTicket}
              </h2>
              <div className="flex space-x-2">
                <button
                  onClick={downloadDossier}
                  className="bg-white text-red-600 px-4 py-2 rounded hover:bg-gray-100 flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>{t("dashboard.download_json")}</span>
                </button>
                <button
                  onClick={closeModal}
                  className="bg-white text-red-600 px-4 py-2 rounded hover:bg-gray-100"
                >
                  X
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
