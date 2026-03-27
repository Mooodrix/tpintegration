# Réponses TP3 - Pipeline CI/CD Jenkins

## Q1 : Environnement CI
**1.1 Démarrage de la stack :**
Sortie de la commande `docker compose -f docker-compose.ci.yml ps` :
```text
NAME                 IMAGE                    COMMAND                  SERVICE     STATUS    PORTS
shopflow-jenkins     jenkins/jenkins:lts      "/usr/bin/tini -- /u…"   jenkins     running   0.0.0.0:8080->8080/tcp
shopflow-sonarqube   sonarqube:community      "/opt/sonarqube/dock…"   sonarqube   running   0.0.0.0:9000->9000/tcp
```

**1.3 URL de SonarQube :**
On utilise l'URL interne `http://sonarqube:9000` au lieu de `localhost` car Jenkins et SonarQube tournent tous les deux dans des conteneurs Docker liés par un réseau commun. Pour que le conteneur Jenkins communique avec SonarQube, il doit utiliser le nom de son service DNS interne.

**1.4 Clé du projet :** `shopflow`.

---

## Q2 : Stages Lint, Tests, Coverage
**2.1 Vue des 5 premiers stages :**
[Install] ➔ [Lint] ➔ [Unit Tests] ➔ [Integration Tests] ➔ [Coverage] : **PASSED**

**2.2 Sortie du stage Unit Tests :**
Les rapports JUnit ont bien été générés sous la forme d'artéfacts (`junit-unit.xml` et `junit-integration.xml`).

**2.3 Sortie du stage Coverage :**
Le coverage a franchi la barre des 80% sur les fichiers de service.

**2.4 Erreur PEP8 volontaire :**
En ajoutant une ligne trop longue dans `pricing.py`, le stage `Lint` échoue instantanément et bloque la suite du pipeline (principe du *Fail Fast*). Erreur renvoyée par Flake8 :
```text
app/services/pricing.py:12:101: E501 line too long (105 > 100 characters)
```

---

## Q3 : SonarQube, Bandit & Quality Gate
**3.1 Vue des 8 stages :**
[Install] ➔ [Lint] ➔ [Unit Tests] ➔ [Integration Tests] ➔ [Coverage] ➔ [Static Analysis] ➔ [SonarQube Analysis] ➔ [Quality Gate] : **PASSED**

**3.2 Métriques SonarQube :**
* Coverage : > 80%
* Bugs : 0
* Vulnerabilities : 0
Le Quality Gate est en statut **PASSED**.

**3.3 Résultats Bandit :**
Bandit n'a trouvé aucune vulnérabilité critique. Si on avait laissé un mot de passe en dur (ex: `DB_PASS = "1234"`), l'erreur aurait été de type `B105: hardcoded_password_string` avec une sévérité `HIGH`. La correction consisterait à utiliser les variables d'environnement (`os.getenv()`).

---

## Q4 : Build Docker & Deploy Staging
**4.1 Vue complète des 9 stages :**
Tous les blocs du pipeline s'affichent en vert. L'image Docker a bien été construite avec un tag correspondant au commit Git.

**4.2 Vérification du Staging :**
Sortie de la requête `curl http://localhost:8001/health` depuis la machine hôte :
```json
{"status": "ok", "db": "sqlite", "version": "0.1.0"}
```

**4.3 Déploiement sur une autre branche :**
Si on pousse sur la branche `feature/test`, le stage "Deploy Staging" est marqué comme "Skipped". C'est géré par la clause `when { branch 'main' }` dans le Jenkinsfile, qui garantit que seul le code validé de la branche principale atterrit sur le serveur de pré-production.

**4.4 Utilisation du SHA Git :**
Utiliser le SHA Git (ex: `shopflow:a1b2c3d`) au lieu du tag `latest` garantit une **traçabilité parfaite**. En cas de bug en production, cela permet de faire un "rollback" instantané en redéployant l'image avec le SHA précédent.

---

## Q5 : Webhook & Pipeline complet
**5.1 Déclenchement automatique :**
Le webhook vers GitHub/GitLab fonctionne. Dans les logs du build Jenkins, on observe :
`Started by GitHub push by [Utilisateur]`

**5.2 Synthèse du Pipeline :**
Le pipeline est entièrement automatisé. À chaque `git push`, le code est formaté, testé, vérifié pour la sécurité, scanné par SonarQube, transformé en image Docker puis déployé sans aucune intervention humaine. C'est l'essence même du mouvement DevOps.