import { useState } from "react";
import { TrendingUp, Loader2 } from "lucide-react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { seasons, weatherConditions, hours, months, weekdays } from "@/lib/mockData";
import { getPrediction } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export default function Prediction() {
  const [isHourly, setIsHourly] = useState(true);
  const [prediction, setPrediction] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();
  const [inputs, setInputs] = useState({
    season: "",
    hour: "",
    month: "",
    weekday: "",
    weather: "",
    temperature: "20",
    humidity: "50",
    workingDay: "yes",
  });

  const handleInputChange = (key: string, value: string) => {
    setInputs((prev) => ({ ...prev, [key]: value }));
    setPrediction(null);
    setError(null);
  };

  const validateInputs = (): boolean => {
    if (!inputs.season || !inputs.weather) {
      return false;
    }
    if (isHourly && !inputs.hour) {
      return false;
    }
    if (!isHourly && (!inputs.month || !inputs.weekday)) {
      return false;
    }
    return true;
  };

  const handlePredict = async () => {
    if (!validateInputs()) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const result = await getPrediction(inputs, isHourly);
      
      if (result.success) {
        setPrediction(result.prediction);
        toast({
          title: "Prediction Generated",
          description: "Demand prediction calculated successfully.",
        });
      } else {
        setError(result.error || "Failed to generate prediction");
        toast({
          title: "Prediction Failed",
          description: result.error || "Failed to generate prediction",
          variant: "destructive",
        });
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to connect to backend";
      setError(errorMessage);
      toast({
        title: "Connection Error",
        description: "Could not connect to the prediction server. Please ensure the backend is running.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Demand Prediction</h1>
          <p className="text-muted-foreground mt-1">
            Predict bike-sharing demand based on weather and temporal factors
          </p>
        </div>

        {/* Toggle Switch */}
        <Card className="shadow-card">
          <CardContent className="py-4">
            <div className="flex items-center justify-center gap-4">
              <span className={`text-sm font-medium ${!isHourly ? "text-muted-foreground" : "text-foreground"}`}>
                Hourly Prediction
              </span>
              <Switch
                checked={!isHourly}
                onCheckedChange={(checked) => {
                  setIsHourly(!checked);
                  setPrediction(null);
                }}
              />
              <span className={`text-sm font-medium ${isHourly ? "text-muted-foreground" : "text-foreground"}`}>
                Daily Prediction
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Input Form */}
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="text-lg">
              {isHourly ? "Hourly" : "Daily"} Prediction Inputs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Season</Label>
                <Select value={inputs.season} onValueChange={(v) => handleInputChange("season", v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select season" />
                  </SelectTrigger>
                  <SelectContent>
                    {seasons.map((s) => (
                      <SelectItem key={s.value} value={s.value}>
                        {s.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {isHourly ? (
                <div className="space-y-2">
                  <Label>Hour</Label>
                  <Select value={inputs.hour} onValueChange={(v) => handleInputChange("hour", v)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select hour" />
                    </SelectTrigger>
                    <SelectContent>
                      {hours.map((h) => (
                        <SelectItem key={h.value} value={h.value}>
                          {h.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              ) : (
                <>
                  <div className="space-y-2">
                    <Label>Month</Label>
                    <Select value={inputs.month} onValueChange={(v) => handleInputChange("month", v)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select month" />
                      </SelectTrigger>
                      <SelectContent>
                        {months.map((m) => (
                          <SelectItem key={m.value} value={m.value}>
                            {m.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Weekday</Label>
                    <Select value={inputs.weekday} onValueChange={(v) => handleInputChange("weekday", v)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select weekday" />
                      </SelectTrigger>
                      <SelectContent>
                        {weekdays.map((w) => (
                          <SelectItem key={w.value} value={w.value}>
                            {w.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </>
              )}

              <div className="space-y-2">
                <Label>Weather Situation</Label>
                <Select value={inputs.weather} onValueChange={(v) => handleInputChange("weather", v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select weather" />
                  </SelectTrigger>
                  <SelectContent>
                    {weatherConditions.map((w) => (
                      <SelectItem key={w.value} value={w.value}>
                        {w.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Temperature (°C)</Label>
                <Input
                  type="number"
                  value={inputs.temperature}
                  onChange={(e) => handleInputChange("temperature", e.target.value)}
                  placeholder="Enter temperature"
                />
              </div>

              <div className="space-y-2">
                <Label>Humidity (%)</Label>
                <Input
                  type="number"
                  value={inputs.humidity}
                  onChange={(e) => handleInputChange("humidity", e.target.value)}
                  placeholder="Enter humidity"
                  min="0"
                  max="100"
                />
              </div>

              <div className="space-y-2">
                <Label>Working Day</Label>
                <Select value={inputs.workingDay} onValueChange={(v) => handleInputChange("workingDay", v)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="yes">Yes</SelectItem>
                    <SelectItem value="no">No (Weekend/Holiday)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button 
              onClick={handlePredict} 
              className="mt-6 w-full sm:w-auto"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Predicting...
                </>
              ) : (
                <>
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Predict Demand
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Error Message */}
        {error && (
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Prediction Result */}
        {prediction !== null && !error && (
          <Card className="shadow-card border-l-4 border-l-accent">
            <CardContent className="py-6">
              <div className="text-center">
                <p className="text-sm text-muted-foreground font-medium">
                  Predicted Bike Rentals
                </p>
                <p className="mt-2 text-4xl font-bold text-primary">
                  {Math.round(prediction).toLocaleString()}
                </p>
                <p className="mt-1 text-sm text-muted-foreground">
                  {isHourly ? "bikes/hour" : "bikes/day"}
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}
