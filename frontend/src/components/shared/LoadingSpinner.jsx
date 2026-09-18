export default function LoadingSpinner({ size = "md", className = "" }) {
  const sizeClasses = {
    sm: "w-4 h-4 border-2",
    md: "w-8 h-8 border-2",
    lg: "w-12 h-12 border-4"
  };

  return (
    <div className={`flex justify-center items-center ${className}`}>
      <div 
        className={`${sizeClasses[size]} rounded-full border-slate-700 border-t-indigo-500 animate-spin`}
      />
    </div>
  );
}
