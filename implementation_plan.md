# Placement Prep Platform - Implementation Plan

## Phase 1: Foundation & Infrastructure (The Skeleton)
- [ ] Initialize FastAPI project structure with `SQLModel`.
- [ ] Setup User Authentication (JWT based, Secure & Scalable).
- [ ] Create a "Health Check" and "Protected Route" to verify the bridge between React & FastAPI.
- [ ] **Learning Goal**: Understand JWT, Password Hashing (bcrypt), and Dependency Injection in FastAPI.

## Phase 2: Aptitude Engine (The Logic)
- [ ] Design the Database Schema for Questions (Topic, Difficulty, Tags).
- [ ] Implement the **Adaptive Difficulty Algorithm** (The logic that picks the next question based on performance).
- [ ] Build the Practice Session API (Timer, Question selection).
- [ ] **Learning Goal**: CRUD operations, complex SQL queries, and algorithmic thinking for difficulty adjustment.

## Phase 3: Gamified Rounds (The Interactive Layer)
- [ ] Design the "Game Session" schema (tracking level reached in 6 mins).
- [ ] Build the first game: **Deductive Reasoning** (React-based logic).
- [ ] Implement the "Adaptive Level Up" logic for games.
- [ ] **Learning Goal**: Frontend state management for timers and game state; syncing game progress with the backend.

## Phase 4: Dashboard & Analytics (The Value)
- [ ] Aggregated statistics (Aptitude vs Games).
- [ ] Historical comparison (Trend lines for improvement).
- [ ] **Learning Goal**: Data aggregation in SQL and data visualization in React (Recharts).

## Phase 5: Security & Scaling
- [ ] Add Rate Limiting (preventing bot spam).
- [ ] Implement Role-Based Access (if we add Admin for adding questions).
- [ ] Database Indexing for performance.
- [ ] **Learning Goal**: System Design for high availability and security.
