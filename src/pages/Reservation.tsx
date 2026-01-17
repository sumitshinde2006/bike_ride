import { useState } from "react";
import { CalendarCheck, Info } from "lucide-react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { timeSlots, stations } from "@/lib/mockData";
import { cn } from "@/lib/utils";

type DemandLevel = "Low" | "Medium" | "High";

export default function Reservation() {
  const [date, setDate] = useState("");
  const [timeSlot, setTimeSlot] = useState("");
  const [station, setStation] = useState("");
  const { toast } = useToast();

  // Mock demand calculation based on selections
  const getDemandLevel = (): DemandLevel | null => {
    if (!timeSlot) return null;
    if (timeSlot === "morning" || timeSlot === "evening") return "High";
    return "Medium";
  };

  const demandLevel = getDemandLevel();

  const handleReserve = () => {
    if (!date || !timeSlot || !station) {
      toast({
        title: "Missing Information",
        description: "Please fill in all fields to make a reservation.",
        variant: "destructive",
      });
      return;
    }

    toast({
      title: "Reservation Confirmed!",
      description: `Your bike has been reserved at ${stations.find(s => s.value === station)?.label} for ${timeSlots.find(t => t.value === timeSlot)?.label}.`,
    });
  };

  const demandStyles: Record<DemandLevel, string> = {
    Low: "bg-success text-success-foreground",
    Medium: "bg-warning text-warning-foreground",
    High: "bg-destructive text-destructive-foreground",
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Bike Reservation</h1>
          <p className="text-muted-foreground mt-1">
            Reserve a bike based on predicted demand availability
          </p>
        </div>

        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="text-lg">Make a Reservation</CardTitle>
            <CardDescription>
              Choose your preferred date, time, and pickup location
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="date">Date</Label>
                <Input
                  id="date"
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label>Time Slot</Label>
                <Select value={timeSlot} onValueChange={setTimeSlot}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select time slot" />
                  </SelectTrigger>
                  <SelectContent>
                    {timeSlots.map((slot) => (
                      <SelectItem key={slot.value} value={slot.value}>
                        {slot.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2 sm:col-span-2">
                <Label>Pickup Station</Label>
                <Select value={station} onValueChange={setStation}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select station" />
                  </SelectTrigger>
                  <SelectContent>
                    {stations.map((s) => (
                      <SelectItem key={s.value} value={s.value}>
                        {s.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Demand Indicator */}
            {demandLevel && (
              <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/50">
                <span className="text-sm text-muted-foreground">Expected Demand:</span>
                <span
                  className={cn(
                    "px-3 py-1 rounded-full text-xs font-medium",
                    demandStyles[demandLevel]
                  )}
                >
                  {demandLevel}
                </span>
              </div>
            )}

            <Button onClick={handleReserve} className="w-full sm:w-auto">
              <CalendarCheck className="h-4 w-4 mr-2" />
              Reserve Bike
            </Button>
          </CardContent>
        </Card>

        {/* Info Card */}
        <Card className="shadow-card border-l-4 border-l-accent">
          <CardContent className="py-4">
            <div className="flex gap-3">
              <Info className="h-5 w-5 text-accent flex-shrink-0 mt-0.5" />
              <p className="text-sm text-muted-foreground">
                Demand-based reservation helps optimize bike availability across all stations. 
                Reserving during off-peak hours increases your chances of bike availability and 
                may offer shorter wait times.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
