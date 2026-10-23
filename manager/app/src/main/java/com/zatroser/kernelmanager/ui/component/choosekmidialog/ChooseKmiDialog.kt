package com.zatroser.kernelmanager.ui.component.choosekmidialog

import androidx.compose.runtime.Composable
import com.zatroser.kernelmanager.ui.LocalUiMode
import com.zatroser.kernelmanager.ui.UiMode

@Composable
fun ChooseKmiDialog(
    show: Boolean,
    onDismissRequest: () -> Unit,
    onSelected: (String?) -> Unit
) {
    when (LocalUiMode.current) {
        UiMode.Miuix -> ChooseKmiDialogMiuix(show, onDismissRequest, onSelected)
        UiMode.Material -> ChooseKmiDialogMaterial(show, onDismissRequest, onSelected)
    }
}
