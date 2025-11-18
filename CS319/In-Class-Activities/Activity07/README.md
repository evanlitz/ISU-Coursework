# Activity 07 - REST API with Node.js and Express

A simple REST API application demonstrating basic Express.js concepts including routing, middleware, and JSON data handling.

## Overview

This project is an in-class activity for CS319 at Iowa State University. It implements a Node.js server using Express.js that provides REST API endpoints for retrieving robot product data and person information.

## Features

- Express.js REST API server
- CORS support for cross-origin requests
- JSON data parsing with body-parser middleware
- File system integration for reading JSON data
- Multiple API endpoints demonstrating GET requests

## Prerequisites

- Node.js (v14 or higher recommended)
- npm (Node Package Manager)

## Installation

1. Clone or download the project
2. Navigate to the project directory:
   ```bash
   cd Activity07
   ```
3. Install dependencies:
   ```bash
   npm install
   ```

## Usage

Start the server:
```bash
node bubaq_Activity07.js
```

The server will start at `http://localhost:8080`

## API Endpoints

### GET `/`
Returns a styled "Hello World" HTML message.

**Response:** HTML content with status 200

---

### GET `/listRobots`
Retrieves a list of robot products from the `robots.json` file.

**Response:** JSON array of robot objects
```json
[
  {
    "id": 1,
    "name": "Robot 1",
    "price": 1999,
    "description": "This is robot 1...",
    "imageUrl": "https://example.com/robot1.jpg"
  }
]
```

---

### GET `/person`
Returns a hardcoded person object.

**Response:** JSON object
```json
{
  "name": "alex",
  "email": "alex@mail.com",
  "job": "software dev"
}
```

## Project Structure

```
Activity07/
├── bubaq_Activity07.js    # Main Express application
├── package.json           # Project configuration and dependencies
├── package-lock.json      # Locked dependency versions
├── robots.json            # Sample robot product data
└── README.md              # This file
```

## Dependencies

- **express** (^5.1.0) - Web framework for Node.js
- **body-parser** (^2.2.0) - Request body parsing middleware
- **cors** (^2.8.5) - Cross-Origin Resource Sharing middleware

## Testing

You can test the API endpoints using curl, Postman, or your browser:

```bash
# Test root endpoint
curl http://localhost:8080/

# Get robot list
curl http://localhost:8080/listRobots

# Get person data
curl http://localhost:8080/person
```

## License

Educational use - Iowa State University CS319
