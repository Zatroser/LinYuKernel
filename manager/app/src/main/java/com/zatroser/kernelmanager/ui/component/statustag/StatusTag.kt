package com.zatroser.kernelmanager.ui.component.statustag

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import com.zatroser.kernelmanager.ui.LocalUiMode
import com.zatroser.kernelmanager.ui.UiMode

@Composable
fun StatusTag(
    label: String,
    modifier: Modifier = Modifier,
    backgroundColor: Color,
    contentColor: Color
) {
    when (LocalUiMode.current) {
        UiMode.Miuix -> StatusTagMiuix(label, modifier, backgroundColor, contentColor)
        UiMode.Material -> StatusTagMaterial(label, modifier, backgroundColor, contentColor)
    }
}
