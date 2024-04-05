# lib-devops.

## Deployment preparation

- UI: yarn build
- UI: copy all files in **dist** folder to API at **core/core-api/src/main/resources/ui** folder
- API: `gradlew build -x test -x functionalTest -x integrationTest` or `gradlew.bat build -x test -x functionalTest -x integrationTest`
- API: get a file `core-api-**.jar` in **core/core-api/build/libs** folder
- Configure env vars and run `java -jar core-api-**.jar`
