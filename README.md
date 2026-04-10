# 🚀 Hangarin Workspace
**Modern Task Orchestration | High-Velocity Productivity**

**Hangarin** is a high-performance dashboard designed for teams who value aesthetic clarity and real-time efficiency. Built with a **Glassmorphism UI**, it provides a seamless experience for tracking roadmaps and managing complex workflows.

---

## ✨ Key Features

* **⚡ Real-Time Interaction:** Powered by **HTMX** for instant updates without page refreshes.
* **🔐 Secure Multi-Auth:** Integrated **Google** and **GitHub** OAuth for frictionless onboarding.
* **🎯 Focus Mode:** A distraction-free toggle to highlight your most critical tasks and silence the noise.
* **📊 Velocity Tracking:** Automated progress bars that dynamically calculate project completion percentages.
* **🎨 Dynamic Design:** Priority colors and Category tags are managed directly from the Django Admin.
* **📁 Task Intelligence:** Integrated sidebar for subtasks, notes, and quick-edit functionality.
* **🌓 Modern UI/UX:** Built with Tailwind CSS for a glassmorphism-inspired aesthetic.
* **⚙️ Full-Cycle Management:** Architected to Create, View, Modify, and Remove tasks instantly via an HTMX-enhanced interface.

## 🛠 Tech Stack
**Backend:** Python 3.10+, Django 5.1+ (Django Allauth)

**Frontend:** Tailwind CSS, Alpine.js, HTMX

**Database:** SQLite (Development) / PostgreSQL (Production)

**Deployment:** PythonAnywhere / GitHub Actions

---

## 🔐 Authentication & Access

Manage your priorities, users, and social application credentials through the secure portal. 

### Social Login Providers
* **Google OAuth 2.0**
* **GitHub OAuth**

### Administrative Credentials
| Field | Local Detail | Deployed Detail (PythonAnywhere) |
| :--- | :--- | :--- |
| **Admin URL** | `http://127.0.0.1:8000/admin` | [Admin Portal](https://nexy.pythonanywhere.com/admin) |
| **User URL** | `http://127.0.0.1:8000/` | [Live App](https://nexy.pythonanywhere.com) |
| **Username** | `Nexie` | `Nexie` |
| **Password** | `nexyness23` | `nexyness23` |

---

## 🖼 Project Interface
![Hangarin Dashboard](assets/dashboard.png)

---

## 🚀 Launch & Installation

Follow these steps to get your local development environment running:

### 1. Setup Environment
```bash
# Clone the repository
git clone [https://github.com/NexieMadia23/Hangarin](https://github.com/NexieMadia23/Hangarin)
cd Hangarin

# Create and activate virtual environment
python -m venv venv
# Windows: venv\Scripts\activate | Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
