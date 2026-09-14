FROM maven:3.8.8-eclipse-temurin-8 AS build
WORKDIR /src
RUN git clone --depth 1 https://github.com/linlinjava/litemall.git .
RUN mvn -B -DskipTests -pl litemall-wx-api -am package

FROM eclipse-temurin:8-jre
WORKDIR /app
COPY --from=build /src/litemall-wx-api/target/litemall-wx-api-0.1.0-exec.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]