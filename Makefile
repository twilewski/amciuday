.PHONY: help dev-backend dev-frontend seed test build-apk clean install

help:
	@echo "Available commands:"
	@echo "  install         - Install all dependencies"
	@echo "  dev-backend     - Run backend development server"
	@echo "  dev-frontend    - Run frontend development server"
	@echo "  seed            - Run seeding script"
	@echo "  test            - Run all tests"
	@echo "  build-apk       - Build Android APK"
	@echo "  clean           - Clean build artifacts"

install:
	@echo "Installing backend dependencies..."
	cd apps/backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd apps/frontend && npm install

dev-backend:
	cd apps/backend && . venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd apps/frontend && npm run dev

seed:
	cd tools/seed && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt && python3 scrape.py
	@echo "Seeding database..."
	curl -X POST http://localhost:8000/api/import/seed

test:
	@echo "Running backend tests..."
	cd apps/backend && . venv/bin/activate && pytest
	@echo "Running frontend tests..."
	cd apps/frontend && npm run test

build-apk:
	cd apps/frontend && npm run build && npx cap sync android && npx cap open android

clean:
	rm -rf apps/backend/venv
	rm -rf apps/backend/__pycache__
	rm -rf apps/frontend/node_modules
	rm -rf apps/frontend/dist
	rm -rf tools/seed/venv
	rm -rf data/*.db