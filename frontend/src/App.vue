<template>
  <div id="app" :class="{ 'dark': isDarkMode }">
    <!-- 导航栏 -->
    <nav class="bg-white shadow-lg border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex justify-between items-center h-16">
          <!-- Logo和标题 -->
          <div class="flex items-center">
            <router-link to="/" class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <i class="fas fa-brain text-white text-lg"></i>
              </div>
              <span class="text-xl font-bold text-gray-900">Gemini 图像处理</span>
            </router-link>
          </div>

          <!-- 导航菜单 -->
          <div class="hidden md:flex items-center space-x-8">
            <router-link to="/" class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
              首页
            </router-link>
            <router-link to="/image-qa" class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
              图像问答
            </router-link>
            <router-link to="/image-generation" class="text-gray-700 hover:text-purple-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
              图像生成
            </router-link>
            <router-link to="/image-editing" class="text-gray-700 hover:text-green-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
              图像编辑
            </router-link>
            <router-link to="/object-detection" class="text-gray-700 hover:text-red-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
              目标检测
            </router-link>
            <router-link to="/image-segmentation" class="text-gray-700 hover:text-yellow-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
              图像分割
            </router-link>
            <router-link to="/video-generation" class="text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
              视频生成
            </router-link>
            <router-link to="/settings" class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors">
              <i class="fas fa-cog"></i>
            </router-link>
          </div>

          <!-- 移动端菜单按钮 -->
          <div class="md:hidden">
            <button @click="mobileMenuOpen = !mobileMenuOpen" class="text-gray-700 hover:text-gray-900 focus:outline-none">
              <i class="fas fa-bars text-xl"></i>
            </button>
          </div>
        </div>

        <!-- 移动端菜单 -->
        <div v-if="mobileMenuOpen" class="md:hidden">
          <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-gray-200">
            <router-link to="/" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50">
              首页
            </router-link>
            <router-link to="/image-qa" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50">
              图像问答
            </router-link>
            <router-link to="/image-generation" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-purple-600 hover:bg-gray-50">
              图像生成
            </router-link>
            <router-link to="/image-editing" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-green-600 hover:bg-gray-50">
              图像编辑
            </router-link>
            <router-link to="/object-detection" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-red-600 hover:bg-gray-50">
              目标检测
            </router-link>
            <router-link to="/image-segmentation" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-yellow-600 hover:bg-gray-50">
              图像分割
            </router-link>
            <router-link to="/video-generation" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-indigo-600 hover:bg-gray-50">
              视频生成
            </router-link>
            <router-link to="/settings" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50">
              设置
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主要内容区域 -->
    <main class="min-h-screen bg-gray-50 py-8">
      <router-view />
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'App',
  setup() {
    const isDarkMode = ref(false)
    const mobileMenuOpen = ref(false)

    // 初始化主题
    onMounted(() => {
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme) {
        isDarkMode.value = savedTheme === 'dark'
      } else {
        // 检测系统主题偏好
        isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
      }

      // 应用主题
      document.documentElement.setAttribute('data-theme', isDarkMode.value ? 'dark' : 'light')
    })

    return {
      isDarkMode,
      mobileMenuOpen
    }
  }
}
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
  transition: all 0.3s ease;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 0 1rem;
  }
}
</style>
