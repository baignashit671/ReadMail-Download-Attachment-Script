# Use the OpenJDK latest image as the base and define an alias for the build stage as "MiraeFixServer"
FROM 919343063061.dkr.ecr.us-east-1.amazonaws.com/openjdk:latest as MiraeFixServer

# Install necessary packages: curl, tar, bash, procps
RUN apk add --no-cache curl tar bash procps

# Define build arguments for Maven version and user home directory
ARG MAVEN_VERSION=3.8.8
ARG USER_HOME_DIR="/root"

# Define the base URL for downloading Maven binaries
ARG BASE_URL=https://apache.osuosl.org/maven/maven-3/${MAVEN_VERSION}/binaries

# Create directories for Maven installation and set up Maven
RUN mkdir -p /usr/share/maven /usr/share/maven/ref \
    && echo "Downlaoding maven" \
    && curl -fsSL -o /tmp/apache-maven.tar.gz ${BASE_URL}/apache-maven-${MAVEN_VERSION}-bin.tar.gz \
    \
    && echo "Unziping maven" \
    && tar -xzf /tmp/apache-maven.tar.gz -C /usr/share/maven --strip-components=1 \
    \
    && echo "Cleaning and setting links" \
    && rm -f /tmp/apache-maven.tar.gz \
    && ln -s /usr/share/maven/bin/mvn /usr/bin/mvn

# Set environment variables for Maven home and configuration directory
ENV MAVEN_HOME /usr/share/maven
ENV MAVEN_CONFIG "$USER_HOME_DIR/.m2"

# Create a volume at /tmp
VOLUME /tmp

# Create directories for the application and set working directory
RUN mkdir -p /usr/app
WORKDIR /usr/app/
WORKDIR /usr/app/MiraeFixServer

# Copy application files to the working directory
COPY . .
COPY ./pom.xml .

# Remove unnecessary files from the application resources
RUN rm /usr/app/MiraeFixServer/src/main/resources/application.properties
RUN rm /usr/app/MiraeFixServer/src/main/resources/MiraeFixServer.cfg
RUN rm /usr/app/MiraeFixServer/src/main/resources/log4j.properties

# Rename the test configuration files to their production names
RUN mv /usr/app/MiraeFixServer/src/main/resources/application.test.properties /usr/app/MiraeFixServer/src/main/resources/application.properties
RUN mv /usr/app/MiraeFixServer/src/main/resources/MiraeFixServer.test.cfg /usr/app/MiraeFixServer/src/main/resources/MiraeFixServer.cfg
RUN mv /usr/app/MiraeFixServer/src/main/resources/log4j.test.properties /usr/app/MiraeFixServer/src/main/resources/log4j.properties

# Build the application using Maven
RUN mvn clean install

# Set the entry point command to run the built application
ENTRYPOINT ["java","-jar","./target/original-MiraeFixServer-1.0-SNAPSHOT.jar"]

