import { Bike, Cloud, Clock, BarChart3 } from "lucide-react";
import { AppLayout } from "@/components/layout/AppLayout";
import { SummaryCard } from "@/components/dashboard/SummaryCard";
import { DemandLineChart } from "@/components/dashboard/DemandLineChart";
import { WeatherBarChart } from "@/components/dashboard/WeatherBarChart";
import { InsightsPanel } from "@/components/dashboard/InsightsPanel";
import { summaryStats } from "@/lib/mockData";

export default function Dashboard() {
  const getWeatherBadge = (impact: string) => {
    switch (impact) {
      case "Low":
        return { text: "Low Impact", variant: "success" as const };
      case "Medium":
        return { text: "Medium Impact", variant: "warning" as const };
      case "High":
        return { text: "High Impact", variant: "destructive" as const };
      default:
        return { text: impact, variant: "default" as const };
    }
  };

  const getPeakBadge = (status: string) => {
    switch (status) {
      case "Peak":
        return { text: "Peak Hours", variant: "warning" as const };
      case "Normal":
        return { text: "Normal", variant: "default" as const };
      case "Off-Peak":
        return { text: "Off-Peak", variant: "success" as const };
      default:
        return { text: status, variant: "default" as const };
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Real-time bike-sharing demand analytics and insights
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <SummaryCard
            title="Predicted Demand"
            value={summaryStats.predictedDemand.toLocaleString()}
            icon={<Bike className="h-5 w-5" />}
            badge={{ text: "bikes/day", variant: "default" }}
          />
          <SummaryCard
            title="Weather Impact"
            value={summaryStats.weatherImpact}
            icon={<Cloud className="h-5 w-5" />}
            badge={getWeatherBadge(summaryStats.weatherImpact)}
          />
          <SummaryCard
            title="Peak Status"
            value={summaryStats.peakStatus}
            icon={<Clock className="h-5 w-5" />}
            badge={getPeakBadge(summaryStats.peakStatus)}
          />
          <SummaryCard
            title="Prediction Type"
            value={summaryStats.predictionType}
            icon={<BarChart3 className="h-5 w-5" />}
          />
        </div>

        {/* Charts Section */}
        <div className="grid gap-6 lg:grid-cols-2">
          <DemandLineChart type="hourly" />
          <WeatherBarChart />
        </div>

        {/* Insights Panel */}
        <InsightsPanel />
      </div>
    </AppLayout>
  );
}
