SpringBoot version 2.4.0
JAVA JDK version 11

# Simple Implementation of websocket
For this example, the user has two options to connect to the public chat room
1. Open the index.html file in Client_JS folder
2. Run the adroid app in Client_Android folder

To run the server on your local machine to test the public chat room, you 
1. Run the server in intelliJ normally (refer to the guide on how to change Java + Springboot version if there are any problems)
2. Execute the command 'java -jar websocketServer.jar' in the terminal to run the included .jar server (for frontend students)

Read the Websockets02.pdf to understand the inner workings of the frontend and backend for this public chat room.

# Dependencies and Configurations

## Backend

- in `pom.xml`:
```
<dependency>
	<groupId>org.springframework.boot</groupId>
	<artifactId>spring-boot-starter-websocket</artifactId>
</dependency>
```

## Frontend

### Option 1. `SocketExample` (uses local library `java_websocket.jar`)

- copy `SocketExample/app/libs/java_websocket.jar` to your project

- in `build.gradle (Module...)`:
```
dependencies {
	...
    implementation files('libs/java_websocket.jar')
    ...
}
```

- in `AndroidManifest.xml`, add permissions:
```
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
    	...
```


### Option 2. `WsExample` (uses `org.java-websocket`)

- in `build.gradle (Module...)`:
```
dependencies {
	...
    implementation 'org.java-websocket:Java-WebSocket:1.5.1'
    ...
}
```

- in `AndroidManifest.xml`, add permissions:
```
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
    	...
```





