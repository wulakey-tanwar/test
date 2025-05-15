# Step 1: Build the app

FROM node:22-alpine AS builder



# Set working directory

WORKDIR /app



# Copy package.json and lock file

COPY package*.json ./



# Install dependencies

RUN npm install



# Copy the rest of the application

COPY . .



# Build the Vite app

RUN npm run build



# Step 2: Serve the app with a lightweight web server

# Step 2: Serve the app with Nginx
FROM nginx:stable-alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built Vite app from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]