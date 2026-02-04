"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import { Spinner } from "@/components/ui/spinner";

// Public routes that don't require authentication
const publicRoutes = ["/", "/login", "/register", "/verify"];

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, isLoading, setLoading, tokens } = useAuthStore();

  useEffect(() => {
    // Check if route is public
    const isPublicRoute = publicRoutes.some(
      (route) => pathname === route || pathname.startsWith("/verify/")
    );

    // Initialize - check if we have stored tokens
    if (isLoading) {
      // Short delay to allow hydration
      const timer = setTimeout(() => {
        setLoading(false);
      }, 100);
      return () => clearTimeout(timer);
    }

    // Redirect logic
    if (!isLoading) {
      if (!isAuthenticated && !isPublicRoute) {
        // Not authenticated and trying to access protected route
        router.push("/login");
      } else if (isAuthenticated && (pathname === "/login" || pathname === "/register")) {
        // Authenticated but on login/register page
        router.push("/dashboard");
      }
    }
  }, [isAuthenticated, isLoading, pathname, router, setLoading, tokens]);

  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  return <>{children}</>;
}
