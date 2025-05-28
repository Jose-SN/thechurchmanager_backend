# Use an official Node.js runtime as a parent image
FROM node:18.20.3

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the container
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Build the TypeScript files
RUN npm run build

# Expose port 5000 for the application
EXPOSE 5000

# Set the default command to start the application
CMD ["npm", "run", "start"]
