import { useState } from "react";
import { X, AlertCircle } from "lucide-react";

export default function ErrorBanner({ message, onRetry }) {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible || !message) return null;

  return (
    <div className="bg-rose-900/50 border border-rose-800/50 rounded-lg p-4 flex items-start gap-4">
      <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
      
      <div className="flex-1">
        <p className="text-sm font-medium text-rose-400">{message}</p>
      </div>

      <div className="flex items-center gap-3">
        {onRetry && (
          <button 
            onClick={onRetry}
            className="text-sm font-medium text-rose-400 hover:text-rose-300 transition-colors"
          >
            Retry
          </button>
        )}
        <button 
          onClick={() => setIsVisible(false)}
          className="text-rose-400 hover:text-rose-300 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
