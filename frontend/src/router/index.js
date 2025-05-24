/**
 * Vue Router 配置
 * 定义应用的路由规则
 */

import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
import Home from '../pages/Home.vue'
import ImageQA from '../pages/ImageQA.vue'
import ImageGeneration from '../pages/ImageGeneration.vue'
import ImageEditing from '../pages/ImageEditing.vue'
import ObjectDetection from '../pages/ObjectDetection.vue'
import ImageSegmentation from '../pages/ImageSegmentation.vue'
import VideoGeneration from '../pages/VideoGeneration.vue'
import Settings from '../pages/Settings.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: '首页'
    }
  },
  {
    path: '/image-qa',
    name: 'ImageQA',
    component: ImageQA,
    meta: {
      title: '图像问答'
    }
  },
  {
    path: '/image-generation',
    name: 'ImageGeneration',
    component: ImageGeneration,
    meta: {
      title: '图像生成'
    }
  },
  {
    path: '/image-editing',
    name: 'ImageEditing',
    component: ImageEditing,
    meta: {
      title: '图像编辑'
    }
  },
  {
    path: '/object-detection',
    name: 'ObjectDetection',
    component: ObjectDetection,
    meta: {
      title: '目标检测'
    }
  },
  {
    path: '/image-segmentation',
    name: 'ImageSegmentation',
    component: ImageSegmentation,
    meta: {
      title: '图像分割'
    }
  },
  {
    path: '/video-generation',
    name: 'VideoGeneration',
    component: VideoGeneration,
    meta: {
      title: '视频生成'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: {
      title: '设置'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - Gemini图像处理应用`
  }
  next()
})

export default router
