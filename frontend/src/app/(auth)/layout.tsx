import { Stethoscope } from "lucide-react";
import Link from "next/link";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-primary/5 to-background">
      {/* Logo */}
      <div className="absolute top-6 left-6">
        <Link href="/" className="flex items-center gap-2">
          <div className="p-2 bg-primary rounded-lg">
            <Stethoscope className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="text-lg font-bold">MediNote AI</span>
        </Link>
      </div>
      {children}
    </div>
  );
}
