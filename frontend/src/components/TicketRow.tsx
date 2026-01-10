import { memo } from "react";
import { Eye, AlertCircle, Clock, CheckCircle, FileText } from "lucide-react";
import { getPriorityColor, getStatusLabel, formatDate } from "../utils/format";
import { useLanguage } from "../context/LanguageContext";

interface TicketRowProps {
  ticket: {
    ticket_id: string;
    customer_name: string | null;
    order_number: string;
    product_name: string;
    problem_description: string;
    priority: string;
    tone: string | null;
    urgency: string | null;
    status: string | null;
    created_at: string | null;
  };
  onViewDossier: (ticketId: string) => void;
}

const getStatusIcon = (status?: string) => {
  switch (status) {
    case "escalated_to_human":
      return <AlertCircle className="w-4 h-4 text-orange-600" />;
    case "awaiting_technician":
      return <Clock className="w-4 h-4 text-blue-600" />;
    case "auto_resolved":
      return <CheckCircle className="w-4 h-4 text-green-600" />;
    case "evidence_collection":
      return <FileText className="w-4 h-4 text-purple-600" />;
    case "unknown":
      return <AlertCircle className="w-4 h-4 text-gray-500" />;
    case "pending":
      return <Clock className="w-4 h-4 text-gray-600" />;
    default:
      return <Clock className="w-4 h-4 text-gray-600" />;
  }
};

const TicketRow = memo(({ ticket, onViewDossier }: TicketRowProps) => {
  const { t } = useLanguage();
  return (
    <tr className="hover:bg-gray-50">
      <td className="px-6 py-4 text-sm font-medium text-gray-900">
        {ticket.ticket_id}
      </td>
      <td className="px-6 py-4 text-sm text-gray-600">
        <div>{ticket.customer_name || t("dashboard.columns.client")}</div>
        <div className="text-xs text-gray-400">{ticket.order_number}</div>
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
          {getStatusIcon(ticket.status ? ticket.status : "")}
          <span className="text-xs text-gray-600">
            {getStatusLabel(ticket.status ?? "")}
          </span>
        </div>
      </td>
      <td className="px-6 py-4 text-sm text-gray-600">
        {formatDate(ticket.created_at)}
      </td>
      <td className="px-6 py-4 text-sm">
        <button
          onClick={() => onViewDossier(ticket.ticket_id)}
          className="text-blue-600 hover:text-blue-800"
          title={t("dashboard.view_dossier")}
        >
          <Eye className="w-5 h-5" />
        </button>
      </td>
    </tr>
  );
});

TicketRow.displayName = "TicketRow";

export default TicketRow;
