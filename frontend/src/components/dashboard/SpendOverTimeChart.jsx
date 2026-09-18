import { ComposedChart, Line, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function SpendOverTimeChart({ monthlyTotals }) {
  if (!monthlyTotals) return null;

  const data = Object.entries(monthlyTotals)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([month, amount]) => {
      // month is "YYYY-MM"
      const date = new Date(month + "-01");
      const formattedMonth = date.toLocaleDateString("en-US", { month: "short", year: "2-digit" });
      return {
        month: formattedMonth,
        amount
      };
    });

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-slate-100 mb-6">Spend Over Time</h3>
      <div className="h-[260px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <XAxis 
              dataKey="month" 
              stroke="#94a3b8" 
              fontSize={12} 
              tickLine={false} 
              axisLine={false}
              dy={10}
            />
            <YAxis 
              width={80}
              tickFormatter={(value) => `₹${value.toLocaleString("en-IN")}`}
              stroke="#94a3b8" 
              fontSize={12} 
              tickLine={false} 
              axisLine={false} 
            />
            <Tooltip 
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg">
                      <p className="text-sm font-medium text-slate-100">{payload[0].payload.month}</p>
                      <p className="text-sm font-mono text-indigo-400 mt-1">
                        ₹{payload[0].value.toLocaleString("en-IN")}
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Area 
              type="monotone" 
              dataKey="amount" 
              fill="#6366f1" 
              fillOpacity={0.1} 
              stroke="none" 
            />
            <Line 
              type="monotone" 
              dataKey="amount" 
              stroke="#6366f1" 
              strokeWidth={2} 
              dot={{ fill: "#6366f1", r: 4, strokeWidth: 0 }}
              activeDot={{ r: 6, fill: "#818cf8", strokeWidth: 0 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
