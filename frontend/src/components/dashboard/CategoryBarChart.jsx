import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function CategoryBarChart({ byCategory }) {
  if (!byCategory) return null;

  const data = Object.entries(byCategory)
    .map(([name, amount]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      amount
    }))
    .sort((a, b) => b.amount - a.amount);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-slate-100 mb-6">Spend by Category</h3>
      <div className="h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
            <XAxis 
              type="number" 
              tickFormatter={(value) => `₹${value.toLocaleString("en-IN")}`}
              stroke="#94a3b8" 
              fontSize={12} 
              tickLine={false} 
              axisLine={false} 
            />
            <YAxis 
              dataKey="name" 
              type="category" 
              width={110}
              stroke="#94a3b8" 
              fontSize={14} 
              tickLine={false} 
              axisLine={false} 
            />
            <Tooltip 
              cursor={{ fill: "#1e293b" }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg">
                      <p className="text-sm font-medium text-slate-100">{payload[0].payload.name}</p>
                      <p className="text-sm font-mono text-indigo-400 mt-1">
                        ₹{payload[0].value.toLocaleString("en-IN")}
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey="amount" fill="#6366f1" radius={[0, 4, 4, 0]} barSize={24} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
