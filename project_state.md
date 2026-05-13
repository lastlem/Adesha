# Project State: Cozy Corner

## 🌟 Overview
**Cozy Corner** is a personalized, romantic web application designed for a long-distance relationship. The application features an interactive "Open When..." envelope system, allowing partners to leave love letters, images, and voice notes for each other in a dreamy, "kawaii" digital environment.

## 🛠️ Technical Stack
- **Backend**: Python / Flask
- **Database**: SQLite (via `sqlite3`)
- **Frontend**: HTML5 / Tailwind CSS (CDN) / Vanilla JavaScript
- **Storage**: Local filesystem for media uploads (Images/Audio)

## 🏛️ Project Architecture

### 1. Database Schema (`db.py`)
The application uses a single SQLite table `envelopes` to store all content.
| Field | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | Unique identifier | PRIMARY KEY, AUTOINCREMENT |
| `title` | TEXT | The "Open When..." trigger | NOT NULL |
| `text_message` | TEXT | The main romantic content | NOT NULL |
| `recipient` | TEXT | Who the envelope is for ('adesha' or 'levon') | NOT NULL |
| `image_path` | TEXT | Path to associated image file | NULLABLE |
| `audio_path` | TEXT | Path to associated audio file | NULLABLE |

### 2. Backend API (`app.py`)
The backend serves as a REST API that manages content and file uploads.
- **Routes**:
  - `/adesha`: Renders the personalized page for Adesha.
  - `/levon`: Renders the personalized page for Levon.
- **API Endpoints**:
  - `GET /api/envelopes/<recipient>`: Retrieves all envelopes filtered by the recipient.
  - `POST /api/envelopes`: Creates a new envelope. Handles `multipart/form-data` for file uploads.
  - `PUT /api/envelopes/<id>`: Updates an existing envelope's content or files.
  - `DELETE /api/envelopes/<id>`: Permanently removes an envelope.
- **File Handling**: Uploads are saved to `static/uploads/` with a UUID prefix to prevent filename collisions.

### 3. User Interface & Experience (`templates/user_page.html`)
The frontend uses a single, unified template to provide a consistent experience for both users.
- **Personalization**: The page dynamically adapts based on the `user` variable passed from the backend.
- **Core Features**:
  - **Envelope Grid**: A responsive layout showing all love letters meant for the current user.
  - **View Modal**: A glassmorphic modal that opens when a letter is clicked, displaying the message and playing associated media.
  - **CRUD Management**: Users can add, edit, and delete envelopes directly from their own page.
  - **Navigation**: A "Switch Corner" button allows seamless switching between Adesha's and Levon's views.
  - **Custom Modals**: All system notifications, error messages, and deletion confirmations are handled via custom-themed modals to avoid browser default alerts.

## 🎨 Aesthetic & Design
The UI is designed with a "Kawaii/Cozy" aesthetic to evoke warmth and romance.
- **Color Palette**: A muted romantic palette using linear gradients of soft pink (`#fbcfe8`), lavender (`#ddd6fe`), and baby blue (`#e0e7ff`).
- **Animations**:
  - **Background**: An animated, shifting gradient background.
  - **Atmosphere**: A JavaScript-powered system that spawns rising hearts that drift upwards.
  - **UI Motion**: "Floating" animations for characters and cards, with cubic-bezier transitions on hover for a "bouncy" feel.
- **Visual Elements**:
  - **Glassmorphism**: Cards and modals use backdrop-blur and semi-transparent white backgrounds.
  - **Characters**: Integrated floating character placeholders (Chiikawa, Hachiware, Usagi, and Chopper).

## 🚀 How to Run
1. Install dependencies: `pip install flask`
2. Run the application: `python app.py`
3. Visit `http://localhost:5000/adesha` for Adesha's view.
4. Visit `http://localhost:5000/levon` for Levon's view.

## 🛠️ Recent Improvements
- **Unified Templates**: Merged `index.html` and `admin.html` into `user_page.html` for better maintainability and a consistent user experience.
- **Full CRUD Access**: Enabled editing and deleting of envelopes for both users.
- **Layout Fix**: Resolved a scrollbar oscillation issue by containing background heart animations within an overflow-hidden container.
- **Custom UI Dialogs**: Replaced standard JavaScript `alert()` and `confirm()` with themed custom modals.
- **Bug Fixes**: Fixed an issue where envelopes were not being created on the management page due to a missing `recipient` field.
