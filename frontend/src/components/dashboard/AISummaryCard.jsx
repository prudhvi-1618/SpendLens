import { Sparkles } from "lucide-react";
import LoadingSpinner from "../shared/LoadingSpinner";

export default function AISummaryCard({ summaryText }) {
  return (
    <div className="bg-slate-900 border border-slate-800 border-l-4 border-l-indigo-500 rounded-2xl p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <h3 className="text-lg font-semibold text-slate-100">AI Spending Insight</h3>
        </div>
        <div className="self-start sm:self-auto">
          <span className="inline-block bg-indigo-950 text-indigo-400 text-xs font-medium px-3 py-1 rounded-full">
            Powered by Gemini
          </span>
        </div>
      </div>
      
      <div className="min-h-[80px] flex items-center">
        {!summaryText ? (
          <div className="w-full flex justify-center py-4">
            <LoadingSpinner size="md" />
          </div>
        ) : (
          <p className="text-sm text-slate-300 leading-relaxed">
            {summaryText}
          </p>
        )}
      </div>
    </div>
  );
}
