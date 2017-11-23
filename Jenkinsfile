#!groovy

pipeline {

  // agent defines where the pipeline will run.
  agent {  
    label {
      label "system_tests_ui"
    }
  }
  
  triggers {
    pollSCM('H/2 * * * *')
    cron('H H/12 * * *')
  }
  
  stages {  
    stage("Checkout") {
      steps {
        echo "Branch: ${env.BRANCH_NAME}"
        checkout scm
      }
    }
    
    stage("Build") {
      steps {
        bat """
            runner.cmd StableTests
            """
      }
    }
    
    stage("Archive artificats") {
        archiveArtifacts allowEmptyArchive: true, artifacts: 'Results/**/*.log,Results/*.html,Results/images/*.png,Results/report.junit.xml'
    }
    
    stage("Unit Test Results") {
      steps {
        junit "**/Results/report.junit.xml"
      }
    }
  }
  
  post {
    failure {
      step([$class: 'Mailer', notifyEveryUnstableBuild: true, recipients: 'icp-buildserver@lists.isis.rl.ac.uk', sendToIndividuals: true])
    }
  }
  
  // The options directive is for configuration that applies to the whole job.
  options {
    buildDiscarder(logRotator(numToKeepStr:'20', daysToKeepStr: '7'))
    timeout(time: 6, unit: 'HOURS')
    disableConcurrentBuilds()
  }
}
