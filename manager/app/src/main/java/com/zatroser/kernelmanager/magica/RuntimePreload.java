package com.zatroser.kernelmanager.magica;

import android.app.ZygotePreload;
import android.content.pm.ApplicationInfo;
import android.util.Log;

import androidx.annotation.NonNull;

import java.io.File;

public class RuntimePreload implements ZygotePreload {
    public static final String TAG = "KernelSUMagica";

    private static native void forkDontCareAndExecKsud(String ksudPath, String packageName);

    @Override
    public void doPreload(@NonNull ApplicationInfo appInfo) {
        File f = new File(appInfo.nativeLibraryDir, "libdaemon.so");
        try {
            System.loadLibrary("linyusu");
            Log.d(TAG, "executing magica ...");
            forkDontCareAndExecKsud(f.getAbsolutePath(), appInfo.packageName);
        } catch (Throwable t) {
            Log.e(TAG, "failed to late load", t);
        }
    }
}
