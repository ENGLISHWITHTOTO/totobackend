push:
	@if [ -z "$(m)" ]; then \
		echo "❌ Please provide a commit message."; \
		echo "Usage: make push m=\"your commit message\""; \
		exit 1; \
	fi
	git config --global user.email "amanuel.demirew@yahoo.com"
	git config --global user.name "Amanuel Demirew"
	git add .
	git commit -m "$(m)"
	git push
	@echo "✅ Changes pushed successfully with commit: \"$(m)\""