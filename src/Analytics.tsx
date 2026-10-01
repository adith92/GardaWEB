import { useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { Download } from "lucide-react";
import { PageTitle, Panel, Badge } from "./ui";
import { download, useDemo } from "./store";
const hourly = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map((n) => ({
  hour: `${n * 2}:00`,
  people: [3, 1, 0, 5, 62, 48, 35, 42, 56, 28, 16, 9][n],
  vehicles: [1, 0, 0, 2, 28, 18, 12, 15, 21, 10, 7, 3][n],
}));
const trend = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map(
  (day, i) => ({
    day,
    incidents: [2, 4, 1, 3, 2, 1, 3][i],
    storage: [10.5, 10.8, 11, 11.3, 11.6, 12, 12.4][i],
  }),
);
export default function Analytics() {
  const [range, setRange] = useState("today");
  const { state, log } = useDemo();
  const rows = range === "today" ? hourly : hourly.filter((_, i) => i >= 9);
  const known = state.faces.filter((f) => f.category === "known").length;
  return (
    <>
      <PageTitle
        title="Operational Analytics"
        description="Pola aktivitas dan kesehatan kawasan · dataset agregat simulasi."
      >
        <select
          aria-label="Rentang analytics"
          value={range}
          onChange={(e) => setRange(e.target.value)}
        >
          <option value="today">01 Oct · 24 hours</option>
          <option value="night">Night shift · 18:00–24:00</option>
        </select>
        <button
          onClick={() => {
            download(
              "GARDA-analytics.json",
              JSON.stringify(
                { simulated: true, range, hourly: rows, trend },
                null,
                2,
              ),
            );
            log("Analytics exported", range);
          }}
        >
          <Download size={15} /> Export data
        </button>
      </PageTitle>
      <div className="analytics-grid">
        <Panel title="People detected by hour">
          <div className="chart">
            <ResponsiveContainer>
              <BarChart data={rows}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="people" fill="#c82430" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Vehicles by hour">
          <div className="chart">
            <ResponsiveContainer>
              <AreaChart data={rows}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Area
                  dataKey="vehicles"
                  stroke="#6f7950"
                  fill="#e1e5d6"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Known vs unknown identities">
          <div className="chart">
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={[
                    { name: "Known", value: known },
                    {
                      name: "Other / unknown",
                      value: state.faces.length - known,
                    },
                  ]}
                  dataKey="value"
                  innerRadius={60}
                  outerRadius={88}
                >
                  <Cell fill="#6f7950" />
                  <Cell fill="#c82430" />
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Incident trend · sample week">
          <div className="chart">
            <ResponsiveContainer>
              <BarChart data={trend}>
                <XAxis dataKey="day" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="incidents" fill="#c82430" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Camera uptime">
          <div className="uptime">
            {Array.from({ length: 8 }, (_, i) => (
              <div key={i}>
                <span>CAM-0{i + 1}</span>
                <div className="progress">
                  <i style={{ width: "100%", background: "#6f7950" }} />
                </div>
                <Badge tone="success">100%</Badge>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Storage growth · TB">
          <div className="chart">
            <ResponsiveContainer>
              <AreaChart data={trend}>
                <XAxis dataKey="day" />
                <YAxis domain={[0, 20]} />
                <Tooltip />
                <Area
                  dataKey="storage"
                  stroke="#c82430"
                  fill="#fce9eb"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>
    </>
  );
}
