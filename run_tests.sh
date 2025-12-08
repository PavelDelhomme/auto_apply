#!/bin/bash
# Script pour lancer tous les tests du projet

set -e

echo "🧪 Lancement de la suite de tests complète pour Auto Apply"
echo "============================================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier si on est dans Docker ou en local
if [ -f /.dockerenv ] || [ -n "$DOCKER_CONTAINER" ]; then
    echo -e "${GREEN}Mode: Docker${NC}"
    PYTHON_CMD="python"
else
    echo -e "${GREEN}Mode: Local${NC}"
    PYTHON_CMD="python3"
fi

# Vérifier que pytest est installé
if ! $PYTHON_CMD -m pytest --version > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  pytest n'est pas installé. Installation...${NC}"
    $PYTHON_CMD -m pip install pytest pytest-cov pytest-mock
fi

echo ""
echo -e "${GREEN}📋 Tests unitaires${NC}"
echo "-------------------"
$PYTHON_CMD -m pytest tests/ -v -m "not integration" --tb=short || echo -e "${YELLOW}⚠️  Certains tests unitaires ont échoué${NC}"

echo ""
echo -e "${GREEN}📋 Tests d'intégration${NC}"
echo "-------------------"
$PYTHON_CMD -m pytest tests/ -v -m integration --tb=short || echo -e "${YELLOW}⚠️  Certains tests d'intégration ont échoué${NC}"

echo ""
echo -e "${GREEN}📋 Tests de complétude${NC}"
echo "-------------------"
$PYTHON_CMD -m pytest tests/test_complete_suite.py -v --tb=short || echo -e "${YELLOW}⚠️  Certains tests de complétude ont échoué${NC}"

echo ""
echo -e "${GREEN}📊 Résumé avec couverture${NC}"
echo "-------------------"
$PYTHON_CMD -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html || echo -e "${YELLOW}⚠️  La génération du rapport de couverture a échoué${NC}"

echo ""
echo -e "${GREEN}✅ Tests terminés!${NC}"
echo ""
echo "Pour voir le rapport de couverture HTML:"
echo "  - Ouvrez htmlcov/index.html dans votre navigateur"

