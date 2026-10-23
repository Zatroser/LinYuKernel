# LinYuKernel

Fork of [tiann/KernelSU](https://github.com/tiann/KernelSU).

- Manager name: **LinYuKernel**
- Android application ID: **com.zatroser.kernelmanager**
- Kernel manager identity: the package above plus the certificate in
  [`signing/manager.der`](signing/manager.der).
- Manager updates: `Zatroser/LinYuKernel` releases.

The Kotlin/JNI implementation namespace remains `me.weishu.kernelsu`.
It is separate from the installed application's package ID.

## Manager icon

The supplied artwork is preserved in `branding/manager-icon.png`. Launcher,
splash, in-app and themed icons use that image. To regenerate the raster assets:

```sh
python -m pip install Pillow
python scripts/generate_manager_icons.py
```

## Builds

Run **Build LinYuKernel** in GitHub Actions. The `manager` artifact contains
the final signed APK with the rebuilt daemons and modules. KMI-specific
`aarch64-*-lkm` and `x86_64-*-lkm` artifacts contain the kernel modules.
`manager-gradle` is an intermediate APK, not the installable deliverable.

Release builds require repository Actions secrets `KEYSTORE` (base64 JKS),
`KEYSTORE_PASSWORD`, `KEY_ALIAS`, and `KEY_PASSWORD`. The signing key must
match `signing/manager.der`. The workflow checks this before compiling and
verifies the final APK's package, v2 certificate and cryptographic signature.
Never commit the private signing key or passwords.

The kernel defaults in `kernel/Kbuild` pin the same certificate, including
for standalone module builds. Signature verification remains enabled.
PR builds retain an isolated `.pr` package and temporary matching certificate.

For a local release build, configure the four signing properties documented
in `manager/sign.example.properties`, using the release keystore, then follow
the upstream build procedure. For verification with Android SDK build-tools:

```sh
python3 scripts/verify_manager_identity.py
python3 scripts/verify_manager_identity.py --apk path/to/LinYuKernel.apk
python3 scripts/verify_manager_identity.py --module path/to/kernelsu.ko
```

Original licenses and upstream attribution are retained. Device installation
and boot testing are separate from CI compilation and identity verification.
