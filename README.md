# Stock Alert Bot

Stock Alert Bot is a Discord bot built with Python that delivers real-time stock price alerts directly to your Discord server. Leveraging the Discord API, yFinance for market data, MongoDB for scalable alert storage, and Pandas for efficient data manipulation, this bot provides a robust solution for managing user-generated stock alerts.

## Features

- **Real-Time Stock Alerts:**  
  Continuously monitors stock prices with a background task that checks every 5 seconds and sends notifications when prices meet alert conditions.

- **Asynchronous & Event-Driven:**  
  Built on Python's `asyncio` to handle multiple concurrent operations—ensuring low latency and responsive user interactions.

- **Custom Caching Layer:**  
  Implements a TTL-based caching mechanism (via a custom `PriceCache` class) to reduce redundant API calls and improve performance.

- **Robust Database Integration:**  
  Utilizes MongoDB to perform CRUD operations for user-generated alerts, enabling efficient management and scalability.

- **Modular Design:**  
  Organized into separate modules (commands, tasks, and utilities) for maintainability and ease of extension.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Commands](#commands)


## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/mthwtsng/StockAlertBot
    cd stock-alert-bot
    ```

2. **Create and Activate a Virtual Environment**

    ```bash
    python -m venv venv
    ```

    # On macOS/Linux:
    ```bash
    source venv/bin/activate
    ```

    # On Windows:
    ```bash
    venv\Scripts\activate
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration
 Before running the bot, configure your credentials and settings:

- **Discord Bot Token:**
Update the BOT_TOKEN in config.py with your Discord bot token.

- **MongoDB URI:**
Set your MongoDB connection string in config.py.

- **Cache Settings:**
Adjust CACHE_TTL (time-to-live) for the caching system if needed.

Example `config.py`:

```bash
# config.py
BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN"
MONGO_URI = "YOUR_MONGODB_URI"
CACHE_TTL = 30  # Time-to-live for cached stock prices in seconds
```

## Commands

Stock Alert Bot provides the following commands to manage stock alerts and retrieve real-time market data.

### 🔔 Alert Commands

- **`!add_alert <symbol> <price>`**  
  Sets an alert for a specific stock price. The bot will notify you when the stock reaches the specified price.  
  **Example:**  
  ```plaintext
  !add_alert AAPL 150

- **`!list_alerts`**  
  Lists all existing alerts that have been created within the channel 


- **`!delete_alert <symbol> <price>`**  
  Deletes an alert set for a specific stock price. 
  **Example:**  
  ```plaintext
  !remove_alert AAPL 150

- **`!delete_all` (SERVER ADMIN(S) ONLY)**
  Deletes all alerts that are set within the channel
  

**More to come ...** 
