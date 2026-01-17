import { ReactNode } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface SummaryCardProps {
  icon: ReactNode;
  title: string;
  value: string | number;
  description?: string;
  trend?: "up" | "down" | "neutral";
  className?: string;
}

export function SummaryCard({
  icon,
  title,
  value,
  description,
  trend,
  className = "",
}: SummaryCardProps) {
  return (
    <Card className={`shadow-card ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
          <div className="text-primary">{icon}</div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-1">
          <div className="text-2xl font-bold text-foreground">{value}</div>
          {description && (
            <p className="text-xs text-muted-foreground">{description}</p>
          )}
          {trend && (
            <div className={`text-xs font-semibold ${
              trend === "up" ? "text-green-600" :
              trend === "down" ? "text-red-600" :
              "text-muted-foreground"
            }`}>
              {trend === "up" ? "↑" : trend === "down" ? "↓" : "→"} {trend}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
