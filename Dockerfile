FROM node:23-bookworm
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN apt-get install git bash curl && \
  yarn install --non-interactive --frozen-lockfile && \
  curl -L https://foundry.paradigm.xyz | bash && \
  /root/.foundry/bin/foundryup && \
  npx hardhat compile
