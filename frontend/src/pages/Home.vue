<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
    <!-- 主页内容 -->
    <div class="max-w-7xl mx-auto px-4 py-12">
      <!-- 欢迎标题 -->
      <div class="text-center mb-16">
        <h1 class="text-5xl font-bold text-gray-900 mb-4">
          Gemini 图像处理平台
        </h1>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">
          基于Google Gemini AI的强大图像处理平台，提供图像问答、生成、编辑、检测和分割等全方位服务
        </p>
      </div>

      <!-- 功能卡片网格 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
        <!-- 图像问答 -->
        <div class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow cursor-pointer border"
             @click="navigateTo('/image-qa')">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <i class="fas fa-question-circle text-2xl text-blue-600"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 ml-4">图像问答</h3>
          </div>
          <p class="text-gray-600 mb-4">上传图像并提问，获得AI驱动的详细中文回答</p>
          <div class="flex items-center text-blue-600 font-medium">
            <span>开始使用</span>
            <i class="fas fa-arrow-right ml-2"></i>
          </div>
        </div>

        <!-- 图像生成 -->
        <div class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow cursor-pointer border"
             @click="navigateTo('/image-generation')">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <i class="fas fa-magic text-2xl text-purple-600"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 ml-4">图像生成</h3>
          </div>
          <p class="text-gray-600 mb-4">使用中文描述创建精美图像，支持多种AI模型</p>
          <div class="flex items-center text-purple-600 font-medium">
            <span>开始创作</span>
            <i class="fas fa-arrow-right ml-2"></i>
          </div>
        </div>

        <!-- 图像编辑 -->
        <div class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow cursor-pointer border"
             @click="navigateTo('/image-editing')">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <i class="fas fa-edit text-2xl text-green-600"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 ml-4">图像编辑</h3>
          </div>
          <p class="text-gray-600 mb-4">使用AI技术和传统算法编辑和修改您的图像</p>
          <div class="flex items-center text-green-600 font-medium">
            <span>开始编辑</span>
            <i class="fas fa-arrow-right ml-2"></i>
          </div>
        </div>

        <!-- 目标检测 -->
        <div class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow cursor-pointer border"
             @click="navigateTo('/object-detection')">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <i class="fas fa-search text-2xl text-red-600"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 ml-4">目标检测</h3>
          </div>
          <p class="text-gray-600 mb-4">识别和定位图像中的物体，支持多种检测算法</p>
          <div class="flex items-center text-red-600 font-medium">
            <span>开始检测</span>
            <i class="fas fa-arrow-right ml-2"></i>
          </div>
        </div>

        <!-- 图像分割 -->
        <div class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow cursor-pointer border"
             @click="navigateTo('/image-segmentation')">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <i class="fas fa-cut text-2xl text-yellow-600"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 ml-4">图像分割</h3>
          </div>
          <p class="text-gray-600 mb-4">精确分割图像中的不同区域和对象</p>
          <div class="flex items-center text-yellow-600 font-medium">
            <span>开始分割</span>
            <i class="fas fa-arrow-right ml-2"></i>
          </div>
        </div>

        <!-- 视频生成 -->
        <div class="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow cursor-pointer border"
             @click="navigateTo('/video-generation')">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
              <i class="fas fa-video text-2xl text-indigo-600"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 ml-4">视频生成</h3>
          </div>
          <p class="text-gray-600 mb-4">使用AI技术生成高质量视频内容</p>
          <div class="flex items-center text-indigo-600 font-medium">
            <span>开始生成</span>
            <i class="fas fa-arrow-right ml-2"></i>
          </div>
        </div>
      </div>

      <!-- 特性介绍 -->
      <div class="bg-white rounded-xl p-8 shadow-lg border">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 text-center">平台特性</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-brain text-2xl text-blue-600"></i>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">AI驱动</h3>
            <p class="text-gray-600">基于Google Gemini最新AI技术，提供智能化图像处理服务</p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-language text-2xl text-green-600"></i>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">中文优化</h3>
            <p class="text-gray-600">专为中文用户优化，支持中文提示词和回答</p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-cogs text-2xl text-purple-600"></i>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">多功能集成</h3>
            <p class="text-gray-600">集成多种图像处理功能，一站式解决所有需求</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'Home',
  setup() {
    const router = useRouter()

    const navigateTo = (path) => {
      router.push(path)
    }

    return {
      navigateTo
    }
  }
}
</script>

<style scoped>
/* 组件特定样式 */
</style>
