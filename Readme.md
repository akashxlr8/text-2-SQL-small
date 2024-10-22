# Natural Language CSV Query Engine

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🧠 Overview

The **Natural Language CSV Query Engine** is a Python application designed to empower users to interact with CSV datasets using plain English. By integrating AI-driven agents, the system translates natural language questions into SQL queries, executes them on a SQLite database, and presents the results in an intuitive manner.

## 🔍 Features

- **Natural Language Interface:** Ask questions in everyday language and receive data-driven answers.
- **AI-Powered SQL Generation:** Utilizes AI models to convert natural language queries into accurate SQL statements.
- **CSV to SQLite Conversion:** Easily transform CSV files into structured SQLite databases for efficient querying.
- **Error Handling & Correction:** Automatically detects and corrects SQL errors, enhancing reliability and user experience.
- **Configurable Logging:** Adjustable logging levels to manage verbosity and facilitate debugging.
- **Modular Design:** Clean and organized code structure for easy maintenance and scalability.

## 🚀 Getting Started

### 📦 Prerequisites

- Python 3.7+
- Virtual Environment tool (optional but recommended)

### 🛠 Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/natural-language-csv-query-engine.git
   cd natural-language-csv-query-engine
   ```

2. **Create a Virtual Environment (Optional):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables:**
   
   Create a `.env` file in the project root and add your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key
   JINA_API_KEY=your_jina_api_key
   ```

### 🎯 Usage

1. **Prepare Your CSV File:**
   
   Ensure your CSV file is placed in the designated directory (e.g., `data/healthcare_dataset.csv`).

2. **Run the Application:**
   ```bash
   python main.py
   ```

3. **Interact with the Query Engine:**
   
   - Enter your natural language queries when prompted.
   - Type `exit` to terminate the application.

### 📝 Example


Enter your prompt: How many patients were discharged last month?



## 📂 Project Structure
```
├── data/
│ └── healthcare_dataset.csv
├── db_maker.py
├── main.py
├── requirements.txt
├── README.md
└── .env
```


- **`db_maker.py`**: Handles CSV to SQLite conversion and SQL query execution.
- **`main.py`**: Orchestrates user interaction, query generation, and result presentation.
- **`requirements.txt`**: Lists all Python dependencies.
- **`data/`**: Contains CSV datasets for querying.

## 🛡 Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📧 Contact

For any questions or suggestions, feel free to reach out at [your.email@example.com](mailto:your.email@example.com).
