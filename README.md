# Daily Email News Digests

This project is an Azure Function App designed to automatically fetch news items from a specified API and send them as daily email digests. It runs on a schedule, making it a "set and forget" solution for staying updated on various topics.

## Features

* **Scheduled Execution:** Uses an Azure Functions Timer Trigger to run automatically at a configured time.
* **Dynamic Content:** Fetches the latest news items from a configurable API endpoint.
* **Formatted Emails:** Sends multipart emails containing both HTML and plain text versions of the digest.
* **Timezone Aware:** The schedule can be configured to run in a specific timezone (e.g., New York time), correctly handling Daylight Saving Time.
* **Robust Configuration:** Uses environment variables for easy configuration in both local and cloud environments.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing.

### Prerequisites

* Python 3.12+
* Poetry for dependency management
* Azure Functions Core Tools
* Azurite for local Azure Storage emulation
* An API endpoint providing daily news items

### Installation & Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/tomboone/dailyEmailNewsDigests.git
    cd dailyEmailNewsDigests
    ```
2. **Install dependencies:** Poetry will create a virtual environment and install the required packages.
    ```bash
    poetry install
    ```
3. **Configure local settings:** Create a ``local.settings.json file`` in the root of the project. This file stores your local environment variables and is ignored by Git.
    ```json
    {
      "IsEncrypted": false,
      "Values": {
        "AzureWebJobsStorage": "UseDevelopmentStorage=true",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "WEBSITE_TIME_ZONE": "Eastern Standard Time",
        "DIGESTS_NCRON": "0 0 10 * * *",
        "ENDPOINT": "YOUR_API_ENDPOINT_HERE",
        "KEY": "YOUR_API_KEY_HERE",
        "SENDER": "sender@example.com",
        "SMTP_SERVER": "smtp.example.com",
        "SMTP_USER": "your_smtp_user",
        "SMTP_PWD": "your_smtp_password",
        "SMTP_PORT": "587"
      }
    }
    ```

### Running Locally

1. **Start the storage emulator:** Open a new terminal and start Azurite. The timer trigger requires this to manage its schedule.
    ```bash
    azurite
    ```
2. Run the Function App: In your project directory, run the following command. The host will start, discover your functions, and wait for the timer to trigger.
    ```bash
    func start
    ```

## Configuration

The application is configured via environment variables, which are loaded from `local.settings.json`. These variables can be set during local development or from Application Settings in Azure.

* `DIGESTS_NCRON`: The NCronTab schedule for the timer trigger (e.g., `0 0 10 * * *` for 10:00 AM).
* `WEBSITE_TIME_ZONE`: (Optional) The timezone for the schedule (e.g., `"Eastern Standard Time"`).
* `ENDPOINT`: The base URL for the news API.
* `KEY`: The API key for authenticating with the news API.
* `SENDER`: The "From" email address for the digests.
* `SMTP_SERVER`: The hostname of your SMTP server.
* `SMTP_USER`: The username for SMTP authentication.
* `SMTP_PWD`: The password for SMTP authentication.
* `SMTP_PORT`: The port for the SMTP server.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Tom Boone.