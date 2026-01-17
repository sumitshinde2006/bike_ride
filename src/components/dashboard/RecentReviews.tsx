import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Review {
  id: number;
  name: string;
  rating: number;
  comment: string;
  date: string;
}

interface RecentReviewsProps {
  reviews?: Review[];
}

export function RecentReviews({
  reviews = [
    {
      id: 1,
      name: "John Smith",
      rating: 5,
      comment: "Great platform for bike sharing analytics!",
      date: "2024-01-15",
    },
    {
      id: 2,
      name: "Sarah Johnson",
      rating: 4,
      comment: "Very accurate predictions. Minor UI improvements needed.",
      date: "2024-01-14",
    },
    {
      id: 3,
      name: "Mike Brown",
      rating: 5,
      comment: "The chatbot feature is incredibly helpful!",
      date: "2024-01-13",
    },
  ],
}: RecentReviewsProps) {
  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="text-base">Recent Reviews</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {reviews.map((review) => (
            <div
              key={review.id}
              className="pb-4 border-b last:border-0 last:pb-0"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="font-medium text-sm text-foreground">
                    {review.name}
                  </p>
                  <p className="text-xs text-muted-foreground">{review.date}</p>
                </div>
                <div className="text-sm font-semibold text-yellow-500">
                  {"★".repeat(review.rating)}{"☆".repeat(5 - review.rating)}
                </div>
              </div>
              <p className="text-sm text-muted-foreground">{review.comment}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
