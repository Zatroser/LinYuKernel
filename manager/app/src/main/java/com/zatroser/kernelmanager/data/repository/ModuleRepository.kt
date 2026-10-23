package com.zatroser.kernelmanager.data.repository

import com.zatroser.kernelmanager.data.model.Module
import com.zatroser.kernelmanager.data.model.ModuleUpdateInfo

interface ModuleRepository {
    suspend fun getModules(): Result<List<Module>>
    suspend fun checkUpdate(module: Module): Result<ModuleUpdateInfo>
}
