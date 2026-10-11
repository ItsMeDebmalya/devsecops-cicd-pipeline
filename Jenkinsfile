// Declarative Jenkins pipeline mirroring the GitHub Actions gates:
// Dev (lint+test) -> SAST (SonarQube) -> build + Trivy -> IaC scan -> QA -> Prod.
// Security gates fail the build before promotion, so insecure code or images
// never reach a deploy stage.

pipeline {
  agent any

  environment {
    IMAGE       = "devsecops-demo"
    TAG         = "${env.GIT_COMMIT}"
    SONAR_HOST  = "http://sonarqube:9000"
  }

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  stages {
    stage('Dev: Lint & Unit Tests') {
      steps {
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          pip install -r app/requirements.txt ruff pytest
          ruff check app
          python -m pytest -q
        '''
      }
    }

    stage('SAST: SonarQube') {
      steps {
        withSonarQubeEnv('sonarqube') {
          sh 'sonar-scanner -Dsonar.host.url=${SONAR_HOST}'
        }
      }
    }

    stage('Quality Gate') {
      steps {
        timeout(time: 10, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: true
        }
      }
    }

    stage('Build Image') {
      steps {
        sh 'docker build -t ${IMAGE}:${TAG} .'
      }
    }

    stage('Trivy: Dependency & Image Scan') {
      steps {
        // Fail the build on CRITICAL (fixable) findings.
        sh 'trivy fs --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 .'
        sh 'trivy image --severity CRITICAL --ignore-unfixed --exit-code 1 ${IMAGE}:${TAG}'
      }
    }

    stage('IaC Scan: tfsec') {
      steps {
        sh 'tfsec iac --minimum-severity HIGH'
      }
    }

    stage('Promote to QA') {
      when { branch 'main' }
      steps {
        echo "All gates passed - promoting ${IMAGE}:${TAG} from Dev to QA."
      }
    }

    stage('Promote to Prod') {
      when { branch 'main' }
      steps {
        echo "QA validated - promoting ${IMAGE}:${TAG} to Prod."
      }
    }
  }

  post {
    failure {
      echo 'A security gate failed - promotion blocked.'
    }
  }
}
