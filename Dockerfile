
############ Image de base pour Go ############
FROM golang:tip-alpine3.23 AS golang-base

WORKDIR /usr/src/app

# Download le logiciel de Air pour hot reload 
RUN go install github.com/air-verse/air@v1.65.1

# Download les dépendances de Go
COPY go.mod go.sum ./
RUN go mod download

# Copie les fichiers de code + fichier de config de Air sauf ceux exclus dans le .dockerignore 
COPY . .


############ Image de developpement de fiber ############
FROM golang-base AS golang-dev

# Lancer le programme de Air qui fait le hot reload
EXPOSE 3000
CMD ["air", "-c", "config/.air.conf"]