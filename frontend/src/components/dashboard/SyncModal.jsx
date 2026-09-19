import React, { useState } from "react";
import { X, CheckCircle, Loader2, ArrowRight, ChevronDown, ChevronRight, Circle } from "lucide-react";
import { useSync } from "../../context/SyncContext";

export default function SyncModal() {
  const { 
    isDetailsModalOpen, 
    closeDetailsModal, 
    stages, 
    fetchedMails, 
    extractedData,
    syncStatus,
    syncError,
    totalMailsProcessed
  } = useSync();

  const [expandedStage, setExpandedStage] = useState("fetch_mails");

  if (!isDetailsModalOpen) return null;

  const toggleStage = (id) => {
    setExpandedStage(prev => prev === id ? null : id);
  };

  const formatDate = (isoString) => {
    if (!isoString) return "";
    const date = new Date(isoString);
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  const renderStageIcon = (status) => {
    switch(status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-emerald-400" />;
      case "processing":
        return <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />;
      case "failed":
        return <X className="w-5 h-5 text-rose-400" />;
      default:
        return <Circle className="w-5 h-5 text-slate-600" />;
    }
  };

  const renderFetchMailsContent = () => (
    <div className="mt-4 border border-slate-700 rounded-lg overflow-hidden divide-y divide-slate-700">
      {fetchedMails.length > 0 ? (
        fetchedMails.map((mail, idx) => (
          <div key={mail.id || idx} className="p-4 bg-slate-800/30 hover:bg-slate-800 transition-colors">
            <div className="flex justify-between items-start mb-1">
              <h3 className="text-slate-200 font-medium truncate pr-4" title={mail.subject}>
                {mail.subject}
              </h3>
            </div>
            
            <div className="flex justify-between items-center text-sm text-slate-400 mb-3">
              <span className="truncate">{mail.sender}</span>
              <span className="shrink-0">{formatDate(mail.date || mail.received_at)}</span>
            </div>

            <button 
              onClick={() => window.open(mail.mail_link, "_blank")}
              className="inline-flex items-center gap-1.5 text-sm text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
            >
              Open mail <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        ))
      ) : (
        <div className="p-8 text-center text-slate-500 italic">
          No financial emails found yet.
        </div>
      )}
    </div>
  );

  const renderExtractDataContent = () => (
    <div className="mt-4 border border-slate-700 rounded-lg overflow-hidden divide-y divide-slate-700">
      {extractedData.length > 0 ? (
        extractedData.map((data, idx) => (
          <div key={idx} className="p-4 bg-slate-800/30 hover:bg-slate-800 transition-colors">
            <h3 className="text-slate-200 font-medium mb-2">{data.merchant}</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-slate-500 block mb-1">Amount</span>
                <span className="text-slate-300 font-medium">{data.currency} {data.amount}</span>
              </div>
              <div>
                <span className="text-slate-500 block mb-1">Category</span>
                <span className="text-slate-300">{data.category}</span>
              </div>
            </div>
          </div>
        ))
      ) : (
        <div className="p-8 text-center text-slate-500 italic">
          Waiting for extracted data...
        </div>
      )}
    </div>
  );

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-700 rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <h2 className="text-xl font-semibold text-slate-100">Processing Details</h2>
          <button
            onClick={closeDetailsModal}
            className="text-slate-400 hover:text-slate-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Error Banner */}
        {syncStatus === "error" && (
          <div className="px-6 py-3 bg-rose-500/10 border-b border-rose-500/20 text-rose-400 text-sm">
            {syncError}
          </div>
        )}

        {/* Stages List */}
        <div className="flex-1 overflow-y-auto p-6 bg-slate-900/50 space-y-4">
          {stages.map((stage) => {
            const isExpanded = expandedStage === stage.id;
            
            return (
              <div key={stage.id} className="border border-slate-800 bg-slate-900 rounded-lg overflow-hidden transition-colors hover:border-slate-700">
                <button
                  onClick={() => toggleStage(stage.id)}
                  className="w-full flex items-center justify-between px-4 py-4 text-left focus:outline-none"
                >
                  <div className="flex items-center gap-3">
                    {renderStageIcon(stage.status)}
                    <span className={`font-medium ${stage.status === 'pending' ? 'text-slate-500' : 'text-slate-200'}`}>
                      {stage.title}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    {stage.id === "fetch_mails" && stage.status !== "pending" && (
                      <span className="text-sm text-slate-400">
                        {fetchedMails.length} mails
                      </span>
                    )}
                    {stage.id === "extract_data" && stage.status !== "pending" && (
                      <span className="text-sm text-slate-400">
                        {extractedData.length} mails
                      </span>
                    )}
                    {stage.status === "processing" && (
                      <span className="text-sm text-indigo-400">Processing...</span>
                    )}
                    {isExpanded ? (
                      <ChevronDown className="w-5 h-5 text-slate-500" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-slate-500" />
                    )}
                  </div>
                </button>
                
                {isExpanded && (
                  <div className="px-4 pb-4">
                    {stage.id === "fetch_mails" && renderFetchMailsContent()}
                    {stage.id === "extract_data" && renderExtractDataContent()}
                    {(stage.id === "categorize" || stage.id === "insights") && (
                      <div className="p-8 text-center text-slate-500 italic mt-2 border border-slate-800 rounded-lg">
                        {stage.status === "processing" 
                          ? `Running backend analytics for ${stage.title.toLowerCase()}...`
                          : stage.status === "completed" 
                            ? "Successfully completed."
                            : "Waiting for previous stages to complete."
                        }
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-900 flex items-center justify-between">
          <div className="text-sm text-slate-400">
            {syncStatus === "completed" ? (
              <span className="text-emerald-400 font-medium">Processing completed successfully</span>
            ) : syncStatus === "processing" ? (
              <span>Running pipeline in background...</span>
            ) : (
              <span>Ready</span>
            )}
          </div>
          
          <button
            onClick={closeDetailsModal}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
