"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import { authApi } from "@/lib/api";
import { queryKeys } from "@/lib/queryClient";
import type { LoginCredentials, RegisterData } from "@/types";

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const {
    user,
    tokens,
    isAuthenticated,
    isLoading,
    login: setLogin,
    logout: clearAuth,
    setLoading,
  } = useAuthStore();

  // Query for current user (validates token)
  const { refetch: refetchUser } = useQuery({
    queryKey: queryKeys.auth.me(),
    queryFn: authApi.getMe,
    enabled: isAuthenticated && !!tokens?.access_token,
    retry: false,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (credentials: LoginCredentials) => authApi.login(credentials),
    onSuccess: ({ user, tokens }) => {
      setLogin(user, tokens);
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.all });
      router.push("/dashboard");
    },
    onError: () => {
      clearAuth();
    },
  });

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: (data: RegisterData) => authApi.register(data),
    onSuccess: () => {
      router.push("/login?registered=true");
    },
  });

  // Logout function
  const logout = () => {
    clearAuth();
    queryClient.clear();
    router.push("/login");
  };

  // Change password mutation
  const changePasswordMutation = useMutation({
    mutationFn: ({
      currentPassword,
      newPassword,
    }: {
      currentPassword: string;
      newPassword: string;
    }) => authApi.changePassword(currentPassword, newPassword),
  });

  // Initialize auth from persisted state
  const initAuth = async () => {
    setLoading(true);
    if (tokens?.access_token) {
      try {
        await refetchUser();
      } catch {
        clearAuth();
      }
    }
    setLoading(false);
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    login: loginMutation.mutate,
    loginAsync: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error,
    register: registerMutation.mutate,
    registerAsync: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    registerError: registerMutation.error,
    logout,
    changePassword: changePasswordMutation.mutate,
    isChangingPassword: changePasswordMutation.isPending,
    changePasswordError: changePasswordMutation.error,
    initAuth,
  };
}
