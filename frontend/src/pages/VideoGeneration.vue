<template>
  <div class="max-w-6xl mx-auto space-y-6">
    <!-- 页面标题 -->
    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">视频生成</h1>
      <p class="text-gray-600">使用AI技术生成高质量视频内容</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 左侧：输入和设置 -->
      <div class="space-y-6">
        <!-- 描述输入卡片 -->
        <div class="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <div class="flex items-center mb-4">
            <i class="fas fa-video text-xl text-indigo-500 mr-3"></i>
            <h2 class="text-lg font-semibold text-gray-900">视频描述</h2>
          </div>

          <textarea v-model="prompt" 
                    placeholder="请输入您想要生成的视频描述..."
                    class="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                    rows="4"></textarea>

          <!-- 示例提示词 -->
          <div class="mt-4">
            <p class="text-sm text-gray-600 mb-2">示例提示词：</p>
            <div class="grid grid-cols-1 gap-2">
              <button v-for="example in examplePrompts" :key="example"
                      @click="prompt = example"
                      class="text-left px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-indigo-100 hover:text-indigo-700 transition-colors">
                {{ example }}
              </button>
            </div>
          </div>
        </div>

        <!-- 生成设置 -->
        <div class="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <div class="flex items-center mb-4">
            <i class="fas fa-cog text-xl text-blue-500 mr-3"></i>
            <h2 class="text-lg font-semibold text-gray-900">生成设置</h2>
          </div>

          <div class="space-y-4">
            <!-- 视频时长 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">视频时长</label>
              <select v-model="duration" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
                <option value="5">5秒</option>
                <option value="10">10秒</option>
                <option value="15">15秒</option>
                <option value="30">30秒</option>
              </select>
            </div>

            <!-- 视频质量 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">视频质量</label>
              <select v-model="quality" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
                <option value="standard">标准 (720p)</option>
                <option value="high">高清 (1080p)</option>
                <option value="ultra">超高清 (4K)</option>
              </select>
            </div>

            <!-- 视频风格 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">视频风格</label>
              <select v-model="style" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
                <option value="realistic">写实风格</option>
                <option value="cinematic">电影风格</option>
                <option value="animated">动画风格</option>
                <option value="artistic">艺术风格</option>
              </select>
            </div>

            <!-- 帧率 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">帧率</label>
              <select v-model="frameRate" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
                <option value="24">24 FPS</option>
                <option value="30">30 FPS</option>
                <option value="60">60 FPS</option>
              </select>
            </div>
          </div>

          <button @click="generateVideo" 
                  :disabled="loading || !prompt.trim()"
                  class="w-full mt-6 bg-indigo-600 text-white py-3 px-6 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors">
            <i v-if="loading" class="fas fa-spinner fa-spin mr-2"></i>
            {{ loading ? '生成中...' : '生成视频' }}
          </button>
        </div>
      </div>

      <!-- 右侧：结果显示 -->
      <div class="space-y-6">
        <!-- 生成进度 -->
        <div v-if="loading" class="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <div class="flex items-center mb-4">
            <i class="fas fa-clock text-xl text-orange-500 mr-3"></i>
            <h2 class="text-lg font-semibold text-gray-900">生成进度</h2>
          </div>
          
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">{{ progressStatus }}</span>
              <span class="text-sm text-gray-600">{{ progressPercent }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-indigo-600 h-2 rounded-full transition-all duration-300" 
                   :style="{ width: progressPercent + '%' }"></div>
            </div>
            <p class="text-sm text-gray-600">预计剩余时间: {{ estimatedTime }}</p>
          </div>
        </div>

        <!-- 生成结果 -->
        <div v-if="result" class="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <div class="flex items-center mb-4">
            <i class="fas fa-play-circle text-xl text-green-500 mr-3"></i>
            <h2 class="text-lg font-semibold text-gray-900">生成结果</h2>
          </div>

          <!-- 视频播放器 -->
          <div v-if="result.video_path" class="mb-4">
            <video :src="getVideoUrl(result.video_path)" 
                   controls 
                   class="w-full rounded-lg shadow-md"
                   :poster="result.thumbnail_path ? getVideoUrl(result.thumbnail_path) : ''">
              您的浏览器不支持视频播放。
            </video>
          </div>

          <!-- 视频信息 -->
          <div class="text-sm text-gray-600 space-y-1">
            <p><strong>原始提示词：</strong>{{ result.original_prompt }}</p>
            <p v-if="result.optimized_prompt"><strong>优化提示词：</strong>{{ result.optimized_prompt }}</p>
            <p><strong>视频时长：</strong>{{ result.duration }}秒</p>
            <p><strong>视频质量：</strong>{{ result.quality }}</p>
            <p><strong>视频风格：</strong>{{ result.style }}</p>
            <p><strong>帧率：</strong>{{ result.frame_rate }} FPS</p>
            <p v-if="result.file_size"><strong>文件大小：</strong>{{ formatFileSize(result.file_size) }}</p>
            <p v-if="result.processing_time"><strong>生成时间：</strong>{{ result.processing_time }}秒</p>
          </div>

          <!-- 下载按钮 -->
          <div class="mt-4 flex space-x-2">
            <a v-if="result.video_path" 
               :href="getVideoUrl(result.video_path)" 
               download
               class="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors text-center">
              <i class="fas fa-download mr-2"></i>
              下载视频
            </a>
            <button @click="shareVideo" 
                    class="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
              <i class="fas fa-share mr-2"></i>
              分享视频
            </button>
          </div>
        </div>

        <!-- 使用说明 -->
        <div v-if="!result && !loading" class="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <div class="flex items-center mb-4">
            <i class="fas fa-info-circle text-xl text-blue-500 mr-3"></i>
            <h2 class="text-lg font-semibold text-gray-900">使用说明</h2>
          </div>
          <div class="space-y-3 text-gray-600">
            <div class="flex items-start">
              <span class="bg-indigo-100 text-indigo-800 rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium mr-3 mt-0.5">1</span>
              <p>输入详细的视频场景描述</p>
            </div>
            <div class="flex items-start">
              <span class="bg-indigo-100 text-indigo-800 rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium mr-3 mt-0.5">2</span>
              <p>选择视频时长、质量和风格</p>
            </div>
            <div class="flex items-start">
              <span class="bg-indigo-100 text-indigo-800 rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium mr-3 mt-0.5">3</span>
              <p>点击"生成视频"开始创作</p>
            </div>
            <div class="flex items-start">
              <span class="bg-indigo-100 text-indigo-800 rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium mr-3 mt-0.5">4</span>
              <p>等待AI生成高质量视频</p>
            </div>
          </div>

          <div class="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div class="flex items-start">
              <i class="fas fa-lightbulb text-yellow-600 mt-1 mr-3"></i>
              <div class="text-yellow-800">
                <p class="font-medium mb-1">提示词建议：</p>
                <p class="text-sm">描述具体的场景、动作、光线和氛围。包含摄像机运动、角度变化等细节可以获得更好的效果。</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/services/api'

export default {
  name: 'VideoGeneration',
  setup() {
    const prompt = ref('')
    const duration = ref('10')
    const quality = ref('high')
    const style = ref('realistic')
    const frameRate = ref('30')
    const loading = ref(false)
    const result = ref(null)
    const progressPercent = ref(0)
    const progressStatus = ref('')
    const estimatedTime = ref('')

    const examplePrompts = ref([
      '一只小猫在花园里玩耍，阳光透过树叶洒下',
      '未来城市的街道，飞行汽车穿梭其中',
      '海浪拍打着沙滩，日落时分的美丽景色',
      '森林中的小溪缓缓流淌，鸟儿在枝头歌唱',
      '雪山之巅的壮丽景色，云雾缭绕',
      '宇宙中的星系旋转，星光闪烁',
      '古老城堡的庭院，月光下的神秘氛围',
      '热带雨林中的瀑布，水花四溅'
    ])

    const generateVideo = async () => {
      if (!prompt.value.trim()) {
        ElMessage.warning('请输入视频描述')
        return
      }

      loading.value = true
      result.value = null
      progressPercent.value = 0
      progressStatus.value = '开始生成...'
      estimatedTime.value = '计算中...'

      // 模拟进度更新
      const progressInterval = setInterval(() => {
        if (progressPercent.value < 90) {
          progressPercent.value += Math.random() * 10
          if (progressPercent.value < 30) {
            progressStatus.value = '分析提示词...'
            estimatedTime.value = '约2分钟'
          } else if (progressPercent.value < 60) {
            progressStatus.value = '生成视频帧...'
            estimatedTime.value = '约1分钟'
          } else {
            progressStatus.value = '合成视频...'
            estimatedTime.value = '约30秒'
          }
        }
      }, 1000)

      try {
        const response = await api.post('/api/video-generation', {
          prompt: prompt.value,
          duration: parseInt(duration.value),
          quality: quality.value,
          style: style.value,
          frame_rate: parseInt(frameRate.value)
        })

        clearInterval(progressInterval)
        progressPercent.value = 100
        progressStatus.value = '生成完成！'

        if (response.data.success) {
          result.value = response.data
          ElMessage.success('视频生成成功！')
        } else {
          throw new Error(response.data.error || '生成失败')
        }
      } catch (error) {
        clearInterval(progressInterval)
        console.error('生成失败:', error)
        ElMessage.error(error.message || '生成失败，请重试')
      } finally {
        loading.value = false
      }
    }

    const getVideoUrl = (videoPath) => {
      return videoPath ? `/${videoPath}` : ''
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const shareVideo = () => {
      if (navigator.share && result.value?.video_path) {
        navigator.share({
          title: '我生成的AI视频',
          text: result.value.original_prompt,
          url: window.location.href
        })
      } else {
        // 复制链接到剪贴板
        navigator.clipboard.writeText(window.location.href)
        ElMessage.success('链接已复制到剪贴板')
      }
    }

    return {
      prompt,
      duration,
      quality,
      style,
      frameRate,
      loading,
      result,
      progressPercent,
      progressStatus,
      estimatedTime,
      examplePrompts,
      generateVideo,
      getVideoUrl,
      formatFileSize,
      shareVideo
    }
  }
}
</script>

<style scoped>
/* 组件特定样式 */
</style>
