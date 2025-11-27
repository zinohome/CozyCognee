# Use an official Node.js runtime as a parent image
FROM node:22-alpine

# Set the working directory to /app
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY ../../project/cognee/cognee-frontend/package.json ../../project/cognee/cognee-frontend/package-lock.json ./

# Install any needed packages specified in package.json
RUN npm ci
RUN npm rebuild lightningcss

# Copy the rest of the application code to the working directory
COPY ../../project/cognee/cognee-frontend/src ./src
COPY ../../project/cognee/cognee-frontend/public ./public
COPY ../../project/cognee/cognee-frontend/next.config.mjs .
COPY ../../project/cognee/cognee-frontend/postcss.config.mjs .
COPY ../../project/cognee/cognee-frontend/tsconfig.json .

# Build the app and run it
CMD ["npm", "run", "dev"]

