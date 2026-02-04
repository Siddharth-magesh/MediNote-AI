import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";

describe("Card", () => {
  it("renders card with content", () => {
    render(
      <Card>
        <CardContent>Card content</CardContent>
      </Card>
    );
    expect(screen.getByText("Card content")).toBeInTheDocument();
  });

  it("renders full card structure", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Card Title</CardTitle>
          <CardDescription>Card Description</CardDescription>
        </CardHeader>
        <CardContent>Main content</CardContent>
        <CardFooter>Footer content</CardFooter>
      </Card>
    );

    expect(screen.getByText("Card Title")).toBeInTheDocument();
    expect(screen.getByText("Card Description")).toBeInTheDocument();
    expect(screen.getByText("Main content")).toBeInTheDocument();
    expect(screen.getByText("Footer content")).toBeInTheDocument();
  });

  it("applies custom className to Card", () => {
    render(
      <Card className="custom-card" data-testid="card">
        Content
      </Card>
    );
    expect(screen.getByTestId("card")).toHaveClass("custom-card");
  });

  it("applies custom className to CardHeader", () => {
    render(
      <CardHeader className="custom-header" data-testid="header">
        Header
      </CardHeader>
    );
    expect(screen.getByTestId("header")).toHaveClass("custom-header");
  });

  it("applies custom className to CardTitle", () => {
    render(
      <CardTitle className="custom-title" data-testid="title">
        Title
      </CardTitle>
    );
    expect(screen.getByTestId("title")).toHaveClass("custom-title");
  });

  it("applies custom className to CardContent", () => {
    render(
      <CardContent className="custom-content" data-testid="content">
        Content
      </CardContent>
    );
    expect(screen.getByTestId("content")).toHaveClass("custom-content");
  });

  it("applies custom className to CardFooter", () => {
    render(
      <CardFooter className="custom-footer" data-testid="footer">
        Footer
      </CardFooter>
    );
    expect(screen.getByTestId("footer")).toHaveClass("custom-footer");
  });

  it("renders with default border and rounded styles", () => {
    render(
      <Card data-testid="card">
        Content
      </Card>
    );
    const card = screen.getByTestId("card");
    expect(card).toHaveClass("rounded-lg");
    expect(card).toHaveClass("border");
  });
});
