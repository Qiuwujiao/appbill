[app]
title = 截图记账APP
package.name = billocr
package.domain = org.bill

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,db
version = 1.0

# 核心依赖（适配安卓编译）
requirements = python3,kivy==2.2.1,kivymd==1.2.0,pillow,requests,urllib3,chardet,idna,certifi,plyer

android.accept_sdk_license = True

# 安卓基础配置
orientation = portrait
fullscreen = 0
android.api = 33
android.ndk = 25b
android.skip_update = False  
# 原来的True会跳过SDK更新，改成False让它自动安装工具
android.buildtools = 33.0.2
android.sdk_path = /home/qiuwujiao/.buildozer/android/platform/android-sdk
android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True
android.use_aapt2 = True

# 关键权限（必须加：网络、存储、读写文件）
android.androidtheme = @android:style/Theme.Material.Light.NoActionBar

# 关闭多余编译项
android.add_assets = .

# 强制使用你本地已经下载好的p4a，完全跳过git检查和下载
p4a.source_dir = /home/qiuwujiao/python-for-android
p4a.extra_args = --break-system-packages --no-download

