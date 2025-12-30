// frontend/src/components/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { FileText, Download, Eye, AlertCircle, Clock, CheckCircle, XCircle, Filter } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL ?? '';

const Dashboard = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterPriority, setFilterPriority] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [dossier, setDossier] = useState(null);

  // Charger tous les tickets
  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    try {
      setLoading(true);
      setError(null); // Reset error state before fetching
      const response = await fetch(`${API_URL}/api/sav/tickets`);
      const data = await response.json();

      console.log('📊 Dashboard - Données reçues:', data);
      console.log('📊 Dashboard - Nombre de tickets:', data.tickets?.length);
      console.log('📊 Dashboard - Premier ticket:', data.tickets?.[0]);

      if (data.success) {
        setTickets(data.tickets);
      } else {
        setError(data.error || 'Erreur lors du chargement des tickets');
      }
    } catch (err) {
      console.error('Erreur:', err);
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const fetchDossier = async (ticketId) => {
    try {
      const response = await fetch(`${API_URL}/api/sav/ticket/${ticketId}/dossier`);
      const data = await response.json();

      if (data.success) {
        setDossier(data.dossier);
        setSelectedTicket(ticketId);
      }
    } catch (err) {
      console.error('Erreur:', err);
      alert('Erreur lors du chargement du dossier');
    }
  };

  const downloadDossier = (ticket) => {
    // Télécharger le dossier au format JSON
    const dataStr = JSON.stringify(dossier, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);

    const exportFileDefaultName = `dossier_${ticket.ticket_id}.json`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // Filtrer les tickets
  const filteredTickets = tickets.filter(ticket => {
    if (filterPriority !== 'all' && ticket.priority !== filterPriority) return false;
    if (filterStatus !== 'all' && ticket.status !== filterStatus) return false;
    return true;
  });

  console.log('🔍 Dashboard - Tickets bruts:', tickets.length);
  console.log('🔍 Dashboard - Tickets filtrés:', filteredTickets.length);
  console.log('🔍 Dashboard - Filtres actifs:', { filterPriority, filterStatus });

  // Statistiques
  const stats = {
    total: tickets.length,
    p0: tickets.filter(t => t.priority === 'P0').length,
    p1: tickets.filter(t => t.priority === 'P1').length,
    p2: tickets.filter(t => t.priority === 'P2').length,
    p3: tickets.filter(t => t.priority === 'P3').length,
    autoResolved: tickets.filter(t => t.auto_resolved).length,
    escalated: tickets.filter(t => t.status === 'escalated_to_human').length,
    awaitingTech: tickets.filter(t => t.status === 'awaiting_technician').length
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'P0': 'bg-red-100 text-red-800 border-red-300',
      'P1': 'bg-orange-100 text-orange-800 border-orange-300',
      'P2': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'P3': 'bg-green-100 text-green-800 border-green-300'
    };
    return colors[priority] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'escalated_to_human':
        return <AlertCircle className="w-4 h-4 text-orange-600" />;
      case 'awaiting_technician':
        return <Clock className="w-4 h-4 text-blue-600" />;
      case 'auto_resolved':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'evidence_collection':
        return <FileText className="w-4 h-4 text-purple-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusLabel = (status) => {
    const labels = {
      'escalated_to_human': 'Escaladé',
      'awaiting_technician': 'En attente technicien',
      'auto_resolved': 'Résolu auto',
      'evidence_collection': 'Collecte preuves',
      'pending': 'En attente'
    };
    return labels[status] || status;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des tickets SAV...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center text-red-600">
          <XCircle className="w-16 h-16 mx-auto mb-4" />
          <p className="text-xl font-semibold">{error}</p>
          <button
            onClick={fetchTickets}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white p-6 shadow-lg">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold">📊 Tableau de Bord SAV</h1>
          <p className="text-sm opacity-90 mt-1">Gestion centralisée des réclamations clients</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* Statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="text-sm text-gray-600">Total Tickets</div>
            <div className="text-3xl font-bold text-gray-800">{stats.total}</div>
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
            <div className="text-3xl font-bold text-green-600">{stats.autoResolved}</div>
          </div>
        </div>

        {/* Filtres */}
        <div className="bg-white p-4 rounded-lg shadow-md mb-6">
          <div className="flex items-center space-x-4">
            <Filter className="w-5 h-5 text-gray-600" />
            <div className="flex-1 flex space-x-4">
              <div>
                <label htmlFor="filter-priority" className="text-sm text-gray-600 mr-2">Priorité:</label>
                <select
                  id="filter-priority"
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
                <label htmlFor="filter-status" className="text-sm text-gray-600 mr-2">Statut:</label>
                <select
                  id="filter-status"
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="border border-gray-300 rounded px-3 py-1"
                >
                  <option value="all">Tous</option>
                  <option value="escalated_to_human">Escaladés</option>
                  <option value="awaiting_technician">En attente technicien</option>
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
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ticket</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Problème</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priorité</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ton</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredTickets.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-6 py-8 text-center text-gray-500">
                    Aucun ticket trouvé
                  </td>
                </tr>
              ) : (
                filteredTickets.map((ticket) => (
                  <tr key={ticket.ticket_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {ticket.numero_ticket || ticket.ticket_id}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      <div>{ticket.nom_client}</div>
                      <div className="text-xs text-gray-400">{ticket.email}</div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      <div className="font-medium">{ticket.produit}</div>
                      <div className="text-xs text-gray-400 truncate max-w-xs">
                        {ticket.probleme}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full border ${getPriorityColor(ticket.priority)}`}>
                        {ticket.priority}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {ticket.tone ? (
                        <div className="flex items-center space-x-1">
                          <div className={`w-2 h-2 rounded-full ${
                            ticket.urgency === 'critical' ? 'bg-red-500' :
                            ticket.urgency === 'high' ? 'bg-orange-500' :
                            ticket.urgency === 'medium' ? 'bg-yellow-500' :
                            'bg-green-500'
                          }`}></div>
                          <span className="text-xs text-gray-600 uppercase">{ticket.tone}</span>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(ticket.status)}
                        <span className="text-xs text-gray-600">{getStatusLabel(ticket.status)}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(ticket.created_at).toLocaleString('fr-FR', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
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
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Dossier */}
      {selectedTicket && dossier && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white p-4 flex justify-between items-center">
              <h2 className="text-xl font-bold">📄 Dossier Client - {selectedTicket}</h2>
              <div className="flex space-x-2">
                <button
                  onClick={() => downloadDossier(tickets.find(t => t.ticket_id === selectedTicket))}
                  className="bg-white text-red-600 px-4 py-2 rounded hover:bg-gray-100 flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>Télécharger JSON</span>
                </button>
                <button
                  onClick={() => { setSelectedTicket(null); setDossier(null); }}
                  className="bg-white text-red-600 px-4 py-2 rounded hover:bg-gray-100"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
              {/* Informations Ticket */}
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-800 mb-3 border-b pb-2">🎫 Informations Ticket</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-600">ID:</span>
                    <span className="ml-2 font-semibold">{dossier.ticket?.ticket_id}</span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Créé le:</span>
                    <span className="ml-2 font-semibold">
                      {new Date(dossier.ticket?.created_at).toLocaleString('fr-FR')}
                    </span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Priorité:</span>
                    <span className={`ml-2 px-3 py-1 text-xs font-semibold rounded-full ${getPriorityColor(dossier.ticket?.priority)}`}>
                      {dossier.ticket?.priority} (Score: {dossier.ticket?.priority_score})
                    </span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Statut:</span>
                    <span className="ml-2 font-semibold">{getStatusLabel(dossier.ticket?.status)}</span>
                  </div>
                </div>
              </div>

              {/* Informations Client */}
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-800 mb-3 border-b pb-2">👤 Informations Client</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-600">Nom:</span>
                    <span className="ml-2 font-semibold">{dossier.client?.customer_name}</span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Email:</span>
                    <span className="ml-2 font-semibold">{dossier.client?.customer_id}</span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Commande:</span>
                    <span className="ml-2 font-semibold">{dossier.client?.order_number}</span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Niveau:</span>
                    <span className="ml-2 font-semibold capitalize">{dossier.client?.customer_tier}</span>
                  </div>
                </div>
              </div>

              {/* Informations Produit */}
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-800 mb-3 border-b pb-2">🛋️ Produit Concerné</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <span className="text-sm text-gray-600">Produit:</span>
                    <span className="ml-2 font-semibold">{dossier.produit?.product_name}</span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">SKU:</span>
                    <span className="ml-2 font-mono text-sm">{dossier.produit?.product_sku}</span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Valeur:</span>
                    <span className="ml-2 font-semibold">{dossier.produit?.product_value}€</span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Date achat:</span>
                    <span className="ml-2">{dossier.produit?.purchase_date ? new Date(dossier.produit.purchase_date).toLocaleDateString('fr-FR') : '-'}</span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Date livraison:</span>
                    <span className="ml-2">{dossier.produit?.delivery_date ? new Date(dossier.produit.delivery_date).toLocaleDateString('fr-FR') : '-'}</span>
                  </div>
                </div>
              </div>

              {/* Problème */}
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-800 mb-3 border-b pb-2">⚠️ Problème Signalé</h3>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-800 mb-3">{dossier.probleme?.description}</p>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Catégorie:</span>
                      <span className="ml-2 font-semibold capitalize">{dossier.probleme?.category}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Sévérité:</span>
                      <span className="ml-2 font-semibold">{dossier.probleme?.severity}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Confiance:</span>
                      <span className="ml-2 font-semibold">{(dossier.probleme?.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Analyse Ton */}
              {dossier.analyse_ton && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-800 mb-3 border-b pb-2">🎭 Analyse du Ton</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-sm text-gray-600">Ton:</span>
                      <span className="ml-2 font-semibold capitalize">{dossier.analyse_ton?.tone}</span>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Urgence:</span>
                      <span className="ml-2 font-semibold capitalize">{dossier.analyse_ton?.urgency}</span>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Score émotion:</span>
                      <span className="ml-2 font-semibold">{dossier.analyse_ton?.emotion_score}/100</span>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Empathie requise:</span>
                      <span className="ml-2 font-semibold">{dossier.analyse_ton?.requires_human_empathy ? '✅ Oui' : '❌ Non'}</span>
                    </div>
                    <div className="col-span-2">
                      <span className="text-sm text-gray-600">Temps réponse recommandé:</span>
                      <span className="ml-2 font-semibold">{dossier.analyse_ton?.recommended_response_time}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Garantie */}
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-800 mb-3 border-b pb-2">🛡️ Garantie</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-600">Couvert:</span>
                    <span className={`ml-2 font-semibold ${dossier.garantie?.covered ? 'text-green-600' : 'text-red-600'}`}>
                      {dossier.garantie?.covered ? '✅ Oui' : '❌ Non'}
                    </span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Composant:</span>
                    <span className="ml-2 font-semibold capitalize">{dossier.garantie?.component || '-'}</span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Type garantie:</span>
                    <span className="ml-2 font-semibold capitalize">{dossier.garantie?.warranty_type || '-'}</span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Expire le:</span>
                    <span className="ml-2">{dossier.garantie?.expiry_date ? new Date(dossier.garantie.expiry_date).toLocaleDateString('fr-FR') : '-'}</span>
                  </div>
                  {dossier.garantie?.reason && (
                    <div className="col-span-2">
                      <span className="text-sm text-gray-600">Raison:</span>
                      <span className="ml-2 text-sm">{dossier.garantie.reason}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Preuves / Photos */}
              {dossier.preuves && dossier.preuves.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-800 mb-3 border-b pb-2">📸 Preuves Fournies ({dossier.preuves.length})</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {dossier.preuves.map((preuve, index) => (
                      <div key={index} className="border rounded-lg p-3 bg-gray-50">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-semibold text-gray-700 uppercase">{preuve.type}</span>
                          <span className="text-xs text-gray-500">
                            {new Date(preuve.uploaded_at).toLocaleString('fr-FR')}
                          </span>
                        </div>
                        {preuve.type === 'photo' && preuve.url && (
                          <img
                            src={preuve.url}
                            alt={preuve.description}
                            className="w-full h-48 object-cover rounded mb-2 cursor-pointer hover:opacity-90"
                            onClick={() => window.open(preuve.url, '_blank')}
                          />
                        )}
                        {preuve.type === 'video' && preuve.url && (
                          <video
                            src={preuve.url}
                            controls
                            className="w-full h-48 rounded mb-2"
                          />
                        )}
                        <p className="text-xs text-gray-600">{preuve.description}</p>
                        <a
                          href={preuve.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline mt-2 inline-block"
                        >
                          Voir en taille réelle →
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* SLA */}
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-800 mb-3 border-b pb-2">⏰ Délais SLA</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-600">Réponse avant:</span>
                    <span className="ml-2 font-semibold">
                      {dossier.sla?.response_deadline ? new Date(dossier.sla.response_deadline).toLocaleString('fr-FR') : '-'}
                    </span>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Intervention avant:</span>
                    <span className="ml-2 font-semibold">
                      {dossier.sla?.intervention_deadline ? new Date(dossier.sla.intervention_deadline).toLocaleString('fr-FR') : '-'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Récapitulatif Client */}
              {dossier.recapitulatif && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-800 mb-3 border-b pb-2">📧 Récapitulatif Client</h3>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <span className="text-sm text-gray-600">ID Récapitulatif:</span>
                        <span className="ml-2 font-mono text-xs">{dossier.recapitulatif.summary_id}</span>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Validation requise:</span>
                        <span className="ml-2 font-semibold">
                          {dossier.recapitulatif.validation_required ? '✅ Oui' : '❌ Non'}
                        </span>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Statut validation:</span>
                        <span className={`ml-2 px-2 py-1 text-xs font-semibold rounded ${
                          dossier.recapitulatif.validation_status === 'validated'
                            ? 'bg-green-200 text-green-800'
                            : dossier.recapitulatif.validation_status === 'rejected'
                            ? 'bg-red-200 text-red-800'
                            : 'bg-yellow-200 text-yellow-800'
                        }`}>
                          {dossier.recapitulatif.validation_status === 'validated' ? '✅ Validé' :
                           dossier.recapitulatif.validation_status === 'rejected' ? '❌ Rejeté' :
                           '⏳ En attente'}
                        </span>
                      </div>
                      {dossier.recapitulatif.validation_link && (
                        <div>
                          <a
                            href={dossier.recapitulatif.validation_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:underline font-semibold"
                          >
                            🔗 Lien de validation →
                          </a>
                        </div>
                      )}
                    </div>

                    {dossier.recapitulatif.email_body && (
                      <details className="mt-3">
                        <summary className="cursor-pointer text-sm text-gray-700 hover:text-gray-900 font-semibold">
                          📄 Voir l'email envoyé au client
                        </summary>
                        <div className="bg-white p-4 rounded mt-2 border border-gray-200">
                          <pre className="text-xs whitespace-pre-wrap text-gray-800 font-sans">
                            {dossier.recapitulatif.email_body}
                          </pre>
                        </div>
                      </details>
                    )}

                    {dossier.recapitulatif.sms_body && (
                      <details className="mt-2">
                        <summary className="cursor-pointer text-sm text-gray-700 hover:text-gray-900 font-semibold">
                          📱 Voir le SMS envoyé au client
                        </summary>
                        <div className="bg-white p-3 rounded mt-2 border border-gray-200">
                          <p className="text-xs text-gray-800">
                            {dossier.recapitulatif.sms_body}
                          </p>
                        </div>
                      </details>
                    )}
                  </div>
                </div>
              )}

              {/* Résolution */}
              {dossier.resolution && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-800 mb-3 border-b pb-2">✅ Résolution</h3>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="mb-2">
                      <span className="text-sm text-gray-600">Auto-résolu:</span>
                      <span className="ml-2 font-semibold">{dossier.resolution?.auto_resolved ? '✅ Oui' : '❌ Non'}</span>
                    </div>
                    {dossier.resolution?.resolution_type && (
                      <div className="mb-2">
                        <span className="text-sm text-gray-600">Type:</span>
                        <span className="ml-2 font-semibold capitalize">{dossier.resolution.resolution_type}</span>
                      </div>
                    )}
                    {dossier.resolution?.resolution_description && (
                      <div>
                        <span className="text-sm text-gray-600">Description:</span>
                        <p className="text-sm text-gray-800 mt-1">{dossier.resolution.resolution_description}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Historique */}
              {dossier.historique && dossier.historique.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-800 mb-3 border-b pb-2">📜 Historique des Actions</h3>
                  <div className="space-y-2">
                    {dossier.historique.map((action, index) => (
                      <div key={index} className="flex items-start space-x-3 bg-gray-50 p-3 rounded">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5"></div>
                        <div className="flex-1">
                          <div className="flex justify-between items-start">
                            <span className="text-sm font-semibold text-gray-800">{action.description}</span>
                            <span className="text-xs text-gray-500">
                              {new Date(action.timestamp).toLocaleString('fr-FR')}
                            </span>
                          </div>
                          <div className="text-xs text-gray-600 mt-1">
                            <span className="font-semibold capitalize">{action.actor}</span>
                            <span className="mx-2">•</span>
                            <span>{action.action_type}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* JSON Brut (repliable) */}
              <details className="mt-6">
                <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800 font-semibold">
                  📋 Voir le JSON brut
                </summary>
                <pre className="bg-gray-50 p-4 rounded-lg text-xs overflow-x-auto mt-2">
                  {JSON.stringify(dossier, null, 2)}
                </pre>
              </details>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
