package com.zatroser.kernelmanager.data.repository

import com.zatroser.kernelmanager.data.model.AppInfo

interface SuperUserRepository {
    suspend fun getAppList(): Result<Pair<List<AppInfo>, List<Int>>>
    suspend fun refreshProfiles(currentApps: List<AppInfo>): Result<List<AppInfo>>
}
