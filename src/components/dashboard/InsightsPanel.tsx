import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, TrendingUp, Cloud, Clock } from "lucide-react";

interface InsightItem {
  icon: React.ReactNode;
  title: string;
  description: string;
}

interface InsightsPanelProps {
  insights?: InsightItem[];
}

export function InsightsPanel({
  insights = [
    {
      icon: <TrendingUp className="h-4 w-4 text-blue-500" />,
      title: "Peak Hours",
      description: "Demand peaks between 7-9 AM and 5-7 PM on weekdays",
    },
    {
      icon: <Cloud className="h-4 w-4 text-gray-500" />,
      title: "Weather Impact",
      description: "Clear weather increases demand by 30-40%",
    },
    {
      icon: <Clock className="h-4 w-4 text-orange-500" />,
      title: "Weekend Pattern",
      description: "Weekend demand is 15-20% higher than weekdays",
    },
  ],
}: InsightsPanelProps) {
  return (
    <Card className="shadow-card">
      <CardHeader>
        <div className="flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-primary" />
          <CardTitle className="text-base">Key Insights</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {insights.map((insight, idx) => (
            <div key={idx} className="flex gap-3 pb-3 last:pb-0 border-b last:border-0">
              <div className="flex-shrink-0 pt-0.5">{insight.icon}</div>
              <div>
                <p className="font-medium text-sm text-foreground">
                  {insight.title}
                </p>
                <p className="text-sm text-muted-foreground">
                  {insight.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
