# Android

The Gradle wrapper JAR is not tracked in version control. If it is missing, download it from the official Gradle distributions:

https://services.gradle.org/distributions/gradle-8.5-bin.zip

Extract `gradle-wrapper.jar` from the archive's `gradle/wrapper/` directory and place it at `android/gradle/wrapper/gradle-wrapper.jar`.
=======
# Rumessendger Android Client

This directory contains a minimal Android client that connects to the ejabberd
server used by the project. It demonstrates basic chat functionality and push
notification registration (XEP‑0357) using the [Smack](https://www.igniterealtime.org/projects/smack/) library.

## Configuration

Update the XMPP connection details in
[`app/src/main/java/com/rumessendger/XmppConfig.kt`](app/src/main/java/com/rumessendger/XmppConfig.kt)
with your server domain, host and user credentials.

Push notification registration requires a device token (for example from FCM).
Invoke `XmppClient.registerPush(token)` once a token is available.

## Build

The Gradle wrapper JAR (`gradle/wrapper/gradle-wrapper.jar`) is excluded from
version control. Download it before running Gradle:

```bash
curl -o gradle/wrapper/gradle-wrapper.jar \
  https://raw.githubusercontent.com/gradle/gradle/v8.4.0/gradle/wrapper/gradle-wrapper.jar
```

```bash
cd android
./gradlew assembleDebug
```

The first build downloads the Android Gradle plugin and Smack dependencies.

## Run

Install the generated APK from `app/build/outputs/apk/` onto an Android device
or emulator:

```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

Once installed, the app connects to the configured server on startup and listens
for incoming messages.

