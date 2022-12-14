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
                    flake8 dl_bareos_tools --max-line-length 140
                '''
            }
        }
        stage('Testing') {
            steps {
                sh '''
                    . ./venv/bin/activate
                    export PYTHONPATH=$(pwd)
                    pytest --junitxml results.xml tests
                '''
            }
        }
    }
    post {
        always {
            junit 'results.xml'
        }
    }
}
