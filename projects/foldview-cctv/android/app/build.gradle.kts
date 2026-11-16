plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.plugin.compose")
}
android {
    namespace = "org.foldview.cctv"
    compileSdk = 37
    defaultConfig {
        applicationId = "org.foldview.cctv"
        minSdk = 29
        targetSdk = 37
        versionCode = 16
        versionName = "0.12.2"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    flavorDimensions += "device"
    productFlavors {
        create("fold") {
            dimension = "device"
            // Preserve the existing application ID and encrypted camera vault.
            resValue("string", "app_name", "GARDA CCTV FOLD edition")
            buildConfigField("boolean", "IS_FOLD_EDITION", "true")
        }
        create("standard") {
            dimension = "device"
            // Independent app, installable alongside Fold edition.
            applicationId = "org.garda.cctv.standard"
            resValue("string", "app_name", "GARDA CCTV Standard edition")
            buildConfigField("boolean", "IS_FOLD_EDITION", "false")
        }
    }
    buildFeatures {
        compose = true
        buildConfig = true
        resValues = true
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}
dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2026.09.00")
    implementation(composeBom)
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.core:core:1.17.0")
    implementation("androidx.activity:activity-compose:1.13.0")
    implementation("androidx.media3:media3-exoplayer:1.11.1")
    implementation("androidx.media3:media3-exoplayer-rtsp:1.11.1")
    implementation("androidx.media3:media3-ui:1.11.1")
    // Stable 1.1.0; SAF tree access for USB HDD/SSD destination.
    implementation("androidx.documentfile:documentfile:1.1.0")
    testImplementation("junit:junit:4.13.2")
}
