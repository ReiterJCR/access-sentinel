# Access Sentinel

Access Sentinel is a realistic cybersecurity monitoring dashboard built with Django. It simulates insider threat detection in an enterprise file system by tracking user file access, classifying sensitivity levels, and detecting anomalies such as after-hours access, geographic mismatches, and potential data leaks.

---

## Features

- **User Authentication** with secure sign up and login
- **File Sensitivity Levels** (Public, Internal, Confidential, Top Secret)
- **Behavioral Baselines** per user and file
- **Interactive Admin Dashboard** with:
  - Live activity feed
  - Top users by file access
  - User risk scoring
  - Anomaly breakdown chart
  - File sensitivity analytics
- **Anomaly Detection** for:
  - After-hours access
  - GeoIP mismatch (simulated)
  - Unusual file access volume

---

## 🛠 Tech Stack

- **Backend:** Django, PostgreSQL
- **Frontend:** Bootstrap 5, Chart.js
- **Auth:** Django’s built-in User model
- **Dev Tools:** `black`, `isort`, `flake8`, `.env` support with `python-decouple`

---