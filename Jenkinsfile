pipeline {
    agent any
    stages {
        stage('Prepare venv') {
            steps {
                sh '''
                    python3 -m venv venv
                    . ./venv/bin/activate
                    pip install pipenv
                    pipenv install --dev
                '''
            }

        }
        stage('Linting') {
            steps {
                sh '''
                    . ./venv/bin/activate
                    flake8 medex url_handlers modules serverside webserver.py --max-line-length 140
                '''
            }
        }
        stage('Testing') {
            steps {
                sh '''
                    . ./venv/bin/activate
                    export PYTHONPATH=$(pwd)
                    pytest --junitxml results.xml tests --cov=medex --cov-report xml
                '''
            }
        }
    }
    post {
        always {
            junit 'results.xml'
            cobertura coberturaReportFile: 'coverage.xml'
        }
        failure {
            emailext to: "medex@dieterichlab.org",
            subject: "jenkins build:${currentBuild.currentResult}: ${env.JOB_NAME}",
            body: "${currentBuild.currentResult}: Job ${env.JOB_NAME}\nMore Info can be found here: ${env.BUILD_URL}"
        }
    }
}
