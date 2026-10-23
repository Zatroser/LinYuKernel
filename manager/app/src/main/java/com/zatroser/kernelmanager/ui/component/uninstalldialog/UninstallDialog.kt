package com.zatroser.kernelmanager.ui.component.uninstalldialog

import androidx.compose.runtime.Composable
import com.zatroser.kernelmanager.ui.LocalUiMode
import com.zatroser.kernelmanager.ui.UiMode

@Composable
fun UninstallDialog(
    show: Boolean,
    onDismissRequest: () -> Unit
) {
    when (LocalUiMode.current) {
        UiMode.Miuix -> UninstallDialogMiuix(show, onDismissRequest)
        UiMode.Material -> UninstallDialogMaterial(show, onDismissRequest)
    }
}
