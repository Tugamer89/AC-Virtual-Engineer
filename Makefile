.PHONY: format format-backend format-frontend

format: format-backend format-frontend
	@echo "All files formatted successfully!"

format-backend:
	@echo "Formatting backend..."
	isort --profile black backend/
	black backend/

format-frontend:
	@echo "Formatting frontend..."
	cd frontend && npx prettier --write . && ESLINT_USE_FLAT_CONFIG=true npx eslint --fix .
