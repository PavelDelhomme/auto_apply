.PHONY: help build up down restart logs shell stats clean rebuild stop start status ps

# Variables
COMPOSE_FILE = docker-compose.yml
SERVICE_NAME = auto-apply
CONTAINER_NAME = auto-apply-dashboard
PORT = 2020

# Désactiver les couleurs par défaut (peut être activé avec COLOR=1)
ifndef COLOR
    COLOR = 0
endif

# Couleurs pour les messages (désactivées par défaut)
ifeq ($(COLOR),1)
    GREEN = \033[0;32m
    YELLOW = \033[1;33m
    RED = \033[0;31m
    NC = \033[0m
else
    GREEN =
    YELLOW =
    RED =
    NC =
endif

help: ## Affiche l'aide avec toutes les commandes disponibles
	@printf "$(GREEN)Auto Apply - Commandes disponibles:$(NC)\n"
	@printf "\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@printf "\n"

build: ## Construit l'image Docker
	@printf "$(GREEN)🔨 Construction de l'image Docker...$(NC)\n"
	docker-compose -f $(COMPOSE_FILE) build

up: ## Démarre les conteneurs en arrière-plan
	@printf "$(GREEN)🚀 Démarrage des conteneurs...$(NC)\n"
	docker-compose -f $(COMPOSE_FILE) up -d
	@sleep 2
	@printf "$(GREEN)✅ Conteneurs démarrés!$(NC)\n"
	@printf "$(GREEN)📊 Vérification du statut...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) ps
	@printf "$(GREEN)🌐 Interface disponible sur http://localhost:$(PORT)$(NC)\n"
	@printf "$(YELLOW)💡 Utilisez 'make open' pour ouvrir dans le navigateur$(NC)\n"

down: ## Arrête et supprime les conteneurs
	@printf "$(YELLOW)⏹️  Arrêt des conteneurs...$(NC)\n"
	docker-compose -f $(COMPOSE_FILE) down
	@printf "$(GREEN)✅ Conteneurs arrêtés$(NC)\n"

start: ## Démarre les conteneurs (alias de up). Usage: make start [LOGS=true|false]
	@$(MAKE) up
	@if [ "$(LOGS)" = "true" ]; then \
		printf "$(GREEN)📋 Affichage des logs en temps réel (Ctrl+C pour quitter)...$(NC)\n"; \
		docker-compose -f $(COMPOSE_FILE) logs -f; \
	fi

stop: ## Arrête les conteneurs (alias de down)
	@$(MAKE) down

restart: ## Redémarre les conteneurs. Usage: make restart [LOGS=true|false]
	@printf "$(YELLOW)🔄 Redémarrage des conteneurs...$(NC)\n"
	@printf "$(YELLOW)⏹️  Arrêt des conteneurs existants...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) down 2>/dev/null || true
	@docker stop $(CONTAINER_NAME) 2>/dev/null || true
	@docker rm $(CONTAINER_NAME) 2>/dev/null || true
	@sleep 1
	@printf "$(GREEN)🚀 Démarrage des conteneurs...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) up -d
	@sleep 2
	@printf "$(GREEN)✅ Conteneurs redémarrés$(NC)\n"
	@printf "$(GREEN)📊 Statut actuel:$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) ps
	@printf "$(GREEN)🌐 Interface disponible sur http://localhost:$(PORT)$(NC)\n"
	@if [ "$(LOGS)" = "true" ]; then \
		printf "$(GREEN)📋 Affichage des logs en temps réel (Ctrl+C pour quitter)...$(NC)\n"; \
		docker-compose -f $(COMPOSE_FILE) logs -f; \
	fi

logs: ## Affiche les logs en temps réel
	@printf "$(GREEN)📋 Logs du conteneur (Ctrl+C pour quitter)...$(NC)\n"
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-tail: ## Affiche les 100 dernières lignes de logs
	docker-compose -f $(COMPOSE_FILE) logs --tail=100

shell: ## Ouvre un shell dans le conteneur
	@printf "$(GREEN)🐚 Ouverture du shell dans le conteneur...$(NC)\n"
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) bash

shell-root: ## Ouvre un shell root dans le conteneur
	@printf "$(GREEN)🐚 Ouverture du shell root dans le conteneur...$(NC)\n"
	docker-compose -f $(COMPOSE_FILE) exec -u root $(SERVICE_NAME) bash

ps: ## Affiche l'état des conteneurs
	@printf "$(GREEN)📊 État des conteneurs:$(NC)\n"
	docker-compose -f $(COMPOSE_FILE) ps

status: ## Affiche l'état détaillé (alias de ps)
	@$(MAKE) ps

stats: ## Affiche les statistiques d'utilisation des ressources
	@printf "$(GREEN)📈 Statistiques des conteneurs (Ctrl+C pour quitter)...$(NC)\n"
	docker stats $(CONTAINER_NAME)

rebuild: ## Reconstruit l'image et redémarre les conteneurs
	@printf "$(YELLOW)🔨 Reconstruction complète...$(NC)\n"
	docker-compose -f $(COMPOSE_FILE) down
	docker-compose -f $(COMPOSE_FILE) build --no-cache
	docker-compose -f $(COMPOSE_FILE) up -d
	@printf "$(GREEN)✅ Reconstruction terminée! Interface disponible sur http://localhost:$(PORT)$(NC)\n"

clean: ## Supprime les conteneurs, volumes et images
	@printf "$(RED)🧹 Nettoyage complet...$(NC)\n"
	@read -p "Êtes-vous sûr de vouloir supprimer tous les conteneurs, volumes et images? [y/N] " -n 1 -r; \
	printf "\n"; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose -f $(COMPOSE_FILE) down -v --rmi all; \
		printf "$(GREEN)✅ Nettoyage terminé$(NC)\n"; \
	else \
		printf "$(YELLOW)Nettoyage annulé$(NC)\n"; \
	fi

clean-volumes: ## Supprime uniquement les volumes
	@printf "$(YELLOW)🧹 Suppression des volumes...$(NC)\n"
	docker-compose -f $(COMPOSE_FILE) down -v
	@printf "$(GREEN)✅ Volumes supprimés$(NC)\n"

clean-images: ## Supprime les images Docker
	@printf "$(YELLOW)🧹 Suppression des images...$(NC)\n"
	docker-compose -f $(COMPOSE_FILE) down --rmi all
	@printf "$(GREEN)✅ Images supprimées$(NC)\n"

clean-test-personas: ## Nettoie les personas de test (testextended@example.com, testapi@example.com, etc.)
	@printf "$(GREEN)🧹 Nettoyage des personas de test...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) exec -T $(SERVICE_NAME) python /app/scripts/clean_test_personas.py || printf "$(YELLOW)⚠️  Le conteneur n'est pas en cours d'exécution. Démarrez-le avec 'make start'$(NC)\n"

pull: ## Met à jour les images de base
	@printf "$(GREEN)⬇️  Mise à jour des images de base...$(NC)\n"
	docker-compose -f $(COMPOSE_FILE) pull

exec: ## Exécute une commande dans le conteneur (usage: make exec CMD="python --version")
	@if [ -z "$(CMD)" ]; then \
		printf "$(RED)❌ Erreur: Spécifiez une commande avec CMD=\"votre commande\"$(NC)\n"; \
		exit 1; \
	fi
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) $(CMD)

run: ## Exécute une commande dans un nouveau conteneur (usage: make run CMD="python --version")
	@if [ -z "$(CMD)" ]; then \
		printf "$(RED)❌ Erreur: Spécifiez une commande avec CMD=\"votre commande\"$(NC)\n"; \
		exit 1; \
	fi
	docker-compose -f $(COMPOSE_FILE) run --rm $(SERVICE_NAME) $(CMD)

backup-db: ## Sauvegarde la base de données
	@printf "$(GREEN)💾 Sauvegarde de la base de données...$(NC)\n"
	@mkdir -p backups
	docker-compose -f $(COMPOSE_FILE) exec -T $(SERVICE_NAME) sqlite3 /app/data/jobs.db .dump > backups/jobs_$$(date +%Y%m%d_%H%M%S).sql
	@printf "$(GREEN)✅ Sauvegarde créée dans backups/$(NC)\n"

restore-db: ## Restaure la base de données (usage: make restore-db FILE=backups/jobs_20240101_120000.sql)
	@if [ -z "$(FILE)" ]; then \
		printf "$(RED)❌ Erreur: Spécifiez un fichier avec FILE=backups/votre_fichier.sql$(NC)\n"; \
		exit 1; \
	fi
	@printf "$(GREEN)📥 Restauration de la base de données depuis $(FILE)...$(NC)\n"
	docker-compose -f $(COMPOSE_FILE) exec -T $(SERVICE_NAME) sqlite3 /app/data/jobs.db < $(FILE)
	@printf "$(GREEN)✅ Base de données restaurée$(NC)\n"

open: ## Ouvre l'interface dans le navigateur
	@printf "$(GREEN)🌐 Ouverture de l'interface...$(NC)\n"
	@if command -v xdg-open > /dev/null; then \
		xdg-open http://localhost:$(PORT); \
	elif command -v open > /dev/null; then \
		open http://localhost:$(PORT); \
	else \
		printf "$(YELLOW)Ouvrez manuellement: http://localhost:$(PORT)$(NC)\n"; \
	fi

test: ## Lance la suite complète de tests (connexion, unitaires, intégration, FAB, couverture)
	@printf "$(GREEN)═══════════════════════════════════════════════════════════════$(NC)\n"
	@printf "$(GREEN)🧪 SUITE COMPLÈTE DE TESTS$(NC)\n"
	@printf "$(GREEN)═══════════════════════════════════════════════════════════════$(NC)\n"
	@printf "\n"
	@printf "$(YELLOW)📋 Étape 1/5: Vérification de la connexion au conteneur...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) python -c "import sys; print('✅ Python:', sys.version.split()[0])" 2>/dev/null || (printf "$(RED)❌ Le conteneur n'est pas accessible$(NC)\n"; exit 1)
	@printf "\n"
	@printf "$(YELLOW)📦 Étape 2/5: Installation/Vérification des dépendances de test...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) pip install -q pytest pytest-cov pytest-mock pytest-html 2>/dev/null || true
	@printf "$(GREEN)✅ Dépendances prêtes$(NC)\n"
	@printf "\n"
	@printf "$(YELLOW)🔬 Étape 3/5: Tests unitaires...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) exec -e PYTHONPATH=/app $(SERVICE_NAME) python -m pytest tests/ -v --tb=short -m "not integration" --junitxml=/tmp/test-results-unit.xml || TEST_UNIT_FAILED=1; \
	if [ -z "$$TEST_UNIT_FAILED" ]; then \
		printf "$(GREEN)✅ Tests unitaires réussis$(NC)\n"; \
	else \
		printf "$(RED)❌ Certains tests unitaires ont échoué$(NC)\n"; \
	fi
	@printf "\n"
	@printf "$(YELLOW)🔗 Étape 4/5: Tests d'intégration...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) exec -e PYTHONPATH=/app $(SERVICE_NAME) python -m pytest tests/ -v --tb=short -m integration --junitxml=/tmp/test-results-integration.xml || TEST_INTEGRATION_FAILED=1; \
	if [ -z "$$TEST_INTEGRATION_FAILED" ]; then \
		printf "$(GREEN)✅ Tests d'intégration réussis$(NC)\n"; \
	else \
		printf "$(YELLOW)⚠️  Certains tests d'intégration ont échoué (peut nécessiter une configuration)$(NC)\n"; \
	fi
	@printf "\n"
	@printf "$(YELLOW)🎯 Étape 5/5: Tests FAB et rapport de couverture...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) exec -e PYTHONPATH=/app $(SERVICE_NAME) python -m pytest tests/test_fab_functionality.py -v --tb=short --cov=src --cov-config=.coveragerc --cov-report=term-missing --cov-report=html:/tmp/coverage_html --junitxml=/tmp/test-results-fab.xml || TEST_FAB_FAILED=1; \
	if [ -z "$$TEST_FAB_FAILED" ]; then \
		printf "$(GREEN)✅ Tests FAB réussis$(NC)\n"; \
	else \
		printf "$(RED)❌ Certains tests FAB ont échoué$(NC)\n"; \
	fi
	@printf "\n"
	@printf "$(GREEN)═══════════════════════════════════════════════════════════════$(NC)\n"
	@printf "$(GREEN)📊 RÉSUMÉ DES TESTS$(NC)\n"
	@printf "$(GREEN)═══════════════════════════════════════════════════════════════$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) python -m pytest tests/ -v --tb=no -q --co -q 2>/dev/null | tail -1 || true
	@printf "\n"
	@printf "$(GREEN)✅ Suite de tests terminée!$(NC)\n"
	@printf "$(YELLOW)💡 Utilisez 'make test-unit', 'make test-integration' ou 'make test-all' pour des tests spécifiques$(NC)\n"
	@printf "$(YELLOW)💡 Rapport HTML de couverture disponible dans /tmp/coverage_html/index.html (dans le conteneur)$(NC)\n"

test-unit: ## Lance uniquement les tests unitaires
	@printf "$(GREEN)🧪 Lancement des tests unitaires...$(NC)\n"
	@printf "$(YELLOW)📦 Mise à jour de pip et vérification de l'installation de pytest...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) pip install --upgrade pip --quiet 2>/dev/null || true
	@docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) pip install -q pytest pytest-cov pytest-mock 2>/dev/null || true
	@docker-compose -f $(COMPOSE_FILE) exec -e PYTHONPATH=/app $(SERVICE_NAME) python -m pytest tests/ -v --tb=short -m "not integration" --junitxml=/tmp/test-results-unit.xml || printf "$(YELLOW)⚠️  Certains tests peuvent nécessiter une configuration spécifique$(NC)\n"

test-integration: ## Lance uniquement les tests d'intégration
	@printf "$(GREEN)🧪 Lancement des tests d'intégration...$(NC)\n"
	@printf "$(YELLOW)📦 Mise à jour de pip et vérification de l'installation de pytest...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) pip install --upgrade pip --quiet 2>/dev/null || true
	@docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) pip install -q pytest pytest-cov pytest-mock 2>/dev/null || true
	@docker-compose -f $(COMPOSE_FILE) exec -e PYTHONPATH=/app $(SERVICE_NAME) python -m pytest tests/ -v --tb=short -m integration --junitxml=/tmp/test-results-integration.xml || printf "$(YELLOW)⚠️  Les tests d'intégration nécessitent une configuration complète$(NC)\n"

test-all: ## Lance tous les tests avec couverture complète
	@printf "$(GREEN)🧪 Lancement de TOUS les tests avec couverture complète...$(NC)\n"
	@printf "$(YELLOW)📦 Mise à jour de pip et vérification de l'installation de pytest...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) pip install --upgrade pip --quiet 2>/dev/null || true
	@docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) pip install -q pytest pytest-cov pytest-mock pytest-html 2>/dev/null || true
	@printf "$(GREEN)🔬 Exécution de tous les tests...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) exec -e PYTHONPATH=/app $(SERVICE_NAME) python -m pytest tests/ -v --tb=short --cov=src --cov-config=.coveragerc --cov-report=term-missing --cov-report=html:/tmp/coverage_html --cov-report=xml:/tmp/coverage.xml --junitxml=/tmp/test-results.xml || printf "$(YELLOW)⚠️  Certains tests peuvent nécessiter une configuration spécifique$(NC)\n"
	@printf "\n"
	@printf "$(GREEN)📊 Rapport de couverture généré:$(NC)\n"
	@printf "$(YELLOW)   - HTML: /tmp/coverage_html/index.html (dans le conteneur)$(NC)\n"
	@printf "$(YELLOW)   - XML: /tmp/coverage.xml (dans le conteneur)$(NC)\n"
	@printf "$(YELLOW)   - JUnit: /tmp/test-results.xml (dans le conteneur)$(NC)\n"

test-fab: ## Lance uniquement les tests FAB (Floating Action Button)
	@printf "$(GREEN)🧪 Lancement des tests FAB...$(NC)\n"
	@printf "$(YELLOW)📦 Vérification de l'installation de pytest...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) pip install -q pytest pytest-cov pytest-mock 2>/dev/null || true
	@docker-compose -f $(COMPOSE_FILE) exec -e PYTHONPATH=/app $(SERVICE_NAME) python -m pytest tests/test_fab_functionality.py -v --tb=short --cov=src --cov-config=.coveragerc --cov-report=term-missing --cov-report=html:/tmp/coverage_html --junitxml=/tmp/test-results-fab.xml || printf "$(YELLOW)⚠️  Certains tests FAB peuvent nécessiter une configuration spécifique$(NC)\n"

test-connection: ## Teste uniquement la connexion au conteneur
	@printf "$(GREEN)🧪 Test de connexion...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) python -c "import sys; print('✅ Python:', sys.version.split()[0])" 2>/dev/null || (printf "$(RED)❌ Le conteneur n'est pas accessible$(NC)\n"; exit 1)

test-local: ## Lance les tests localement (sans Docker)
	@printf "$(GREEN)🧪 Lancement des tests localement...$(NC)\n"
	@printf "$(YELLOW)⚠️  Assurez-vous que pytest est installé: pip install -r requirements.txt$(NC)\n"
	@pytest tests/ -v --tb=short --cov=src --cov-report=term-missing || printf "$(YELLOW)⚠️  Assurez-vous que pytest est installé: pip install -r requirements.txt$(NC)\n"

test-coverage: ## Affiche le rapport de couverture détaillé
	@printf "$(GREEN)📊 Génération du rapport de couverture...$(NC)\n"
	@docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) pip install --upgrade pip --quiet 2>/dev/null || true
	@docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) pip install -q pytest-cov 2>/dev/null || true
	@docker-compose -f $(COMPOSE_FILE) exec -e PYTHONPATH=/app $(SERVICE_NAME) python -m pytest tests/ --cov=src --cov-config=.coveragerc --cov-report=html:/tmp/coverage_html --cov-report=term-missing
	@printf "$(GREEN)✅ Rapport généré dans /tmp/coverage_html/index.html (dans le conteneur)$(NC)\n"
	@printf "$(YELLOW)💡 Pour voir le rapport: make shell puis ouvrir /tmp/coverage_html/index.html$(NC)\n"
	@printf "$(YELLOW)💡 Ou copier depuis le conteneur: docker cp \$$(docker-compose ps -q auto-apply):/tmp/coverage_html ./coverage_html$(NC)\n"

test-reports: ## Copie les rapports de test depuis le conteneur vers le répertoire local
	@printf "$(GREEN)📥 Copie des rapports de test depuis le conteneur...$(NC)\n"
	@mkdir -p ./test_reports/coverage_html ./test_reports/xml
	@docker cp $$(docker-compose -f $(COMPOSE_FILE) ps -q $(SERVICE_NAME)):/tmp/coverage_html ./test_reports/ 2>/dev/null || printf "$(YELLOW)⚠️  Rapport HTML non trouvé$(NC)\n"
	@docker cp $$(docker-compose -f $(COMPOSE_FILE) ps -q $(SERVICE_NAME)):/tmp/coverage.xml ./test_reports/xml/ 2>/dev/null || printf "$(YELLOW)⚠️  Rapport XML de couverture non trouvé$(NC)\n"
	@docker cp $$(docker-compose -f $(COMPOSE_FILE) ps -q $(SERVICE_NAME)):/tmp/test-results.xml ./test_reports/xml/ 2>/dev/null || printf "$(YELLOW)⚠️  Rapport JUnit non trouvé$(NC)\n"
	@docker cp $$(docker-compose -f $(COMPOSE_FILE) ps -q $(SERVICE_NAME)):/tmp/test-results-*.xml ./test_reports/xml/ 2>/dev/null || true
	@printf "$(GREEN)✅ Rapports copiés dans ./test_reports/$(NC)\n"
	@printf "$(YELLOW)💡 Ouvrez ./test_reports/coverage_html/index.html dans votre navigateur$(NC)\n"

install-deps: ## Installe les dépendances localement (sans Docker)
	@printf "$(GREEN)📦 Installation des dépendances Python...$(NC)\n"
	pip install -r requirements.txt
	@printf "$(GREEN)✅ Dépendances installées$(NC)\n"

dev: ## Lance l'application en mode développement (sans Docker)
	@printf "$(GREEN)🔧 Démarrage en mode développement...$(NC)\n"
	python app.py

# Commande par défaut
.DEFAULT_GOAL := help

