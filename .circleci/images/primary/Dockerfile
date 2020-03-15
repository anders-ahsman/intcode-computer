FROM circleci/python:3.8.1
RUN sudo chown -R circleci:circleci /usr/local/bin && \
    sudo chown -R circleci:circleci /usr/local/lib/python3.8/site-packages
RUN sudo apt-get update && \
    sudo apt-get install -y npm
RUN sudo npm i -g serverless
RUN sudo pip install pipenv
