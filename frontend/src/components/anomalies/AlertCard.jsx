import { AlertTriangle } from "lucide-react";

export default function AlertCard({ anomaly }) {
  const { 
    merchant, 
    amount, 
    date, 
    category, 
    flag_reason, 
    gmail_message_id 
  } = anomaly;

  const formattedDate = new Date(date).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric"
  });

  return (
    <div className="bg-slate-900 border-l-4 border-amber-500 rounded-2xl p-5 shadow-lg">
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <h3 className="text-slate-100 font-semibold">{merchant}</h3>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className="font-mono text-lg text-slate-100">
            ₹{amount.toLocaleString("en-IN")}
          </span>
          {category && (
            <span className="bg-slate-800 text-slate-400 text-xs rounded-full px-2 py-0.5 capitalize">
              {category}
            </span>
          )}
        </div>
      </div>
      
      <div className="mb-4">
        <p className="text-slate-300 text-sm">{flag_reason}</p>
      </div>

      <div className="flex justify-between items-center text-xs text-slate-500">
        <span>{formattedDate}</span>
        {gmail_message_id && (
          <a
            href={`https://mail.google.com/mail/u/0/#inbox/${gmail_message_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-400 hover:text-indigo-300 transition-colors font-medium flex items-center gap-1"
          >
            View in Gmail &rarr;
          </a>
        )}
      </div>
    </div>
  );
}
