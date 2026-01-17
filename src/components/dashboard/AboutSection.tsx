import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export function AboutSection() {
  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="text-lg">About RideWise</CardTitle>
        <CardDescription>
          Intelligent Bike-Sharing Analytics Platform
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h3 className="font-semibold text-foreground mb-2">Project Overview</h3>
          <p className="text-sm text-muted-foreground">
            RideWise is a comprehensive bike-sharing demand prediction and analytics platform
            powered by machine learning models trained on real-world bike rental data. Our system
            provides accurate hourly and daily demand forecasts to optimize bike fleet management.
          </p>
        </div>
        
        <div>
          <h3 className="font-semibold text-foreground mb-2">Key Features</h3>
          <div className="space-y-2">
            <Badge variant="secondary" className="mr-2">ML Predictions</Badge>
            <Badge variant="secondary" className="mr-2">Real-time Analytics</Badge>
            <Badge variant="secondary" className="mr-2">Weather Integration</Badge>
            <Badge variant="secondary" className="mr-2">AI Chatbot</Badge>
            <Badge variant="secondary" className="mr-2">Reservation System</Badge>
          </div>
        </div>

        <div>
          <h3 className="font-semibold text-foreground mb-2">Technologies</h3>
          <p className="text-sm text-muted-foreground">
            Built with React, TypeScript, Vite, Flask, scikit-learn, and Google Gemini API.
            Features real-time backend communication, responsive design, and advanced analytics.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
