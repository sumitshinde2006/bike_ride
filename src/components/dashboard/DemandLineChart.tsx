import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ChartData {
  name: string;
  value: number;
  fill?: string;
}

interface DemandLineChartProps {
  data?: ChartData[];
  title?: string;
  description?: string;
}

export function DemandLineChart({
  data = [],
  title = "Demand Trend",
  description = "24-hour bike demand pattern",
}: DemandLineChartProps) {
  // Simple bar chart visualization using HTML
  const maxValue = Math.max(...(data?.map(d => d.value) || [100]), 100);
  
  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
        {description && (
          <p className="text-sm text-muted-foreground mt-1">{description}</p>
        )}
      </CardHeader>
      <CardContent>
        {data && data.length > 0 ? (
          <div className="space-y-4">
            {data.map((item, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="font-medium">{item.name}</span>
                  <span className="text-muted-foreground">{item.value}</span>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className="bg-primary rounded-full h-2 transition-all duration-300"
                    style={{ width: `${(item.value / maxValue) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            <p>No data available</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
