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

FROM nginx:stable-alpine



# Remove default nginx static assets

RUN rm -rf /usr/share/nginx/html/*



# Copy built assets from builder

COPY --from=builder /app/dist /usr/share/nginx/html




# Expose port

EXPOSE 80



# Start nginx server

CMD ["nginx", "-g", "daemon off;"]