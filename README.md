# TP-Devops-GR4
### BLANQUAERT Antoine - SERRANO Louis - MORNEAU Theo
Ce projet est une application web complète avec un backend Python, un frontend React et une base de données MySQL, orchestrés avec Docker Compose. Un workflow GitHub Actions permet le build et le déploiement automatique sur Coolify.

## Structure du projet

```
TP-Devops-GR4/
├── back/         # Backend Python (API, logique métier)
├── front/        # Frontend React (interface utilisateur)
├── data/         # Données persistantes MySQL (à ne pas modifier à la main)
├── init/         # Scripts d'initialisation de la base (SQL)
├── docker-compose.yml  # Orchestration multi-conteneurs
└── .github/workflows/deploy-to-coolify.yml  # CI/CD
```

## Prérequis
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé et lancé
- [Git](https://git-scm.com/) pour cloner le repo

## Lancement rapide

1. **Cloner le dépôt**
   ```powershell
   git clone https://github.com/bromade8300/TP-Devops-GR4.git
   cd TP-Devops-GR4
   ```

2. **Lancer l'environnement complet**
   ```powershell
   docker-compose up --build
   ```
   Cela va :
   - Démarrer la base MySQL (données persistées dans un volume Docker)
   - Démarrer le backend Python (connexion à la base)
   - Démarrer le frontend React (connexion au backend)

3. **Accéder aux services**
   - Frontend : [http://localhost:3000](http://localhost:3000)
   - Backend : [http://localhost:8000](http://localhost:8000)
   - MySQL : port 3306 (utiliser un client MySQL si besoin)

## Variables d'environnement importantes
- Les mots de passe et utilisateurs MySQL sont définis dans `docker-compose.yml` (modifiables si besoin).
- Le backend lit la config DB via les variables d'environnement Docker Compose.

## Scripts d'initialisation
- Placez vos scripts `.sql` dans le dossier `init/` pour qu'ils soient exécutés à la première création du conteneur MySQL.

## CI/CD et déploiement
- Un workflow GitHub Actions (`.github/workflows/deploy-to-coolify.yml`) build l'image Docker et déclenche le déploiement sur Coolify à chaque push sur `main` ou `dev/add-surveillance`.
- Les secrets nécessaires (`COOLIFY_WEBHOOK`, `COOLIFY_TOKEN`) doivent être configurés dans les secrets du repo GitHub.

## Conseils pour le debug
- Pour voir les logs d'un service :
  ```powershell
  docker-compose logs backend
  docker-compose logs frontend
  docker-compose logs mysql
  ```
- Pour accéder à un shell dans un conteneur :
  ```powershell
  docker-compose exec backend bash
  docker-compose exec mysql bash
  ```

---

Pour toute question ou contribution, ouvrez une issue ou une pull request sur GitHub.
