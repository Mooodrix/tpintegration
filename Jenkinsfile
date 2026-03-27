pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
            args '-u root'
        }
    }
    environment {
        APP_NAME = 'shopflow'
        // IMAGE_TAG sera défini dans le stage Build Docker
    }
    stages {
        stage('Install') {
            steps {
                sh '''
                pip install --upgrade pip -q
                pip install -r requirements.txt -q
                echo "Dépendances installées"
                '''
            }
        }
        stage('Lint') {
            steps {
                sh '''
                flake8 app/ --max-line-length=100 --exclude __init__.py -v --format=default
                '''
            }
            post {
                failure { echo 'Lint échoué : corriger les erreurs PEP8' }
            }
        }
        stage('Unit Tests') {
            steps {
                sh '''
                pytest tests/unit/ -v --junitxml=junit-unit.xml --no-cov
                '''
            }
            post {
                always { junit 'junit-unit.xml' }
            }
        }
        stage('Integration Tests') {
            steps {
                sh '''
                pytest tests/integration/ -v --junitxml=junit-integration.xml --no-cov
                '''
            }
            post {
                always { junit 'junit-integration.xml' }
            }
        }
        stage('Coverage') {
            steps {
                sh '''
                pytest tests/ \
                  --cov=app \
                  --cov-report=xml:coverage.xml \
                  --cov-report=html:htmlcov \
                  --cov-report=term-missing \
                  --cov-fail-under=80 \
                  --junitxml=junit-report.xml
                '''
            }
            post {
                always {
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
                failure { echo 'Coverage < 80% = ajouter des tests !' }
            }
        }
        stage('Static Analysis') {
            steps {
                sh '''
                pylint app/ --output-format=parseable --exit-zero > pylint-report.txt || true
                echo "Pylint terminé"
                bandit -r app/ -f json -o bandit-report.json --exit-zero
                '''
            }
        }
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                    sonar-scanner \
                      -Dsonar.projectKey=shopflow \
                      -Dsonar.sources=app \
                      -Dsonar.tests=tests \
                      -Dsonar.python.coverage.reportPaths=coverage.xml \
                      -Dsonar.python.pylint.reportPaths=pylint-report.txt
                    '''
                }
            }
        }
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        stage('Build Docker') {
            steps {
                script {
                    env.IMAGE_TAG = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    echo "Build image shopflow:${env.IMAGE_TAG}"
                    sh "docker build -t shopflow:${env.IMAGE_TAG} ."
                }
            }
        }
        stage('Deploy Staging') {
            when { branch 'main' }
            steps {
                sh '''
                export IMAGE_TAG=${IMAGE_TAG}
                docker compose -f docker-compose.staging.yml pull || true
                docker compose -f docker-compose.staging.yml up -d --remove-orphans
                sleep 5
                curl -f http://localhost:8001/health || exit 1
                echo "Staging déployé et opérationnel"
                '''
            }
            post {
                failure { sh 'docker compose -f docker-compose.staging.yml logs --tail=50' }
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'junit-*.xml,coverage.xml,bandit-report.json', allowEmptyArchive: true
            sh 'docker system prune -f --filter label=stage=ci || true'
        }
        success { echo "Pipeline OK : ShopFlow déployé" }
        failure { echo "Pipeline FAILED : voir les logs" }
    }
}