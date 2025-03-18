# Notes Management System API

## API service for notes management with analytics and AI summarization.

Notes Management System – allows users to create, edit, and delete notes.
During note updates, it automatically stores the previous version of the note.
Integrated with an AI summarization service to provide summaries of notes.
Provides analytics such as:
	•	Total word count across all notes
	•	Average note length
	•	Most common words or phrases
	•	Identifies the top 3 longest and shortest notes


### Technologies
- FastAPI
- AQLAlchemy
- Alembic
- Pydantic
- NLTK
- Gemini API
- Asyncio




## 📦 &nbsp; Installation

> **Important:**  Make sure [Docker](https://www.docker.com/) is installed and running.

1. Clone the repository:
    ```shell
    git clone https://github.com/mykytaso/notes-management-system.git
    ```
    
    
2. Please make sure to set `src` directory as Source Root in your IDE.
    
    
3. Create and activate virtual environment:
    ```shell
    python3 -m venv .venv
    source .venv/bin/activate
    ```
      
    
    
    
5. Install the required dependencies:
    ```shell
   pip install -r requirements.txt
    ```

4. Set up environment variables:
   - Create a `.env` file.
   - Copy the content from `.env.sample` to `.env`.
   - Update the values in `.env` with your specific configuration.


<br>



## 📡 &nbsp; Available Endpoints

- Documentation: `/docs`
<br>
- `/api/v1/notes` [GET] – List of notes.
- `/api/v1/notes` [POST] – Create a note.
- `/api/v1/notes/{id}` [GET] – Retrieve a note.
- `/api/v1/notes/{id}` [PUT] – Update a note.
- `/api/v1/notes/{id}` [DELETE] – Delete a note.
<br>

- `/api/v1/versions/?note_id={note_id}` [GET] – Get all note versions.
- `/api/v1/versions/?note_id={note_id}&version_id={version_id}` [GET] – Get a one note version.
- `/api/v1/versions/?note_id={note_id}&version_id={version_id}` [DELETE] – Delete a note version.
<br>

- `/api/v1/notes/{id}/summary/?max_words={int}` [GET] – Get a summary of a note. Optional parametr max_words is he maximum number of words in the summary (default: 10)
- `/api/v1/notes/analytics/total-words` [GET] – Get the total word count across all notes.
- `/api/v1/notes/analytics/avg-note-length` [GET] – Get the average note length.
- `/api/v1/notes/analytics/most-common-words-or-phrases/?max_phrase_length={int}` [GET] – Get the most common words or phrases from all notes in the database. Parametr max_phrase_length is the maximum length of phrases to consider, ranging from 1 to 10 words (default: 3 words).
- `/api/v1/notes/analytics/top-3-longest-notes` [GET] – Get the top 3 longest notes.
- `/api/v1/notes/analytics/top-3-shortest-notes` [GET] – Get the top 3 shortest notes.

>**Example:** `http://127.0.0.1:8000/api/v1/notes`

<br>


## 🧪 &nbsp; Testing
The project includes comprehensive unit and integration tests using `pytest`.<br>
Currently, **86%** of the codebase is covered by tests.

**⚠️ IMPORTANT**: Make sure to set the environment variable `ENVIRONMENT=testing` in the `.env` file before running tests. This ensures the use of a temporary in-memory database for testing purposes.

<br>

## 👾 &nbsp; Features
- Asynchronous API
- AI-powered Summarization of notes
- Notes Analytics
- Notes Versioning History to track changes over time
<br>



## ✍️ &nbsp; Author
<img src="https://github.com/mykytaso.png" alt="@mykytaso" width="24" height="24" valign="bottom" /> Mykyta Soloviov <a href="https://github.com/mykytaso">@mykytaso</a>
