# FastWhisper

A fast speech-to-text transcription service.

## How to Run on Mac

This guide will help you set up and run the FastWhisper application on your macOS system.

### Prerequisites

*   **Python 3.8+**: Ensure you have Python installed. You can download it from [python.org](https://www.python.org/) or use a package manager like Homebrew.
*   **pip**: Python's package installer, usually comes with Python.
*   **Homebrew**: A package manager for macOS, recommended for installing `ffmpeg`. Install it by following instructions on [brew.sh](https://brew.sh/).

### Installation Steps

1.  **Clone the Repository**:
    Open your terminal and clone the FastWhisper repository:
    ```bash
    git clone https://github.com/mayurbt12/fast_whisper.git
    cd fast_whisper
    ```

2.  **Install `ffmpeg`**:
    `ffmpeg` is required for processing video files. Install it using Homebrew:
    ```bash
    brew install ffmpeg
    ```

3.  **Create a Virtual Environment (Recommended)**:
    It's good practice to use a virtual environment to manage dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Install Python Dependencies**:
    Install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the Application**:
    Start the FastAPI application using Uvicorn:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 1990
    ```
    The application will be accessible at `http://0.0.0.0:1990`.

### Usage

Once the server is running, you can interact with the API using tools like `curl`, Postman, or a custom client to send audio/video files for transcription to the `/transcribe/` endpoint.


curl -X POST "http://localhost:1990/transcribe" \
     -F "file=@path_to_audio.mp3"
