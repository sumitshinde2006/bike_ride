import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Review {
  id: number;
  name: string;
  rating: number;
  comment: string;
  date: string;
}

interface ReviewsProps {
  reviews?: Review[];
  title?: string;
}

export function Reviews({
  reviews = [],
  title = "User Reviews",
}: ReviewsProps) {
  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {reviews && reviews.length > 0 ? (
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
        ) : (
          <p className="text-sm text-muted-foreground">No reviews yet</p>
        )}
      </CardContent>
    </Card>
  );
}
