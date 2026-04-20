# Multi-stage build for Next.js Frontend
# Optimized for production deployment with minimal size

# ============================================
# Stage 1: Dependencies - Install packages
# ============================================
FROM node:18-alpine AS deps

# Install libc6-compat for Alpine compatibility
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files
COPY apps/web/package*.json ./

# Install full dependency set for the build stage
RUN npm ci && \
    npm cache clean --force

# ============================================
# Stage 2: Builder - Build the application
# ============================================
FROM node:18-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application code
COPY apps/web/ ./

# Set build-time environment variables
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_SUPABASE_URL
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL \
    NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY \
    NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production

# Build the Next.js application
RUN npm run build

# ============================================
# Stage 3: Runner - Minimal production image
# ============================================
FROM node:18-alpine AS runner

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs && \
    mkdir -p /app/.next && \
    chown -R nextjs:nodejs /app

# Set runtime environment
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Copy package files and production-ready node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

# Copy built application from builder
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder /app/next.config.ts ./

# Remove development-only dependencies before runtime
RUN npm prune --omit=dev

# Switch to non-root user
USER nextjs

# Expose Next.js port
EXPOSE 3000

# Health check (Next.js built-in health endpoint)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Set runtime environment variables
ENV PORT=3000 \
    HOSTNAME="0.0.0.0"

# Start the Next.js application
CMD ["npm", "start"]
