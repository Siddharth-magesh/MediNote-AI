import { describe, it, expect, beforeEach, vi } from "vitest";
import { useAuthStore } from "@/stores/authStore";

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, "localStorage", { value: localStorageMock });

describe("authStore", () => {
  beforeEach(() => {
    localStorageMock.clear();
    // Reset the store
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it("has correct initial state", () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.refreshToken).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.isLoading).toBe(false);
  });

  it("sets user and tokens on login", () => {
    const { setAuth } = useAuthStore.getState();

    setAuth({
      user: { id: "1", email: "test@example.com", name: "Test User" },
      accessToken: "access-token",
      refreshToken: "refresh-token",
    });

    const state = useAuthStore.getState();
    expect(state.user?.email).toBe("test@example.com");
    expect(state.accessToken).toBe("access-token");
    expect(state.refreshToken).toBe("refresh-token");
    expect(state.isAuthenticated).toBe(true);
  });

  it("clears state on logout", () => {
    const { setAuth, logout } = useAuthStore.getState();

    // Login first
    setAuth({
      user: { id: "1", email: "test@example.com", name: "Test User" },
      accessToken: "access-token",
      refreshToken: "refresh-token",
    });

    // Logout
    logout();

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.refreshToken).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it("updates access token", () => {
    const { setAuth, setAccessToken } = useAuthStore.getState();

    setAuth({
      user: { id: "1", email: "test@example.com", name: "Test User" },
      accessToken: "old-token",
      refreshToken: "refresh-token",
    });

    setAccessToken("new-token");

    const state = useAuthStore.getState();
    expect(state.accessToken).toBe("new-token");
  });

  it("sets loading state", () => {
    const { setLoading } = useAuthStore.getState();

    setLoading(true);
    expect(useAuthStore.getState().isLoading).toBe(true);

    setLoading(false);
    expect(useAuthStore.getState().isLoading).toBe(false);
  });

  it("updates user data", () => {
    const { setAuth, updateUser } = useAuthStore.getState();

    setAuth({
      user: { id: "1", email: "test@example.com", name: "Test User" },
      accessToken: "token",
      refreshToken: "refresh",
    });

    updateUser({ name: "Updated Name" });

    const state = useAuthStore.getState();
    expect(state.user?.name).toBe("Updated Name");
    expect(state.user?.email).toBe("test@example.com"); // unchanged
  });
});
