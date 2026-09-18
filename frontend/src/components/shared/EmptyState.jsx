export default function EmptyState({ icon: Icon, title, description, actionLabel, onAction }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="bg-slate-800/50 p-4 rounded-full mb-4">
        <Icon className="w-12 h-12 text-slate-400" />
      </div>
      <h3 className="text-xl font-semibold text-slate-200 mb-2">{title}</h3>
      <p className="text-sm text-slate-400 max-w-sm mb-6">{description}</p>
      
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-6 py-2.5 rounded-lg transition-colors"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
