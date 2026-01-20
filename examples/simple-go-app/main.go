package main

import (
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"time"
)

const version = "0.0.1"

var htmlTemplate = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Engine - Go App</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a2e2e 0%, #1a4a4a 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #00ffcc;
            padding: 20px;
        }

        .container {
            background: rgba(10, 46, 46, 0.8);
            border: 3px solid #ff1493;
            border-radius: 15px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 0 30px rgba(0, 255, 204, 0.3),
                        0 0 60px rgba(255, 20, 147, 0.2);
            animation: glow 2s ease-in-out infinite alternate;
        }

        @keyframes glow {
            from {
                box-shadow: 0 0 20px rgba(0, 255, 204, 0.3),
                            0 0 40px rgba(255, 20, 147, 0.2);
            }
            to {
                box-shadow: 0 0 30px rgba(0, 255, 204, 0.5),
                            0 0 60px rgba(255, 20, 147, 0.3);
            }
        }

        .header {
            background: linear-gradient(90deg, #00ffcc 0%, #00cc99 100%);
            border: 2px solid #fff;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.5);
        }

        .header h1 {
            color: #0a2e2e;
            font-size: 2em;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .header .subtitle {
            color: #0a2e2e;
            font-size: 0.9em;
            margin-top: 5px;
            opacity: 0.8;
        }

        .info-grid {
            display: grid;
            gap: 15px;
            margin-bottom: 20px;
        }

        .info-item {
            background: rgba(0, 255, 204, 0.1);
            border-left: 4px solid #00ffcc;
            padding: 15px;
            border-radius: 5px;
        }

        .info-item .label {
            color: #ff1493;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }

        .info-item .value {
            color: #00ffcc;
            font-size: 1.2em;
            font-weight: bold;
        }

        .status {
            text-align: center;
            padding: 20px;
            background: rgba(0, 255, 204, 0.1);
            border-radius: 8px;
            margin-top: 20px;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #00ff00;
            border-radius: 50%;
            animation: pulse 1.5s ease-in-out infinite;
            margin-right: 8px;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }

        .footer {
            text-align: center;
            margin-top: 30px;
            color: #00ffcc;
            opacity: 0.7;
            font-size: 0.85em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Go App</h1>
            <div class="subtitle">Code Engine Demo</div>
        </div>

        <div class="info-grid">
            <div class="info-item">
                <div class="label">Version</div>
                <div class="value">{{.Version}}</div>
            </div>

            <div class="info-item">
                <div class="label">Environment</div>
                <div class="value">{{.Environment}}</div>
            </div>

            <div class="info-item">
                <div class="label">Hostname</div>
                <div class="value">{{.Hostname}}</div>
            </div>

            <div class="info-item">
                <div class="label">Timestamp</div>
                <div class="value">{{.Timestamp}}</div>
            </div>
        </div>

        <div class="status">
            <span class="status-indicator"></span>
            <span>System Online</span>
        </div>

        <div class="footer">
            Powered by Go on IBM Code Engine
        </div>
    </div>
</body>
</html>
`

type PageData struct {
	Version     string
	Environment string
	Hostname    string
	Timestamp   string
}

type InfoResponse struct {
	Message     string `json:"message"`
	Version     string `json:"version"`
	Environment string `json:"environment"`
	Hostname    string `json:"hostname"`
	Timestamp   string `json:"timestamp"`
}

type HealthResponse struct {
	Status string `json:"status"`
}

func getEnvironment() string {
	env := os.Getenv("ENVIRONMENT")
	if env == "" {
		return "development"
	}
	return env
}

func getHostname() string {
	hostname, err := os.Hostname()
	if err != nil {
		return "unknown"
	}
	return hostname
}

func indexHandler(w http.ResponseWriter, r *http.Request) {
	tmpl, err := template.New("index").Parse(htmlTemplate)
	if err != nil {
		http.Error(w, "Template parsing error", http.StatusInternalServerError)
		return
	}

	data := PageData{
		Version:     version,
		Environment: getEnvironment(),
		Hostname:    getHostname(),
		Timestamp:   time.Now().UTC().Format("2006-01-02 15:04:05 UTC"),
	}

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	if err := tmpl.Execute(w, data); err != nil {
		http.Error(w, "Template execution error", http.StatusInternalServerError)
		return
	}
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(HealthResponse{Status: "healthy"})
}

func infoHandler(w http.ResponseWriter, r *http.Request) {
	response := InfoResponse{
		Message:     "Hello from Code Engine!",
		Version:     version,
		Environment: getEnvironment(),
		Hostname:    getHostname(),
		Timestamp:   time.Now().UTC().Format(time.RFC3339),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/", indexHandler)
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/api/info", infoHandler)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	addr := fmt.Sprintf("0.0.0.0:%s", port)
	log.Printf("Server starting on %s", addr)
	if err := http.ListenAndServe(addr, nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
