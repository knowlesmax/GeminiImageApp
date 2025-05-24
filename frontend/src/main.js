/**
 * Vue.js 3 应用主入口文件
 * 初始化Vue应用和全局配置
 */

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

// 导入样式
import './assets/css/style.css'
import './assets/css/themes.css'

// 创建Vue应用实例
const app = createApp(App)

// 使用路由
app.use(router)

// 使用Element Plus
app.use(ElementPlus, {
  locale: zhCn
})

// 全局配置
app.config.globalProperties.$apiBase = '/api'

// 挂载应用
app.mount('#app')
