import { betterAuth } from "better-auth";

/**
 * Better Auth configuration
 * Configured for JWT-based authentication with httpOnly cookies
 */
export const auth = betterAuth({
  database: {
    // Better Auth will use the backend API for authentication
    // We don't need a database connection here
    provider: "sqlite",
    url: ":memory:",
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Disabled for MVP
  },
  session: {
    expiresIn: 60 * 60 * 24, // 24 hours
    updateAge: 60 * 60, // Update session every hour
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },
  advanced: {
    cookiePrefix: "todo_app",
    useSecureCookies: process.env.NODE_ENV === "production",
  },
});

export type Session = typeof auth.$Infer.Session;
