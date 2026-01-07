import { useState } from "react";
import { Send, Bot, Info } from "lucide-react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { chatMessages } from "@/lib/mockData";
import { cn } from "@/lib/utils";

interface Message {
  id: number;
  type: "user" | "assistant";
  message: string;
}

const staticResponses = [
  "Based on historical data, bike demand peaks between 7-9 AM and 5-7 PM on working days.",
  "Clear weather conditions typically increase bike rentals by 30-40% compared to cloudy days.",
  "Weekend demand is generally 15-20% higher than weekday demand, especially during good weather.",
  "Temperature between 18-25°C shows the highest correlation with increased bike rentals.",
  "Holiday periods show different patterns - morning peaks are delayed and overall demand is more evenly distributed.",
];

export default function Chatbot() {
  const [messages, setMessages] = useState<Message[]>(chatMessages);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      type: "user",
      message: input.trim(),
    };

    // Pick a random static response
    const response = staticResponses[Math.floor(Math.random() * staticResponses.length)];
    const assistantMessage: Message = {
      id: messages.length + 2,
      type: "assistant",
      message: response,
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6 h-[calc(100vh-12rem)] flex flex-col">
        <div>
          <h1 className="text-2xl font-bold text-foreground">RideWise Assistant</h1>
          <p className="text-muted-foreground mt-1">
            Get insights about bike-sharing demand patterns
          </p>
        </div>

        {/* Info Card */}
        <Card className="shadow-card border-l-4 border-l-accent flex-shrink-0">
          <CardContent className="py-3">
            <div className="flex gap-3">
              <Info className="h-5 w-5 text-accent flex-shrink-0 mt-0.5" />
              <p className="text-sm text-muted-foreground">
                The RideWise Assistant provides textual insights to help users understand 
                how weather and temporal factors influence bike-sharing demand.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Chat Interface */}
        <Card className="shadow-card flex-1 flex flex-col min-h-0">
          <CardHeader className="flex-shrink-0 pb-3">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary">
                <Bot className="h-4 w-4 text-primary-foreground" />
              </div>
              <div>
                <CardTitle className="text-base">RideWise Assistant</CardTitle>
                <CardDescription className="text-xs">Demand Insights Bot</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col min-h-0 pt-0">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 pr-2">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={cn(
                    "flex",
                    msg.type === "user" ? "justify-end" : "justify-start"
                  )}
                >
                  <div
                    className={cn(
                      "max-w-[80%] rounded-lg px-4 py-2.5 text-sm",
                      msg.type === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-foreground"
                    )}
                  >
                    {msg.message}
                  </div>
                </div>
              ))}
            </div>

            {/* Input */}
            <div className="flex gap-2 pt-4 flex-shrink-0 border-t mt-4">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about bike demand patterns..."
                className="flex-1"
              />
              <Button onClick={handleSend} size="icon">
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
